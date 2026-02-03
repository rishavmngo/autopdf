"""Placeholder data model."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


# Placeholder types
PLACEHOLDER_TYPE_COLUMN = "column"  # Maps to CSV column
PLACEHOLDER_TYPE_STATIC = "static"  # Static text
PLACEHOLDER_TYPE_SERIAL = "serial"  # Serial number (row index)


@dataclass
class Placeholder:
    """Represents a placeholder on a PDF page."""
    
    name: str  # e.g., "first_name" (without curly braces)
    page: int  # 0-indexed page number
    x: float  # X coordinate on page
    y: float  # Y coordinate on page
    font_name: str = "helv"  # Default Helvetica
    font_size: float = 12.0
    font_color: tuple = field(default_factory=lambda: (0, 0, 0))  # RGB, 0-1 range
    placeholder_type: str = PLACEHOLDER_TYPE_COLUMN  # Type of placeholder
    static_value: str = ""  # Value for static type
    serial_prefix: str = ""  # Prefix for serial number
    serial_start: int = 1  # Starting number for serial
    
    def get_display_name(self) -> str:
        """Return the placeholder name with curly braces for display."""
        if self.placeholder_type == PLACEHOLDER_TYPE_STATIC:
            return self.static_value or f"[Static: {self.name}]"
        elif self.placeholder_type == PLACEHOLDER_TYPE_SERIAL:
            return f"#{self.serial_prefix}"
        return f"{{{{{self.name}}}}}"
    
    def get_value(self, row_index: int, row_data: dict) -> str:
        """Get the value for this placeholder for a given row."""
        if self.placeholder_type == PLACEHOLDER_TYPE_STATIC:
            return self.static_value
        elif self.placeholder_type == PLACEHOLDER_TYPE_SERIAL:
            return f"{self.serial_prefix}{self.serial_start + row_index}"
        else:
            return row_data.get(self.name, "")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "page": self.page,
            "x": self.x,
            "y": self.y,
            "font_name": self.font_name,
            "font_size": self.font_size,
            "font_color": list(self.font_color),
            "placeholder_type": self.placeholder_type,
            "static_value": self.static_value,
            "serial_prefix": self.serial_prefix,
            "serial_start": self.serial_start
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Placeholder":
        """Create Placeholder from dictionary."""
        data = data.copy()
        if "font_color" in data:
            data["font_color"] = tuple(data["font_color"])
        # Handle old format without type fields
        if "placeholder_type" not in data:
            data["placeholder_type"] = PLACEHOLDER_TYPE_COLUMN
        if "static_value" not in data:
            data["static_value"] = ""
        if "serial_prefix" not in data:
            data["serial_prefix"] = ""
        if "serial_start" not in data:
            data["serial_start"] = 1
        return cls(**data)


class PlaceholderManager:
    """Manages a collection of placeholders."""
    
    def __init__(self):
        self.placeholders: list[Placeholder] = []
    
    def add(self, placeholder: Placeholder) -> None:
        """Add a new placeholder."""
        self.placeholders.append(placeholder)
    
    def remove(self, placeholder: Placeholder) -> None:
        """Remove a placeholder."""
        self.placeholders.remove(placeholder)
    
    def remove_by_name(self, name: str) -> None:
        """Remove placeholder by name."""
        self.placeholders = [p for p in self.placeholders if p.name != name]
    
    def get_by_name(self, name: str) -> Optional[Placeholder]:
        """Get placeholder by name."""
        for p in self.placeholders:
            if p.name == name:
                return p
        return None
    
    def get_for_page(self, page: int) -> list[Placeholder]:
        """Get all placeholders for a specific page."""
        return [p for p in self.placeholders if p.page == page]
    
    def get_all_names(self) -> list[str]:
        """Get list of all placeholder names (only for column type)."""
        return [p.name for p in self.placeholders if p.placeholder_type == PLACEHOLDER_TYPE_COLUMN]
    
    def clear(self) -> None:
        """Remove all placeholders."""
        self.placeholders.clear()
    
    def to_list(self) -> list[dict]:
        """Convert all placeholders to list of dictionaries."""
        return [p.to_dict() for p in self.placeholders]
    
    def from_list(self, data: list[dict]) -> None:
        """Load placeholders from list of dictionaries."""
        self.clear()
        for item in data:
            self.add(Placeholder.from_dict(item))
