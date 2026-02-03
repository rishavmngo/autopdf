"""Dialog for mapping CSV headers to placeholders."""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class CSVMappingDialog(tk.Toplevel):
    """Dialog for mapping CSV columns to placeholders."""
    
    def __init__(
        self,
        parent: tk.Widget,
        csv_headers: list[str],
        placeholder_names: list[str]
    ):
        super().__init__(parent)
        
        self.csv_headers = csv_headers
        self.placeholder_names = placeholder_names
        self.result: Optional[dict[str, str]] = None
        self.combos: dict[str, ttk.Combobox] = {}
        
        # Window setup
        self.title("Map CSV Columns to Placeholders")
        self.configure(bg="#2b2b2b")
        self.resizable(True, True)
        self.transient(parent)
        
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Main frame
        main_frame = tk.Frame(self, bg="#2b2b2b", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(
            main_frame,
            text="Map each placeholder to a CSV column:",
            bg="#2b2b2b", fg="white", font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Scrollable frame for mappings
        canvas_frame = tk.Frame(main_frame, bg="#2b2b2b")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#2b2b2b", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        self.mappings_frame = tk.Frame(canvas, bg="#2b2b2b")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas.create_window((0, 0), window=self.mappings_frame, anchor=tk.NW)
        
        self.mappings_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create mapping rows
        label_style = {"bg": "#2b2b2b", "fg": "white", "font": ("Arial", 10)}
        
        # Add "None" option to headers
        header_options = ["(Not mapped)"] + csv_headers
        
        for i, placeholder in enumerate(placeholder_names):
            row = tk.Frame(self.mappings_frame, bg="#2b2b2b")
            row.pack(fill=tk.X, pady=5)
            
            # Placeholder name
            tk.Label(
                row, text=f"{{{{{placeholder}}}}}:", width=20, anchor=tk.E, **label_style
            ).pack(side=tk.LEFT)
            
            # Arrow
            tk.Label(row, text="→", bg="#2b2b2b", fg="#888888").pack(side=tk.LEFT, padx=10)
            
            # CSV header dropdown
            combo = ttk.Combobox(row, values=header_options, state="readonly", width=25)
            combo.pack(side=tk.LEFT)
            
            # Try to auto-match by name
            matched = False
            for header in csv_headers:
                if header.lower().replace(" ", "_") == placeholder.lower():
                    combo.set(header)
                    matched = True
                    break
                elif header.lower() == placeholder.lower():
                    combo.set(header)
                    matched = True
                    break
            
            if not matched:
                combo.set("(Not mapped)")
            
            self.combos[placeholder] = combo
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2b2b2b")
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(
            btn_frame, text="Cancel", command=self._on_cancel,
            bg="#3c3c3c", fg="white", width=10
        ).pack(side=tk.RIGHT)
        
        tk.Button(
            btn_frame, text="Apply Mapping", command=self._on_ok,
            bg="#4a9eff", fg="white", width=12
        ).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Bind Escape key
        self.bind("<Escape>", lambda e: self._on_cancel())
        
        # Size window based on content
        self.update_idletasks()
        width = max(500, self.mappings_frame.winfo_reqwidth() + 60)
        height = min(500, self.mappings_frame.winfo_reqheight() + 150)
        self.geometry(f"{width}x{height}")
        
        # Center on parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_ok(self) -> None:
        """Handle OK button click."""
        self.result = {}
        
        for placeholder, combo in self.combos.items():
            header = combo.get()
            if header and header != "(Not mapped)":
                self.result[placeholder] = header
        
        self.destroy()
    
    def _on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.result = None
        self.destroy()
    
    def show(self) -> Optional[dict[str, str]]:
        """Show dialog and return mapping result."""
        # Wait for window to be visible before grabbing
        self.wait_visibility()
        self.grab_set()
        self.focus_force()
        self.wait_window()
        return self.result
