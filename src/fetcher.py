from bs4 import BeautifulSoup
import re
import utils
import os

def fetch_hero_data(hero_id_data: dict) -> dict:
    """Get the hero data as a CSV dictionary"""
    hero_page = utils.open_page(f"https://feheroes.fandom.com/wiki/{hero_id_data['url_id']}")
    return __extract_hero_data_from_wiki_page(hero_page, hero_id_data['hero_id'])


def get_heroes_to_update(heroes, folder_path, file_name, heroes_page=None) -> list:
    """Get list of heroes that need to be updated"""
    saved_heroes_list = __get_heroes_from_txt(folder_path, file_name)
    # Convert to set for O(1) lookup instead of O(n) list search
    saved_heroes_set = set(saved_heroes_list)
    
    # Get icon-based hero IDs for proper matching
    heroes_icon_map = {}
    if heroes_page:
        try:
            heroes_with_icons = fetcher.get_heroes_with_icons(heroes_page)
            for hero_id, icon_url in heroes_with_icons:
                icon_based_id = extract_hero_id_from_icon_url(icon_url)
                heroes_icon_map[hero_id] = icon_based_id
        except Exception:
            # Fallback to old logic if something fails
            pass
    
    to_update = []
    for hero_id in heroes:
        # Use icon-based ID if available, otherwise fallback
        if hero_id in heroes_icon_map:
            icon_based_id = heroes_icon_map[hero_id]
        else:
            # Fallback: generate from hero_id (but this should rarely happen now)
            icon_based_id = hero_id.replace(":", "_")
        
        # O(1) lookup instead of O(n) loop - major performance improvement
        if icon_based_id not in saved_heroes_set:
            to_update.append(icon_based_id)
    
    return to_update


def __get_heroes_from_txt(folder_path, file_name) -> list:
    """Read hero IDs from a text file"""
    filename = os.path.join(folder_path, file_name)
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        # Use list comprehension for better performance
        return [line.strip() for line in f if line.strip()]



def __extract_hero_data_from_wiki_page(hero_page:BeautifulSoup, hero_id:str) -> dict:
    """
    Convert hero page HTML to a dictionary of CSV data.
    Handles special characters in hero names and titles consistently.
    """
    csv_dict = {}

    info_table = hero_page.find("table", class_="hero-infobox")
    if info_table:
        info = utils.table_to_list(info_table)
        
        # Get the hero's name and title from the page if possible
        name_elem = hero_page.find('h1', {'class': 'page-header__title'})

        if name_elem:
            # Get the full title text and clean it up
            full_title = name_elem.get_text(strip=True)
            # Remove any extra text like "Edit" or "History" that might be in the title
            full_title = full_title.split('[')[0].strip()
            # Split into name and title if there's a colon
            if ':' in full_title:
                name, title = [part.strip() for part in full_title.split(':', 1)]
            else:
                name = full_title
                title = ""
        else:
            # Fallback to parsing from hero_id if we can't get it from the page
            hero_title = hero_id.replace("_", " ")
            if ":" in hero_title:
                name, title = [part.strip() for part in hero_title.split(":", 1)]
            else:
                parts = hero_title.split(" ", 1)
                name = parts[0]
                title = parts[1] if len(parts) > 1 else ""
        
        # Remove the header rows
        if info:
            info.pop(0)  # Remove header row
        
        # Extract artist information if available
        artists = [None, None]
        if info and info[0]:  # Check if there's an artist row
            artists = __extract_artists(info.pop(0)[0]) or artists
        
        # Prepare the basic info to add
        info_to_add = [
            ["Name", name],
            ["Title", title],
            ["Standard Artist", artists[0] or "Unknown"]
        ]
       
        if artists[1]:
            info_to_add.append(["Resplendent Artist", artists[1]])

        info_to_add.reverse()
        for new_info in info_to_add:
            info.insert(0, new_info)

        for info_bit in info:
            info_bit[0] = info_bit[0].replace("[ExpandCollapse]", "")
        
        csv_dict["Info"] = info

    csv_dict["Related Heroes"] = __extract_related_heroes(hero_page)
    csv_dict["Portraits"] = __extract_hero_portraits(hero_page, hero_id)

    csv_dict.update(__extract_data_tables(hero_page))

    def fill_missing_types(csv_text):
        rows = csv_text.split("\n")
        last_type = None
        filled_csv_text = ""
        for row in rows:
            fields = row.split(",")
            if fields[0] == "":
                fields[0] = last_type
            else:
                last_type = fields[0]
            filled_csv_text += ",".join(fields) + "\n"

        return filled_csv_text
    
    if csv_dict.get("Passives", None):
        csv_dict["Passives"] = fill_missing_types(csv_dict["Passives"])
    
    return csv_dict


def __extract_artists(text: str) -> list:
    """Extracts artist names from text, handling both standard and resplendent artists."""
    matches = re.findall(r'Art by:(.*?)(?=Resplendent Attire|Art by:|$)', text)
    artists = [m.strip() for m in matches if m.strip()]
    
    if len(artists) == 1:
        artists.append(None)
    elif len(artists) == 0:
        artists = [None, None]
    
    return artists


def __extract_related_heroes(hero_page: BeautifulSoup) -> str:
    """Extracts related heroes from the character-about table."""
    related_heroes_table = hero_page.find("table", class_="character-about")
    if not related_heroes_table:
        return ""
    
    related_heroes_list = utils.extract_hero_ids_from_table(related_heroes_table)

    return ",".join(related_heroes_list)


def __extract_data_tables(hero_page: BeautifulSoup) -> dict:
    """Extracts all tables from headlines and returns them as a dictionary."""
    tables_dict = {}
    tables_headlines = hero_page.select("h3 > span.mw-headline")

    def get_next_tag_sibling(tag):
        next_node = tag.next_sibling
        while next_node and (getattr(next_node, "name", None) is None) and str(next_node).strip() == "":
            next_node = next_node.next_sibling
        if next_node and getattr(next_node, "name", None):
            return next_node
        return None
    
    for headline in tables_headlines:
        h3_tag = headline.find_parent("h3")
        next_tag = get_next_tag_sibling(h3_tag)
        if next_tag and next_tag.name == "table":
            table_name = headline.get_text(strip=True)
            tables_dict[table_name] = utils.table_to_csv(next_tag)
    
    return tables_dict


def __extract_hero_portraits(hero_page, hero_id) -> dict[str,str]:
    """Extract portrait/art image links from hero page"""
    portraits = {}
    
    info_table = hero_page.find("table", class_="hero-infobox")
    if not info_table:
        return portraits
    
    keys = [
        "Portrait",
        "Attack",
        "Special",
        "Damage",
        "Resplendent_Portrait",
        "Resplendent_Attack",
        "Resplendent_Special",
        "Resplendent_Damage",
    ]
    i=0

    images = info_table.find_all('img')
    for img in images:
        img_src = img.get('data-src') or img.get('src')
        if img_src:
            img_src = utils.extract_icon_url_from_img_tag(img)
            
            if hero_id in img_src:
                portraits[keys[i]] = img_src
                i+=1
    return portraits
