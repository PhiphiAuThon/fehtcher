"""
Hero information processing module
Handles conversion of hero info data to CSV fields and lines.
"""
import re

def get_clean_text(element):
    """Recursively extract and clean text from an element."""
    if hasattr(element, 'get_text'):
        return element.get_text(strip=True)
    if isinstance(element, list):
        return " ".join(get_clean_text(item) for item in element)
    return str(element)

def hero_info_to_csv_fields(hero_id: str, hero_data: dict) -> dict:
    """
    Convert hero info to a dictionary of CSV fields.
    
    Args:
        hero_id: The hero's identifier (used for URLs).
        hero_data: Dictionary containing hero information.
        
    Returns:
        Dictionary with field names as keys and values as strings
    """
    # The first field is the hero's ID.
    icon_filename = hero_data.get("Icon Filename", "")
    if icon_filename:
        # Clean the icon filename
        key_value = icon_filename.replace("_Face_FC.webp","").replace("_Face_FC.png","")
    else:
        # Fall back to hero_id if no icon filename
        key_value = hero_id
    
    info_dict = {
        "Key": key_value,
    }
    
    for info_entry in hero_data.get("Info", []):
        if isinstance(info_entry, (list, tuple)):
            if len(info_entry) == 2:
                field, value = info_entry
            elif len(info_entry) > 2:
                field = info_entry[0]
                value = " ".join(str(item) for item in info_entry[1:])
            else:
                continue

            # Clean value: replace non-breaking spaces
            cleaned_value = value.replace(u'\xa0', u' ')
            info_dict[field] = cleaned_value

    
    return info_dict



