"""PDF Viewer component for displaying and interacting with PDF pages."""

import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Canvas
from typing import Callable, Optional
from .placeholder import Placeholder, PlaceholderManager


class PDFViewer:
    """Component for viewing PDF pages and managing placeholder positions."""
    
    def __init__(
        self,
        parent: tk.Widget,
        placeholder_manager: PlaceholderManager,
        on_click: Optional[Callable[[int, float, float], None]] = None,
        on_placeholder_edit: Optional[Callable[[Placeholder], None]] = None,
        on_placeholder_move: Optional[Callable[[Placeholder, float, float], None]] = None
    ):
        """
        Initialize PDF viewer.
        
        Args:
            parent: Parent tkinter widget
            placeholder_manager: Manager for placeholders
            on_click: Callback when PDF is clicked (page, x, y)
            on_placeholder_edit: Callback when placeholder is double-clicked
            on_placeholder_move: Callback when placeholder is dragged (placeholder, new_x, new_y)
        """
        self.parent = parent
        self.placeholder_manager = placeholder_manager
        self.on_click = on_click
        self.on_placeholder_edit = on_placeholder_edit
        self.on_placeholder_move = on_placeholder_move
        
        self.doc: Optional[fitz.Document] = None
        self.current_page = 0
        self.zoom = 1.0
        self.page_image: Optional[ImageTk.PhotoImage] = None
        self.placeholder_items: dict[int, Placeholder] = {}  # canvas item ID -> Placeholder
        
        # Drag state
        self.dragging_placeholder: Optional[Placeholder] = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Create main frame
        self.frame = tk.Frame(parent, bg="#2b2b2b")
        
        # Create canvas with scrollbars
        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        
        self.canvas = Canvas(
            self.canvas_frame,
            bg="#404040",
            highlightthickness=0,
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Navigation controls
        self.nav_frame = tk.Frame(self.frame, bg="#2b2b2b", pady=5)
        self.nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.prev_btn = tk.Button(
            self.nav_frame, text="◀ Prev", command=self.prev_page,
            bg="#3c3c3c", fg="white", activebackground="#505050"
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(
            self.nav_frame, text="Page 0 / 0", bg="#2b2b2b", fg="white"
        )
        self.page_label.pack(side=tk.LEFT, expand=True)
        
        self.next_btn = tk.Button(
            self.nav_frame, text="Next ▶", command=self.next_page,
            bg="#3c3c3c", fg="white", activebackground="#505050"
        )
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        # Zoom controls
        zoom_frame = tk.Frame(self.nav_frame, bg="#2b2b2b")
        zoom_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            zoom_frame, text="-", width=2, command=self.zoom_out,
            bg="#3c3c3c", fg="white"
        ).pack(side=tk.LEFT)
        
        self.zoom_label = tk.Label(
            zoom_frame, text="100%", bg="#2b2b2b", fg="white", width=5
        )
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            zoom_frame, text="+", width=2, command=self.zoom_in,
            bg="#3c3c3c", fg="white"
        ).pack(side=tk.LEFT)
        
        # Bind events
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        
        # Store page offset for coordinate calculation
        self.page_offset_x = 0
        self.page_offset_y = 0
    
    def pack(self, **kwargs):
        """Pack the viewer frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the viewer frame."""
        self.frame.grid(**kwargs)
    
    def load_pdf(self, path: str) -> None:
        """Load a PDF file."""
        if self.doc:
            self.doc.close()
        
        self.doc = fitz.open(path)
        self.current_page = 0
        self._render_page()
    
    def _render_page(self) -> None:
        """Render the current page to the canvas."""
        if not self.doc or self.current_page >= len(self.doc):
            return
        
        page = self.doc[self.current_page]
        
        # Create pixmap with zoom
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        self.page_image = ImageTk.PhotoImage(img)
        
        # Clear canvas and draw page
        self.canvas.delete("all")
        
        # Center the page on canvas
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        self.page_offset_x = max(20, (canvas_width - pix.width) // 2)
        self.page_offset_y = 20
        
        self.canvas.create_image(
            self.page_offset_x, self.page_offset_y,
            anchor=tk.NW, image=self.page_image, tags="page"
        )
        
        # Update scroll region
        self.canvas.config(scrollregion=(
            0, 0,
            max(canvas_width, pix.width + 40),
            max(canvas_height, pix.height + 40)
        ))
        
        # Draw placeholders
        self._draw_placeholders()
        
        # Update page label
        self.page_label.config(
            text=f"Page {self.current_page + 1} / {len(self.doc)}"
        )
        self.zoom_label.config(text=f"{int(self.zoom * 100)}%")
    
    def _draw_placeholders(self) -> None:
        """Draw placeholder markers on the canvas with live preview."""
        # Clear mapping
        self.placeholder_items.clear()
        
        # Get placeholders for current page
        placeholders = self.placeholder_manager.get_for_page(self.current_page)
        
        for p in placeholders:
            # Convert PDF coordinates to canvas coordinates
            canvas_x = self.page_offset_x + (p.x * self.zoom)
            canvas_y = self.page_offset_y + (p.y * self.zoom)
            
            # Calculate font size for preview (scaled)
            preview_size = max(8, int(p.font_size * self.zoom * 0.8))
            
            # Convert color
            if any(c > 1 for c in p.font_color):
                color = f"#{int(p.font_color[0]):02x}{int(p.font_color[1]):02x}{int(p.font_color[2]):02x}"
            else:
                color = f"#{int(p.font_color[0]*255):02x}{int(p.font_color[1]*255):02x}{int(p.font_color[2]*255):02x}"
            
            # Display text - show the placeholder name as preview
            display_text = p.get_display_name()
            
            # Create draggable text with styling
            # Background for visibility
            text_id = self.canvas.create_text(
                canvas_x, canvas_y,
                text=display_text,
                anchor=tk.SW,  # Bottom-left anchor to match PDF text positioning
                fill=color,
                font=("Arial", preview_size, "bold"),
                tags=("placeholder", f"ph_{p.name}")
            )
            
            # Get text bounds for background
            bbox = self.canvas.bbox(text_id)
            if bbox:
                # Create semi-transparent background
                bg_id = self.canvas.create_rectangle(
                    bbox[0] - 2, bbox[1] - 1,
                    bbox[2] + 2, bbox[3] + 1,
                    fill="#ffffff", outline="#4a9eff", width=2,
                    stipple="gray50",
                    tags=("placeholder_bg", f"ph_{p.name}")
                )
                # Raise text above background
                self.canvas.tag_raise(text_id, bg_id)
                
                # Map both items to placeholder
                self.placeholder_items[bg_id] = p
            
            self.placeholder_items[text_id] = p
    
    def _find_placeholder_at(self, x: float, y: float) -> Optional[Placeholder]:
        """Find placeholder at canvas coordinates."""
        items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        for item_id in items:
            if item_id in self.placeholder_items:
                return self.placeholder_items[item_id]
        return None
    
    def _on_canvas_click(self, event: tk.Event) -> None:
        """Handle click on canvas - either start drag or add new placeholder."""
        if not self.doc:
            return
        
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Check if clicking on a placeholder
        placeholder = self._find_placeholder_at(canvas_x, canvas_y)
        
        if placeholder:
            # Start dragging
            self.dragging_placeholder = placeholder
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
            self.canvas.config(cursor="fleur")  # Move cursor
        else:
            # Convert to PDF coordinates and trigger new placeholder
            pdf_x = (canvas_x - self.page_offset_x) / self.zoom
            pdf_y = (canvas_y - self.page_offset_y) / self.zoom
            
            # Check if within page bounds
            page = self.doc[self.current_page]
            rect = page.rect
            
            if 0 <= pdf_x <= rect.width and 0 <= pdf_y <= rect.height:
                if self.on_click:
                    self.on_click(self.current_page, pdf_x, pdf_y)
    
    def _on_drag(self, event: tk.Event) -> None:
        """Handle drag motion."""
        if not self.dragging_placeholder:
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Calculate delta
        dx = canvas_x - self.drag_start_x
        dy = canvas_y - self.drag_start_y
        
        # Move all items with this placeholder's tag
        tag = f"ph_{self.dragging_placeholder.name}"
        self.canvas.move(tag, dx, dy)
        
        # Also move background
        for item_id, p in self.placeholder_items.items():
            if p == self.dragging_placeholder:
                tags = self.canvas.gettags(item_id)
                if "placeholder_bg" in tags:
                    self.canvas.move(item_id, dx, dy)
        
        self.drag_start_x = canvas_x
        self.drag_start_y = canvas_y
    
    def _on_drag_end(self, event: tk.Event) -> None:
        """Handle end of drag."""
        if not self.dragging_placeholder:
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to PDF coordinates
        new_x = (canvas_x - self.page_offset_x) / self.zoom
        new_y = (canvas_y - self.page_offset_y) / self.zoom
        
        # Clamp to page bounds
        if self.doc:
            page = self.doc[self.current_page]
            rect = page.rect
            new_x = max(0, min(new_x, rect.width))
            new_y = max(0, min(new_y, rect.height))
        
        # Update placeholder position
        self.dragging_placeholder.x = new_x
        self.dragging_placeholder.y = new_y
        
        # Notify callback
        if self.on_placeholder_move:
            self.on_placeholder_move(self.dragging_placeholder, new_x, new_y)
        
        self.dragging_placeholder = None
        self.canvas.config(cursor="")
        
        # Refresh to redraw cleanly
        self._render_page()
    
    def _on_double_click(self, event: tk.Event) -> None:
        """Handle double-click to edit placeholder."""
        if not self.doc:
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        placeholder = self._find_placeholder_at(canvas_x, canvas_y)
        
        if placeholder and self.on_placeholder_edit:
            self.on_placeholder_edit(placeholder)
    
    def refresh(self) -> None:
        """Refresh the display."""
        self._render_page()
    
    def prev_page(self) -> None:
        """Go to previous page."""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self._render_page()
    
    def next_page(self) -> None:
        """Go to next page."""
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self._render_page()
    
    def zoom_in(self) -> None:
        """Increase zoom level."""
        if self.zoom < 3.0:
            self.zoom += 0.25
            self._render_page()
    
    def zoom_out(self) -> None:
        """Decrease zoom level."""
        if self.zoom > 0.5:
            self.zoom -= 0.25
            self._render_page()
    
    def get_current_page(self) -> int:
        """Get current page number."""
        return self.current_page
    
    def get_page_count(self) -> int:
        """Get total page count."""
        return len(self.doc) if self.doc else 0
    
    def close(self) -> None:
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None
