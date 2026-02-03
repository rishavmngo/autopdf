"""PDF generation engine."""

import os
import fitz  # PyMuPDF
from typing import Callable, Optional
from .placeholder import Placeholder, PlaceholderManager, PLACEHOLDER_TYPE_COLUMN
from .csv_handler import CSVHandler


# Font mapping for PyMuPDF
FONT_MAP = {
    "helv": "helv",      # Helvetica
    "tiro": "tiro",      # Times Roman
    "cour": "cour",      # Courier
    "symb": "symb",      # Symbol
    "zadb": "zadb",      # ZapfDingbats
}

FONT_DISPLAY_NAMES = {
    "helv": "Helvetica",
    "tiro": "Times Roman", 
    "cour": "Courier",
    "symb": "Symbol",
    "zadb": "ZapfDingbats",
}


class PDFGenerator:
    """Generates PDFs with placeholder values filled in."""
    
    def __init__(
        self,
        pdf_path: str,
        placeholder_manager: PlaceholderManager,
        csv_handler: CSVHandler
    ):
        self.pdf_path = pdf_path
        self.placeholder_manager = placeholder_manager
        self.csv_handler = csv_handler
    
    def generate_single(self, row_index: int, output_path: str) -> None:
        """Generate a single PDF for one row of data."""
        # Open the original PDF
        doc = fitz.open(self.pdf_path)
        
        # Get data for this row
        row_data = self.csv_handler.get_row_data(row_index)
        
        # Process each placeholder
        for placeholder in self.placeholder_manager.placeholders:
            # Use the placeholder's get_value method which handles all types
            value = placeholder.get_value(row_index, row_data)
            if not value:
                continue
            
            page = doc[placeholder.page]
            
            # Convert color from 0-255 to 0-1 range if needed
            color = placeholder.font_color
            if any(c > 1 for c in color):
                color = tuple(c / 255 for c in color)
            
            # Insert text at placeholder position
            page.insert_text(
                point=(placeholder.x, placeholder.y),
                text=value,
                fontname=placeholder.font_name,
                fontsize=placeholder.font_size,
                color=color
            )
        
        # Save the modified PDF
        doc.save(output_path)
        doc.close()
    
    def generate_preview(self, output_path: str) -> None:
        """Generate a preview PDF with placeholder names as text (without braces)."""
        doc = fitz.open(self.pdf_path)
        
        for placeholder in self.placeholder_manager.placeholders:
            # For preview, show the name without braces
            if placeholder.placeholder_type == PLACEHOLDER_TYPE_COLUMN:
                value = placeholder.name
            else:
                # For static/serial, show actual value
                value = placeholder.get_value(0, {})
            
            if not value:
                continue
            
            page = doc[placeholder.page]
            
            color = placeholder.font_color
            if any(c > 1 for c in color):
                color = tuple(c / 255 for c in color)
            
            page.insert_text(
                point=(placeholder.x, placeholder.y),
                text=value,
                fontname=placeholder.font_name,
                fontsize=placeholder.font_size,
                color=color
            )
        
        doc.save(output_path)
        doc.close()
    
    def generate_batch(
        self,
        output_dir: str,
        filename_pattern: str = "output_{index}.pdf",
        progress_callback: Optional[Callable[[int, int], None]] = None,
        start_row: int = 0,
        end_row: Optional[int] = None
    ) -> list[str]:
        """
        Generate PDFs for a range of rows in the CSV.
        
        Args:
            output_dir: Directory to save generated PDFs
            filename_pattern: Pattern for output filenames. 
                             Use {index} for row number, or {column_name} for CSV values
            progress_callback: Function called with (current, total) for progress updates
            start_row: First row to process (0-indexed)
            end_row: Last row to process (exclusive), None for all rows
        
        Returns:
            List of generated file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        
        total_rows = self.csv_handler.get_row_count()
        
        # Calculate range
        start = max(0, min(start_row, total_rows))
        end = total_rows if end_row is None else min(end_row, total_rows)
        
        generated_files = []
        count = end - start
        
        for idx, i in enumerate(range(start, end)):
            # Generate filename
            filename = filename_pattern.replace("{index}", str(i + 1))
            
            # Replace any column placeholders in filename
            row_data = self.csv_handler.get_row_data(i)
            for name, value in row_data.items():
                # Sanitize value for filename
                safe_value = "".join(c for c in str(value) if c.isalnum() or c in "._- ")
                filename = filename.replace(f"{{{name}}}", safe_value)
            
            output_path = os.path.join(output_dir, filename)
            
            # Generate the PDF
            self.generate_single(i, output_path)
            generated_files.append(output_path)
            
            # Report progress
            if progress_callback:
                progress_callback(idx + 1, count)
        
        return generated_files
    
    def merge_pdfs(self, pdf_files: list[str], output_path: str) -> None:
        """
        Merge multiple PDFs into a single file.
        
        Args:
            pdf_files: List of PDF file paths to merge
            output_path: Path for the merged output PDF
        """
        merged_doc = fitz.open()
        
        for pdf_path in pdf_files:
            doc = fitz.open(pdf_path)
            merged_doc.insert_pdf(doc)
            doc.close()
        
        merged_doc.save(output_path)
        merged_doc.close()

