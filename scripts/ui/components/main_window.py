"""
Main Window Component

The primary UI controller that manages the overall application layout and coordinates
between different panels and handlers.
"""

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSplitter
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
import os
import sys

from .base_component import BaseComponent
from .left_panel import LeftPanel
from .right_panel import RightPanel
from ..styles.app_styles import get_app_styles


class MainWindow(BaseComponent):
    """
    Main application window that coordinates all UI components.
    
    This class manages the overall layout and serves as the central
    coordinator for all UI components and handlers.
    """
    
    # Signals for main window events
    window_closing = pyqtSignal()
    pdf_dropped = pyqtSignal(str)  # PDF file path
    pdf_selected = pyqtSignal(str)  # PDF file path
    pdf_preprocess_requested = pyqtSignal(str)  # PDF file path
    process_pdf_requested = pyqtSignal(str)  # PDF file path
    stop_processing_requested = pyqtSignal()
    clear_console_requested = pyqtSignal()
    refresh_pdf_list_requested = pyqtSignal()
    open_prompt_editor_requested = pyqtSignal()
    open_model_selector_requested = pyqtSignal()
    open_text_preview_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('PDF Power Converter')
        self.left_panel = None
        self.right_panel = None
        self.main_splitter = None
        
        # Handlers
        self.pdf_handler = None
        
        self._setup_window_properties()
        
    def _setup_window_properties(self):
        """Setup basic window properties like size and icon."""
        self.resize(1200, 800)  # Increased size for better layout
        self.setMinimumSize(800, 600)
        
        # Apply theme-aware styling
        styles = get_app_styles()
        self.setStyleSheet(styles.get_main_window_style())
        
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
        
        # Create main splitter for left and right panels
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter)
        
        # Initialize panels
        self._setup_left_panel()
        self._setup_right_panel()
        
        # Set splitter proportions (70% left panel, 30% right panel)
        self.main_splitter.setSizes([840, 360])
        
    def _setup_left_panel(self):
        """Setup the left panel containing PDF list and console logs."""
        self.left_panel = LeftPanel()
        self.left_panel.initialize()
        self.main_splitter.addWidget(self.left_panel)
        
    def _setup_right_panel(self):
        """Setup the right panel containing control buttons."""
        self.right_panel = RightPanel()
        self.right_panel.initialize()
        self.main_splitter.addWidget(self.right_panel)
        
    def _setup_connections(self):
        """Setup signal/slot connections for the main window."""
        # Setup handlers first
        self._setup_handlers()
        
        # Connect left panel signals
        if self.left_panel:
            self.left_panel.pdf_dropped.connect(self.pdf_dropped.emit)
            self.left_panel.pdf_selected.connect(self.pdf_selected.emit)
            self.left_panel.pdf_preprocess_requested.connect(self.pdf_preprocess_requested.emit)
            
        # Connect right panel signals
        if self.right_panel:
            self.right_panel.process_pdf_requested.connect(self._on_process_pdf_requested)
            self.right_panel.stop_processing_requested.connect(self.stop_processing_requested.emit)
            self.right_panel.clear_console_requested.connect(self._on_clear_console_requested)
            self.right_panel.refresh_pdf_list_requested.connect(self._on_refresh_pdf_list_requested)
            self.right_panel.open_prompt_editor_requested.connect(self.open_prompt_editor_requested.emit)
            self.right_panel.open_model_selector_requested.connect(self.open_model_selector_requested.emit)
            self.right_panel.open_text_preview_requested.connect(self.open_text_preview_requested.emit)
            
        # Connect cross-panel interactions
        if self.left_panel and self.right_panel:
            # Update right panel when PDF is selected or dropped
            self.left_panel.pdf_selected.connect(self.right_panel.set_current_pdf)
            self.left_panel.pdf_dropped.connect(self.right_panel.set_current_pdf)
            
        # Connect handler signals
        self._connect_handler_signals()
            
    def _on_process_pdf_requested(self, pdf_path: str):
        """
        Handle process PDF request from right panel.
        
        Args:
            pdf_path: PDF file path (empty string means use selected PDF)
        """
        if not pdf_path and self.left_panel:
            pdf_path = self.left_panel.get_selected_pdf()
            
        if pdf_path:
            self.process_pdf_requested.emit(pdf_path)
        else:
            self.show_status_message("No PDF selected for processing", "warning")
            
    def _on_clear_console_requested(self):
        """Handle clear console request from right panel."""
        if self.left_panel:
            self.left_panel.clear_console_output()
        self.clear_console_requested.emit()
        
    def _on_refresh_pdf_list_requested(self):
        """Handle refresh PDF list request from right panel."""
        if self.left_panel:
            self.left_panel.refresh_pdf_list()
        self.refresh_pdf_list_requested.emit()
        
    def handle_pdf_drop(self, pdf_path: str):
        """
        Handle PDF file drop events.
        
        Args:
            pdf_path: Path to the dropped PDF file
        """
        self._emit_status(f"PDF dropped: {os.path.basename(pdf_path)}")
        self.pdf_dropped.emit(pdf_path)
        
    def append_console_output(self, text: str):
        """
        Append text to the console output.
        
        Args:
            text: Text to append to console
        """
        if self.left_panel:
            self.left_panel.append_console_output(text)
            
    def show_status_message(self, message: str, status_type: str = "info"):
        """
        Show a status message in the right panel.
        
        Args:
            message: Status message to display
            status_type: Type of status ('info', 'success', 'warning', 'error')
        """
        if self.right_panel:
            self.right_panel.set_status(message, status_type)
            
            # Also add to enhanced status system
            from ..utils.status_manager import StatusLevel
            level_map = {
                'info': StatusLevel.INFO,
                'success': StatusLevel.SUCCESS,
                'warning': StatusLevel.WARNING,
                'error': StatusLevel.ERROR
            }
            level = level_map.get(status_type, StatusLevel.INFO)
            self.right_panel.add_status_message(message, level, source="MainWindow")
            
    def add_processing_detail(self, detail: str):
        """
        Add a processing detail to the right panel.
        
        Args:
            detail: Processing detail message
        """
        if self.right_panel:
            self.right_panel.add_processing_detail(detail)
            
    def set_processing_active(self, active: bool):
        """
        Set the processing state across panels.
        
        Args:
            active: True if processing is active, False otherwise
        """
        if self.right_panel:
            self.right_panel.set_processing_active(active)
            
    def set_progress(self, value: int, maximum: int = 100):
        """
        Set the progress bar value.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        if self.right_panel:
            self.right_panel.set_progress(value, maximum)
    
    # Enhanced progress and status management methods
    
    def start_progress_operation(self, title: str, message: str = "", maximum: int = 100) -> str:
        """
        Start a progress operation with enhanced tracking.
        
        Args:
            title: Operation title
            message: Initial message
            maximum: Maximum progress value
            
        Returns:
            Progress ID for tracking
        """
        if self.right_panel:
            from ..utils.status_manager import ProgressType
            return self.right_panel.start_progress_indicator(title, ProgressType.DETERMINATE, maximum, message)
        return ""
    
    def update_progress_operation(self, progress_id: str, current: int, message: str = None) -> bool:
        """
        Update a progress operation.
        
        Args:
            progress_id: Progress ID to update
            current: Current progress value
            message: Optional progress message
            
        Returns:
            True if updated successfully
        """
        if self.right_panel:
            return self.right_panel.update_progress_indicator(progress_id, current=current, message=message)
        return False
    
    def finish_progress_operation(self, progress_id: str, message: str = None) -> bool:
        """
        Finish a progress operation.
        
        Args:
            progress_id: Progress ID to finish
            message: Completion message
            
        Returns:
            True if finished successfully
        """
        if self.right_panel:
            return self.right_panel.finish_progress_indicator(progress_id, message)
        return False
    
    def start_busy_operation(self, operation: str, message: str = "") -> str:
        """
        Start a busy indicator for indeterminate operations.
        
        Args:
            operation: Operation description
            message: Status message
            
        Returns:
            Busy indicator ID
        """
        if self.right_panel:
            return self.right_panel.start_busy_indicator(operation, message)
        return ""
    
    def finish_busy_operation(self, busy_id: str) -> bool:
        """
        Finish a busy indicator.
        
        Args:
            busy_id: Busy indicator ID
            
        Returns:
            True if finished successfully
        """
        if self.right_panel:
            return self.right_panel.finish_busy_indicator(busy_id)
        return False
    
    def add_enhanced_status_message(self, message: str, level: str = "info", 
                                  source: str = None, persistent: bool = False,
                                  auto_remove_ms: int = None) -> str:
        """
        Add an enhanced status message.
        
        Args:
            message: Status message text
            level: Message level ('info', 'success', 'warning', 'error')
            source: Source component name
            persistent: Whether message should persist
            auto_remove_ms: Auto-remove after milliseconds
            
        Returns:
            Message ID for tracking
        """
        if self.right_panel:
            from ..utils.status_manager import StatusLevel
            level_map = {
                'info': StatusLevel.INFO,
                'success': StatusLevel.SUCCESS,
                'warning': StatusLevel.WARNING,
                'error': StatusLevel.ERROR,
                'debug': StatusLevel.DEBUG
            }
            status_level = level_map.get(level, StatusLevel.INFO)
            
            # Set default auto-remove times based on severity
            if auto_remove_ms is None and not persistent:
                auto_remove_times = {
                    'info': 3000,      # 3 seconds
                    'success': 5000,   # 5 seconds
                    'warning': 8000,   # 8 seconds
                    'error': 12000,    # 12 seconds
                    'debug': 2000      # 2 seconds
                }
                auto_remove_ms = auto_remove_times.get(level, 5000)
            
            return self.right_panel.add_status_message(
                message, status_level, source or "MainWindow", persistent, auto_remove_ms
            )
        return ""
    
    def show_notification(self, title: str, message: str, level: str = "info", duration_ms: int = 4000):
        """
        Show a temporary notification message.
        
        Args:
            title: Notification title
            message: Notification message
            level: Message level ('info', 'success', 'warning', 'error')
            duration_ms: Display duration in milliseconds
        """
        full_message = f"{title}: {message}" if title else message
        self.add_enhanced_status_message(
            full_message, level, "Notification", persistent=False, auto_remove_ms=duration_ms
        )
        
        # Also show in status bar for immediate visibility
        self.show_status_message(full_message, level)
    
    def is_system_busy(self) -> bool:
        """
        Check if the system is currently busy with operations.
        
        Returns:
            True if busy, False otherwise
        """
        if self.right_panel:
            return self.right_panel.is_system_busy()
        return False
    
    def get_status_manager(self):
        """
        Get the status manager instance.
        
        Returns:
            StatusManager instance or None
        """
        if self.right_panel:
            return self.right_panel.get_status_manager()
        return None
            
    def get_selected_pdf(self) -> str:
        """
        Get the currently selected PDF file path.
        
        Returns:
            Path to selected PDF file, or empty string if none selected
        """
        if self.left_panel:
            return self.left_panel.get_selected_pdf()
        return ""
        
    def refresh_pdf_list(self):
        """Refresh the PDF file list."""
        if self.left_panel:
            self.left_panel.refresh_pdf_list()
            
    def clear_console_output(self):
        """Clear the console output."""
        if self.left_panel:
            self.left_panel.clear_console_output()
            
    def clear_processing_details(self):
        """Clear the processing details."""
        if self.right_panel:
            self.right_panel.clear_processing_details()
            
    def get_splitter_sizes(self) -> list:
        """Get the current main splitter sizes."""
        if self.main_splitter:
            return self.main_splitter.sizes()
        return []
        
    def set_splitter_sizes(self, sizes: list):
        """
        Set the main splitter sizes.
        
        Args:
            sizes: List of sizes for splitter sections
        """
        if self.main_splitter and len(sizes) >= 2:
            self.main_splitter.setSizes(sizes)
            
    def _setup_handlers(self):
        """Setup application handlers."""
        from ..handlers import PDFHandler
        
        # Initialize PDF handler
        self.pdf_handler = PDFHandler(self)
        self.pdf_handler.initialize()
        
        # Set status manager on PDF handler
        status_manager = self.get_status_manager()
        if status_manager and hasattr(self.pdf_handler, 'set_status_manager'):
            self.pdf_handler.set_status_manager(status_manager)
        
    def _connect_handler_signals(self):
        """Connect handler signals to UI components."""
        if self.pdf_handler:
            # Connect PDF handler signals to main window
            self.pdf_handler.pdf_copied.connect(self.pdf_dropped.emit)  # Use pdf_copied instead of pdf_dropped
            self.pdf_handler.pdf_processing_started.connect(self._on_pdf_processing_started)
            self.pdf_handler.pdf_processing_finished.connect(self._on_pdf_processing_finished)
            self.pdf_handler.pdf_segmentation_finished.connect(self._on_pdf_segmentation_finished)
            self.pdf_handler.llm_processing_finished.connect(self._on_llm_processing_finished)
            self.pdf_handler.processing_progress.connect(self._on_processing_progress)
            
            # Connect enhanced progress signals to status manager
            status_manager = self.get_status_manager()
            if status_manager:
                self.pdf_handler.progress_started.connect(self._on_handler_progress_started)
                self.pdf_handler.progress_updated.connect(self._on_handler_progress_updated)
                self.pdf_handler.progress_finished.connect(self._on_handler_progress_finished)
                
                # Connect process manager signals if available
                if hasattr(self.pdf_handler, 'process_manager') and self.pdf_handler.process_manager:
                    process_manager = self.pdf_handler.process_manager
                    process_manager.process_started.connect(self._on_process_started)
                    process_manager.process_finished.connect(self._on_process_finished)
                    process_manager.process_output.connect(self._on_process_output)
                    process_manager.process_error.connect(self._on_process_error)
                    process_manager.process_queued.connect(self._on_process_queued)
                    process_manager.process_cancelled.connect(self._on_process_cancelled)
                    process_manager.queue_empty.connect(self._on_queue_empty)
                    process_manager.process_progress_updated.connect(self._on_process_progress_updated)
                    process_manager.queue_status_changed.connect(self._on_queue_status_changed)
            
            # Connect main window signals to PDF handler
            self.pdf_dropped.connect(self.pdf_handler.handle_pdf_drop)
            self.process_pdf_requested.connect(self.pdf_handler.start_full_processing)
            self.stop_processing_requested.connect(self.pdf_handler.cancel_all_processing)
            
    def _on_pdf_processing_started(self, pdf_path: str):
        """Handle PDF processing started."""
        self.set_processing_active(True)
        self.add_enhanced_status_message(
            f"Started processing: {os.path.basename(pdf_path)}", 
            "info", "PDFHandler"
        )
        
    def _on_pdf_processing_finished(self, pdf_path: str, success: bool):
        """Handle PDF processing finished."""
        self.set_processing_active(False)
        if success:
            self.add_enhanced_status_message(
                f"Completed processing: {os.path.basename(pdf_path)}", 
                "success", "PDFHandler"
            )
        else:
            self.add_enhanced_status_message(
                f"Failed processing: {os.path.basename(pdf_path)}", 
                "error", "PDFHandler"
            )
            
    def _on_pdf_segmentation_finished(self, pdf_path: str, success: bool):
        """Handle PDF segmentation finished."""
        if success:
            self.add_enhanced_status_message(
                f"Segmentation completed: {os.path.basename(pdf_path)}", 
                "success", "PDFHandler"
            )
        else:
            self.add_enhanced_status_message(
                f"Segmentation failed: {os.path.basename(pdf_path)}", 
                "error", "PDFHandler"
            )
            
    def _on_llm_processing_finished(self, pdf_path: str, success: bool):
        """Handle LLM processing finished."""
        if success:
            self.add_enhanced_status_message(
                f"LLM processing completed: {os.path.basename(pdf_path)}", 
                "success", "PDFHandler"
            )
        else:
            self.add_enhanced_status_message(
                f"LLM processing failed: {os.path.basename(pdf_path)}", 
                "error", "PDFHandler"
            )
            
    def _on_processing_progress(self, pdf_path: str, step: int, description: str):
        """Handle processing progress updates."""
        self.add_processing_detail(f"Step {step}: {description}")
        
    def _on_handler_progress_started(self, progress_id: str, title: str):
        """Handle enhanced progress started from handlers."""
        if self.right_panel:
            from ..utils.status_manager import ProgressType
            self.right_panel.start_progress_indicator(title, ProgressType.INDETERMINATE, 100, "Starting...")
            
    def _on_handler_progress_updated(self, progress_id: str, current: int, message: str):
        """Handle enhanced progress updated from handlers."""
        if self.right_panel and current >= 0:  # -1 means no progress change
            self.right_panel.update_progress_indicator(progress_id, current=current, message=message)
            
    def _on_handler_progress_finished(self, progress_id: str, success: bool, message: str):
        """Handle enhanced progress finished from handlers."""
        if self.right_panel:
            self.right_panel.finish_progress_indicator(progress_id, message)
    
    def _on_process_queued(self, process_id: str):
        """Handle process queued from process manager."""
        self.add_enhanced_status_message(
            f"Process queued: {process_id}", 
            "info", "ProcessManager"
        )
        
        # Start a busy indicator for queued process
        if self.right_panel:
            self.right_panel.start_busy_indicator(f"Queued: {process_id}", "Waiting in queue...")
    
    def _on_process_cancelled(self, process_id: str):
        """Handle process cancelled from process manager."""
        self.add_enhanced_status_message(
            f"Process cancelled: {process_id}", 
            "warning", "ProcessManager"
        )
        
        # Finish any busy indicators for this process
        if self.right_panel:
            # Note: We'd need to track busy IDs per process for proper cleanup
            # For now, we'll rely on the process handler to manage this
            pass
    
    def _on_queue_empty(self):
        """Handle queue empty from process manager."""
        self.add_enhanced_status_message(
            "All processes completed", 
            "success", "ProcessManager"
        )
        
        # Update processing state
        self.set_processing_active(False)
    
    def _on_process_progress_updated(self, process_id: str, percentage: int, message: str):
        """Handle process progress updates from process manager."""
        # Update any progress indicators with meaningful progress
        if self.right_panel:
            # Try to find matching progress indicator by process_id
            status_manager = self.get_status_manager()
            if status_manager:
                active_progress = status_manager.get_active_progress()
                for progress in active_progress:
                    if process_id in progress.title or process_id in progress.message:
                        status_manager.update_progress(progress.id, current=percentage, message=message)
                        break
        
        # Also add to console output with progress info
        self.append_console_output(f"[{process_id}] Progress: {percentage}% - {message}")
    
    def _on_queue_status_changed(self, queue_length: int, active_count: int):
        """Handle queue status changes from process manager."""
        if queue_length > 0 or active_count > 0:
            status_msg = f"Queue: {queue_length} waiting, {active_count} active"
            self.add_enhanced_status_message(
                status_msg, "info", "ProcessManager", persistent=True, auto_remove_ms=5000
            )
        
        # Update processing state based on activity
        is_busy = queue_length > 0 or active_count > 0
        self.set_processing_active(is_busy)
    
    def _on_process_started(self, process_id: str):
        """Handle process started from process manager."""
        self.add_enhanced_status_message(
            f"Process started: {process_id}", 
            "info", "ProcessManager"
        )
        
        # Start a busy indicator for the process
        if self.right_panel:
            self.right_panel.start_busy_indicator(f"Running {process_id}", "Process executing...")
    
    def _on_process_finished(self, process_id: str, exit_code: int):
        """Handle process finished from process manager."""
        success = exit_code == 0
        status_level = "success" if success else "error"
        message = f"Process {process_id} {'completed' if success else 'failed'}"
        
        self.add_enhanced_status_message(message, status_level, "ProcessManager")
        
        # Finish any busy indicators for this process
        if self.right_panel:
            # Note: We'd need to track busy IDs per process for proper cleanup
            # For now, we'll rely on the process handler to manage this
            pass
    
    def _on_process_output(self, process_id: str, output: str):
        """Handle process output from process manager."""
        # Add to console output
        self.append_console_output(f"[{process_id}] {output}")
        
        # Update any progress indicators with meaningful output
        if self.right_panel and len(output.strip()) < 100:  # Only short messages
            # This would need process-to-progress mapping for proper implementation
            pass
    
    def _on_process_error(self, process_id: str, error: str):
        """Handle process error from process manager."""
        # Add to console output with error formatting
        self.append_console_output(f"[{process_id}] ERROR: {error}")
        
        # Add error status message
        self.add_enhanced_status_message(
            f"Process error in {process_id}: {error}", 
            "error", "ProcessManager", auto_remove_ms=10000
        )
            
    def get_pdf_handler(self):
        """Get the PDF handler instance."""
        return self.pdf_handler
        
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
        self._handle_error(error_type, error_message)
        self.show_status_message(f"Error: {error_message}", "error")