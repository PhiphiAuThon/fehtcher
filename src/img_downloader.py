import utils
import os
from bs4 import Tag
import requests
from typing import List


def get_heroes_icons_links(page_link: str) -> List[str]:
    table_html = utils.open_page(page_link).find("table", class_="sortable")
    tr_html = table_html.find_all('tr')
    icons_links = []

    for tr in tr_html:
        img_html = tr.find('img')
        if img_html:
            img_link = get_image_link(img_html)
            if img_link:
                icons_links.append(img_link)

    return icons_links


def get_image_link(img_html:Tag):
    link = img_html.get('data-src') or img_html.get('src')
    if link:
        EXTENSIONS = ['.webp','.png']
        for extension in EXTENSIONS:
            if extension in link:
                return link.split(extension)[0]+extension
    return None


def download_image(url, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return True
    return False
