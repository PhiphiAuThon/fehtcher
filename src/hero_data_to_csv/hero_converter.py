"""
Hero data to CSV conversion - Main orchestration
This module coordinates the conversion of hero data to CSV format.
"""

from .hero_info import hero_info_to_csv_fields
from .related_heroes import related_heroes_to_csv_line
from .table_processor import hero_table_to_csv_lines, extract_tables_from_output
from .skills_processor import (
    extract_skills_from_output, 
    extract_clean_skills,
    process_hero_skills_table,
    process_skill_csv
)

def hero_table_to_csv_data(hero_id: str, hero_data: dict):
    """
    Main function: Convert hero data to CSV format.
    This is the primary interface for the rest of the codebase.
    
    Args:
        hero_id: The hero's identifier
        hero_data: Dictionary containing hero information
        
    Returns:
        Dictionary with processed CSV data for different sections
    """
    # Remove empty column from Passives table CSV formatted string
    __remove_empty_column_from_passives(hero_data)
    
    info_dict = hero_info_to_csv_fields(hero_id, hero_data)
    # Use the computed Key (clean icon name) for all downstream CSVs
    key_for_csv = info_dict.get("Key", hero_id)
    related_heroes_csv_line = related_heroes_to_csv_line(key_for_csv, hero_data)
    
    # Single-pass processing: generate tables and extract all needed data in one go
    tables_csv_output = hero_table_to_csv_lines(key_for_csv, hero_data)
    
    # Process all extractions in a single pass for better performance
    tables_data, hero_skills_data, clean_skills_data = __extract_all_data_single_pass(tables_csv_output)
    
    data = {
        "Info": info_dict,
        "Related Heroes": related_heroes_csv_line,
        "Tables": tables_data,
        "Hero Skills": hero_skills_data,
        "Skills": clean_skills_data,
    }

    return data


def __remove_empty_column_from_passives(hero_data):
    """
    Remove empty column from Passives table CSV string.
    The Passives table has an empty column that needs to be removed.
    """
    if "Passives" not in hero_data or not hero_data["Passives"]:
        return
        
    passives_data = hero_data["Passives"]
    if not passives_data.strip():
        return
    
    # Use list comprehension for better performance
    lines = passives_data.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if line.strip():
            # Use CSV parsing to properly handle commas in quoted fields
            import csv
            import io
            try:
                reader = csv.reader([line])
                fields = next(reader)
                # Filter out empty fields
                cleaned_fields = [field for field in fields if field.strip()]
                if cleaned_fields:
                    # Rebuild line with proper CSV escaping
                    output = io.StringIO()
                    writer = csv.writer(output)
                    writer.writerow(cleaned_fields)
                    cleaned_lines.append(output.getvalue().strip())
            except (csv.Error, StopIteration):
                # Fallback to simple processing if CSV parsing fails
                fields = line.split(',')
                cleaned_fields = [field.strip() for field in fields if field.strip()]
                if cleaned_fields:
                    cleaned_lines.append(','.join(cleaned_fields))
    
    # Update the hero data with cleaned passives
    hero_data["Passives"] = '\n'.join(cleaned_lines)


def __extract_all_data_single_pass(tables_csv_output):
    """
    Extract all data types in a single pass for better performance.
    Replaces multiple separate extraction functions.
    
    Args:
        tables_csv_output: Output from hero_table_to_csv_lines
        
    Returns:
        Tuple of (tables_data, hero_skills_data, clean_skills_data)
    """
    # Initialize result containers
    tables_data = {}
    hero_skills_data = {}
    clean_skills_data = {}
    
    # Pre-compile check sets for better performance
    passives_required_cols = {"Type", "SP", "Unlock"}
    processing = False
    
    for table_name, (header_line, csv_lines) in tables_csv_output.items():
        # Start processing from Weapons table
        if not processing and table_name == "Weapons":
            processing = True
        
        if not processing:
            continue
        
        # Process Tables extraction
        should_include_in_tables = False
        if table_name == "Passives":
            # Use set intersection for faster checking
            header_cols = set(header_line.split(','))
            if header_cols & passives_required_cols:
                should_include_in_tables = True
        elif "Name" in header_line:
            should_include_in_tables = True
        
        if should_include_in_tables:
            tables_data[table_name] = csv_lines
        
        # Process Hero Skills extraction (keep Key, Name, Default, Unlock fields)
        if csv_lines:
            processed_hero_skills = process_hero_skills_table(header_line, csv_lines, table_name)
            if processed_hero_skills:
                hero_skills_data[table_name] = processed_hero_skills
        
        # Process Clean Skills extraction
        if csv_lines:
            if table_name == "Passives":
                # Passives table should exclude SP, Description, Type (hero type)
                clean_lines = process_skill_csv(header_line, csv_lines, "hero")
            else:
                # Other skill tables exclude Key, Unlock, Default (skill type)
                clean_lines = process_skill_csv(header_line, csv_lines, "skill")
            
            if clean_lines:
                clean_skills_data[table_name] = clean_lines
    
    return tables_data, hero_skills_data, clean_skills_data
