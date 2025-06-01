import csv
from io import StringIO

# --- Main orchestration function ---

def hero_table_to_csv_data(hero_id: str, hero_data: dict):
    info_dict = hero_info_to_csv_fields(hero_id, hero_data)
    related_heroes_csv_line = related_heroes_to_csv_line(hero_id, hero_data)
    tables_csv_output = hero_table_to_csv_lines(hero_id, hero_data)
    data = {
        "Info": info_dict,
        "Related Heroes": related_heroes_csv_line,
        "Tables": extract_tables_from_output(tables_csv_output),
        "Skills": extract_skills_from_output(tables_csv_output),
    }
    return data

# --- CSV line generation for hero info and related heroes ---

def hero_info_to_csv_fields(hero_id: str, hero_data: dict) -> dict:
    info_dict = {"Key": hero_id}
    for info_entry in hero_data.get("Info", []):
        if isinstance(info_entry, (list, tuple)):
            if len(info_entry) == 2:
                field, value = info_entry
            elif len(info_entry) > 2:
                field = info_entry[0]
                value = " ".join(str(item) for item in info_entry[1:])
            else:
                continue
            info_dict[field] = value
    return info_dict


def hero_info_to_csv_lines(hero_id: str, hero_data: dict):
    fields = ["Key"]
    values = [hero_id]
    info_fields = {}
    for info_entry in hero_data.get("Info", []):
        if isinstance(info_entry, (list, tuple)):
            if len(info_entry) == 2:
                field, value = info_entry
            elif len(info_entry) > 2:
                field = info_entry[0]
                value = " ".join(str(item) for item in info_entry[1:])
            else:
                continue
            info_fields[field] = value
    for field in sorted(info_fields.keys()):
        fields.append(field)
        values.append(str(info_fields[field]))
    fields_line = ",".join(fields)
    csv_line = ",".join(values)
    return fields_line, csv_line


def related_heroes_to_csv_line(hero_id: str, hero_data: dict) -> str:
    related_heroes = hero_data.get("Related Heroes", [])
    if related_heroes:
        return hero_id + "," + ",".join(related_heroes)
    else:
        return hero_id


def hero_table_to_csv_lines(hero_id: str, hero_data: dict, skip_header=False):
    csv_output = {}
    table_entries = list(hero_data.items())[2:]
    for table_name, csv_content in table_entries:
        lines = csv_content.strip().splitlines()
        if not lines:
            continue
        header_line = "Key," + lines[0]
        csv_lines = []
        if not skip_header:
            csv_lines.append(header_line)
        for row in lines[1:]:
            if row.strip():
                csv_lines.append(f"{hero_id},{row.strip()}")
        csv_output[table_name] = (header_line, csv_lines)
    return csv_output

# --- Table and skill extraction logic ---

def extract_tables_from_output(tables_csv_output):
    processing = False
    tables_with_names = {}
    for table_name, (header_line, csv_lines) in tables_csv_output.items():
        if not processing and should_start_processing(table_name):
            processing = True
        if not processing:
            continue
        name_index = get_name_column_index(header_line)
        if name_index is None:
            continue
        name_only_lines = extract_columns(csv_lines, [0,name_index,-2,-1])
        tables_with_names[table_name] = name_only_lines
    return tables_with_names

def extract_skills_from_output(tables_csv_output):
    keep_tables = False
    skills_tables = {}
    for table_name, (header_line, csv_lines) in tables_csv_output.items():
        if table_name == "Weapons":
            keep_tables = True
        if not keep_tables:
            continue
        all_lines = [header_line] + csv_lines
        if table_name == "Weapons":
            skills_tables[table_name] = extract_columns(all_lines, [1,2,3,4,5])
        else:
            skills_tables[table_name] = extract_columns(all_lines, [1,2,3,4])
        if table_name == "Passives":
            skills_tables[table_name] = [move_column_1_in_front(line) for line in skills_tables[table_name]]
    return skills_tables


# --- Helper functions for table processing ---

def move_column_1_in_front(csv_line):
    reader = csv.reader([csv_line])
    row = next(reader)
    if len(row) > 1:
        reordered = [row[1], row[0]] + row[2:]
    else:
        reordered = row
    output = StringIO()
    csv.writer(output).writerow(reordered)
    return output.getvalue().strip()

def should_start_processing(table_name, start_table="Weapons"):
    return table_name == start_table

def get_name_column_index(header_line):
    columns = header_line.split(",")
    return columns.index("Name") if "Name" in columns else None

def extract_columns(csv_lines, indexes_to_keep):
    if not csv_lines:
        return []
    csv_content = "\n".join(csv_lines)
    reader = csv.reader(StringIO(csv_content))
    output_lines = []
    for row in reader:
        selected = [row[i] for i in indexes_to_keep if i < len(row)]
        output_lines.append(",".join(csv_quote_if_needed(v) for v in selected))
    return output_lines

def csv_quote_if_needed(value):
    if ',' in value or '"' in value:
        return '"' + value.replace('"', '""') + '"'
    return value


def move_name_to_front(fields):
    name_index = fields.index("Name")
    return ["Name"] + [f for i, f in enumerate(fields) if i != name_index]

def reorder_line(fields, values):
    name_index = fields.index("Name")
    name_value = values[name_index]
    return [name_value] + [v for i, v in enumerate(values) if i != name_index]

def process_table(header_line, csv_lines):
    header_fields = header_line.split(",")[1:]
    new_header_fields = move_name_to_front(header_fields)
    new_header = ",".join(new_header_fields)
    new_lines = [new_header]
    for line in csv_lines[1:]:
        values = line.split(",")[1:]
        new_values = reorder_line(header_fields, values)
        new_line = ",".join(new_values)
        new_lines.append(new_line)
    return new_lines