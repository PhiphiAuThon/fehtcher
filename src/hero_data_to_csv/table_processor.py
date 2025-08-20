"""
Table processing module
Handles conversion of table data to CSV format.
"""


def hero_table_to_csv_lines(hero_id: str, hero_data: dict, skip_header=False):
    """
    Convert hero table data to CSV lines with hero ID prefix.
    
    Args:
        hero_id: The hero's identifier
        hero_data: Dictionary containing hero information
        skip_header: Whether to skip the header line
        
    Returns:
        Dictionary mapping table names to (header_line, csv_lines) tuples
    """
    csv_output = {}
    
    # Use iterator instead of creating list copy - more memory efficient
    hero_data_items = iter(hero_data.items())
    
    # Skip Info and Related Heroes entries
    next(hero_data_items, None)  # Skip Info
    next(hero_data_items, None)  # Skip Related Heroes
    
    # Define fields that should be excluded from table processing
    excluded_fields = {
        "Icon URL", 
        "Icon Filename", 
        "icon url", 
        "icon filename"
    }
    
    for table_name, csv_content in hero_data_items:
        # Skip icon-related fields
        if table_name in excluded_fields:
            continue
            
        # Pre-filter empty content before processing
        if not csv_content or not csv_content.strip():
            continue
            
        lines = csv_content.strip().splitlines()
        if not lines:
            continue
        
        # Build header line once
        header_line = "Key," + lines[0]
        csv_lines = []
        
        if not skip_header:
            csv_lines.append(header_line)
        
        # Process data rows with list comprehension for better performance
        data_rows = [f"{hero_id},{row.strip()}" for row in lines[1:] if row.strip()]
        csv_lines.extend(data_rows)
        
        if csv_lines:  # Only add if we have content
            csv_output[table_name] = (header_line, csv_lines)

    return csv_output


def extract_tables_from_output(tables_csv_output):
    """
    Extract tables that should be processed (starting from Weapons table).
    
    Args:
        tables_csv_output: Output from hero_table_to_csv_lines
        
    Returns:
        Dictionary of tables with names as keys and CSV lines as values
    """
    processing = False
    tables_with_names = {}
    
    # Pre-compile check sets for better performance
    passives_required_cols = {"Type", "SP", "Unlock"}
    
    for table_name, (header_line, csv_lines) in tables_csv_output.items():
        if not processing and table_name == "Weapons":
            processing = True
        
        if not processing:
            continue
        
        # For Passives table, check if it has skill-related columns
        if table_name == "Passives":
            # Use set intersection for faster checking
            header_cols = set(header_line.split(','))
            if header_cols & passives_required_cols:  # Intersection check
                tables_with_names[table_name] = csv_lines
            continue
        
        # For other tables, check if header has a Name column
        if "Name" not in header_line:
            continue
        
        # csv_lines already contains the header when skip_header=False, so don't add it again
        tables_with_names[table_name] = csv_lines
    
    return tables_with_names



