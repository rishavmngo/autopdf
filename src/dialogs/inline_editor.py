"""Inline editor widget for editing placeholders with live preview."""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Optional, Callable, Tuple
from ..placeholder import Placeholder
from ..pdf_generator import FONT_DISPLAY_NAMES


class InlineEditor(tk.Frame):
    """Inline editor panel for editing placeholders with live updates."""
    
    def __init__(
        self,
        parent: tk.Widget,
        on_change: Optional[Callable[[Placeholder], None]] = None,
        on_delete: Optional[Callable[[Placeholder], None]] = None
    ):
        super().__init__(parent, bg="#3a3a3a")
        
        self.on_change = on_change
        self.on_delete = on_delete
        self.current_placeholder: Optional[Placeholder] = None
        self._updating = False  # Prevent recursive updates
        
        self._create_ui()
        self.hide()
    
    def _create_ui(self) -> None:
        """Create the editor UI."""
        # Header with title and close button
        header = tk.Frame(self, bg="#4a9eff")
        header.pack(fill=tk.X)
        
        self.title_label = tk.Label(
            header, text="Edit Placeholder",
            bg="#4a9eff", fg="white", font=("Arial", 10, "bold"),
            padx=10, pady=5
        )
        self.title_label.pack(side=tk.LEFT)
        
        tk.Button(
            header, text="✕", command=self.hide,
            bg="#4a9eff", fg="white", bd=0,
            font=("Arial", 10), padx=8
        ).pack(side=tk.RIGHT)
        
        # Main content
        content = tk.Frame(self, bg="#3a3a3a", padx=10, pady=10)
        content.pack(fill=tk.BOTH, expand=True)
        
        label_style = {"bg": "#3a3a3a", "fg": "white", "font": ("Arial", 9)}
        
        # Name field
        name_frame = tk.Frame(content, bg="#3a3a3a")
        name_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(name_frame, text="Name:", width=6, anchor=tk.W, **label_style).pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            name_frame, textvariable=self.name_var,
            bg="#2b2b2b", fg="white", insertbackground="white", width=20
        )
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.name_var.trace_add("write", lambda *args: self._on_field_change())
        
        # Position controls
        pos_frame = tk.Frame(content, bg="#3a3a3a")
        pos_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(pos_frame, text="X:", **label_style).pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        self.x_spin = tk.Spinbox(
            pos_frame, from_=0, to=2000, increment=1,
            textvariable=self.x_var, width=6,
            bg="#2b2b2b", fg="white",
            command=self._on_field_change
        )
        self.x_spin.pack(side=tk.LEFT, padx=(2, 10))
        self.x_spin.bind("<Return>", lambda e: self._on_field_change())
        self.x_spin.bind("<FocusOut>", lambda e: self._on_field_change())
        
        tk.Label(pos_frame, text="Y:", **label_style).pack(side=tk.LEFT)
        self.y_var = tk.StringVar()
        self.y_spin = tk.Spinbox(
            pos_frame, from_=0, to=2000, increment=1,
            textvariable=self.y_var, width=6,
            bg="#2b2b2b", fg="white",
            command=self._on_field_change
        )
        self.y_spin.pack(side=tk.LEFT, padx=2)
        self.y_spin.bind("<Return>", lambda e: self._on_field_change())
        self.y_spin.bind("<FocusOut>", lambda e: self._on_field_change())
        
        # Nudge buttons
        nudge_frame = tk.Frame(pos_frame, bg="#3a3a3a")
        nudge_frame.pack(side=tk.RIGHT)
        
        btn_style = {"bg": "#2b2b2b", "fg": "white", "width": 2, "font": ("Arial", 8)}
        tk.Button(nudge_frame, text="◀", command=lambda: self._nudge(-5, 0), **btn_style).pack(side=tk.LEFT)
        tk.Button(nudge_frame, text="▲", command=lambda: self._nudge(0, -5), **btn_style).pack(side=tk.LEFT)
        tk.Button(nudge_frame, text="▼", command=lambda: self._nudge(0, 5), **btn_style).pack(side=tk.LEFT)
        tk.Button(nudge_frame, text="▶", command=lambda: self._nudge(5, 0), **btn_style).pack(side=tk.LEFT)
        
        # Font and size
        font_frame = tk.Frame(content, bg="#3a3a3a")
        font_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(font_frame, text="Font:", width=6, anchor=tk.W, **label_style).pack(side=tk.LEFT)
        self.font_var = tk.StringVar()
        self.font_combo = ttk.Combobox(
            font_frame,
            textvariable=self.font_var,
            values=list(FONT_DISPLAY_NAMES.keys()),
            state="readonly",
            width=10
        )
        self.font_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.font_combo.bind("<<ComboboxSelected>>", lambda e: self._on_field_change())
        
        tk.Label(font_frame, text="Size:", **label_style).pack(side=tk.LEFT)
        self.size_var = tk.StringVar()
        self.size_spin = tk.Spinbox(
            font_frame, from_=6, to=72, increment=1,
            textvariable=self.size_var, width=4,
            bg="#2b2b2b", fg="white",
            command=self._on_field_change
        )
        self.size_spin.pack(side=tk.LEFT, padx=2)
        self.size_spin.bind("<Return>", lambda e: self._on_field_change())
        self.size_spin.bind("<FocusOut>", lambda e: self._on_field_change())
        
        # Color picker
        color_frame = tk.Frame(content, bg="#3a3a3a")
        color_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(color_frame, text="Color:", width=6, anchor=tk.W, **label_style).pack(side=tk.LEFT)
        self.color_btn = tk.Button(
            color_frame, text="   ", width=4,
            command=self._pick_color
        )
        self.color_btn.pack(side=tk.LEFT)
        
        self.color_label = tk.Label(
            color_frame, text="#000000",
            bg="#3a3a3a", fg="#888888", font=("Arial", 9)
        )
        self.color_label.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        btn_frame = tk.Frame(content, bg="#3a3a3a")
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(
            btn_frame, text="🗑 Delete",
            command=self._on_delete_click,
            bg="#5a3030", fg="white", font=("Arial", 9)
        ).pack(side=tk.RIGHT)
        
        # Store color
        self.selected_color = (0, 0, 0)
    
    def show(self, placeholder: Placeholder) -> None:
        """Show editor with placeholder data."""
        self._updating = True
        self.current_placeholder = placeholder
        
        self.title_label.config(text=f"Edit: {placeholder.get_display_name()}")
        self.name_var.set(placeholder.name)
        self.x_var.set(f"{placeholder.x:.1f}")
        self.y_var.set(f"{placeholder.y:.1f}")
        self.font_var.set(placeholder.font_name)
        self.size_var.set(str(int(placeholder.font_size)))
        
        self.selected_color = placeholder.font_color
        color_hex = self._color_to_hex(self.selected_color)
        self.color_btn.config(bg=color_hex)
        self.color_label.config(text=color_hex)
        
        self._updating = False
        self.pack(fill=tk.X, pady=(0, 10))
    
    def hide(self) -> None:
        """Hide the editor."""
        self.current_placeholder = None
        self.pack_forget()
    
    def _nudge(self, dx: float, dy: float) -> None:
        """Move position by delta."""
        if not self.current_placeholder:
            return
        
        try:
            x = float(self.x_var.get()) + dx
            y = float(self.y_var.get()) + dy
            x = max(0, x)
            y = max(0, y)
            self.x_var.set(f"{x:.1f}")
            self.y_var.set(f"{y:.1f}")
            self._on_field_change()
        except ValueError:
            pass
    
    def _on_field_change(self) -> None:
        """Handle any field change - update placeholder live."""
        if self._updating or not self.current_placeholder:
            return
        
        try:
            # Update placeholder from fields
            name = self.name_var.get().strip()
            if name:
                name = name.replace("{", "").replace("}", "")
                self.current_placeholder.name = name
            
            self.current_placeholder.x = float(self.x_var.get())
            self.current_placeholder.y = float(self.y_var.get())
            self.current_placeholder.font_name = self.font_var.get()
            self.current_placeholder.font_size = float(self.size_var.get())
            self.current_placeholder.font_color = self.selected_color
            
            # Notify callback to refresh view
            if self.on_change:
                self.on_change(self.current_placeholder)
        except ValueError:
            pass
    
    def _color_to_hex(self, color: Tuple[float, ...]) -> str:
        """Convert RGB tuple to hex."""
        if any(c > 1 for c in color):
            r, g, b = int(color[0]), int(color[1]), int(color[2])
        else:
            r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _pick_color(self) -> None:
        """Open color picker."""
        if not self.current_placeholder:
            return
        
        initial = self._color_to_hex(self.selected_color)
        result = colorchooser.askcolor(color=initial, parent=self)
        
        if result[0]:
            self.selected_color = tuple(c / 255 for c in result[0])
            self.color_btn.config(bg=result[1])
            self.color_label.config(text=result[1])
            self._on_field_change()
    
    def _on_delete_click(self) -> None:
        """Handle delete button."""
        if self.current_placeholder and self.on_delete:
            placeholder = self.current_placeholder
            self.hide()
            self.on_delete(placeholder)
