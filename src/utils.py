import os
from bs4 import BeautifulSoup
import requests


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


def save_string_to_txt(text, filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        return True
    except Exception as e:
        return False


def read_txt_to_string(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return None


def lists_difference(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))


def to_snake_case(text):
    return text.lower().replace(" ","_")
