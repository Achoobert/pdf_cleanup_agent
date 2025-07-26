"""
Left Panel Component

Contains the PDF list and console logs display.
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                             QSplitter, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from .base_component import BaseComponent
from .pdf_drop_widget import PDFDropWidget
from ..styles.app_styles import get_app_styles


class LeftPanel(BaseComponent):
    """
    Left panel containing PDF list and console logs.
    
    This panel provides the main interface for PDF file management
    and displays console output from processing operations.
    """
    
    # Signals for left panel events
    pdf_selected = pyqtSignal(str)  # PDF file path
    pdf_dropped = pyqtSignal(str)   # PDF file path
    pdf_preprocess_requested = pyqtSignal(str)  # PDF file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_drop_widget = None
        self.console_output = None
        self.splitter = None
        
    def _setup_ui(self):
        """Setup the left panel UI layout."""
        # Main vertical layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create splitter for PDF list and console
        self.splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.splitter)
        
        # Setup PDF list section
        self._setup_pdf_section()
        
        # Setup console section
        self._setup_console_section()
        
        # Set splitter proportions (60% PDF list, 40% console)
        self.splitter.setSizes([360, 240])
        
    def _setup_pdf_section(self):
        """Setup the PDF list section."""
        # Create frame for PDF section
        pdf_frame = QFrame()
        pdf_frame.setFrameStyle(QFrame.StyledPanel)
        
        # Layout for PDF section
        pdf_layout = QVBoxLayout()
        pdf_frame.setLayout(pdf_layout)
        
        # PDF section header
        pdf_header = QLabel("PDF Files v1.0")
        styles = get_app_styles()
        pdf_header.setStyleSheet(styles.HEADER_LABEL)
        pdf_layout.addWidget(pdf_header)
        
        # PDF drop widget
        self.pdf_drop_widget = PDFDropWidget()
        self.pdf_drop_widget.logger = self.logger
        pdf_layout.addWidget(self.pdf_drop_widget)
        
        # Add to splitter
        self.splitter.addWidget(pdf_frame)
        
    def _setup_console_section(self):
        """Setup the console output section."""
        # Create frame for console section
        console_frame = QFrame()
        console_frame.setFrameStyle(QFrame.StyledPanel)
        
        # Layout for console section
        console_layout = QVBoxLayout()
        console_frame.setLayout(console_layout)
        
        # Console section header
        console_header = QLabel("Console")
        styles = get_app_styles()
        console_header.setStyleSheet(styles.HEADER_LABEL)
        console_layout.addWidget(console_header)
        
        # Console output text area
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 10))
        self.console_output.setStyleSheet(styles.CONSOLE_STYLE)
        self.console_output.setPlaceholderText("Console output will appear here...")
        console_layout.addWidget(self.console_output)
        
        # Add to splitter
        self.splitter.addWidget(console_frame)
        
    def _setup_connections(self):
        """Setup signal/slot connections for the left panel."""
        if self.pdf_drop_widget:
            # Connect PDF drop widget signals
            self.pdf_drop_widget.pdf_dropped.connect(self.pdf_dropped.emit)
            self.pdf_drop_widget.pdf_preprocess_requested.connect(self.pdf_preprocess_requested.emit)
            self.pdf_drop_widget.itemSelectionChanged.connect(self._on_pdf_selection_changed)
            
    def _on_pdf_selection_changed(self):
        """Handle PDF selection changes."""
        selected_pdf = self.pdf_drop_widget.get_selected_pdf()
        if selected_pdf:
            self.pdf_selected.emit(selected_pdf)
            self._emit_status(f"Selected PDF: {selected_pdf}")
            
    def append_console_output(self, text: str):
        """
        Append text to the console output.
        
        Args:
            text: Text to append to console
        """
        if self.console_output:
            self.console_output.append(text)
            # Auto-scroll to bottom
            cursor = self.console_output.textCursor()
            cursor.movePosition(cursor.End)
            self.console_output.setTextCursor(cursor)
            
    def clear_console_output(self):
        """Clear the console output."""
        if self.console_output:
            self.console_output.clear()
            self._emit_status("Console output cleared")
            
    def refresh_pdf_list(self):
        """Refresh the PDF file list."""
        if self.pdf_drop_widget:
            self.pdf_drop_widget.refresh_pdf_list()
            self._emit_status("PDF list refreshed")
            
    def get_selected_pdf(self) -> str:
        """
        Get the currently selected PDF file path.
        
        Returns:
            Path to selected PDF file, or empty string if none selected
        """
        if self.pdf_drop_widget:
            return self.pdf_drop_widget.get_selected_pdf()
        return ""
        
    def add_pdf_programmatically(self, pdf_path: str) -> bool:
        """
        Add a PDF file programmatically.
        
        Args:
            pdf_path: Path to PDF file to add
            
        Returns:
            True if successful, False otherwise
        """
        if self.pdf_drop_widget:
            return self.pdf_drop_widget.add_pdf_programmatically(pdf_path)
        return False
        
    def set_console_font_size(self, size: int):
        """
        Set the console output font size.
        
        Args:
            size: Font size in points
        """
        if self.console_output:
            font = self.console_output.font()
            font.setPointSize(size)
            self.console_output.setFont(font)
            
    def get_splitter_sizes(self) -> list:
        """Get the current splitter sizes."""
        if self.splitter:
            return self.splitter.sizes()
        return []
        
    def set_splitter_sizes(self, sizes: list):
        """
        Set the splitter sizes.
        
        Args:
            sizes: List of sizes for splitter sections
        """
        if self.splitter and len(sizes) >= 2:
            self.splitter.setSizes(sizes)