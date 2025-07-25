"""
Base Component Class

Provides common functionality for all UI components.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from abc import ABC, abstractmethod
import logging


class BaseComponent(QWidget):
    """
    Base class for all UI components.
    
    This class provides common functionality like error handling,
    logging, and signal management for all UI components.
    """
    
    # Common signals that all components can emit
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    status_changed = pyqtSignal(str)       # status_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_initialized = False
        
    def initialize(self):
        """
        Initialize the component. Should be called after construction.
        Subclasses should override this method for custom initialization.
        """
        if self._is_initialized:
            return
            
        try:
            self._setup_ui()
            self._setup_connections()
            self._is_initialized = True
            self.status_changed.emit(f"{self.__class__.__name__} initialized")
        except Exception as e:
            self._handle_error("initialization", str(e))
            
    def _setup_ui(self):
        """
        Setup the UI layout and widgets. Subclasses should implement this.
        """
        pass
        
    def _setup_connections(self):
        """
        Setup signal/slot connections. Subclasses can override this.
        """
        pass
        
    def _handle_error(self, error_type: str, error_message: str):
        """
        Handle errors in a consistent way across all components.
        
        Args:
            error_type: Type of error (e.g., 'ui_error', 'layout_error')
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
        """Check if the component has been initialized."""
        return self._is_initialized
        
    def cleanup(self):
        """
        Cleanup method called when the component is being destroyed.
        Subclasses should override this for custom cleanup.
        """
        self.logger.info(f"{self.__class__.__name__} cleanup completed")