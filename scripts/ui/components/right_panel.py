"""
Right Panel Component

Contains control buttons and status information.
"""

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QProgressBar, QFrame, QGroupBox, QTextEdit, QSpacerItem,
    QSizePolicy, QSplitter)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from .base_component import BaseComponent
from .progress_widgets import AnimatedProgressBar
from ..utils.status_manager import StatusManager, StatusLevel, ProgressType
from ..styles.app_styles import get_app_styles


class RightPanel(BaseComponent):
    """
    Right panel containing control buttons and status information.
    
    This panel provides the main controls for PDF processing operations
    and displays current status and progress information.
    """
    
    # Signals for right panel events
    process_pdf_requested = pyqtSignal(str)  # PDF file path
    stop_processing_requested = pyqtSignal()
    clear_console_requested = pyqtSignal()
    refresh_pdf_list_requested = pyqtSignal()
    open_prompt_editor_requested = pyqtSignal()
    open_model_selector_requested = pyqtSignal()
    open_text_preview_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process_button = None
        self.stop_button = None
        self.progress_bar = None
        self.status_label = None
        self.current_pdf_label = None
        self.processing_status = None
        
        # Enhanced progress and status management
        self.status_manager = None
        
    def _setup_ui(self):
        """Setup the right panel UI layout."""
        try:
            # Main vertical layout
            layout = QVBoxLayout()
            self.setLayout(layout)
            
            # Initialize status manager (simplified)
            self.status_manager = StatusManager(self)
            
            # Setup control buttons section
            self._setup_control_buttons(layout)
            
            # Setup status section
            self._setup_status_section(layout)
            
            # Setup utility buttons section
            self._setup_utility_buttons(layout)
            
            # Add spacer to push everything to top
            spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            layout.addItem(spacer)
            
            # Apply overall styling
            self._apply_panel_styling()
            
        except Exception as e:
            self.logger.error(f"Error setting up right panel UI: {e}")
            # Fallback to basic setup
            self._setup_basic_ui()
        

        
    def _setup_control_buttons(self, parent_layout):
        """Setup the main control buttons."""
        # Get app styles
        styles = get_app_styles()
        
        # Control buttons group
        control_group = QGroupBox("Processing Controls")
        control_group.setVisible(True)  # Explicitly set visible
        control_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        control_group.setStyleSheet(styles.GROUP_BOX)
        control_layout = QVBoxLayout()
        control_layout.setSpacing(8)  # Increased spacing between buttons
        control_layout.setContentsMargins(12, 15, 12, 12)  # Better margins
        control_group.setLayout(control_layout)
        
        # Process PDF button
        self.process_button = QPushButton("Process Selected PDF")
        styles = get_app_styles()
        self.process_button.setStyleSheet(styles.BUTTON_PRIMARY)
        self.process_button.clicked.connect(self._on_process_pdf_clicked)
        self.process_button.setVisible(True)  # Explicitly set visible
        self.process_button.setMinimumHeight(35)  # Ensure minimum height
        self.process_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        control_layout.addWidget(self.process_button)
        
        # Stop processing button
        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.setStyleSheet(styles.BUTTON_ERROR)
        self.stop_button.clicked.connect(self.stop_processing_requested.emit)
        self.stop_button.setEnabled(False)  # Initially disabled
        self.stop_button.setVisible(True)  # Explicitly set visible
        self.stop_button.setMinimumHeight(35)  # Ensure minimum height
        self.stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        control_layout.addWidget(self.stop_button)
        
        parent_layout.addWidget(control_group)
        
    def _setup_status_section(self, parent_layout):
        """Setup the status information section."""
        # Get app styles
        styles = get_app_styles()
        
        # Status group
        status_group = QGroupBox("Status Information")
        status_group.setStyleSheet(styles.GROUP_BOX)
        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)  # Better spacing
        status_layout.setContentsMargins(12, 15, 12, 12)  # Better margins
        status_group.setLayout(status_layout)
        
        # Current PDF label
        self.current_pdf_label = QLabel("No PDF selected")
        self.current_pdf_label.setStyleSheet(styles.INFO_LABEL)
        self.current_pdf_label.setWordWrap(True)
        self.current_pdf_label.setMinimumHeight(30)  # Ensure readable height
        
        # current_pdf_title = QLabel("Current PDF:")
        # current_pdf_title.setStyleSheet(styles.SECTION_TITLE_LABEL)
        # status_layout.addWidget(current_pdf_title)
        status_layout.addWidget(self.current_pdf_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        # Initial styling will be set by set_status method
        # status_title = QLabel("Status:")
        # status_title.setStyleSheet(styles.SECTION_TITLE_LABEL)
        # status_layout.addWidget(status_title)
        status_layout.addWidget(self.status_label)
        
        # Set initial status
        self.set_status("Ready", "success")
        
        # Simple progress bar for current operation
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setVisible(False)  # Initially hidden
        status_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(status_group)
        

        
    def _setup_utility_buttons(self, parent_layout):
        """Setup utility buttons section."""
        # Get app styles
        styles = get_app_styles()
        
        # Utility buttons group
        utility_group = QGroupBox("Utilities")
        utility_group.setStyleSheet(styles.GROUP_BOX)
        utility_layout = QVBoxLayout()
        utility_layout.setSpacing(8)  # Better spacing
        utility_layout.setContentsMargins(12, 15, 12, 12)  # Better margins
        utility_group.setLayout(utility_layout)
        
        # Clear console button
        clear_console_btn = QPushButton("Clear Console")
        clear_console_btn.clicked.connect(self.clear_console_requested.emit)
        utility_layout.addWidget(clear_console_btn)
        
        # Refresh PDF list button
        refresh_list_btn = QPushButton("Refresh PDF List")
        refresh_list_btn.clicked.connect(self.refresh_pdf_list_requested.emit)
        utility_layout.addWidget(refresh_list_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        utility_layout.addWidget(separator)
        
        # Advanced buttons
        prompt_editor_btn = QPushButton("Edit Prompt")
        prompt_editor_btn.clicked.connect(self._on_edit_prompts_clicked)
        utility_layout.addWidget(prompt_editor_btn)
        
        model_selector_btn = QPushButton("Select Model")
        model_selector_btn.clicked.connect(self._on_select_model_clicked)
        utility_layout.addWidget(model_selector_btn)
        
        open_data_btn = QPushButton("Open Data Directory")
        open_data_btn.clicked.connect(self._on_open_data_directory)
        utility_layout.addWidget(open_data_btn)
        
        # Style utility buttons
        for button in [clear_console_btn, refresh_list_btn, prompt_editor_btn, 
                      model_selector_btn, open_data_btn]:
            button.setStyleSheet(styles.BUTTON_SECONDARY)
            button.setMinimumHeight(32)  # Consistent height
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        parent_layout.addWidget(utility_group)
        
    def _setup_connections(self):
        """Setup signal/slot connections for the right panel."""
        # Connect status manager signals
        if self.status_manager:
            self.status_manager.status_message_added.connect(self._on_status_message_added)
            self.status_manager.progress_started.connect(self._on_progress_started)
            self.status_manager.progress_updated.connect(self._on_progress_updated)
            self.status_manager.progress_finished.connect(self._on_progress_finished)
        
    def _on_process_pdf_clicked(self):
        """Handle process PDF button click."""
        # This will be connected to get the selected PDF from left panel
        self.process_pdf_requested.emit("")  # Empty string means use selected PDF
        
    def _on_open_data_directory(self):
        """Handle open data directory button click."""
        import os
        import subprocess
        import sys
        
        try:
            # Get the data directory path
            data_dir = os.path.join(os.getcwd(), "data")
            
            # Create directory if it doesn't exist
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                self._emit_status(f"Created data directory: {data_dir}")
            
            # Open directory in file manager
            if sys.platform == "win32":
                os.startfile(data_dir)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", data_dir], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", data_dir], check=True)
            
            self._emit_status(f"Opened data directory: {data_dir}")
            
        except subprocess.CalledProcessError as e:
            self._emit_status(f"Failed to open data directory - subprocess error: {e}")
        except FileNotFoundError as e:
            self._emit_status(f"Failed to open data directory - file not found: {e}")
        except PermissionError as e:
            self._emit_status(f"Failed to open data directory - permission denied: {e}")
        except Exception as e:
            self._emit_status(f"Failed to open data directory - unexpected error: {e}")
            # Log the full error for debugging
            import traceback
            self.logger.error(f"Data directory error: {traceback.format_exc()}")
            
    def _on_edit_prompts_clicked(self):
        """Handle edit prompts button click."""
        import os
        import subprocess
        import sys
        import yaml
        
        try:
            # Load config to get prompt file path - find project root
            def find_project_root():
                # Start from current file location
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Try multiple approaches to find project root
                search_paths = [
                    current_dir,
                    os.getcwd(),  # Current working directory
                    os.path.dirname(os.path.dirname(os.path.dirname(current_dir))),  # Go up 3 levels from scripts/ui/components
                ]
                
                for path in search_paths:
                    config_file = os.path.join(path, 'pipeline_config.yml')
                    if os.path.exists(config_file):
                        return path
                
                # If not found, navigate up from current file
                project_root = current_dir
                while project_root and project_root != os.path.dirname(project_root):
                    if os.path.exists(os.path.join(project_root, 'pipeline_config.yml')):
                        return project_root
                    project_root = os.path.dirname(project_root)
                
                return os.getcwd()  # fallback to current working directory
            
            project_root = find_project_root()
            config_path = os.path.join(project_root, 'pipeline_config.yml')
            self._emit_status(f"Project root: {project_root}")
            self._emit_status(f"Loading config from: {config_path}")
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            prompts_file = os.path.join(project_root, config['settings']['prompt'])
            self._emit_status(f"Prompt file path: {prompts_file}")
            
            # Check if file exists
            if not os.path.exists(prompts_file):
                self._emit_status(f"Prompt file not found at: {prompts_file}")
                # Try to create it if directory exists
                prompt_dir = os.path.dirname(prompts_file)
                if not os.path.exists(prompt_dir):
                    self._emit_status(f"Creating prompt directory: {prompt_dir}")
                    os.makedirs(prompt_dir, exist_ok=True)
            
            # Create default prompts file if it doesn't exist
            if not os.path.exists(prompts_file):
                os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
                default_prompts = """Act as a text normalization expert. Clean and repair the following PDF-extracted text by performing the following operations:

1. **Line Break Repair**  
   - Remove mid-sentence line breaks while preserving paragraph breaks.  
   - Join hyphenated words across lines (e.g., "exam-\\nple" → "example").  
   - Keep bullet points and numbered lists intact.

2. **Spacing Correction**  
   - Fix irregular letter spacing (e.g., "w o r d" → "word").  
   - Remove excessive spaces between words (e.g., "too     much" → "too much").  
   - Preserve meaningful indentation (e.g., code blocks).

3. **Character Restoration**  
   - Replace common OCR errors (e.g., corrupted characters or missing punctuation).  
   - Infer missing characters using context clues.  
   - Use `[UNCERTAIN]` only when the correct fix is ambiguous.

4. **Special Cases**  
   - Preserve numbers, dates, URLs, and emails.  
   - Preserve technical terms and proper nouns.  
   - Remove repeated words from scan errors (e.g., "the the" → "the").
   - **Handle OCR artifacts**: When you encounter vertical columns of single characters (like "s\\nh\\no\\no\\nt\\ni\\nn\\ng\\nd\\ne\\ne\\np\\no\\nn\\ne\\ns"), these are OCR artifacts where text was incorrectly split vertically. Reconstruct these into proper words by reading the characters horizontally. For example:
     - "B\\nO\\nO\\nK\\nT\\nH\\nR\\nE\\nE" → "BOOK THREE"
     - "2\\n0\\n2\\n0" → "2020"
   - **Remove page artifacts**: Delete page headers, footers, and page numbers that are not part of the actual content. Examples to remove:
     - "--- Page 21 ---"
     - "2121" (when appearing as page numbers)
     - Repeated headers like "EDGE OF DARKNESS" appearing multiple times on the same page
     - Footer text that repeats across pages

---

**Input text starts below:**  

"""
                with open(prompts_file, 'w', encoding='utf-8') as f:
                    f.write(default_prompts)
                self._emit_status(f"Created default prompts file: {prompts_file}")
            
            # Open prompts file in default text editor
            if sys.platform == "win32":
                os.startfile(prompts_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", prompts_file], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", prompts_file], check=True)
            
            self._emit_status(f"Opened prompts file: {prompts_file}")
            
        except subprocess.CalledProcessError as e:
            self._emit_status(f"Failed to open prompts file - subprocess error: {e}")
        except FileNotFoundError as e:
            self._emit_status(f"Failed to open prompts file - file not found: {e}")
        except PermissionError as e:
            self._emit_status(f"Failed to open prompts file - permission denied: {e}")
        except Exception as e:
            self._emit_status(f"Failed to open prompts file - unexpected error: {e}")
            # Log the full error for debugging
            import traceback
            self.logger.error(f"Prompts file error: {traceback.format_exc()}")
            
    def _on_select_model_clicked(self):
        """Handle select model button click."""
        import os
        import subprocess
        import sys
        
        try:
            # Look for model config file in data directory (YAML format)
            config_file = os.path.join(os.getcwd(), "data", "model_config.yml")
            
            # Create default model config if it doesn't exist
            if not os.path.exists(config_file):
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                default_config = """# Model Configuration
# Edit this file to configure your AI model settings

model_settings:
  default_model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2000
  api_key: "your-api-key-here"

available_models:
  - "gpt-3.5-turbo"
  - "gpt-4"
  - "gpt-4-turbo"
  - "claude-3-sonnet"
  - "claude-3-haiku"
  - "claude-3-opus"

# Instructions:
# - Edit the default_model to change which model is used
# - Set your API key in the api_key field
# - Adjust temperature (0.0-1.0) for creativity level (higher = more creative)
# - Adjust max_tokens for response length (higher = longer responses)
# - Save this file after making changes
"""
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(default_config)
                self._emit_status(f"Created default model config: {config_file}")
            
            # Open config file in default text editor
            if sys.platform == "win32":
                os.startfile(config_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", config_file], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", config_file], check=True)
            
            self._emit_status(f"Opened model config: {config_file}")
            
        except subprocess.CalledProcessError as e:
            self._emit_status(f"Failed to open model config - subprocess error: {e}")
        except FileNotFoundError as e:
            self._emit_status(f"Failed to open model config - file not found: {e}")
        except PermissionError as e:
            self._emit_status(f"Failed to open model config - permission denied: {e}")
        except Exception as e:
            self._emit_status(f"Failed to open model config - unexpected error: {e}")
            # Log the full error for debugging
            import traceback
            self.logger.error(f"Model config error: {traceback.format_exc()}")
        
    def set_current_pdf(self, pdf_path: str):
        """
        Set the current PDF being processed.
        
        Args:
            pdf_path: Path to the current PDF file
        """
        if self.current_pdf_label:
            if pdf_path:
                import os
                filename = os.path.basename(pdf_path)
                self.current_pdf_label.setText(filename)
                self._emit_status(f"Current PDF set to: {filename}")
            else:
                self.current_pdf_label.setText("No PDF selected")
                
    def set_status(self, status: str, status_type: str = "info"):
        """
        Set the status message with appropriate styling.
        
        Args:
            status: Status message
            status_type: Type of status ('info', 'success', 'warning', 'error')
        """
        if self.status_label:
            self.status_label.setText(status)
            
            styles = get_app_styles()
            
            # Apply styling based on status type
            self.status_label.setStyleSheet(styles.get_status_label_style(status_type))
            self.status_label.setMinimumHeight(30)  # Ensure readable height
            self._emit_status(f"Status updated: {status} ({status_type})")
            
    def add_processing_detail(self, detail: str):
        """
        Add a processing detail to the status area.
        
        Args:
            detail: Processing detail message
        """
        # Processing details now go to console in left panel
        self._emit_status(f"Processing: {detail}")
            
    def clear_processing_details(self):
        """Clear the processing details."""
        # Processing details now go to console in left panel
        pass
            
    def set_processing_active(self, active: bool):
        """
        Set the processing state (enable/disable buttons and show/hide progress).
        
        Args:
            active: True if processing is active, False otherwise
        """
        if self.process_button:
            self.process_button.setEnabled(not active)
        if self.stop_button:
            self.stop_button.setEnabled(active)
        if self.progress_bar:
            self.progress_bar.setVisible(active)
            if not active:
                self.progress_bar.setValue(0)
                
        status_type = "info" if active else "success"
        status_msg = "Processing..." if active else "Ready"
        self.set_status(status_msg, status_type)
        
    def set_progress(self, value: int, maximum: int = 100):
        """
        Set the progress bar value.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        if self.progress_bar:
            self.progress_bar.setMaximum(maximum)
            self.progress_bar.setValue(value)
            
    def get_processing_state(self) -> bool:
        """
        Get the current processing state.
        
        Returns:
            True if processing is active, False otherwise
        """
        if self.stop_button:
            return self.stop_button.isEnabled()
        return False
    
    # Enhanced status and progress management methods
    
    def add_status_message(self, message: str, level: StatusLevel = StatusLevel.INFO,
                          source: str = None, persistent: bool = False, auto_remove_ms: int = None) -> str:
        """
        Add a status message using the enhanced status system.
        
        Args:
            message: Status message text
            level: Message severity level
            source: Source component name
            persistent: Whether message should persist
            auto_remove_ms: Auto-remove after milliseconds
            
        Returns:
            Message ID for tracking
        """
        if self.status_manager:
            return self.status_manager.add_status_message(
                message, level, source, persistent=persistent, auto_remove_ms=auto_remove_ms
            )
        return ""
    
    def start_progress_indicator(self, title: str, progress_type: ProgressType = ProgressType.DETERMINATE,
                               maximum: int = 100, message: str = "") -> str:
        """
        Start a progress indicator.
        
        Args:
            title: Progress title
            progress_type: Type of progress indicator
            maximum: Maximum progress value
            message: Initial progress message
            
        Returns:
            Progress ID for tracking
        """
        if self.status_manager:
            return self.status_manager.start_progress(title, progress_type, maximum, message)
        return ""
    
    def update_progress_indicator(self, progress_id: str, current: int = None,
                                maximum: int = None, message: str = None) -> bool:
        """
        Update a progress indicator.
        
        Args:
            progress_id: Progress ID to update
            current: New current progress value
            maximum: New maximum progress value
            message: New progress message
            
        Returns:
            True if updated successfully
        """
        if self.status_manager:
            return self.status_manager.update_progress(progress_id, current, maximum, message)
        return False
    
    def finish_progress_indicator(self, progress_id: str, message: str = None) -> bool:
        """
        Finish a progress indicator.
        
        Args:
            progress_id: Progress ID to finish
            message: Completion message
            
        Returns:
            True if finished successfully
        """
        if self.status_manager:
            return self.status_manager.finish_progress(progress_id, message)
        return False
    
    def start_busy_indicator(self, operation: str, message: str = "") -> str:
        """
        Start a busy indicator for long-running operations.
        
        Args:
            operation: Operation description
            message: Status message
            
        Returns:
            Busy indicator ID
        """
        if self.status_manager:
            return self.status_manager.start_busy_indicator(operation, message)
        return ""
    
    def finish_busy_indicator(self, busy_id: str) -> bool:
        """
        Finish a busy indicator.
        
        Args:
            busy_id: Busy indicator ID
            
        Returns:
            True if finished successfully
        """
        if self.status_manager:
            return self.status_manager.finish_busy_indicator(busy_id)
        return False
    
    def is_system_busy(self) -> bool:
        """
        Check if the system is currently busy with any operations.
        
        Returns:
            True if busy, False otherwise
        """
        if self.status_manager:
            return self.status_manager.is_busy()
        return False
    
    def clear_all_status_messages(self, level: StatusLevel = None):
        """
        Clear status messages.
        
        Args:
            level: If specified, only clear messages of this level
        """
        if self.status_manager:
            self.status_manager.clear_status_messages(level)
    
    # Signal handlers for enhanced status system
    
    def _on_status_message_added(self, status_message):
        """Handle new status message."""
        # Status messages now go to console in left panel
        self._emit_status(f"Status: {status_message.message}")
    
    def _on_progress_started(self, progress_info):
        """Handle progress started."""
        # Update main progress bar for primary operation
        if self.progress_bar and progress_info.progress_type == ProgressType.DETERMINATE:
            self.progress_bar.setMaximum(progress_info.maximum)
            self.progress_bar.setValueAnimated(progress_info.current)
            self.progress_bar.setVisible(True)
    
    def _on_progress_updated(self, progress_info):
        """Handle progress updated."""
        # Update main progress bar for primary operation
        if self.progress_bar and progress_info.progress_type == ProgressType.DETERMINATE:
            self.progress_bar.setMaximum(progress_info.maximum)
            self.progress_bar.setValueAnimated(progress_info.current)
    
    def _on_progress_finished(self, progress_id: str):
        """Handle progress finished."""
        # Hide main progress bar if no active progress
        if self.progress_bar and self.status_manager:
            active_progress = self.status_manager.get_active_progress()
            if not active_progress:
                self.progress_bar.setVisible(False)
                self.progress_bar.setValue(0)
    
    def get_status_manager(self) -> StatusManager:
        """
        Get the status manager instance.
        
        Returns:
            StatusManager instance
        """
        return self.status_manager
    
    def _apply_panel_styling(self):
        """Apply overall panel styling."""
        try:
            styles = get_app_styles()
            self.setStyleSheet(styles.PANEL_STYLE)
        except Exception as e:
            self.logger.error(f"Error applying panel styling: {e}")
    
    def _setup_basic_ui(self):
        """Fallback basic UI setup."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Basic control buttons
        self.process_button = QPushButton("Process Selected PDF")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.process_button.clicked.connect(self._on_process_pdf_clicked)
        layout.addWidget(self.process_button)
        
        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #a4262c;
            }
        """)
        self.stop_button.clicked.connect(self.stop_processing_requested.emit)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        # Basic status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 5px;
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Add spacer
        layout.addStretch()
    
    def cleanup(self):
        """Cleanup right panel resources."""
        if self.status_manager:
            self.status_manager.cleanup()
        super().cleanup()