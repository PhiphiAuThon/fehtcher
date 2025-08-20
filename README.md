# FEH Data Fetcher

A Python-based data extraction tool for Fire Emblem Heroes (FEH) that fetches hero data, skills, weapons, and images from the FEH Wiki.


## 🎮 Usage
1. Double-click `fehtcher.bat`
2. The launcher will start automatically
3. Cache files are automatically cleaned after each run

Data collected (info, hero icons and protraits) are stored in a folder called "database" at the root of the project. This is not a compiled project so you will need Python and all the dependencies that come with it.

### Manual Launch
```bash
python src/launcher.py
```

### Cache Cleanup
The launcher automatically cleans Python cache files, but you can also run cleanup manually:
```bash
# Windows Batch
src\cache_cleanup\clean_cache.bat

# PowerShell
src\cache_cleanup\clean_cache.ps1

# Python
python src\cache_cleanup\clean_cache.py
```

## 💾 Data Storage

The tool automatically creates organized data directories and files in `database/`:

- **CSV files**: Comprehensive hero data, skills, weapons, assists, specials
- **TXT files**: Tracking files for heroes, refined heroes, and resplendent heroes
- **Icons folder**: Hero icon images
- **Portraits folder**: Hero portrait images
- **Skills folder**: Skills-related data


## 🏗️ Architecture Overview

- **`launcher.py`**: Main entry point with menu system
- **`bootstrap.py`**: Application initialization and setup
- **`fetcher.py`**: Handles web scraping and data extraction from FEH Wiki
- **`hero_data_to_csv/`**: Converts HTML tables to structured CSV data
- **`save_hero/`**: Manages file operations and data persistence
- **`cache_cleanup/`**: Handles Python cache management


## 🚨 Requirements

- Python 3.6+
- Required packages (install via pip):
  - `beautifulsoup4` - HTML parsing
  - `requests` - HTTP requests
  - `tqdm` - Progress bars
  - `lxml` - XML/HTML processing


## 📝 Notes

- Data is cached locally to minimize repeated downloads using .txt files.
- If you want to change the data folder name, you can change it in `src/launcher.py`
- You can force reupload by removing the heroes name in the .txt files in 'database' folder
- This project is provided as-is for educational and personal use.