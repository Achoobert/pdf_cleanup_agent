"""
Base Dialog Class

Provides common functionality for all dialog components.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal
from abc import ABC, abstractmethod
import logging


class BaseDialog(QDialog):
    """
    Base class for all dialog components.
    
    This class provides common functionality like error handling,
    logging, and standard dialog behavior.
    """
    
    # Common signals that all dialogs can emit
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    status_changed = pyqtSignal(str)       # status_message
    
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle(title)
        self._is_initialized = False
        
    def initialize(self):
        """
        Initialize the dialog. Should be called after construction.
        """
        if self._is_initialized:
            return
            
        try:
            self._setup_ui()
            self._setup_connections()
            self._setup_buttons()
            self._is_initialized = True
            self.status_changed.emit(f"{self.__class__.__name__} initialized")
        except Exception as e:
            self._handle_error("initialization", str(e))
            
    def _setup_ui(self):
        """
        Setup the dialog UI layout and widgets. Subclasses should implement this.
        """
        pass
        
    def _setup_connections(self):
        """
        Setup signal/slot connections. Subclasses can override this.
        """
        pass
        
    def _setup_buttons(self):
        """
        Setup standard dialog buttons. Subclasses can override this.
        """
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        
        # Add button box to main layout if it exists
        if hasattr(self, 'main_layout'):
            self.main_layout.addWidget(self.button_box)
            
    def _on_accept(self):
        """
        Handle the accept action. Subclasses can override this.
        """
        if self._validate_input():
            self.accept()
            
    def _validate_input(self) -> bool:
        """
        Validate dialog input before accepting. Subclasses can override this.
        
        Returns:
            True if input is valid, False otherwise
        """
        return True
        
    def _handle_error(self, error_type: str, error_message: str):
        """
        Handle errors in a consistent way across all dialogs.
        
        Args:
            error_type: Type of error (e.g., 'validation_error', 'ui_error')
            error_message: Detailed error message
        """
        self.logger.error(f"{error_type}: {error_message}")
        self.error_occurred.emit(error_type, error_message)
        
    def _emit_status(self, message: str):
        """
        Emit a status update message.
        
        Args:
            message: Status message to emit
        """
        self.logger.info(message)
        self.status_changed.emit(message)
        
    @property
    def is_initialized(self) -> bool:
        """Check if the dialog has been initialized."""
        return self._is_initialized
        
    def cleanup(self):
        """
        Cleanup method called when the dialog is being destroyed.
        Subclasses should override this for custom cleanup.
        """
        self.logger.info(f"{self.__class__.__name__} cleanup completed")