"""
PDF Handler

Manages PDF file operations and processing pipeline.
"""

from PyQt5.QtCore import pyqtSignal
import os
import shutil
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import sys

from .base_handler import BaseHandler
from .process_handler import ProcessManager
from ..utils.status_manager import StatusLevel


@dataclass
class ProcessingState:
    """
    Manages the state of PDF processing operations.
    
    This dataclass tracks the current processing state including
    active PDFs, processing queue, and pipeline status.
    """
    current_pdf: Optional[str] = None
    processing_queue: List[str] = field(default_factory=list)
    active_processes: Dict[str, str] = field(default_factory=dict)  # process_id -> pdf_path
    last_output_path: Optional[str] = None
    processing_history: List[Dict[str, Any]] = field(default_factory=list)
    failed_pdfs: List[str] = field(default_factory=list)
    
    def add_to_queue(self, pdf_path: str):
        """Add a PDF to the processing queue."""
        if pdf_path not in self.processing_queue:
            self.processing_queue.append(pdf_path)
            
    def remove_from_queue(self, pdf_path: str):
        """Remove a PDF from the processing queue."""
        if pdf_path in self.processing_queue:
            self.processing_queue.remove(pdf_path)
            
    def start_processing(self, pdf_path: str, process_id: str):
        """Mark a PDF as currently being processed."""
        self.current_pdf = pdf_path
        self.active_processes[process_id] = pdf_path
        self.remove_from_queue(pdf_path)
        
    def finish_processing(self, process_id: str, success: bool, output_path: Optional[str] = None):
        """Mark processing as finished for a process."""
        if process_id in self.active_processes:
            pdf_path = self.active_processes[process_id]
            del self.active_processes[process_id]
            
            # Update history
            self.processing_history.append({
                'pdf_path': pdf_path,
                'process_id': process_id,
                'success': success,
                'output_path': output_path,
                'timestamp': self._get_timestamp()
            })
            
            if success and output_path:
                self.last_output_path = output_path
            elif not success:
                self.failed_pdfs.append(pdf_path)
                
            # Clear current PDF if this was the active one
            if self.current_pdf == pdf_path:
                self.current_pdf = None
                
    def is_processing(self, pdf_path: str) -> bool:
        """Check if a PDF is currently being processed."""
        return pdf_path in self.active_processes.values()
        
    def get_queue_position(self, pdf_path: str) -> int:
        """Get the position of a PDF in the processing queue."""
        try:
            return self.processing_queue.index(pdf_path)
        except ValueError:
            return -1
            
    def clear_failed(self):
        """Clear the list of failed PDFs."""
        self.failed_pdfs.clear()
        
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()


