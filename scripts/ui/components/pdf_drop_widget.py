"""
PDF Drop Widget Component

Enhanced drag and drop widget for PDF files with proper visual feedback
and file validation.
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt, QMimeDatabase
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
import os
import shutil

from .base_component import BaseComponent


class PDFDropWidget(QListWidget):
    """
    Enhanced PDF drag and drop widget with visual feedback and validation.
    
    This widget provides a drop zone for PDF files with proper visual feedback
    during drag operations and file validation. Only performs pre-processing
    (convert to text) without triggering the full processing pipeline.
    """
    
    # Signals for PDF drop events
    pdf_dropped = pyqtSignal(str)  # PDF file path
    pdf_drop_rejected = pyqtSignal(str, str)  # file_path, reason
    pdf_preprocess_requested = pyqtSignal(str)  # PDF file path for pre-processing only
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_active = False
        self._mime_db = QMimeDatabase()
        self.logger = None  # Will be set by parent if needed
        self.initialize()
        
    def initialize(self):
        """Initialize the widget."""
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI layout and drag/drop configuration."""
        self._setup_drag_drop()
        self._setup_styling()
        self.refresh_pdf_list()
        
    def _setup_drag_drop(self):
        """Configure drag and drop settings."""
        # Set drag drop mode first, then accept drops
        self.setDragDropMode(QListWidget.NoDragDrop)
        self.setAcceptDrops(True)
        
    def _setup_styling(self):
        """Setup basic styling for the widget."""
        self.setStyleSheet("""
            QListWidget {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #fafafa;
                font-family: Arial, sans-serif;
                font-size: 12px;
                padding: 10px;
            }
            QListWidget:hover {
                border-color: #999999;
            }
            QListWidget[dragActive="true"] {
                border-color: #0078d4;
                background-color: #f0f8ff;
            }
        """)
        
    def refresh_pdf_list(self):
        """Refresh the list of PDF files from the data/pdf directory."""
        self.clear()
        pdf_dir = self._get_pdf_directory()
        
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)
            return
            
        try:
            for fname in os.listdir(pdf_dir):
                if fname.lower().endswith('.pdf'):
                    self.addItem(QListWidgetItem(fname))
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error refreshing PDF list: {e}")
                
    def _get_pdf_directory(self) -> str:
        """Get the PDF directory path."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data', 'pdf'
        ))
        
    def dragEnterEvent(self, event):
        """Handle drag enter events with proper MIME type validation."""
        try:
            if not event:
                return
            if not event.mimeData():
                event.ignore()
                return
                
            mime = event.mimeData()
            if not mime.hasUrls():
                event.ignore()
                return
                
            # Check if any of the dragged files are PDFs using MIME type
            valid_pdf_found = False
            for url in mime.urls():
                file_path = url.toLocalFile()
                if self._is_valid_pdf_file(file_path):
                    valid_pdf_found = True
                    break
                    
            if valid_pdf_found:
                self._drag_active = True
                self.setProperty("dragActive", True)
                self.style().polish(self)  # Refresh styling
                self.update()  # Trigger repaint for visual feedback
                event.acceptProposedAction()
                self._emit_status("PDF file detected - ready to drop")
            else:
                event.ignore()
                
        except Exception as e:
            self._handle_error("drag_enter", f"Error handling drag enter: {e}")
            event.ignore()
            
    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if self._drag_active:
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """Handle drag leave events."""
        self._drag_active = False
        self.setProperty("dragActive", False)
        self.style().polish(self)  # Refresh styling
        self.update()  # Remove visual feedback
        self._emit_status("Drag operation cancelled")
        
    def dropEvent(self, event):
        """Handle drop events with comprehensive file validation and copying."""
        self._drag_active = False
        self.setProperty("dragActive", False)
        self.style().polish(self)  # Refresh styling
        self.update()  # Remove visual feedback
        
        try:
            if not event:
                return
            if not event.mimeData():
                event.ignore()
                return
                
            mime = event.mimeData()
            if not mime.hasUrls():
                event.ignore()
                return
                
            processed_files = []
            
            # Process each dropped file
            for url in mime.urls():
                file_path = url.toLocalFile()
                
                # Validate PDF file
                validation_result = self._validate_pdf_file(file_path)
                if not validation_result['valid']:
                    self.pdf_drop_rejected.emit(file_path, validation_result['reason'])
                    continue
                
                # Copy PDF to data directory and request pre-processing
                try:
                    copied_path = self._copy_pdf_to_data_dir(file_path)
                    if copied_path:
                        processed_files.append(copied_path)
                        self.pdf_dropped.emit(copied_path)
                        # Request pre-processing only (convert to text)
                        self.pdf_preprocess_requested.emit(copied_path)
                        
                except Exception as e:
                    self._handle_error("file_copy", f"Failed to copy {file_path}: {e}")
                    self.pdf_drop_rejected.emit(file_path, f"Copy failed: {e}")
                    
            if processed_files:
                self._emit_status(f"Successfully processed {len(processed_files)} PDF file(s)")
                self.refresh_pdf_list()
            
            event.acceptProposedAction()
            
        except Exception as e:
            self._handle_error("drop_event", f"Error handling drop event: {e}")
            event.ignore()
        
    def paintEvent(self, event):
        """Custom paint event to provide visual feedback during drag operations."""
        super().paintEvent(event)
        
        if self._drag_active:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw highlight overlay
            pen = QPen(QColor(0, 120, 215), 3)  # Blue highlight
            brush = QBrush(QColor(0, 120, 215, 30))  # Semi-transparent blue
            
            painter.setPen(pen)
            painter.setBrush(brush)
            
            rect = self.viewport().rect()
            rect.adjust(2, 2, -2, -2)  # Small margin
            painter.drawRoundedRect(rect, 5, 5)
            
            painter.end()
            
    def _is_valid_pdf_file(self, file_path: str) -> bool:
        """Check if file is a valid PDF using MIME type detection."""
        if not file_path or not os.path.isfile(file_path):
            return False
            
        try:
            # Check file extension first (quick check)
            if not file_path.lower().endswith('.pdf'):
                return False
                
            # Check MIME type for more robust validation
            mime_type = self._mime_db.mimeTypeForFile(file_path)
            return mime_type.name() == 'application/pdf'
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error checking PDF file {file_path}: {e}")
            return False
            
    def _validate_pdf_file(self, file_path: str) -> dict:
        """Comprehensive PDF file validation."""
        if not file_path:
            return {'valid': False, 'reason': 'Empty file path'}
            
        if not os.path.exists(file_path):
            return {'valid': False, 'reason': 'File does not exist'}
            
        if not os.path.isfile(file_path):
            return {'valid': False, 'reason': 'Path is not a file'}
            
        # Check file size (avoid empty files or extremely large files)
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {'valid': False, 'reason': 'File is empty'}
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                return {'valid': False, 'reason': 'File too large (>100MB)'}
        except Exception as e:
            return {'valid': False, 'reason': f'Cannot read file size: {e}'}
            
        # Check if it's a valid PDF
        if not self._is_valid_pdf_file(file_path):
            return {'valid': False, 'reason': 'Not a valid PDF file'}
            
        return {'valid': True, 'reason': 'Valid PDF file'}
        
    def _copy_pdf_to_data_dir(self, source_path: str) -> str:
        """Copy PDF file to the data/pdf directory."""
        if not source_path or not os.path.isfile(source_path):
            raise ValueError("Invalid source file path")
            
        pdf_dir = self._get_pdf_directory()
        os.makedirs(pdf_dir, exist_ok=True)
        
        filename = os.path.basename(source_path)
        dest_path = os.path.join(pdf_dir, filename)
        
        # Handle duplicate filenames
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(dest_path):
            new_filename = f"{base_name}_{counter}{ext}"
            dest_path = os.path.join(pdf_dir, new_filename)
            counter += 1
            
        try:
            shutil.copy2(source_path, dest_path)
            if self.logger:
                self.logger.info(f"PDF copied to: {dest_path}")
            return dest_path
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to copy PDF: {e}")
            raise
            
    def _emit_status(self, message: str):
        """Emit status message if logger is available."""
        if self.logger:
            self.logger.info(f"PDFDropWidget: {message}")
            
    def _handle_error(self, operation: str, error_message: str):
        """Handle errors with proper logging."""
        if self.logger:
            self.logger.error(f"PDFDropWidget [{operation}]: {error_message}")
            
    def get_selected_pdf(self) -> str:
        """Get the currently selected PDF file path."""
        current_item = self.currentItem()
        if current_item:
            filename = current_item.text()
            return os.path.join(self._get_pdf_directory(), filename)
        return ""
        
    def add_pdf_programmatically(self, pdf_path: str) -> bool:
        """Add a PDF file programmatically (for testing purposes)."""
        try:
            validation_result = self._validate_pdf_file(pdf_path)
            if not validation_result['valid']:
                self.pdf_drop_rejected.emit(pdf_path, validation_result['reason'])
                return False
                
            copied_path = self._copy_pdf_to_data_dir(pdf_path)
            if copied_path:
                self.pdf_dropped.emit(copied_path)
                self.pdf_preprocess_requested.emit(copied_path)
                self.refresh_pdf_list()
                return True
                
        except Exception as e:
            self._handle_error("programmatic_add", f"Failed to add PDF {pdf_path}: {e}")
            self.pdf_drop_rejected.emit(pdf_path, f"Add failed: {e}")
            
        return False