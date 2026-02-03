"""CSV handling and mapping functionality."""

import csv
from typing import Optional


class CSVHandler:
    """Handles CSV parsing and data mapping."""
    
    def __init__(self):
        self.headers: list[str] = []
        self.rows: list[dict] = []
        self.file_path: Optional[str] = None
        self.mapping: dict[str, str] = {}  # placeholder_name -> csv_header
    
    def load(self, file_path: str) -> None:
        """Load CSV file and parse content."""
        self.file_path = file_path
        self.headers = []
        self.rows = []
        
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames or []
            self.rows = list(reader)
    
    def get_headers(self) -> list[str]:
        """Return list of CSV headers."""
        return self.headers.copy()
    
    def get_row_count(self) -> int:
        """Return number of data rows."""
        return len(self.rows)
    
    def set_mapping(self, mapping: dict[str, str]) -> None:
        """Set the placeholder-to-header mapping."""
        self.mapping = mapping.copy()
    
    def get_value_for_placeholder(self, row_index: int, placeholder_name: str) -> str:
        """Get the value for a placeholder from a specific row."""
        if row_index < 0 or row_index >= len(self.rows):
            return ""
        
        header = self.mapping.get(placeholder_name)
        if not header:
            return ""
        
        return self.rows[row_index].get(header, "")
    
    def get_row_data(self, row_index: int) -> dict[str, str]:
        """Get mapped data for a specific row."""
        result = {}
        for placeholder_name, header in self.mapping.items():
            if row_index < len(self.rows):
                result[placeholder_name] = self.rows[row_index].get(header, "")
        return result
    
    def clear(self) -> None:
        """Clear all data."""
        self.headers = []
        self.rows = []
        self.file_path = None
        self.mapping = {}
