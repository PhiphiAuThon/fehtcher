"""
Related heroes processing module
Handles conversion of related heroes data to CSV format.
"""


def related_heroes_to_csv_line(hero_id: str, hero_data: dict) -> str:
    """
    Convert related heroes data to a CSV line.
    
    Args:
        hero_id: The hero's identifier
        hero_data: Dictionary containing hero information
        
    Returns:
        Comma-separated string with hero_id and related heroes
    """
    related_heroes = hero_data.get("Related Heroes", "")
    
    if isinstance(related_heroes, str) and related_heroes.strip():
        related_list = [h.strip() for h in related_heroes.split(",") if h.strip()]
        if related_list:
            result = hero_id + "," + ",".join(related_list)
            return result
    elif isinstance(related_heroes, list) and related_heroes:
        result = hero_id + "," + ",".join(related_heroes)
        return result
    
    return hero_id
