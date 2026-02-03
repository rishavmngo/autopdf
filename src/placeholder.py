"""Placeholder data model."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


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
    
    def get_display_name(self) -> str:
        """Return the placeholder name with curly braces for display."""
        return f"{{{{{self.name}}}}}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "page": self.page,
            "x": self.x,
            "y": self.y,
            "font_name": self.font_name,
            "font_size": self.font_size,
            "font_color": list(self.font_color)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Placeholder":
        """Create Placeholder from dictionary."""
        data = data.copy()
        if "font_color" in data:
            data["font_color"] = tuple(data["font_color"])
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
        """Get list of all placeholder names."""
        return [p.name for p in self.placeholders]
    
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
