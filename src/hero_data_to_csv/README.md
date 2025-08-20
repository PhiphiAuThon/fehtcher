# Hero Data to CSV Module

Module for converting hero data tables to structured CSV format.

## Architecture

- **`hero_converter.py`** - Main orchestration and conversion interface
- **`hero_info.py`** - Hero information extraction and conversion
- **`related_heroes.py`** - Related heroes processing
- **`table_processor.py`** - Main table processing and conversion
- **`skills_processor.py`** - Skills table processing and conversion

## Module Structure

```
hero_data_to_csv/
├── __init__.py          # Main interface exports
├── hero_converter.py    # Main conversion orchestration
├── hero_info.py         # Hero information processing
├── related_heroes.py    # Related heroes processing
├── table_processor.py   # Table processing and conversion
├── skills_processor.py  # Skills processing and conversion
└── README.md           # This file
```

## Key Functions

### Hero Converter
- `hero_table_to_csv_data()` - Main conversion function

### Hero Info
- `hero_info_to_csv_fields()` - Convert hero info to CSV fields

### Related Heroes
- `related_heroes_to_csv_line()` - Convert related heroes to CSV

### Table Processor
- `hero_table_to_csv_lines()` - Convert table data to CSV lines
- `extract_tables_from_output()` - Extract tables from conversion output

### Skills Processor
- `extract_skills_from_output()` - Extract skills tables
- `create_hero_skill_info()` - Create hero+skill information

## Data Flow

1. Input: Hero data from fetcher
2. Processing: Convert to appropriate CSV formats
3. Output: Structured dictionary with different data sections

## Output Structure

```python
{
    "Info": dict,              # Hero basic information
    "Related Heroes": str,      # Related heroes CSV line
    "Tables": dict,            # Game tables (weapons, skills, etc.)
    "Skills": dict,            # Processed skills data
    "Hero Skills": dict        # Hero+skill combinations
}
```

## File Formats

- **Info**: Name, title, artist, etc.
- **Tables**: Weapons, assists, specials, passives, ally/enemy skills
- **Skills**: Processed skills with cleaned formatting
- **Hero Skills**: Hero+skill combinations with essential fields
