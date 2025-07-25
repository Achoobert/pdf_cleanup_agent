"""
File Handler

Manages file operations and directory management.
"""

import os
import shutil
from typing import List, Optional
from PyQt5.QtCore import pyqtSignal

from .base_handler import BaseHandler


class FileHandler(BaseHandler):
    """
    Handles file operations and directory management.
    
    This class provides utilities for file operations, directory management,
    and path resolution throughout the application.
    """
    
    # Signals for file events
    file_copied = pyqtSignal(str, str)  # source_path, dest_path
    file_deleted = pyqtSignal(str)  # file_path
    directory_created = pyqtSignal(str)  # directory_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_data_dir = self._get_base_data_directory()
        
    def _setup(self):
        """Setup the file handler."""
        # Ensure base data directories exist
        self._ensure_data_directories()
        
    def _get_base_data_directory(self) -> str:
        """Get the base data directory path."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data'
        ))
        
    def _ensure_data_directories(self):
        """Ensure all required data directories exist."""
        directories = [
            'pdf',
            'markdown', 
            'json',
            'output',
            'temp'
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.base_data_dir, directory)
            self.ensure_directory_exists(dir_path)
            
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                self.directory_created.emit(directory_path)
                self._emit_status(f"Created directory: {directory_path}")
            return True
        except Exception as e:
            self._handle_error("file_error", f"Failed to create directory {directory_path}: {e}")
            return False
            
    def copy_file(self, source_path: str, dest_path: str, overwrite: bool = False) -> bool:
        """
        Copy a file from source to destination.
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if copy was successful
        """
        try:
            if not os.path.isfile(source_path):
                self._handle_error("file_error", f"Source file does not exist: {source_path}")
                return False
                
            if os.path.exists(dest_path) and not overwrite:
                self._handle_error("file_error", f"Destination file exists: {dest_path}")
                return False
                
            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest_path)
            if not self.ensure_directory_exists(dest_dir):
                return False
                
            shutil.copy2(source_path, dest_path)
            self.file_copied.emit(source_path, dest_path)
            self._emit_status(f"File copied: {os.path.basename(dest_path)}")
            return True
            
        except Exception as e:
            self._handle_error("file_error", f"Failed to copy file: {e}")
            return False
            
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            if not os.path.isfile(file_path):
                self._handle_error("file_error", f"File does not exist: {file_path}")
                return False
                
            os.remove(file_path)
            self.file_deleted.emit(file_path)
            self._emit_status(f"File deleted: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            self._handle_error("file_error", f"Failed to delete file: {e}")
            return False
            
    def list_files_in_directory(self, directory_path: str, extension: str = None) -> List[str]:
        """
        List files in a directory, optionally filtered by extension.
        
        Args:
            directory_path: Directory to list files from
            extension: File extension to filter by (e.g., '.pdf')
            
        Returns:
            List of file paths
        """
        try:
            if not os.path.isdir(directory_path):
                return []
                
            files = []
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    if extension is None or filename.lower().endswith(extension.lower()):
                        files.append(file_path)
                        
            return sorted(files)
            
        except Exception as e:
            self._handle_error("file_error", f"Failed to list files in {directory_path}: {e}")
            return []
            
    def get_pdf_directory(self) -> str:
        """Get the PDF data directory path."""
        return os.path.join(self.base_data_dir, 'pdf')
        
    def get_markdown_directory(self) -> str:
        """Get the markdown data directory path."""
        return os.path.join(self.base_data_dir, 'markdown')
        
    def get_json_directory(self) -> str:
        """Get the JSON data directory path."""
        return os.path.join(self.base_data_dir, 'json')
        
    def get_output_directory(self) -> str:
        """Get the output data directory path."""
        return os.path.join(self.base_data_dir, 'output')
        
    def get_temp_directory(self) -> str:
        """Get the temporary data directory path."""
        return os.path.join(self.base_data_dir, 'temp')
        
    def find_unique_filename(self, directory: str, base_name: str, extension: str) -> str:
        """
        Find a unique filename in a directory by appending numbers if necessary.
        
        Args:
            directory: Target directory
            base_name: Base filename without extension
            extension: File extension (including dot)
            
        Returns:
            Unique filename
        """
        filename = f"{base_name}{extension}"
        file_path = os.path.join(directory, filename)
        
        counter = 1
        while os.path.exists(file_path):
            filename = f"{base_name}_{counter}{extension}"
            file_path = os.path.join(directory, filename)
            counter += 1
            
        return filename