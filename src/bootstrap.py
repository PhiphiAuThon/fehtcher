import utils

# Master function that orchestrates everything
def bootstrap_database() -> dict[str, list[dict]]:
    """
    Master function that initializes the entire database.
    Returns a dictionary with all collected data.
    """
    HEROES_PAGE = "https://feheroes.fandom.com/wiki/List_of_Heroes"
    RESPLENDENTS_PAGE = "https://feheroes.fandom.com/wiki/Resplendent_Heroes"
    REFINES_PAGE = "https://feheroes.fandom.com/wiki/Weapon_Refinery"
    MANUALS_PAGE = "https://feheroes.fandom.com/wiki/Combat_Manuals"

    print("Starting database bootstrap...")
    
    data = {}
    
    # Collect all data
    data['heroes'] = __collect_heroes(HEROES_PAGE,"Collecting heroes data...")
    data['refines'] = __collect_refines(REFINES_PAGE,"Collecting refines data...")
    data['resplendents'] = __collect_heroes(RESPLENDENTS_PAGE,"Collecting resplendent heroes data...")
    data['manuals'] = __collect_manuals(MANUALS_PAGE,"Collecting manuals data...")
    
    print(f"Bootstrap complete! Collected:")
    print(f"- {len(data['heroes'])} heroes")
    print(f"- {len(data['refines'])} refines")
    print(f"- {len(data['resplendents'])} resplendents")
    print(f"- {len(data['manuals'])} manuals")
    
    return data


def __collect_heroes(page_link: str, print_message: str) -> dict[str, dict]:
    """Extracts hero IDs and their icon URLs from the main hero list page."""
    print(print_message)
    soup = utils.open_page(page_link)
    hero_table = soup.find("table", class_="sortable")
    if not hero_table:
        return {}

    heroes_data = {}
    # Find all table rows, skipping the header row
    for row in hero_table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        # The second cell contains the hero's name and link
        hero_id_cell = cells[1]
        hero_link = hero_id_cell.find('a')
        if not hero_link or not hero_link.get('title'):
            continue
    
        url_id = hero_link.get('title').replace(" ", "_")

        # The first cell contains the hero's icon
        icon_cell = cells[0]
        img_tag = icon_cell.find('img')
        icon_url = utils.extract_icon_url_from_img_tag(img_tag)

        if url_id and icon_url:
            hero_id = utils.extract_hero_id_from_icon_url(icon_url)
            heroes_data[hero_id] = {
                'hero_id': hero_id,
                'url_id': url_id,
                'icon_url': icon_url,
                'category': "resplendents" if ("resplendent" in print_message) else "heroes",
            } 

    return heroes_data


def __collect_refines(page_link: str, print_message: str) -> dict[str, dict]:
    """
    Extracts refine data from weapon refinery tables.
    Returns: Dictionary with hero_id as key and refine data as value
    """
    print(print_message)
    weapons_tables = utils.open_page(page_link).find_all("table")
    FIRST_REFINE_INDEX = 1

    refines = {}
    
    for weapon_table in weapons_tables[FIRST_REFINE_INDEX:-1]:
        hero_links = weapon_table.find("tr").find_all("a")
        hero_imgs = weapon_table.find("tr").find_all("img")
    
        # Filter for face images (preserving the original logic)
        hero_imgs = [html for html in hero_imgs if "_Face_FC" in str(html)]
        face_fc_imgs = [str(img).split('_Face_FC')[0] for img in hero_imgs]
        hero_ids = [img.split('key="')[-1] for img in face_fc_imgs]

        # Extract hero IDs from links
        url_ids= []
        for hero_link in hero_links:
            url_id = hero_link.get('title')
            if url_id and not url_id.endswith("5★"):
                url_ids.append(url_id.replace(" ", "_"))
        url_ids = list(set(url_ids))
        
        csv_string = utils.refine_table_to_csv(weapon_table)

        for url_id, hero_id in zip(url_ids,hero_ids):
            refines[hero_id] = {
                'hero_id': hero_id,
                'url_id': url_id,
                'refine_data': hero_id + ',' + csv_string,
                'category': "refines",
            }

    return refines


def __collect_manuals(page_link: str, print_message: str) -> list[dict]:
    """
    Extracts manual data from combat manuals tables.
    Returns: Dictionary with hero_id as key and manual data as value
    """
    print(print_message)
    manuals_tables = utils.open_page(page_link).find_all("table")
    first_manuals_index = 1
    
    manuals = []
    
    for table in manuals_tables[first_manuals_index:]:
        # Get the table caption if it exists
        caption = ''
        caption_tag = table.find('caption')
        if caption_tag:
            caption = caption_tag.get_text(strip=True)
        
        csv_without_manuals = utils.table_to_csv(table)
        csv_lines = csv_without_manuals.split('\n')
        hero_ids = utils.extract_hero_ids_from_table(table)
        hero_ids_str = f'"{','.join(hero_ids)}"'

        # Skip if no data lines
        if not csv_lines or len(csv_lines) < 2:
            continue

        # Add caption to header
        header = 'Caption,' + csv_lines[0]
        data_lines = csv_lines[1:]

        combined_lines = []
        for line in data_lines:
            if not line.strip():
                continue
            fields = utils.split_csv_line(line)
            fields[-1] = hero_ids_str
            # Add caption as first field
            combined_line = f'"{caption}",' + ','.join(fields)
            combined_lines.append(combined_line)

        result_csv = '\n'.join([header] + combined_lines)

        if caption.strip():
            manuals.append({
                'caption': caption,
                'manual_data': result_csv,
                'category': "manuals",
            })

    return manuals
