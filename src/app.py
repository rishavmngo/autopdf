"""Main application window."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from .pdf_viewer import PDFViewer
from .placeholder import PlaceholderManager, Placeholder
from .template import Template
from .csv_handler import CSVHandler
from .pdf_generator import PDFGenerator, FONT_DISPLAY_NAMES
from .dialogs.placeholder_dialog import PlaceholderDialog
from .dialogs.csv_mapping_dialog import CSVMappingDialog
from .dialogs.inline_editor import InlineEditor


class PDFTemplateApp:
    """Main application for PDF template generation."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF Template Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        
        # Set minimum size
        self.root.minsize(900, 600)
        
        # Initialize data
        self.template = Template()
        self.csv_handler = CSVHandler()
        self.current_pdf_path: str = None
        
        # Create UI
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = tk.Menu(self.root, bg="#2b2b2b", fg="white")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Open PDF...", command=self._open_pdf, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Load Template...", command=self._load_template)
        file_menu.add_command(label="Save Template...", command=self._save_template, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        
        # CSV menu
        csv_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="CSV", menu=csv_menu)
        
        csv_menu.add_command(label="Import CSV...", command=self._import_csv)
        csv_menu.add_command(label="Configure Mapping...", command=self._configure_mapping)
        
        # Generate menu
        gen_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Generate", menu=gen_menu)
        
        gen_menu.add_command(label="Generate PDFs...", command=self._generate_pdfs, accelerator="Ctrl+G")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        
        help_menu.add_command(label="How to Use", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self._open_pdf())
        self.root.bind("<Control-s>", lambda e: self._save_template())
        self.root.bind("<Control-g>", lambda e: self._generate_pdfs())
    
    def _create_main_layout(self) -> None:
        """Create the main application layout."""
        # Main container
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: PDF Viewer with all callbacks
        self.pdf_viewer = PDFViewer(
            main_container,
            self.template.placeholder_manager,
            on_click=self._on_pdf_click,
            on_placeholder_select=self._on_placeholder_select,
            on_placeholder_move=self._on_placeholder_moved
        )
        self.pdf_viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel: Sidebar
        self._create_sidebar(main_container)
    
    def _create_sidebar(self, parent: tk.Widget) -> None:
        """Create the right sidebar with placeholder list and controls."""
        sidebar = tk.Frame(parent, bg="#2b2b2b", width=320)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        sidebar.pack_propagate(False)
        
        # Title
        tk.Label(
            sidebar, text="Placeholders", 
            bg="#2b2b2b", fg="white", font=("Arial", 12, "bold")
        ).pack(fill=tk.X, pady=10)
        
        # Instructions
        self.instruction_label = tk.Label(
            sidebar,
            text="Click on PDF to add • Click placeholder to edit",
            bg="#2b2b2b", fg="#888888", font=("Arial", 9),
            justify=tk.CENTER
        )
        self.instruction_label.pack(fill=tk.X, pady=5)
        
        # Inline editor (hidden by default)
        self.inline_editor = InlineEditor(
            sidebar,
            on_change=self._on_inline_editor_change,
            on_delete=self._on_inline_editor_delete
        )
        
        # Placeholder list frame
        list_frame = tk.Frame(sidebar, bg="#3c3c3c")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox with scrollbar
        self.placeholder_listbox = tk.Listbox(
            list_frame,
            bg="#3c3c3c", fg="white",
            selectbackground="#4a9eff",
            selectforeground="white",
            font=("Arial", 10),
            borderwidth=0,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(list_frame, command=self.placeholder_listbox.yview)
        self.placeholder_listbox.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.placeholder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Click to select and edit
        self.placeholder_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        
        # Placeholder actions
        actions_frame = tk.Frame(sidebar, bg="#2b2b2b")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            actions_frame, text="Clear All", command=self._clear_placeholders,
            bg="#5a3030", fg="white", width=10
        ).pack(side=tk.RIGHT, padx=2)
        
        # Separator
        tk.Frame(sidebar, bg="#404040", height=2).pack(fill=tk.X, padx=10, pady=15)
        
        # CSV Section
        tk.Label(
            sidebar, text="CSV Data",
            bg="#2b2b2b", fg="white", font=("Arial", 12, "bold")
        ).pack(fill=tk.X)
        
        self.csv_label = tk.Label(
            sidebar, text="No CSV loaded",
            bg="#2b2b2b", fg="#888888", font=("Arial", 9)
        )
        self.csv_label.pack(fill=tk.X, pady=5)
        
        # Mapping status label
        self.mapping_label = tk.Label(
            sidebar, text="",
            bg="#2b2b2b", fg="#4a9eff", font=("Arial", 9)
        )
        self.mapping_label.pack(fill=tk.X)
        
        csv_btn_frame = tk.Frame(sidebar, bg="#2b2b2b")
        csv_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            csv_btn_frame, text="Import CSV", command=self._import_csv,
            bg="#3c3c3c", fg="white"
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            csv_btn_frame, text="Map Columns", command=self._configure_mapping,
            bg="#3c3c3c", fg="white"
        ).pack(side=tk.LEFT, padx=2)
        
        # Separator
        tk.Frame(sidebar, bg="#404040", height=2).pack(fill=tk.X, padx=10, pady=15)
        
        # Generate Section
        tk.Label(
            sidebar, text="Generate PDFs",
            bg="#2b2b2b", fg="white", font=("Arial", 12, "bold")
        ).pack(fill=tk.X)
        
        # Output naming pattern
        pattern_frame = tk.Frame(sidebar, bg="#2b2b2b")
        pattern_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            pattern_frame, text="Filename pattern:",
            bg="#2b2b2b", fg="#888888", font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        self.pattern_entry = tk.Entry(
            pattern_frame, bg="#3c3c3c", fg="white", insertbackground="white"
        )
        self.pattern_entry.insert(0, "output_{index}.pdf")
        self.pattern_entry.pack(fill=tk.X, pady=2)
        
        tk.Label(
            pattern_frame, text="Use {index} or {column_name}",
            bg="#2b2b2b", fg="#666666", font=("Arial", 8)
        ).pack(anchor=tk.W)
        
        # Row range controls
        range_frame = tk.Frame(sidebar, bg="#2b2b2b")
        range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            range_frame, text="Row range:",
            bg="#2b2b2b", fg="#888888", font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        range_inputs = tk.Frame(range_frame, bg="#2b2b2b")
        range_inputs.pack(fill=tk.X)
        
        tk.Label(range_inputs, text="Start:", bg="#2b2b2b", fg="white", font=("Arial", 9)).pack(side=tk.LEFT)
        self.start_row_var = tk.StringVar(value="1")
        self.start_row_entry = tk.Entry(
            range_inputs, textvariable=self.start_row_var,
            bg="#3c3c3c", fg="white", insertbackground="white", width=6
        )
        self.start_row_entry.pack(side=tk.LEFT, padx=(2, 10))
        
        tk.Label(range_inputs, text="End:", bg="#2b2b2b", fg="white", font=("Arial", 9)).pack(side=tk.LEFT)
        self.end_row_var = tk.StringVar(value="")
        self.end_row_entry = tk.Entry(
            range_inputs, textvariable=self.end_row_var,
            bg="#3c3c3c", fg="white", insertbackground="white", width=6
        )
        self.end_row_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(
            range_frame, text="Leave End empty for all rows",
            bg="#2b2b2b", fg="#666666", font=("Arial", 8)
        ).pack(anchor=tk.W)
        
        # Preview button
        tk.Button(
            sidebar, text="👁 Preview Sample",
            command=self._preview_pdf,
            bg="#3c3c3c", fg="white", font=("Arial", 10)
        ).pack(fill=tk.X, padx=10, pady=5)
        
        # Generate button
        self.generate_btn = tk.Button(
            sidebar, text="🚀 Generate PDFs",
            command=self._generate_pdfs,
            bg="#4a9eff", fg="white", font=("Arial", 11, "bold"),
            pady=10
        )
        self.generate_btn.pack(fill=tk.X, padx=10, pady=10)
    
    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = tk.Label(
            self.root,
            text="Ready - Open a PDF to start",
            bg="#1e1e1e", fg="#888888",
            anchor=tk.W, padx=10, pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _set_status(self, message: str) -> None:
        """Update status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def _update_placeholder_list(self) -> None:
        """Update the placeholder listbox."""
        self.placeholder_listbox.delete(0, tk.END)
        
        for p in self.template.placeholder_manager.placeholders:
            display = f"{p.get_display_name()} (pg {p.page + 1})"
            self.placeholder_listbox.insert(tk.END, display)
    
    def _update_mapping_label(self) -> None:
        """Update the mapping status label."""
        if self.csv_handler.mapping:
            count = len(self.csv_handler.mapping)
            self.mapping_label.config(text=f"✓ {count} column(s) mapped")
        else:
            self.mapping_label.config(text="")
    
    # File operations
    def _open_pdf(self) -> None:
        """Open a PDF file."""
        path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if path:
            self.current_pdf_path = path
            self.template.pdf_path = path
            self.template.placeholder_manager.clear()
            self.inline_editor.hide()
            self.pdf_viewer.load_pdf(path)
            self._update_placeholder_list()
            self._set_status(f"Opened: {os.path.basename(path)}")
    
    def _save_template(self) -> None:
        """Save the current template."""
        if not self.template.pdf_path:
            messagebox.showwarning("No PDF", "Please open a PDF first.")
            return
        
        path = filedialog.asksaveasfilename(
            title="Save Template",
            defaultextension=".json",
            filetypes=[("Template files", "*.json")],
            initialdir="templates"
        )
        
        if path:
            self.template.save(path)
            self._set_status(f"Template saved: {os.path.basename(path)}")
    
    def _load_template(self) -> None:
        """Load a template file."""
        path = filedialog.askopenfilename(
            title="Load Template",
            filetypes=[("Template files", "*.json")],
            initialdir="templates"
        )
        
        if path:
            try:
                self.template.load(path)
                
                if self.template.is_valid():
                    self.current_pdf_path = self.template.pdf_path
                    self.inline_editor.hide()
                    self.pdf_viewer.load_pdf(self.template.pdf_path)
                    self._update_placeholder_list()
                    self._set_status(f"Template loaded: {os.path.basename(path)}")
                else:
                    messagebox.showerror(
                        "PDF Not Found",
                        f"The PDF file referenced in this template was not found:\n{self.template.pdf_path}"
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load template: {e}")
    
    # Placeholder operations
    def _on_pdf_click(self, page: int, x: float, y: float) -> None:
        """Handle click on empty PDF area to add placeholder."""
        # Use simple dialog for new placeholder name
        dialog = PlaceholderDialog(self.root, page, x, y)
        result = dialog.show()
        
        if result and result != "DELETE":
            # Check for duplicate name
            existing = self.template.placeholder_manager.get_by_name(result.name)
            if existing:
                messagebox.showwarning(
                    "Duplicate Name",
                    f"A placeholder named '{result.name}' already exists."
                )
                return
            
            self.template.placeholder_manager.add(result)
            self._update_placeholder_list()
            self.pdf_viewer.refresh()
            self._set_status(f"Added placeholder: {result.get_display_name()}")
            
            # Show inline editor for the new placeholder
            self.inline_editor.show(result)
    
    def _on_placeholder_select(self, placeholder: Placeholder) -> None:
        """Handle placeholder selection in viewer - show inline editor."""
        self.inline_editor.show(placeholder)
        
        # Also select in listbox
        try:
            index = self.template.placeholder_manager.placeholders.index(placeholder)
            self.placeholder_listbox.selection_clear(0, tk.END)
            self.placeholder_listbox.selection_set(index)
            self.placeholder_listbox.see(index)
        except ValueError:
            pass
    
    def _on_listbox_select(self, event) -> None:
        """Handle listbox selection."""
        selection = self.placeholder_listbox.curselection()
        if selection:
            index = selection[0]
            placeholder = self.template.placeholder_manager.placeholders[index]
            self.inline_editor.show(placeholder)
            self.pdf_viewer.highlight_placeholder(placeholder)
    
    def _on_placeholder_moved(self, placeholder: Placeholder, new_x: float, new_y: float) -> None:
        """Handle placeholder drag move."""
        self._update_placeholder_list()
        
        # Update inline editor if showing this placeholder
        if self.inline_editor.current_placeholder == placeholder:
            self.inline_editor.show(placeholder)
    
    def _on_inline_editor_change(self, placeholder: Placeholder) -> None:
        """Handle live changes from inline editor."""
        self._update_placeholder_list()
        self.pdf_viewer.refresh()
    
    def _on_inline_editor_delete(self, placeholder: Placeholder) -> None:
        """Handle delete from inline editor."""
        self.template.placeholder_manager.remove(placeholder)
        self._update_placeholder_list()
        self.pdf_viewer.refresh()
        self._set_status(f"Deleted placeholder")
    
    def _clear_placeholders(self) -> None:
        """Clear all placeholders."""
        if self.template.placeholder_manager.placeholders:
            if messagebox.askyesno("Clear All", "Delete all placeholders?"):
                self.template.placeholder_manager.clear()
                self.inline_editor.hide()
                self._update_placeholder_list()
                self.pdf_viewer.refresh()
    
    # CSV operations
    def _import_csv(self) -> None:
        """Import CSV file."""
        path = filedialog.askopenfilename(
            title="Import CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if path:
            try:
                self.csv_handler.load(path)
                self.csv_label.config(
                    text=f"{os.path.basename(path)}\n{self.csv_handler.get_row_count()} rows, {len(self.csv_handler.headers)} columns"
                )
                self._set_status(f"Imported CSV: {os.path.basename(path)}")
                
                # Auto-open mapping dialog if placeholders exist
                if self.template.placeholder_manager.placeholders:
                    self._configure_mapping()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {e}")
    
    def _configure_mapping(self) -> None:
        """Open CSV mapping dialog."""
        if not self.csv_handler.headers:
            messagebox.showwarning("No CSV", "Please import a CSV file first.")
            return
        
        placeholder_names = self.template.placeholder_manager.get_all_names()
        if not placeholder_names:
            messagebox.showwarning("No Placeholders", "Please add placeholders to the PDF first.")
            return
        
        dialog = CSVMappingDialog(
            self.root,
            self.csv_handler.headers,
            placeholder_names
        )
        result = dialog.show()
        
        if result is not None:
            self.csv_handler.set_mapping(result)
            self._update_mapping_label()
            if result:
                self._set_status(f"Mapped {len(result)} columns to placeholders")
            else:
                self._set_status("No columns mapped")
    
    # PDF Generation
    def _preview_pdf(self) -> None:
        """Generate a preview PDF with placeholder names."""
        if not self.template.pdf_path:
            messagebox.showwarning("No PDF", "Please open a PDF first.")
            return
        
        if not self.template.placeholder_manager.placeholders:
            messagebox.showwarning("No Placeholders", "Please add placeholders first.")
            return
        
        # Ask where to save preview
        output_path = filedialog.asksaveasfilename(
            title="Save Preview PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="preview.pdf"
        )
        
        if not output_path:
            return
        
        try:
            generator = PDFGenerator(
                self.template.pdf_path,
                self.template.placeholder_manager,
                self.csv_handler
            )
            generator.generate_preview(output_path)
            self._set_status(f"Preview saved: {os.path.basename(output_path)}")
            
            # Ask if user wants to open it
            if messagebox.askyesno("Preview Created", "Open the preview PDF?"):
                import subprocess
                subprocess.Popen(["xdg-open", output_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create preview: {e}")
    
    def _generate_pdfs(self) -> None:
        """Generate PDFs for CSV rows."""
        # Validate
        if not self.template.pdf_path:
            messagebox.showwarning("No PDF", "Please open a PDF first.")
            return
        
        if not self.template.placeholder_manager.placeholders:
            messagebox.showwarning("No Placeholders", "Please add placeholders first.")
            return
        
        if not self.csv_handler.rows:
            messagebox.showwarning("No CSV Data", "Please import a CSV file first.")
            return
        
        # Check if mapping has been configured
        if self.csv_handler.mapping is None or (not self.csv_handler.mapping and self.csv_handler.file_path):
            self._auto_map_columns()
        
        # Get row range
        try:
            start_row = int(self.start_row_var.get()) - 1  # Convert to 0-indexed
            start_row = max(0, start_row)
        except ValueError:
            start_row = 0
        
        end_row_str = self.end_row_var.get().strip()
        if end_row_str:
            try:
                end_row = int(end_row_str)  # Keep as 1-indexed for user, convert in generator
            except ValueError:
                end_row = None
        else:
            end_row = None
        
        # Get output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return
        
        # Get filename pattern
        pattern = self.pattern_entry.get().strip()
        if not pattern:
            pattern = "output_{index}.pdf"
        
        # Calculate how many PDFs
        total_rows = self.csv_handler.get_row_count()
        actual_end = total_rows if end_row is None else min(end_row, total_rows)
        count = actual_end - start_row
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Generating PDFs")
        progress_window.geometry("400x150")
        progress_window.configure(bg="#2b2b2b")
        progress_window.transient(self.root)
        progress_window.update_idletasks()
        progress_window.grab_set()
        
        tk.Label(
            progress_window, text="Generating PDFs...",
            bg="#2b2b2b", fg="white", font=("Arial", 11)
        ).pack(pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_window, variable=progress_var,
            maximum=count
        )
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        progress_label = tk.Label(
            progress_window, text="0 / 0",
            bg="#2b2b2b", fg="#888888"
        )
        progress_label.pack()
        
        def update_progress(current: int, total: int):
            progress_var.set(current)
            progress_label.config(text=f"{current} / {total}")
            progress_window.update()
        
        try:
            generator = PDFGenerator(
                self.template.pdf_path,
                self.template.placeholder_manager,
                self.csv_handler
            )
            
            generated = generator.generate_batch(
                output_dir,
                pattern,
                progress_callback=update_progress,
                start_row=start_row,
                end_row=end_row
            )
            
            progress_window.destroy()
            
            messagebox.showinfo(
                "Complete",
                f"Successfully generated {len(generated)} PDFs in:\n{output_dir}"
            )
            self._set_status(f"Generated {len(generated)} PDFs")
            
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"Failed to generate PDFs: {e}")
    
    def _auto_map_columns(self) -> None:
        """Auto-map columns by matching names."""
        mapping = {}
        placeholder_names = self.template.placeholder_manager.get_all_names()
        
        for placeholder in placeholder_names:
            for header in self.csv_handler.headers:
                if header.lower().replace(" ", "_") == placeholder.lower():
                    mapping[placeholder] = header
                    break
                elif header.lower() == placeholder.lower():
                    mapping[placeholder] = header
                    break
        
        if mapping:
            self.csv_handler.set_mapping(mapping)
            self._update_mapping_label()
    
    # Help dialogs
    def _show_help(self) -> None:
        """Show help dialog."""
        help_text = """PDF Template Generator - How to Use

1. OPEN PDF
   Click File → Open PDF to load your base PDF document.

2. ADD PLACEHOLDERS
   Click anywhere on the PDF to add a placeholder.
   The inline editor will appear for live editing.

3. EDIT PLACEHOLDERS
   - Click a placeholder on PDF or in list to edit
   - Changes apply live as you type
   - Use position arrows for precise placement
   - Drag placeholders directly on the PDF

4. SAVE TEMPLATE
   Save your template (File → Save Template) to reuse later.

5. IMPORT CSV & MAP
   Import CSV, then map columns to placeholders.

6. GENERATE PDFs
   Click 'Generate All PDFs' - one per CSV row.

TIPS:
- Use {index} in filename for row numbers
- Use {first_name} etc. for data-based names
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("How to Use")
        help_window.geometry("450x450")
        help_window.configure(bg="#2b2b2b")
        
        text = tk.Text(
            help_window, bg="#2b2b2b", fg="white",
            font=("Arial", 10), wrap=tk.WORD, padx=15, pady=15
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.insert("1.0", help_text)
        text.config(state=tk.DISABLED)
    
    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "PDF Template Generator\n\n"
            "Create PDF templates with placeholders and\n"
            "generate personalized PDFs from CSV data.\n\n"
            "Built with Python, Tkinter, and PyMuPDF"
        )
    
    def _on_close(self) -> None:
        """Handle window close."""
        self.pdf_viewer.close()
        self.root.destroy()
