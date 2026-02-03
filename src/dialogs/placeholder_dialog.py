"""Dialog for adding/editing placeholders with position controls."""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Optional, Tuple, Callable
from ..placeholder import Placeholder
from ..pdf_generator import FONT_DISPLAY_NAMES


class PlaceholderDialog(tk.Toplevel):
    """Dialog for adding or editing a placeholder with live positioning."""
    
    def __init__(
        self,
        parent: tk.Widget,
        page: int,
        x: float,
        y: float,
        existing: Optional[Placeholder] = None,
        on_position_change: Optional[Callable[[float, float], None]] = None
    ):
        super().__init__(parent)
        
        self.result: Optional[Placeholder] = None
        self.page = page
        self.x = x
        self.y = y
        self.selected_color = existing.font_color if existing else (0, 0, 0)
        self.on_position_change = on_position_change
        self.existing = existing
        
        # Window setup
        self.title("Edit Placeholder" if existing else "Add Placeholder")
        self.geometry("420x480")
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)
        self.transient(parent)
        
        # Make modal - delayed until window is visible
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Main frame
        main_frame = tk.Frame(self, bg="#2b2b2b", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style for labels
        label_style = {"bg": "#2b2b2b", "fg": "white", "font": ("Arial", 10)}
        entry_style = {"bg": "#3c3c3c", "fg": "white", "insertbackground": "white"}
        
        # Name field
        tk.Label(main_frame, text="Placeholder Name:", **label_style).pack(anchor=tk.W)
        self.name_entry = tk.Entry(main_frame, width=40, **entry_style)
        self.name_entry.pack(fill=tk.X, pady=(5, 10))
        if existing:
            self.name_entry.insert(0, existing.name)
        
        # Help text
        tk.Label(
            main_frame, 
            text="Enter name without curly braces (e.g., 'first_name')",
            bg="#2b2b2b", fg="#888888", font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        # Separator
        tk.Frame(main_frame, bg="#404040", height=1).pack(fill=tk.X, pady=15)
        
        # Position controls
        pos_label_frame = tk.Frame(main_frame, bg="#2b2b2b")
        pos_label_frame.pack(fill=tk.X)
        tk.Label(pos_label_frame, text="Position:", **label_style).pack(side=tk.LEFT)
        tk.Label(
            pos_label_frame, text="(drag on PDF or use arrows)",
            bg="#2b2b2b", fg="#888888", font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=10)
        
        pos_frame = tk.Frame(main_frame, bg="#2b2b2b")
        pos_frame.pack(fill=tk.X, pady=10)
        
        # X position
        x_frame = tk.Frame(pos_frame, bg="#2b2b2b")
        x_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(x_frame, text="X:", **label_style).pack(side=tk.LEFT)
        self.x_var = tk.StringVar(value=f"{self.x:.1f}")
        self.x_spin = tk.Spinbox(
            x_frame, from_=0, to=1000, increment=1,
            textvariable=self.x_var, width=8,
            bg="#3c3c3c", fg="white",
            command=self._on_position_spin
        )
        self.x_spin.pack(side=tk.LEFT, padx=5)
        self.x_spin.bind("<Return>", lambda e: self._on_position_spin())
        
        # Y position
        y_frame = tk.Frame(pos_frame, bg="#2b2b2b")
        y_frame.pack(side=tk.LEFT)
        
        tk.Label(y_frame, text="Y:", **label_style).pack(side=tk.LEFT)
        self.y_var = tk.StringVar(value=f"{self.y:.1f}")
        self.y_spin = tk.Spinbox(
            y_frame, from_=0, to=1000, increment=1,
            textvariable=self.y_var, width=8,
            bg="#3c3c3c", fg="white",
            command=self._on_position_spin
        )
        self.y_spin.pack(side=tk.LEFT, padx=5)
        self.y_spin.bind("<Return>", lambda e: self._on_position_spin())
        
        # Nudge buttons
        nudge_frame = tk.Frame(main_frame, bg="#2b2b2b")
        nudge_frame.pack(pady=5)
        
        btn_style = {"bg": "#3c3c3c", "fg": "white", "width": 3, "font": ("Arial", 10)}
        
        # Create arrow button layout
        tk.Button(nudge_frame, text="▲", command=lambda: self._nudge(0, -5), **btn_style).grid(row=0, column=1)
        tk.Button(nudge_frame, text="◀", command=lambda: self._nudge(-5, 0), **btn_style).grid(row=1, column=0)
        tk.Button(nudge_frame, text="•", command=lambda: None, bg="#2b2b2b", fg="#2b2b2b", width=3, bd=0).grid(row=1, column=1)
        tk.Button(nudge_frame, text="▶", command=lambda: self._nudge(5, 0), **btn_style).grid(row=1, column=2)
        tk.Button(nudge_frame, text="▼", command=lambda: self._nudge(0, 5), **btn_style).grid(row=2, column=1)
        
        tk.Label(
            main_frame, text="Fine: hold Shift for 1px nudge",
            bg="#2b2b2b", fg="#666666", font=("Arial", 8)
        ).pack()
        
        # Separator
        tk.Frame(main_frame, bg="#404040", height=1).pack(fill=tk.X, pady=15)
        
        # Font selection
        font_frame = tk.Frame(main_frame, bg="#2b2b2b")
        font_frame.pack(fill=tk.X)
        
        tk.Label(font_frame, text="Font:", **label_style).pack(side=tk.LEFT)
        
        self.font_var = tk.StringVar(value=existing.font_name if existing else "helv")
        self.font_combo = ttk.Combobox(
            font_frame, 
            textvariable=self.font_var,
            values=list(FONT_DISPLAY_NAMES.keys()),
            state="readonly",
            width=12
        )
        self.font_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Size field
        tk.Label(font_frame, text="Size:", **label_style).pack(side=tk.LEFT)
        
        self.size_var = tk.StringVar(value=str(existing.font_size if existing else 12))
        self.size_spin = tk.Spinbox(
            font_frame,
            from_=6, to=72, increment=1,
            textvariable=self.size_var,
            width=5,
            bg="#3c3c3c", fg="white"
        )
        self.size_spin.pack(side=tk.LEFT, padx=5)
        
        # Color picker
        color_frame = tk.Frame(main_frame, bg="#2b2b2b")
        color_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(color_frame, text="Color:", **label_style).pack(side=tk.LEFT)
        
        self.color_btn = tk.Button(
            color_frame,
            text="     ",
            bg=self._color_to_hex(self.selected_color),
            command=self._pick_color,
            width=5
        )
        self.color_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.color_label = tk.Label(
            color_frame,
            text=self._color_to_hex(self.selected_color),
            bg="#2b2b2b", fg="#888888"
        )
        self.color_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2b2b2b")
        btn_frame.pack(fill=tk.X, pady=(25, 0))
        
        if existing:
            tk.Button(
                btn_frame, text="Delete", command=self._on_delete,
                bg="#5a3030", fg="white", width=8
            ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame, text="Cancel", command=self._on_cancel,
            bg="#3c3c3c", fg="white", width=10
        ).pack(side=tk.RIGHT)
        
        tk.Button(
            btn_frame, text="OK", command=self._on_ok,
            bg="#4a9eff", fg="white", width=10
        ).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Focus on name entry
        self.name_entry.focus_set()
        
        # Bind Enter key
        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel())
        
        # Bind arrow keys for nudging
        self.bind("<Up>", lambda e: self._nudge(0, -5 if not e.state & 1 else -1))
        self.bind("<Down>", lambda e: self._nudge(0, 5 if not e.state & 1 else 1))
        self.bind("<Left>", lambda e: self._nudge(-5 if not e.state & 1 else -1, 0))
        self.bind("<Right>", lambda e: self._nudge(5 if not e.state & 1 else 1, 0))
        
        # Center on parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - self.winfo_width()) // 2
        y = parent_y + (parent_h - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _nudge(self, dx: float, dy: float) -> None:
        """Move position by delta."""
        try:
            self.x = float(self.x_var.get()) + dx
            self.y = float(self.y_var.get()) + dy
        except ValueError:
            pass
        
        self.x = max(0, self.x)
        self.y = max(0, self.y)
        
        self.x_var.set(f"{self.x:.1f}")
        self.y_var.set(f"{self.y:.1f}")
        
        if self.on_position_change:
            self.on_position_change(self.x, self.y)
    
    def _on_position_spin(self) -> None:
        """Handle position spinbox change."""
        try:
            self.x = float(self.x_var.get())
            self.y = float(self.y_var.get())
            if self.on_position_change:
                self.on_position_change(self.x, self.y)
        except ValueError:
            pass
    
    def _color_to_hex(self, color: Tuple[float, ...]) -> str:
        """Convert RGB tuple (0-1 range) to hex color."""
        if any(c > 1 for c in color):
            r, g, b = int(color[0]), int(color[1]), int(color[2])
        else:
            r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _pick_color(self) -> None:
        """Open color picker dialog."""
        initial_color = self._color_to_hex(self.selected_color)
        color = colorchooser.askcolor(color=initial_color, parent=self)
        if color[0]:
            self.selected_color = tuple(c / 255 for c in color[0])
            self.color_btn.configure(bg=color[1])
            self.color_label.configure(text=color[1])
    
    def _on_ok(self) -> None:
        """Handle OK button click."""
        name = self.name_entry.get().strip()
        if not name:
            self.name_entry.configure(bg="#5a3030")
            return
        
        # Remove curly braces if user included them
        name = name.replace("{", "").replace("}", "")
        
        try:
            size = float(self.size_var.get())
        except ValueError:
            size = 12.0
        
        try:
            final_x = float(self.x_var.get())
            final_y = float(self.y_var.get())
        except ValueError:
            final_x = self.x
            final_y = self.y
        
        self.result = Placeholder(
            name=name,
            page=self.page,
            x=final_x,
            y=final_y,
            font_name=self.font_var.get(),
            font_size=size,
            font_color=self.selected_color
        )
        
        self.destroy()
    
    def _on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.result = None
        self.destroy()
    
    def _on_delete(self) -> None:
        """Handle Delete button click."""
        self.result = "DELETE"  # Special marker
        self.destroy()
    
    def show(self) -> Optional[Placeholder]:
        """Show dialog and return result."""
        self.wait_visibility()
        self.grab_set()
        self.focus_force()
        self.name_entry.focus_set()
        self.wait_window()
        return self.result
