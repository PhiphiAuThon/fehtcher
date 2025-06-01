from bs4 import BeautifulSoup
import utils
import re


def get_heroes_ids(page_link:str,) -> list[str]:
    heroes_list = utils.table_to_list(utils.open_page(page_link).find("table",class_="sortable"))
    HERO_ID_INDEX = 1

    all_heroes_ids = []
    for hero in heroes_list[1:]:
        hero_id = str(hero[HERO_ID_INDEX]).replace(" ","_")
        all_heroes_ids.append(hero_id)

    return all_heroes_ids

def get_hero_data(hero_id: str):
    HERO_PAGE_LINK = "https://feheroes.fandom.com/wiki/"
    hero_page = utils.open_page(HERO_PAGE_LINK + hero_id)
    hero_data = hero_page_to_csv_dict(hero_page, hero_id)
    return hero_data

def hero_page_to_csv_dict(hero_page:BeautifulSoup, hero_id:str) -> dict:
    csv_dict = {}

    info_table = hero_page.find("table", class_="hero-infobox")
    if info_table:
        info = utils.table_to_list(info_table)
        hero_title = hero_id.replace("_"," ")
        hero_title = [part.strip() for part in hero_title.split(":")]
        info.pop(0)
        artists = extract_artists(info.pop(0)[0])
        info_to_add = [
            ["Name",hero_title[0]],
            ["Title",hero_title[1]],
            ["Standard Artist",artists[0]]
        ]
       
        has_resplendent =  artists[1]
        if has_resplendent:
            info_to_add.append(["Resplendent Artist",artists[1]])

        info_to_add.reverse()
        for new_info in info_to_add:
            info.insert(0,new_info)

        for info_bit in info:
            info_bit[0] =  info_bit[0].replace("[ExpandCollapse]","")
        
        csv_dict["Info"] = info

    related_heroes_table = hero_page.find("table", class_="character-about")
    if related_heroes_table:
        related_heroes_list = get_heroes_icons_from_table(related_heroes_table,False)[0]
        csv_dict["Related Heroes"] = related_heroes_list
    
    tables_headlines = hero_page.select("h3 > span.mw-headline")
    for headline in tables_headlines:
        h3_tag = headline.find_parent("h3")
        next_tag = get_next_tag_sibling(h3_tag)
        if next_tag and next_tag.name == "table":
            csv_dict[headline.get_text(strip=True)] = utils.table_to_csv(next_tag)

    if csv_dict.get("Passives", None):
        csv_dict["Passives"] = fill_missing_types(csv_dict["Passives"])
    
    return csv_dict

def get_next_tag_sibling(tag):
    next_node = tag.next_sibling
    while next_node and (getattr(next_node, "name", None) is None) and str(next_node).strip() == "":
        next_node = next_node.next_sibling
    if next_node and getattr(next_node, "name", None):
        return next_node
    return None

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
        fields = [f for f in fields if f != ""]
        filled_csv_text += ",".join(fields) + "\n"

    return filled_csv_text

def extract_artists(text):
    matches = re.findall(r'Art by:(.*?)(?=Resplendent Attire|Art by:|$)', text)
    artists = [m.strip() for m in matches]
    if len(artists) == 1:
        artists.append(None)
    return artists

def get_refines(page_link:str) -> dict:
    weapons_tables = utils.open_page(page_link).find_all("table")
    FIRST_REFINE_INDEX = 1

    refines = {}
    for weapon_table in weapons_tables[FIRST_REFINE_INDEX:-1]:
        hero_links = weapon_table.find("tr").find_all("a")
        hero_ids = []
        for hero_link in hero_links:
            hero_id = hero_link.get('title')
            if hero_id and not hero_id.endswith("5★"):
                hero_ids.append(hero_id.replace(" ","_"))
        csv_string = utils.table_to_csv(weapon_table)
        for hero_id in hero_ids:
            refines[hero_id] = csv_string

    return refines

def get_manuals(page_link:str) -> list:
    #TODO: get captions
    manuals_tables = utils.open_page(page_link).find_all("table")
    FIRST_MANUALS_INDEX = 1

    csv_list = []
    
    for table in manuals_tables[FIRST_MANUALS_INDEX:]:
        csv_without_manuals = utils.table_to_csv(table)
        csv_lines = csv_without_manuals.split('\n')
        manuals_string_list = get_heroes_icons_from_table(table,True)

        header = csv_lines[0]
        data_lines = csv_lines[1:]

        combined_lines = []
        for line, manual in zip(data_lines, manuals_string_list):
            if not line.strip():
                continue
            fields = utils.split_csv_line(line)
            fields[-1] = manual
            combined_lines.append(','.join(fields))

        result_csv = '\n'.join([header] + combined_lines)
        csv_list.append(result_csv)

    return csv_list

def get_heroes_icons_from_table(table:BeautifulSoup, as_string:bool) -> list:
    td_elements = table.find_all('td')
    manuals_list = []
    for td in td_elements:
        a_elements = td.find_all('a')
        if a_elements:
            has_divine_codes_text = any(a_element.get('title') == "Divine Codes" for a_element in a_elements)
            if not has_divine_codes_text:
                manuals_list.append(a_elements_heroes_to_data(a_elements, as_string))
    return manuals_list

def a_elements_heroes_to_data(a_elements:list, as_string:bool) -> str:
    seen_hrefs = set()
    manuals = []
    for a_element in a_elements:
        href = a_element.get('href')
        if href and href not in seen_hrefs:
            seen_hrefs.add(href)
            hero_id = a_element.get('title').replace(" ", "_")
            manuals.append(hero_id)
    
    if not as_string:
        return manuals
    str_manuals = ",".join(manuals)
    str_manuals = f'"{str_manuals}"'
    return str_manuals
