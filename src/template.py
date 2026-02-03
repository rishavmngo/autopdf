"""Template save/load functionality."""

import json
import os
from pathlib import Path
from typing import Optional
from .placeholder import PlaceholderManager


class Template:
    """Represents a PDF template with placeholders."""
    
    def __init__(self):
        self.pdf_path: Optional[str] = None
        self.placeholder_manager = PlaceholderManager()
    
    def save(self, template_path: str) -> None:
        """Save template to JSON file."""
        data = {
            "pdf_path": self.pdf_path,
            "placeholders": self.placeholder_manager.to_list()
        }
        
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def load(self, template_path: str) -> None:
        """Load template from JSON file."""
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.pdf_path = data.get("pdf_path")
        self.placeholder_manager.from_list(data.get("placeholders", []))
    
    def is_valid(self) -> bool:
        """Check if template is valid (PDF exists)."""
        if not self.pdf_path:
            return False
        return os.path.exists(self.pdf_path)
    
    def clear(self) -> None:
        """Clear the template."""
        self.pdf_path = None
        self.placeholder_manager.clear()
