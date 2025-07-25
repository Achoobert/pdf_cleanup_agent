"""
Main Window Component

The primary UI controller that manages the overall application layout and coordinates
between different panels and handlers.
"""

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
import os
import sys

from .base_component import BaseComponent


class MainWindow(BaseComponent):
    """
    Main application window that coordinates all UI components.
    
    This class manages the overall layout and serves as the central
    coordinator for all UI components and handlers.
    """
    
    # Signals for main window events
    window_closing = pyqtSignal()
    pdf_dropped = pyqtSignal(str)  # PDF file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('PDF Power Converter')
        self._setup_window_properties()
        
    def _setup_window_properties(self):
        """Setup basic window properties like size and icon."""
        self.resize(900, 600)
        
        # Set window icon if it exists
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
    def _setup_ui(self):
        """
        Setup the main window UI layout.
        Creates the horizontal split layout with left and right panels.
        """
        # Main horizontal layout
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        
        # Initialize panels (will be implemented in future tasks)
        self._setup_left_panel()
        self._setup_right_panel()
        
    def _setup_left_panel(self):
        """
        Setup the left panel containing PDF list and console logs.
        This is a placeholder that will be implemented in future tasks.
        """
        # Placeholder for left panel
        # Will be implemented when LeftPanel component is created
        pass
        
    def _setup_right_panel(self):
        """
        Setup the right panel containing control buttons.
        This is a placeholder that will be implemented in future tasks.
        """
        # Placeholder for right panel  
        # Will be implemented when RightPanel component is created
        pass
        
    def _setup_connections(self):
        """Setup signal/slot connections for the main window."""
        # Connections will be established when handlers are integrated
        pass
        
    def handle_pdf_drop(self, pdf_path: str):
        """
        Handle PDF file drop events.
        
        Args:
            pdf_path: Path to the dropped PDF file
        """
        self._emit_status(f"PDF dropped: {os.path.basename(pdf_path)}")
        self.pdf_dropped.emit(pdf_path)
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.window_closing.emit()
        self.cleanup()
        event.accept()
        
    def show_error_message(self, error_type: str, error_message: str):
        """
        Display error messages to the user.
        
        Args:
            error_type: Type of error
            error_message: Error message to display
        """
        # This will be implemented when error handling is added
        self._handle_error(error_type, error_message)