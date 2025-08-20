"""
Table to CSV conversion module - Main interface
This module provides a clean interface for converting hero data to CSV format.
"""

from .hero_converter import hero_table_to_csv_data

# Main public interface - this is what the rest of the code uses
__all__ = ['hero_table_to_csv_data']
