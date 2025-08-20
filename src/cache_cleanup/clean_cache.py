#!/usr/bin/env python3
"""
Python Cache Cleaner
Automatically removes all __pycache__ folders and .pyc files from the project.
"""

import os
import shutil
from pathlib import Path

def clean_python_cache():
    """Clean all Python cache files from the current directory and subdirectories"""
    print("🧹 Cleaning Python cache files...")
    
    # Get the project root (current directory)
    project_root = Path.cwd()
    
    # Count cache items before cleanup
    cache_folders = list(project_root.rglob("__pycache__"))
    pyc_files = list(project_root.rglob("*.pyc"))
    
    total_cache_folders = len(cache_folders)
    total_pyc_files = len(pyc_files)
    
    if total_cache_folders == 0 and total_pyc_files == 0:
        print("✅ No cache files found - project is already clean!")
        return
    
    print(f"Found {total_cache_folders} __pycache__ folders and {total_pyc_files} .pyc files")
    print("🗑️  Removing __pycache__ folders...")

    # Remove all __pycache__ folders
    if total_cache_folders > 0:
        for cache_folder in cache_folders:
            try:
                shutil.rmtree(cache_folder)
            except Exception as e:
                pass
    
    # Remove all .pyc files
    if total_pyc_files > 0:
        print("🗑️  Removing .pyc files...")
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
            except Exception as e:
                pass
    
    print("✅ Cache cleanup completed!")
    print(f"Removed {total_cache_folders} __pycache__ folders and {total_pyc_files} .pyc files")

if __name__ == "__main__":
    clean_python_cache()
