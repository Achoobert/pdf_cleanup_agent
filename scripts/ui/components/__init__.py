"""
UI Components Module

This module contains all UI components including panels, widgets, and the main window.
"""

from .base_component import BaseComponent
from .main_window import MainWindow
from .pdf_drop_widget import PDFDropWidget

__all__ = [
    'BaseComponent',
    'MainWindow',
    'PDFDropWidget',
]