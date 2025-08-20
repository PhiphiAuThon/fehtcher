"""
CSV Operations - CSV file handling
This module handles CSV-specific file operations like reading, writing, and merging CSV data.
"""

import os
import csv
from pathlib import Path

# Cache for file existence checks to reduce filesystem calls
_file_exists_cache = {}


def _file_exists_cached(filename: str) -> bool:
    """Check if file exists with caching to reduce filesystem calls"""
    if filename not in _file_exists_cache:
        _file_exists_cache[filename] = os.path.exists(filename)
    return _file_exists_cache[filename]


def _invalidate_file_cache(filename: str):
    """Invalidate cache entry when file is modified"""
    _file_exists_cache.pop(filename, None)


def get_first_field(csv_line: str) -> str:
    """Get the first field from a CSV line"""
    if not csv_line:
        return ""
    # Use partition instead of split for better performance when only need first field
    return csv_line.partition(",")[0]


def read_lines_excluding_id(filename: str, hero_id: str) -> list:
    """Read CSV lines from file, excluding lines with the specified hero ID"""
    if not _file_exists_cached(filename):
        return []
    
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    
    # Use list comprehension for better performance
    return [line for line in lines if hero_id not in line]


def write_lines_to_file(filename: str, lines: list):
    """Write lines to a file efficiently"""
    if not lines:
        # Create empty file if no lines
        with open(filename, "w", encoding="utf-8") as f:
            pass
    else:
        # Use join for more efficient writing - single I/O operation
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    
    # Invalidate cache since file was modified
    _invalidate_file_cache(filename)


def related_heroes_csv_to_file(csv_line: str, filename="related_heroes.csv"):
    """Save related heroes CSV line to file"""
    # Extract hero_id from the CSV line (first field)
    hero_id = get_first_field(csv_line)
    
    # Read existing lines and filter out lines that contain either the hero_id or icon_name
    if _file_exists_cached(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        # Use list comprehension for better performance
        filtered_lines = [line for line in lines if hero_id not in line]
    else:
        filtered_lines = []
    
    filtered_lines.append(csv_line)
    write_lines_to_file(filename, filtered_lines)


def info_dict_to_csv(info_dict, info_path):
    """Convert info dictionary to CSV and merge with existing data using atomic operations"""
    import tempfile
    import shutil
    
    # Read existing data first
    header, data_lines = read_csv_header_and_lines(info_path)
    fields = list(info_dict.keys())
    merged_header = list(header)
    for field in fields:
        if field not in merged_header:
            merged_header.append(field)
    value_line = [str(info_dict.get(field, "")) for field in merged_header]
    
    # Use Key field (which now contains the icon name)
    key_field = "Key"
    new_key = info_dict.get(key_field, "")
    
    # Create temporary file in the same directory as target file
    temp_dir = os.path.dirname(info_path) if os.path.dirname(info_path) else "."
    temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', dir=temp_dir)
    
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(merged_header)
            found = False
            
            # Write existing data, replacing if key matches
            for row in data_lines:
                row_dict = dict(zip(header, row))
                if row_dict.get(key_field, "") == new_key:
                    writer.writerow(value_line)
                    found = True
                else:
                    padded_row = [row_dict.get(field, "") for field in merged_header]
                    writer.writerow(padded_row)
            
            # Add new hero if not found in existing data
            if not found:
                writer.writerow(value_line)
        
        # Atomic move: replace original file only after successful write
        shutil.move(temp_path, info_path)
        
        # Invalidate cache since file was modified
        _invalidate_file_cache(info_path)
        
    except Exception as e:
        # Clean up temp file if something goes wrong
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise e


def csv_to_file(header, lines, filename, key_field):
    """Save CSV data to file with key-based deduplication"""
    existing_map = {}
    if _file_exists_cached(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_lines = f.read().splitlines()
        if existing_lines:
            file_header = existing_lines[0]
            for line in existing_lines[1:]:
                key = get_field_value(file_header, line, key_field)
                if key:
                    existing_map[key] = line
            header = file_header
    
    # Ensure header is a string
    if isinstance(header, list):
        header = ",".join(header)
    
    for line in lines[1:]:
        # Ensure line is a string
        if isinstance(line, list):
            line = ",".join(line)
        key = get_field_value(header, line, key_field)
        if key:
            existing_map[key] = line
    
    # More efficient: build all content then write once
    all_lines = [header] + list(existing_map.values())
    write_lines_to_file(filename, all_lines)


def read_csv_header_and_lines(info_path):
    """Read CSV header and data lines from file"""
    if _file_exists_cached(info_path):
        with open(info_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            lines = list(reader)
        if lines:
            header = lines[0]
            data_lines = lines[1:]
            return header, data_lines
    return [], []


def get_field_index(header, field_name):
    """Get the index of a field in the header"""
    if isinstance(header, str):
        header = header.split(",")
    
    for i, field in enumerate(header):
        if field.strip() == field_name.strip():
            return i
    return None


def get_field_value(header, line, field_name):
    """Get the value of a specific field from a CSV line"""
    index = get_field_index(header, field_name)
    if index is None:
        return None
    
    # Handle both string and list inputs
    if isinstance(line, list):
        return line[index] if len(line) > index else None
    
    # More efficient: only split up to the needed index + 1
    values = line.split(",", index + 1)
    return values[index] if len(values) > index else None


def hero_skills_to_file(header, lines, filename, key_field):
    """Save hero skills CSV data to file with proper hero-based replacement
    
    This function is specifically for hero skills where we want to:
    1. Remove all existing entries for the specific hero (by key_field)
    2. Add all new entries for that hero
    """
    # Read existing data
    existing_lines = []
    if _file_exists_cached(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_lines = f.read().splitlines()
    
    # Ensure header is a string
    if isinstance(header, list):
        header = ",".join(header)
    
    # Get the hero key from the new data (assuming all lines have the same key)
    hero_key = None
    if lines and len(lines) > 1:  # Skip header
        hero_key = get_field_value(header, lines[1], key_field)
    
    # Filter out existing entries for this hero, but keep other heroes' data
    filtered_lines = []
    if existing_lines:
        file_header = existing_lines[0]
        filtered_lines.append(file_header)  # Keep header
        
        for line in existing_lines[1:]:  # Process data lines
            line_key = get_field_value(file_header, line, key_field)
            # Only keep lines that don't match the hero key
            if line_key != hero_key:
                filtered_lines.append(line)
        
        # Use existing header if available
        header = file_header
    else:
        # No existing file, just use provided header
        if isinstance(header, list):
            header = ",".join(header)
        filtered_lines.append(header)
    
    # Add all new data for this hero
    for line in lines[1:]:  # Skip header in new data
        if isinstance(line, list):
            line = ",".join(line)
        filtered_lines.append(line)
    
    # Write all data back to file efficiently
    write_lines_to_file(filename, filtered_lines)