class PDFHandler(BaseHandler):
    """
    Handles PDF file operations and processing pipeline.
    
    This class manages PDF file copying, validation, and processing
    through the application pipeline. It integrates the functionality
    from pdf_segmenter.py, agent_stream.py, and pdf_process_pipeline.py.
    """
    
    # Signals for PDF events
    pdf_copied = pyqtSignal(str)  # pdf_path
    pdf_processing_started = pyqtSignal(str)  # pdf_path
    pdf_processing_finished = pyqtSignal(str, bool)  # pdf_path, success
    pdf_segmentation_finished = pyqtSignal(str, bool)  # pdf_path, success
    llm_processing_finished = pyqtSignal(str, bool)  # pdf_path, success
    processing_progress = pyqtSignal(str, int, str)  # pdf_path, step, description
    
    # Enhanced progress signals
    progress_started = pyqtSignal(str, str)  # progress_id, title
    progress_updated = pyqtSignal(str, int, str)  # progress_id, current, message
    progress_finished = pyqtSignal(str, bool, str)  # progress_id, success, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process_manager: Optional[ProcessManager] = None
        self.processing_state = ProcessingState()
        self.active_progress_ids: Dict[str, str] = {}  # process_id -> progress_id
        self.status_manager = None  # Will be set by main window  # process_id -> progress_id
        
    def _setup(self):
        """Setup the PDF handler."""
        self.process_manager = ProcessManager(self)
        self.process_manager.initialize()
        
        # Connect process manager signals
        self.process_manager.process_finished.connect(self._on_process_finished)
        self.process_manager.process_output.connect(self._on_process_output)
        self.process_manager.process_error.connect(self._on_process_error)
        self.process_manager.error_occurred.connect(self._on_handler_error)
    
    def set_status_manager(self, status_manager):
        """
        Set the status manager for enhanced progress tracking.
        
        Args:
            status_manager: StatusManager instance
        """
        self.status_manager = status_manager
        
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
        
        # Add to processing queue (but don't start LLM processing automatically)
        self.processing_state.add_to_queue(dest_path)
        
        # Start only PDF-to-text conversion (segmentation)
        return self._start_pdf_segmentation(dest_path)
        
    def start_full_processing(self, pdf_path: str) -> bool:
        """
        Start the full PDF processing pipeline including LLM processing.
        
        Args:
            pdf_path: Path to the PDF file to process
            
        Returns:
            True if pipeline started successfully, False otherwise
        """
        if not os.path.exists(pdf_path):
            self._handle_error("file_error", f"PDF file not found: {pdf_path}")
            return False
            
        # Add to queue if not already there
        self.processing_state.add_to_queue(pdf_path)
        
        # Start full processing pipeline
        return self._start_processing_pipeline(pdf_path)
        
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
            
    def _start_pdf_segmentation(self, pdf_path: str) -> bool:
        """
        Start PDF segmentation (PDF to text conversion only).
        
        Args:
            pdf_path: Path to the PDF file to segment
            
        Returns:
            True if segmentation started successfully, False otherwise
        """
        if not self.process_manager:
            self._handle_error("process_error", "Process manager not initialized")
            return False
            
        try:
            segmenter_script = self._get_segmenter_script_path()
            python_exe = self.process_manager.get_python_executable()
            
            # Get output directory for text files
            txt_output_dir = self._get_txt_output_directory()
            
            process_id = f"pdf_segment_{os.path.basename(pdf_path)}"
            
            success = self.process_manager.start_process(
                process_id=process_id,
                command=python_exe,
                args=[segmenter_script, pdf_path, "--output-dir", txt_output_dir]
            )
            
            if success:
                self.processing_state.start_processing(pdf_path, process_id)
                self.processing_progress.emit(pdf_path, 1, "PDF segmentation started")
                self._emit_status(f"Started segmentation: {os.path.basename(pdf_path)}")
                
                # Start progress tracking
                progress_id = f"progress_{process_id}"
                self.active_progress_ids[process_id] = progress_id
                self.progress_started.emit(progress_id, f"Segmenting {os.path.basename(pdf_path)}")
                
            return success
            
        except Exception as e:
            self._handle_error("process_error", f"Failed to start segmentation: {e}")
            return False
            
    def _start_processing_pipeline(self, pdf_path: str) -> bool:
        """
        Start the full PDF processing pipeline (segmentation + LLM processing).
        
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
                self.processing_state.start_processing(pdf_path, process_id)
                self.pdf_processing_started.emit(pdf_path)
                self.processing_progress.emit(pdf_path, 1, "Full pipeline started")
                self._emit_status(f"Started full processing: {os.path.basename(pdf_path)}")
                
                # Start progress tracking
                progress_id = f"progress_{process_id}"
                self.active_progress_ids[process_id] = progress_id
                self.progress_started.emit(progress_id, f"Processing {os.path.basename(pdf_path)}")
                
            return success
            
        except Exception as e:
            self._handle_error("process_error", f"Failed to start pipeline: {e}")
            return False
            
    def _start_llm_processing(self, pdf_path: str) -> bool:
        """
        Start LLM processing for a PDF that has already been segmented.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if LLM processing started successfully, False otherwise
        """
        if not self.process_manager:
            self._handle_error("process_error", "Process manager not initialized")
            return False
            
        try:
            agent_script = self._get_agent_script_path()
            python_exe = self.process_manager.get_python_executable()
            
            # Get the text input directory for this PDF
            pdf_stem = Path(pdf_path).stem
            txt_input_dir = os.path.join(self._get_txt_output_directory(), pdf_stem)
            
            if not os.path.exists(txt_input_dir):
                self._handle_error("file_error", f"Text input directory not found: {txt_input_dir}")
                return False
                
            process_id = f"llm_process_{os.path.basename(pdf_path)}"
            
            success = self.process_manager.start_process(
                process_id=process_id,
                command=python_exe,
                args=[agent_script, txt_input_dir]
            )
            
            if success:
                self.processing_state.start_processing(pdf_path, process_id)
                self.processing_progress.emit(pdf_path, 2, "LLM processing started")
                self._emit_status(f"Started LLM processing: {os.path.basename(pdf_path)}")
                
                # Start progress tracking
                progress_id = f"progress_{process_id}"
                self.active_progress_ids[process_id] = progress_id
                self.progress_started.emit(progress_id, f"LLM Processing {os.path.basename(pdf_path)}")
                
            return success
            
        except Exception as e:
            self._handle_error("process_error", f"Failed to start LLM processing: {e}")
            return False
            
    def _get_pdf_directory(self) -> str:
        """Get the PDF data directory path."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data', 'pdf'
        ))
        
    def _get_txt_output_directory(self) -> str:
        """Get the text output directory path."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data', 'txt_input'
        ))
        
    def _get_markdown_output_directory(self) -> str:
        """Get the markdown output directory path."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data', 'markdown'
        ))
        
    def _get_segmenter_script_path(self) -> str:
        """Get the path to the PDF segmenter script."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'pdf_segmenter.py'
        ))
        
    def _get_agent_script_path(self) -> str:
        """Get the path to the agent stream script."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'agent_stream.py'
        ))
        
    def _get_pipeline_script_path(self) -> str:
        """Get the path to the PDF processing pipeline script."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'pdf_process_pipeline.py'
        ))
        
    def _on_process_finished(self, process_id: str, exit_code: int):
        """Handle process completion."""
        success = exit_code == 0
        
        # Handle different types of processes
        if process_id.startswith("pdf_segment_"):
            self._handle_segmentation_finished(process_id, success)
        elif process_id.startswith("llm_process_"):
            self._handle_llm_processing_finished(process_id, success)
        elif process_id.startswith("pdf_pipeline_"):
            self._handle_pipeline_finished(process_id, success)
            
    def _handle_segmentation_finished(self, process_id: str, success: bool):
        """Handle PDF segmentation completion."""
        pdf_name = process_id.replace("pdf_segment_", "")
        pdf_path = os.path.join(self._get_pdf_directory(), pdf_name)
        
        # Update processing state
        output_path = None
        if success:
            pdf_stem = Path(pdf_path).stem
            output_path = os.path.join(self._get_txt_output_directory(), pdf_stem)
            
        self.processing_state.finish_processing(process_id, success, output_path)
        
        # Emit signals
        self.pdf_segmentation_finished.emit(pdf_path, success)
        
        # Update progress tracking
        if process_id in self.active_progress_ids:
            progress_id = self.active_progress_ids[process_id]
            if success:
                self.progress_finished.emit(progress_id, True, "Segmentation completed")
            else:
                self.progress_finished.emit(progress_id, False, "Segmentation failed")
            del self.active_progress_ids[process_id]
        
        if success:
            self.processing_progress.emit(pdf_path, 1, "PDF segmentation completed")
            self._emit_status(f"Segmentation completed: {pdf_name}")
            
            # Emit success notification
            if self.status_manager:
                self.status_manager.add_status_message(
                    f"Successfully segmented: {pdf_name}",
                    StatusLevel.SUCCESS,
                    "PDFHandler",
                    auto_remove_ms=5000
                )
        else:
            self._emit_status(f"Segmentation failed: {pdf_name}")
            
            # Emit error notification
            if self.status_manager:
                self.status_manager.add_status_message(
                    f"Segmentation failed: {pdf_name}",
                    StatusLevel.ERROR,
                    "PDFHandler",
                    auto_remove_ms=10000
                )
            
    def _handle_llm_processing_finished(self, process_id: str, success: bool):
        """Handle LLM processing completion."""
        pdf_name = process_id.replace("llm_process_", "")
        pdf_path = os.path.join(self._get_pdf_directory(), pdf_name)
        
        # Update processing state
        output_path = None
        if success:
            pdf_stem = Path(pdf_path).stem
            output_path = os.path.join(self._get_markdown_output_directory(), pdf_stem)
            
        self.processing_state.finish_processing(process_id, success, output_path)
        
        # Emit signals
        self.llm_processing_finished.emit(pdf_path, success)
        
        # Update progress tracking
        if process_id in self.active_progress_ids:
            progress_id = self.active_progress_ids[process_id]
            if success:
                self.progress_finished.emit(progress_id, True, "LLM processing completed")
            else:
                self.progress_finished.emit(progress_id, False, "LLM processing failed")
            del self.active_progress_ids[process_id]
        
        if success:
            self.processing_progress.emit(pdf_path, 2, "LLM processing completed")
            self._emit_status(f"LLM processing completed: {pdf_name}")
            
            # Emit success notification
            if self.status_manager:
                self.status_manager.add_status_message(
                    f"LLM processing completed: {pdf_name}",
                    StatusLevel.SUCCESS,
                    "PDFHandler",
                    auto_remove_ms=5000
                )
        else:
            self._emit_status(f"LLM processing failed: {pdf_name}")
            
            # Emit error notification
            if self.status_manager:
                self.status_manager.add_status_message(
                    f"LLM processing failed: {pdf_name}",
                    StatusLevel.ERROR,
                    "PDFHandler",
                    auto_remove_ms=10000
                )
            
    def _handle_pipeline_finished(self, process_id: str, success: bool):
        """Handle full pipeline completion."""
        pdf_name = process_id.replace("pdf_pipeline_", "")
        pdf_path = os.path.join(self._get_pdf_directory(), pdf_name)
        
        # Update processing state
        output_path = None
        if success:
            pdf_stem = Path(pdf_path).stem
            output_path = os.path.join(self._get_markdown_output_directory(), pdf_stem)
            
        self.processing_state.finish_processing(process_id, success, output_path)
        
        # Emit signals
        self.pdf_processing_finished.emit(pdf_path, success)
        
        # Update progress tracking
        if process_id in self.active_progress_ids:
            progress_id = self.active_progress_ids[process_id]
            if success:
                self.progress_finished.emit(progress_id, True, "Full pipeline completed")
            else:
                self.progress_finished.emit(progress_id, False, "Full pipeline failed")
            del self.active_progress_ids[process_id]
        
        if success:
            self.processing_progress.emit(pdf_path, 3, "Full pipeline completed")
            self._emit_status(f"Full processing completed: {pdf_name}")
            
            # Emit success notification
            if self.status_manager:
                self.status_manager.add_status_message(
                    f"Full processing completed: {pdf_name}",
                    StatusLevel.SUCCESS,
                    "PDFHandler",
                    auto_remove_ms=8000
                )
        else:
            self._emit_status(f"Full processing failed: {pdf_name}")
            
            # Emit error notification
            if self.status_manager:
                self.status_manager.add_status_message(
                    f"Full processing failed: {pdf_name}",
                    StatusLevel.ERROR,
                    "PDFHandler",
                    auto_remove_ms=12000
                )
            
    def _on_process_output(self, process_id: str, output: str):
        """Handle process output for logging."""
        # Forward output to status for logging
        self._emit_status(f"[{process_id}] {output}")
        
        # Update progress message if available
        if process_id in self.active_progress_ids:
            progress_id = self.active_progress_ids[process_id]
            # Extract meaningful progress information from output
            clean_output = output.strip()
            if clean_output and len(clean_output) < 100:  # Only short, meaningful messages
                # Try to extract progress percentage from common patterns
                progress_value = self._extract_progress_from_output(clean_output)
                if progress_value >= 0:
                    self.progress_updated.emit(progress_id, progress_value, clean_output)
                else:
                    self.progress_updated.emit(progress_id, -1, clean_output)  # -1 means no progress change
        
    def _on_process_error(self, process_id: str, error: str):
        """Handle process error output."""
        self._emit_status(f"[{process_id}] ERROR: {error}")
        
    def _on_handler_error(self, error_type: str, error_message: str):
        """Handle process manager errors."""
        self._handle_error(error_type, error_message)
        
    def get_processing_state(self) -> ProcessingState:
        """Get the current processing state."""
        return self.processing_state
        
    def get_pdf_list(self) -> List[str]:
        """Get list of PDF files in the PDF directory."""
        pdf_dir = self._get_pdf_directory()
        if not os.path.exists(pdf_dir):
            return []
            
        pdf_files = []
        for filename in os.listdir(pdf_dir):
            if filename.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(pdf_dir, filename))
        return pdf_files
        
    def is_pdf_processed(self, pdf_path: str) -> bool:
        """Check if a PDF has been processed (has markdown output)."""
        pdf_stem = Path(pdf_path).stem
        markdown_dir = os.path.join(self._get_markdown_output_directory(), pdf_stem)
        return os.path.exists(markdown_dir) and os.listdir(markdown_dir)
        
    def is_pdf_segmented(self, pdf_path: str) -> bool:
        """Check if a PDF has been segmented (has text output)."""
        pdf_stem = Path(pdf_path).stem
        txt_dir = os.path.join(self._get_txt_output_directory(), pdf_stem)
        return os.path.exists(txt_dir) and os.listdir(txt_dir)
        
    def cancel_processing(self, pdf_path: str) -> bool:
        """Cancel processing for a specific PDF."""
        pdf_name = os.path.basename(pdf_path)
        
        # Find and stop any active processes for this PDF
        processes_to_stop = []
        for process_id in self.processing_state.active_processes:
            if pdf_name in process_id:
                processes_to_stop.append(process_id)
                
        success = True
        for process_id in processes_to_stop:
            if not self.process_manager.stop_process(process_id, force=True):
                success = False
                
        # Remove from queue
        self.processing_state.remove_from_queue(pdf_path)
        
        if success:
            self._emit_status(f"Cancelled processing: {pdf_name}")
        else:
            self._emit_status(f"Failed to cancel processing: {pdf_name}")
            
        return success
        
    def cancel_all_processing(self) -> bool:
        """Cancel all active processing."""
        if self.process_manager:
            self.process_manager.stop_all_processes()
            
        # Clear processing state
        self.processing_state.processing_queue.clear()
        self.processing_state.active_processes.clear()
        self.processing_state.current_pdf = None
        
        self._emit_status("All processing cancelled")
        return True
        
    def retry_failed_pdf(self, pdf_path: str) -> bool:
        """Retry processing a failed PDF."""
        if pdf_path in self.processing_state.failed_pdfs:
            self.processing_state.failed_pdfs.remove(pdf_path)
            
        return self.start_full_processing(pdf_path)
        
    def _extract_progress_from_output(self, output: str) -> int:
        """
        Extract progress percentage from process output.
        
        Args:
            output: Process output string
            
        Returns:
            Progress percentage (0-100) or -1 if no progress found
        """
        import re
        
        # Common progress patterns
        patterns = [
            r'(\d+)%',  # "50%"
            r'(\d+)/(\d+)',  # "5/10"
            r'Progress:\s*(\d+)',  # "Progress: 75"
            r'Step\s*(\d+)\s*of\s*(\d+)',  # "Step 3 of 5"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    # Direct percentage
                    return min(100, max(0, int(match.group(1))))
                elif len(match.groups()) == 2:
                    # Fraction format
                    current = int(match.group(1))
                    total = int(match.group(2))
                    if total > 0:
                        return min(100, max(0, int((current / total) * 100)))
        
        return -1  # No progress found
    
    def cleanup(self):
        """Cleanup PDF handler resources."""
        # Cancel all processing before cleanup
        self.cancel_all_processing()
        
        if self.process_manager:
            self.process_manager.cleanup()
        super().cleanup()