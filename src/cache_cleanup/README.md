# Cache Cleanup Module

Tools for cleaning Python cache files (`__pycache__` folders and `.pyc` files).

## Architecture

- **`clean_cache.py`** - Python script for cache cleanup
- **`clean_cache.ps1`** - PowerShell script for Windows
- **`clean_cache.bat`** - Batch file for Windows

## Module Structure

```
cache_cleanup/
├── __init__.py          # Module initialization
├── clean_cache.py       # Python cleanup script
├── clean_cache.ps1      # PowerShell script
├── clean_cache.bat      # Batch file
└── README.md           # This file
```

## Key Functions

### Python Script
- `clean_cache.py` - Cross-platform cache cleanup

### PowerShell Script
- `clean_cache.ps1` - Windows-specific cleanup

### Batch File
- `clean_cache.bat` - Windows command prompt cleanup

## What Gets Cleaned

- `__pycache__/` folders - Python bytecode cache directories
- `*.pyc` files - Compiled Python bytecode files
- `*.pyo` files - Optimized Python bytecode files

## Usage

```bash
# Python script (recommended)
python src/cache_cleanup/clean_cache.py

# PowerShell
.\src\cache_cleanup\clean_cache.ps1

# Batch file
src\cache_cleanup\clean_cache.bat
```

