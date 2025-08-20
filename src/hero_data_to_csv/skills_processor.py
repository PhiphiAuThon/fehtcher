"""
Skills processing module
Handles conversion of skills data to CSV format.
"""

import csv
import io
import re

# Cache for field mappings to avoid repeated calculations
_field_mapping_cache = {}

# Optimized CSV utilities for better performance
def _parse_csv_line_fast(line: str) -> list:
    """
    Fast CSV line parsing that properly handles commas in quoted fields.
    Optimized alternative to csv.reader for single line parsing.
    """
    if not line.strip():
        return []
    
    # Use csv.reader for proper comma handling in quoted fields
    # This is more reliable than regex for complex CSV parsing
    reader = csv.reader([line])
    try:
        return next(reader)
    except (StopIteration, csv.Error):
        # Fallback: simple split if CSV parsing fails
        return [field.strip() for field in line.split(',')]

def _build_csv_line_fast(fields: list) -> str:
    """
    Fast CSV line building that properly escapes fields with commas.
    Optimized alternative to csv.writer for single line building.
    """
    if not fields:
        return ""
    
    # Use csv.writer for proper escaping of fields with commas
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)
    return output.getvalue().strip()

def _extract_fields_by_indexes(line: str, field_indexes: list) -> list:
    """
    Extract specific fields from CSV line by index positions.
    Handles commas in quoted fields properly.
    """
    fields = _parse_csv_line_fast(line)
    return [fields[i] if i < len(fields) else "" for i in field_indexes]

def _get_field_indexes_cached(header_fields: list, field_type: str) -> list:
    """
    Get field indexes for specific field type with caching for better performance.
    
    Args:
        header_fields: List of header field names
        field_type: Type of field extraction ('hero_skills', 'skill', 'hero')
        
    Returns:
        List of field indexes to extract
    """
    # Create cache key
    header_key = ','.join(header_fields)
    cache_key = f"{field_type}:{header_key}"
    
    if cache_key in _field_mapping_cache:
        return _field_mapping_cache[cache_key]
    
    # Calculate field indexes based on type
    if field_type == 'hero_skills':
        # For hero skills: Key=0, Name=1, Default=last-1, Unlock=last
        field_indexes = [0]  # Always keep Key (first field)
        if len(header_fields) > 1:
            field_indexes.append(1)  # Keep Name (second field)
        if len(header_fields) > 2:
            field_indexes.append(len(header_fields) - 2)  # Default (second to last)
        if len(header_fields) > 1:
            field_indexes.append(len(header_fields) - 1)  # Unlock (last)
        
        # Remove duplicates and sort indexes
        field_indexes = sorted(list(set(field_indexes)))
        
    elif field_type == 'hero_skills_passives':
        # Special case for Passives: Key, Name, SP, Unlock
        # Passives structure is different: we want Key=0, Name=1, SP=2, Unlock=3
        # But the actual data might have Type instead of Name at position 1
        field_indexes = []
        
        # Always include Key (position 0)
        field_indexes.append(0)
        
        # For Passives, we need to find Name field specifically
        name_idx = None
        sp_idx = None
        unlock_idx = None
        
        for i, field_name in enumerate(header_fields):
            if field_name.strip().lower() == 'name':
                name_idx = i
            elif field_name.strip().lower() == 'sp':
                sp_idx = i
            elif field_name.strip().lower() == 'unlock':
                unlock_idx = i
        
        # Add the fields we found
        if name_idx is not None:
            field_indexes.append(name_idx)
        if sp_idx is not None:
            field_indexes.append(sp_idx)
        if unlock_idx is not None:
            field_indexes.append(unlock_idx)
        
        # Sort the indexes
        field_indexes = sorted(field_indexes)
        
    elif field_type == 'skill':
        # For skill tables: exclude Key, Unlock, Default
        exclude_fields = {"Key", "Unlock", "Default"}
        field_indexes = [i for i, field_name in enumerate(header_fields) 
                        if field_name.strip() and field_name not in exclude_fields]
        
    elif field_type == 'hero':
        # For hero skill tables: exclude Key, Unlock, reorder by desired fields
        exclude_fields = {"Key", "Unlock"}
        desired_order = ["Name", "Type", "Description", "SP"]
        
        # Build mapping of available fields
        available_fields = {field_name: i for i, field_name in enumerate(header_fields) 
                           if field_name.strip() and field_name not in exclude_fields}
        
        # Build indexes in desired order - only include fields that exist
        field_indexes = []
        for desired_field in desired_order:
            if desired_field in available_fields:
                field_indexes.append(available_fields[desired_field])
        
        # If no desired fields found, fall back to all non-excluded fields
        if not field_indexes:
            field_indexes = [i for i, field_name in enumerate(header_fields) 
                           if field_name.strip() and field_name not in exclude_fields]
    
    else:
        field_indexes = list(range(len(header_fields)))
    
    # Cache the result
    _field_mapping_cache[cache_key] = field_indexes
    return field_indexes


