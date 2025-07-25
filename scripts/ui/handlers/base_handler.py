"""
Base Handler Class

Provides common functionality for all handler classes.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from abc import ABC, abstractmethod
import logging


class BaseHandler(QObject):
    """
    Base class for all handler classes that manage business logic.
    
    This class provides common functionality like error handling,
    logging, and signal management for all handlers.
    """
    
    # Common signals that all handlers can emit
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    status_changed = pyqtSignal(str)       # status_message
    progress_updated = pyqtSignal(int)     # progress_percentage
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_initialized = False
        
    def initialize(self):
        """
        Initialize the handler. Should be called after construction.
        Subclasses should override this method for custom initialization.
        """
        if self._is_initialized:
            return
            
        try:
            self._setup()
            self._is_initialized = True
            self.status_changed.emit(f"{self.__class__.__name__} initialized")
        except Exception as e:
            self._handle_error("initialization", str(e))
            
    def _setup(self):
        """
        Setup method that subclasses should implement.
        This is called during initialization.
        """
        pass
        
    def _handle_error(self, error_type: str, error_message: str):
        """
        Handle errors in a consistent way across all handlers.
        
        Args:
            error_type: Type of error (e.g., 'file_operation', 'process_error')
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
        
    def _emit_progress(self, percentage: int):
        """
        Emit a progress update.
        
        Args:
            percentage: Progress percentage (0-100)
        """
        if 0 <= percentage <= 100:
            self.progress_updated.emit(percentage)
        else:
            self.logger.warning(f"Invalid progress percentage: {percentage}")
            
    @property
    def is_initialized(self) -> bool:
        """Check if the handler has been initialized."""
        return self._is_initialized
        
    def cleanup(self):
        """
        Cleanup method called when the handler is being destroyed.
        Subclasses should override this for custom cleanup.
        """
        self.logger.info(f"{self.__class__.__name__} cleanup completed")