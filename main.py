"""PDF Template Generator - Main entry point."""

import sys
import tkinter as tk
from src.app import PDFTemplateApp


def main():
    """Initialize and run the application."""
    root = tk.Tk()
    app = PDFTemplateApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
