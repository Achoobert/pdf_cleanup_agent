"""
UI Helper Utilities

Common utility functions for UI operations.
"""

from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import os
from typing import Optional, Callable


class UIHelpers:
    """
    Collection of utility functions for common UI operations.
    """
    
    @staticmethod
    def show_info_message(parent: QWidget, title: str, message: str):
        """
        Show an information message box.
        
        Args:
            parent: Parent widget
            title: Message box title
            message: Message to display
        """
        QMessageBox.information(parent, title, message)
        
    @staticmethod
    def show_error_message(parent: QWidget, title: str, message: str):
        """
        Show an error message box.
        
        Args:
            parent: Parent widget
            title: Message box title
            message: Error message to display
        """
        QMessageBox.critical(parent, title, message)
        
    @staticmethod
    def show_warning_message(parent: QWidget, title: str, message: str):
        """
        Show a warning message box.
        
        Args:
            parent: Parent widget
            title: Message box title
            message: Warning message to display
        """
        QMessageBox.warning(parent, title, message)
        
    @staticmethod
    def show_question(parent: QWidget, title: str, message: str) -> bool:
        """
        Show a yes/no question dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Question to ask
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
        
    @staticmethod
    def open_file_in_system(file_path: str) -> bool:
        """
        Open a file using the system's default application.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            True if file was opened successfully
        """
        try:
            if os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                return True
            return False
        except Exception:
            return False
            
    @staticmethod
    def open_directory_in_system(directory_path: str) -> bool:
        """
        Open a directory using the system's default file manager.
        
        Args:
            directory_path: Path to the directory to open
            
        Returns:
            True if directory was opened successfully
        """
        try:
            if os.path.exists(directory_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(directory_path))
                return True
            return False
        except Exception:
            return False
            
    @staticmethod
    def create_timer(parent: QWidget, interval_ms: int, callback: Callable) -> QTimer:
        """
        Create and configure a QTimer.
        
        Args:
            parent: Parent widget
            interval_ms: Timer interval in milliseconds
            callback: Function to call when timer fires
            
        Returns:
            Configured QTimer instance
        """
        timer = QTimer(parent)
        timer.timeout.connect(callback)
        timer.setInterval(interval_ms)
        return timer
        
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
            
        return f"{size:.1f} {size_names[i]}"
        
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to a maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncating
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
        
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Get the file extension from a file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File extension (including dot) or empty string
        """
        return os.path.splitext(file_path)[1].lower()
        
    @staticmethod
    def is_pdf_file(file_path: str) -> bool:
        """
        Check if a file is a PDF based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file has .pdf extension
        """
        return UIHelpers.get_file_extension(file_path) == '.pdf'
        
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Convert a string to a safe filename by removing/replacing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Characters that are not allowed in filenames
        invalid_chars = '<>:"/\\|?*'
        
        safe_name = filename
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
            
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')
        
        # Ensure filename is not empty
        if not safe_name:
            safe_name = "untitled"
            
        return safe_name