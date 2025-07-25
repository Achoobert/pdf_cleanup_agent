"""
PDF Handler

Manages PDF file operations and processing pipeline.
"""

from PyQt5.QtCore import pyqtSignal
import os
import shutil
from typing import Optional

from .base_handler import BaseHandler
from .process_handler import ProcessManager


class PDFHandler(BaseHandler):
    """
    Handles PDF file operations and processing pipeline.
    
    This class manages PDF file copying, validation, and processing
    through the application pipeline.
    """
    
    # Signals for PDF events
    pdf_copied = pyqtSignal(str)  # pdf_path
    pdf_processing_started = pyqtSignal(str)  # pdf_path
    pdf_processing_finished = pyqtSignal(str, bool)  # pdf_path, success
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process_manager: Optional[ProcessManager] = None
        
    def _setup(self):
        """Setup the PDF handler."""
        self.process_manager = ProcessManager(self)
        self.process_manager.initialize()
        
        # Connect process manager signals
        self.process_manager.process_finished.connect(self._on_process_finished)
        self.process_manager.error_occurred.connect(self._on_process_error)
        
    def handle_pdf_drop(self, pdf_path: str) -> bool:
        """
        Handle a dropped PDF file.
        
        Args:
            pdf_path: Path to the dropped PDF file
            
        Returns:
            True if handling was successful, False otherwise
        """
        if not self._validate_pdf_file(pdf_path):
            return False
            
        # Copy PDF to data directory
        dest_path = self._copy_pdf_to_data_dir(pdf_path)
        if not dest_path:
            return False
            
        self.pdf_copied.emit(dest_path)
        
        # Start processing pipeline
        return self._start_processing_pipeline(dest_path)
        
    def _validate_pdf_file(self, pdf_path: str) -> bool:
        """
        Validate that the file is a valid PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.isfile(pdf_path):
            self._handle_error("file_error", f"File does not exist: {pdf_path}")
            return False
            
        if not pdf_path.lower().endswith('.pdf'):
            self._handle_error("file_error", f"Not a PDF file: {pdf_path}")
            return False
            
        # Additional validation could be added here (file size, PDF header check, etc.)
        return True
        
    def _copy_pdf_to_data_dir(self, pdf_path: str) -> Optional[str]:
        """
        Copy PDF file to the data/pdf directory.
        
        Args:
            pdf_path: Source PDF file path
            
        Returns:
            Destination path if successful, None otherwise
        """
        try:
            pdf_dir = self._get_pdf_directory()
            os.makedirs(pdf_dir, exist_ok=True)
            
            filename = os.path.basename(pdf_path)
            dest_path = os.path.join(pdf_dir, filename)
            
            # Handle duplicate filenames
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                new_filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(pdf_dir, new_filename)
                counter += 1
                
            shutil.copy2(pdf_path, dest_path)
            self._emit_status(f"PDF copied: {os.path.basename(dest_path)}")
            return dest_path
            
        except Exception as e:
            self._handle_error("file_error", f"Failed to copy PDF: {e}")
            return None
            
    def _start_processing_pipeline(self, pdf_path: str) -> bool:
        """
        Start the PDF processing pipeline.
        
        Args:
            pdf_path: Path to the PDF file to process
            
        Returns:
            True if pipeline started successfully, False otherwise
        """
        if not self.process_manager:
            self._handle_error("process_error", "Process manager not initialized")
            return False
            
        try:
            pipeline_script = self._get_pipeline_script_path()
            python_exe = self.process_manager.get_python_executable()
            
            process_id = f"pdf_pipeline_{os.path.basename(pdf_path)}"
            
            success = self.process_manager.start_process(
                process_id=process_id,
                command=python_exe,
                args=[pipeline_script, pdf_path]
            )
            
            if success:
                self.pdf_processing_started.emit(pdf_path)
                self._emit_status(f"Started processing: {os.path.basename(pdf_path)}")
                
            return success
            
        except Exception as e:
            self._handle_error("process_error", f"Failed to start pipeline: {e}")
            return False
            
    def _get_pdf_directory(self) -> str:
        """Get the PDF data directory path."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data', 'pdf'
        ))
        
    def _get_pipeline_script_path(self) -> str:
        """Get the path to the PDF processing pipeline script."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'pdf_process_pipeline.py'
        ))
        
    def _on_process_finished(self, process_id: str, exit_code: int):
        """Handle process completion."""
        if process_id.startswith("pdf_pipeline_"):
            pdf_name = process_id.replace("pdf_pipeline_", "")
            success = exit_code == 0
            
            # Reconstruct full path for signal
            pdf_path = os.path.join(self._get_pdf_directory(), pdf_name)
            self.pdf_processing_finished.emit(pdf_path, success)
            
            if success:
                self._emit_status(f"Processing completed: {pdf_name}")
            else:
                self._emit_status(f"Processing failed: {pdf_name}")
                
    def _on_process_error(self, error_type: str, error_message: str):
        """Handle process errors."""
        self._handle_error(error_type, error_message)
        
    def cleanup(self):
        """Cleanup PDF handler resources."""
        if self.process_manager:
            self.process_manager.cleanup()
        super().cleanup()