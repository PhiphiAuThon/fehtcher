"""
Core Save Operations - Main orchestration
This module coordinates the saving of hero data to various file formats.
"""

import os
from hero_data_to_csv import hero_table_to_csv_data

from .csv_operations import (
    related_heroes_csv_to_file,
    info_dict_to_csv,
    csv_to_file,
    hero_skills_to_file
)

from .img_downloader import download_hero_icon, download_image

def save_manuals(manuals: list[dict], folder_path: str):
    """Save manuals to files"""
    os.makedirs(folder_path, exist_ok=True)

    for manual_group in manuals:
        with open(os.path.join(folder_path, "manuals.csv"), "a") as f:
            f.write(manual_group["manual_data"])


def save_hero_to_files(hero_info: dict, hero_page_data: dict, folder_path: str):
    """Main function: Save hero data to various file formats"""
    
    os.makedirs(folder_path, exist_ok=True)

    hero_id = hero_info["hero_id"]
    category = hero_info["category"]
    portraits = hero_page_data.pop("Portraits")
    hero_csv_data = hero_table_to_csv_data(hero_id, hero_page_data)
    
    # The Key field now contains the icon name (clean icon name)
    icon_name = hero_csv_data["Info"].get("Key", hero_id)

    # Batch file operations for better performance
    file_operations = []
    
    # Prepare related heroes operation
    related_heroes_path = os.path.join(folder_path, "related_heroes.csv")
    file_operations.append(('related_heroes', related_heroes_path, hero_csv_data["Related Heroes"]))

    # Prepare hero info operation
    info_path = os.path.join(folder_path, "info.csv")
    file_operations.append(('info', info_path, hero_csv_data["Info"]))
    
    # Prepare hero skills operations
    hero_skills = hero_csv_data["Hero Skills"]
    for table_name, table_lines in hero_skills.items():
        if table_lines:
            filename = os.path.join(folder_path, f"{table_name.lower()}.csv")
            file_operations.append(('hero_skills', filename, table_lines, table_name))
    
    # Execute all file operations
    __execute_bulk_file_operations(file_operations)
    
    # Save skills to skills folder
    __save_skills_to_folder(folder_path, hero_csv_data["Skills"])

    #icon_url is default if category is "heroes" and resplendent when category is "resplendents"
    if category == "heroes" or category == "resplendents":
        icon_url = hero_info["icon_url"]
        download_hero_icon(icon_url, folder_path)
        __save_portraits_to_files(hero_id, portraits, f"{folder_path}/portraits")
    if category == "refines":
        refine_header = "Key,Name,Stats,Description,Refine Description,Cost"
        skill_refine_csv = {
            "Refines":  [refine_header, hero_info["refine_data"]]
        }
        __save_skills_to_folder(folder_path, skill_refine_csv)


    __save_hero_id_to_done(hero_id, folder_path, category+".txt")


def __save_portraits_to_files(hero_id: str, portraits: dict, folder_path: str):
    """Save hero portraits to files"""
    os.makedirs(folder_path, exist_ok=True)

    for key, value in portraits.items():
        extension = value.split(".")[-1]
        path = f"{folder_path}/{hero_id}"
        if "Resplendent" in key:
            path = f"{path}/resplendent"
        filename = os.path.join(path, f"{hero_id}_{key}.{extension}")
        download_image(value, filename)


def __execute_bulk_file_operations(operations):
    """Execute multiple file operations efficiently"""
    for operation in operations:
        op_type = operation[0]
        if op_type == 'related_heroes':
            _, filepath, csv_line = operation
            related_heroes_csv_to_file(csv_line, filepath)
        elif op_type == 'info':
            _, filepath, info_dict = operation
            info_dict_to_csv(info_dict, filepath)
        elif op_type == 'hero_skills':
            _, filepath, table_lines, table_name = operation
            hero_skills_to_file(table_lines[0], table_lines, filepath, "Key")


def __save_skills_to_folder(folder_name: str, skills_data: dict):
    """Save skills data to the skills folder with skill_*.csv naming convention"""
    skills_folder = os.path.join(folder_name, "skills")
    os.makedirs(skills_folder, exist_ok=True)
    
    # Batch skills operations
    skills_operations = []
    for skill_type, skill_lines in skills_data.items():
        if skill_lines:
            filename = os.path.join(skills_folder, f"skill_{skill_type.lower()}.csv")
            skills_operations.append((filename, skill_lines))
    
    # Execute all skills operations efficiently
    for filename, skill_lines in skills_operations:
        # Use csv_to_file with "Name" field for proper skill deduplication
        # Skills are deduplicated by their Name field to avoid duplicates
        csv_to_file(skill_lines[0], skill_lines, filename, "Name")


def __save_hero_id_to_done(hero_id, folder_path, file_name):
    """Save hero ID to completion tracking file"""
    filename = os.path.join(folder_path, file_name)
    
    # The hero_id should now be in the correct icon-based format
    # No need for normalization since get_heroes_to_update handles this
    
    # Read existing IDs efficiently
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            ids = set(line.strip() for line in f if line.strip())
    else:
        ids = set()
    
    # Save the hero ID as-is (should be icon-based format)
    if hero_id not in ids:
        # Use append mode for efficiency - single write operation
        with open(filename, "a", encoding="utf-8") as f:
            f.write(hero_id + "\n")
