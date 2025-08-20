# Save Hero Module

Module for saving hero data to various file formats with tracking capabilities.

## Architecture

- **`core_saver.py`** - Main orchestration and core saving functionality
- **`csv_operations.py`** - CSV-specific file operations and deduplication
- **`img_downloader.py`** - Image downloading functionality

## Module Structure

```
save_hero/
├── __init__.py          # Main interface exports
├── core_saver.py        # Core saving orchestration
├── csv_operations.py    # CSV file operations
├── img_downloader.py    # Image downloading
└── README.md           # This file
```

## Key Functions

### Core Saver
- `get_heroes_to_update()` - Get heroes needing updates
- `save_hero_to_files()` - Save hero data to files
- `save_hero_id_to_done()` - Track completion

### CSV Operations
- `related_heroes_csv_to_file()` - Save related heroes data
- `info_dict_to_csv()` - Convert hero info to CSV
- `csv_to_file()` - Save with key-based deduplication

### Image Downloader
- `download_hero_image()` - Download hero images

## Data Flow

1. Input: Hero data from fetcher
2. Processing: Convert to appropriate formats
3. Storage: Save to CSV files and tracking files
4. Tracking: Monitor progress in text files

## File Formats

- **CSV**: Hero info, skills, related heroes, tables
- **Tracking**: heroes.txt, refined_heroes.txt, resplendent_heroes.txt
- **Images**: Hero portrait downloads
