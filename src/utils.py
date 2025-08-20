from bs4 import BeautifulSoup
import requests
import csv
import io


def open_page(page_link:str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(page_link).content, "html.parser")


def table_to_list(table:BeautifulSoup) -> list:
    rows = []
    for row in table.find_all('tr'):
        cols = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        if cols:
            rows.append(cols)
    return rows


def table_to_csv(table_tag) -> str:
    lines = []
    for row in table_tag.find_all('tr'):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        cells = [f'"{c.replace("\"", "\"\"")}"' if (',' in c or '"' in c) else c for c in cells]
        lines.append(','.join(cells))
    return '\n'.join(lines)


def refine_table_to_csv(table_tag) -> str:
    lines = []
    for row in table_tag.find_all('tr'):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        cells = [f'"{c.replace("\"", "\"\"")}"' if (',' in c or '"' in c) else c for c in cells]
        cells = [cell for cell in cells if cell]
        lines.append(','.join(cells))
    lines = [line for line in lines if line]
    return ','.join(lines)


def split_csv_line(line:str) -> list:
    fields = []
    field = ''
    in_quotes = False
    i = 0
    while i < len(line):
        char = line[i]
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                field += '"'
                i += 1
            else:
                in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(field)
            field = ''
        else:
            field += char
        i += 1
    fields.append(field)
    return fields


def extract_hero_ids_from_table(table) -> list[str]:
    td_elements = table.find_all('td')
    manuals_list = []
    for td in td_elements:
        imgs = td.find_all('img')
        if imgs:
            for img in imgs:
                icon_url = extract_icon_url_from_img_tag(img)
                hero_id = extract_hero_id_from_icon_url(icon_url)
                manuals_list.append(hero_id)
    manuals_list = [hero_id for hero_id in manuals_list if not hero_id.endswith('.png') and not hero_id.endswith('.webp')]

    return manuals_list


def extract_icon_url_from_img_tag(img_tag) -> str:
    """
    Extract icon URL from img tag, handling both data-src and src attributes.
    Returns the icon URL or empty string if not found.
    """
    if not img_tag:
        return ""
    
    # Try data-src first (lazy loading), then fallback to src
    icon_url = img_tag.get('data-src') or img_tag.get('src')
    img_extension = icon_url.split('.')[-1].split('/')[0]
    icon_url = icon_url.split('.'+img_extension)[0]
    
    return icon_url + '.' + img_extension or ""

def extract_hero_id_from_icon_url(icon_url: str) -> str:
    return icon_url.split('/')[-1].split('_Face')[0]
