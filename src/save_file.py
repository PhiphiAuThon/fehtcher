import os
import csv
import table_to_csv

# === MAIN FUNCTIONALITY ===

def get_heroes_to_update(heroes, folder_path, file_name):
    saved_heroes = get_heroes_from_txt(folder_path, file_name)
    to_update = [hero_id for hero_id in heroes if hero_id not in saved_heroes]
    return to_update

def save_hero_to_files(hero_id: str, hero_data: dict, folder_path: str):
    os.makedirs(folder_path, exist_ok=True)
    hero_csv_data = table_to_csv.hero_table_to_csv_data(hero_id, hero_data)
    
    related_heroes_path = os.path.join(folder_path, "related_heroes.csv")
    related_heroes_csv_to_file(hero_csv_data["Related Heroes"], related_heroes_path)
    
    info_path = os.path.join(folder_path, "info.csv")
    info_dict_to_csv(hero_csv_data["Info"], info_path)

    skills_tables = hero_csv_data["Skills"]
    for table_name, skill_lines in skills_tables.items():
        if not skill_lines:
            continue
        header = skill_lines[0]
        filename = os.path.join(folder_path, f"skill_{table_name.lower()}.csv")
        csv_to_file(header, skill_lines, filename, key_field="Name")

    tables = hero_csv_data["Tables"]
    for table_name, table_lines in tables.items():
        if not table_lines:
            continue
        header = table_lines[0]
        filename = os.path.join(folder_path, f"{table_name.lower()}.csv")
        csv_to_file(header, table_lines, filename, key_field="Key")

def save_hero_id_to_done(hero_id, folder_path, file_name):
    filename = os.path.join(folder_path, file_name)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            ids = set(line.strip() for line in f if line.strip())
    else:
        ids = set()
    if hero_id not in ids:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(hero_id + "\n")

# === FILE READING/WRITING HELPERS ===

def get_heroes_from_txt(folder_path, file_name):
    filename = os.path.join(folder_path, file_name)
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def related_heroes_csv_to_file(csv_line: str, filename="related_heroes.csv"):
    hero_id = get_first_field(csv_line)
    lines = read_lines_excluding_id(filename, hero_id)
    lines.append(csv_line)
    write_lines_to_file(filename, lines)

def info_dict_to_csv(info_dict, info_path):
    header, data_lines = read_csv_header_and_lines(info_path)
    fields = list(info_dict.keys())
    merged_header = list(header)
    for field in fields:
        if field not in merged_header:
            merged_header.append(field)
    value_line = [str(info_dict.get(field, "")) for field in merged_header]
    key_field = "Key"
    new_key = info_dict.get(key_field, "")
    with open(info_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(merged_header)
        found = False
        for row in data_lines:
            row_dict = dict(zip(header, row))
            if row_dict.get(key_field, "") == new_key:
                writer.writerow(value_line)
                found = True
            else:
                padded_row = [row_dict.get(field, "") for field in merged_header]
                writer.writerow(padded_row)
        if not found:
            writer.writerow(value_line)

def csv_to_file(header, lines, filename, key_field):
    existing_map = {}
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_lines = f.read().splitlines()
        if existing_lines:
            file_header = existing_lines[0]
            for line in existing_lines[1:]:
                key = get_field_value(file_header, line, key_field)
                if key:
                    existing_map[key] = line
            header = file_header
    for line in lines[1:]:
        key = get_field_value(header, line, key_field)
        if key:
            existing_map[key] = line
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for line in existing_map.values():
            f.write(line + "\n")

# === CSV/LINE HELPERS ===

def read_csv_header_and_lines(info_path):
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            lines = list(reader)
        if lines:
            header = lines[0]
            data_lines = lines[1:]
            return header, data_lines
    return [], []

def get_first_field(csv_line: str) -> str:
    return csv_line.split(",")[0] if csv_line else ""

def read_lines_excluding_id(file_path: str, hero_id: str):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [line for line in lines if get_first_field(line) != hero_id]

def write_lines_to_file(file_path: str, lines):
    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

# === SKILLS/NAME HELPERS ===

def get_name_index(header):
    fields = header.split(",")
    return fields.index("Name") if "Name" in fields else None

def get_name_from_line(header, line):
    index = get_name_index(header)
    values = line.split(",")
    return values[index] if index is not None and len(values) > index else None

def read_existing_skill_names(filename, header):
    if not os.path.exists(filename):
        return set(), None, []
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines:
        return set(), header, []
    file_header = lines[0]
    names = set(get_name_from_line(file_header, line) for line in lines[1:])
    return names, file_header, lines

def merge_skills(header, skill_lines, filename):
    existing_names, file_header, existing_lines = read_existing_skill_names(filename, header)
    lines_to_write = [file_header if file_header else header]
    if not file_header or file_header != header:
        lines_to_write[0] = header
    else:
        lines_to_write.extend(existing_lines[1:])
    for line in skill_lines[1:]:
        name = get_name_from_line(header, line)
        if name and name not in existing_names:
            lines_to_write.append(line)
            existing_names.add(name)
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines_to_write:
            f.write(line + "\n")

def read_existing_lines_and_names(filename):
    if not os.path.exists(filename):
        return [], set()
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines:
        return [], set()
    header = lines[0]
    names = set(get_name_from_line(header, line) for line in lines[1:] if line.strip())
    return lines, names

def skills_csv_to_file(header, skill_lines, filename):
    existing_lines, existing_names = read_existing_lines_and_names(filename)
    lines_to_write = []
    if existing_lines:
        file_header = existing_lines[0]
        lines_to_write.append(header if file_header != header else file_header)
        lines_to_write.extend(line for line in existing_lines[1:] if line.strip())
    else:
        lines_to_write.append(header)
    for line in skill_lines[1:]:
        name = get_name_from_line(header, line)
        if name and name not in existing_names:
            lines_to_write.append(line)
            existing_names.add(name)
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines_to_write:
            f.write(line + "\n")

# === FIELD HELPERS ===

def get_field_index(header, field_name):
    fields = header.split(",")
    return fields.index(field_name) if field_name in fields else None

def get_field_value(header, line, field_name):
    index = get_field_index(header, field_name)
    values = line.split(",")
    return values[index] if index is not None and len(values) > index else None