def extract_skills_from_output(tables_csv_output):
    """
    Extract skills tables and process them for hero skill files.
    Keeps only Key, Name, Default, and Unlock fields.
    
    Args:
        tables_csv_output: Output from hero_table_to_csv_lines
        
    Returns:
        Dictionary of skills tables with processed CSV lines
    """
    keep_tables = False
    skills_tables = {}
    
    for table_name, (header_line, csv_lines) in tables_csv_output.items():
        if table_name == "Weapons":
            keep_tables = True
        
        if not keep_tables:
            continue
        
        # Process the table data to keep only Key, Name, Default, Unlock fields
        processed_lines = process_hero_skills_table(header_line, csv_lines, table_name)
        skills_tables[table_name] = processed_lines
    
    return skills_tables


def process_hero_skills_table(header_line, csv_lines, table_name=None):
    """
    Process a hero skills table to keep only Key, Name, Default, and Unlock fields.
    
    Args:
        header_line: CSV header line (starts with "Key,")
        csv_lines: List of CSV data lines (already includes header)
        table_name: Name of the table (used for special handling)
        
    Returns:
        List of processed CSV lines with only Key, Name, Default, Unlock fields
    """
    if not csv_lines:
        return []
    
    # Get the wanted field indexes using cached mapping
    header_fields = _parse_csv_line_fast(csv_lines[0])
    
    # Use special field mapping for Passives table
    if table_name and table_name.lower() == 'passives':
        wanted_indexes = _get_field_indexes_cached(header_fields, 'hero_skills_passives')
    else:
        wanted_indexes = _get_field_indexes_cached(header_fields, 'hero_skills')
    
    processed_lines = []
    for line in csv_lines:
        if not line.strip():
            continue
            
        try:
            # Extract only the fields we need using optimized function
            filtered_fields = _extract_fields_by_indexes(line, wanted_indexes)
            
            if filtered_fields and any(field.strip() for field in filtered_fields):
                # Build CSV line with proper escaping
                processed_line = _build_csv_line_fast(filtered_fields)
                processed_lines.append(processed_line)
                
        except Exception as e:
            print(f"Warning: CSV parsing failed for line: {line[:50]}... Error: {e}")
            continue
    
    return processed_lines


def process_skill_csv(header_line, csv_lines, csv_type="skill"):
    """
    Process skill CSV data by keeping only relevant fields.
    
    Args:
        header_line: CSV header line
        csv_lines: List of CSV data lines
        csv_type: Either "skill" or "hero" to determine field filtering
        
    Returns:
        List of processed CSV lines with only relevant fields
    """
    if not csv_lines:
        return []
    
    # Parse header to get field names using optimized function
    header_fields = _parse_csv_line_fast(header_line)
    
    # Get field indexes using cached mapping
    field_indexes = _get_field_indexes_cached(header_fields, csv_type)
    
    # Process each line using optimized functions
    result = []
    for line in csv_lines:
        if not line.strip():
            continue
            
        try:
            # Extract fields using optimized function
            extracted_fields = _extract_fields_by_indexes(line, field_indexes)
            
            # Only add lines that have meaningful content
            if extracted_fields and any(field.strip() for field in extracted_fields):
                processed_line = _build_csv_line_fast(extracted_fields)
                result.append(processed_line)
                
        except Exception as e:
            print(f"Warning: Failed to process line: {line[:50]}... Error: {e}")
            continue
    
    return result


def extract_clean_skills(tables_csv_output):
    """
    Extract clean skills data without hero references for the skills folder.
    
    Args:
        tables_csv_output: Output from hero_table_to_csv_lines
        
    Returns:
        Dictionary of clean skills tables without Key field
    """
    keep_tables = False
    clean_skills_tables = {}
    
    for table_name, (header_line, csv_lines) in tables_csv_output.items():
        if table_name == "Weapons":
            keep_tables = True
        
        if not keep_tables:
            continue
        
        # Extract only the skill data without hero references
        if table_name == "Passives":
            # Passives table should exclude SP, Description, Type (hero type)
            clean_lines = process_skill_csv(header_line, csv_lines, "hero")
        else:
            # Other skill tables exclude Key, Unlock, Default (skill type)
            clean_lines = process_skill_csv(header_line, csv_lines, "skill")
        
        if clean_lines:
            clean_skills_tables[table_name] = clean_lines
    
    return clean_skills_tables






