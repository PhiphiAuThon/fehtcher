"""
Save File module - Main interface
This module provides a clean interface for saving hero data to various file formats.
"""

from .core_saver import (
    save_hero_to_files,
    save_manuals,
)

# Main public interface - this is what the rest of the code uses
__all__ = [
    'save_hero_to_files',
    'save_manuals',
]
