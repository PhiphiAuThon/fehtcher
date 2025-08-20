import os
import requests


def download_hero_icon(icon_url: str,database_folder:str):
    """Download the icon for a given hero"""
    if "Resplendent" in icon_url:
        download_image(icon_url, os.path.join(database_folder, "icons", "resplendents", icon_url.split('/')[-1]))
    else:
        download_image(icon_url, os.path.join(database_folder, "icons", icon_url.split('/')[-1]))


def download_image(url, filename):
    """Download an image from URL and save it to filename"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200 and len(response.content) > 0:
            with open(filename, 'wb') as file:
                file.write(response.content)
            return True
        return False
        
    except Exception as e:
        print(f"Download error: {e}")
        return False

