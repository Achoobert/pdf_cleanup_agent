"""
Application Controller

Main application controller that manages the application lifecycle,
coordinates components, and handles application-wide exception handling.
"""

import sys
import logging
import traceback
from PyQt5.QtWidgets import QApplication

from ui.components import MainWindow
from ui.utils import AppConfig, PathManager
from ui.styles.app_styles import get_app_styles


class PDFCleanupApp:
    """
    Main application class for the PDF Cleanup Agent.
    
    This class manages the application lifecycle, coordinates the main window
    and configuration, and handles application-wide exception handling.
    """
    
    def __init__(self, debug_mode: bool = False, log_level: str = "INFO"):
        """
        Initialize the PDF Cleanup application.
        
        Args:
            debug_mode: Enable debug mode with additional logging
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.debug_mode = debug_mode
        self.log_level = log_level
        
        # Setup application-wide exception handling
        sys.excepthook = self._handle_exception
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PDF Cleanup Agent")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("PDF Power Converter")
        
        # Initialize theme system
        self.styles = get_app_styles()
        self.app.setStyleSheet(self.styles.get_main_window_style())
        
        # Initialize components
        self.config = AppConfig()
        self.path_manager = PathManager()
        self.main_window = None
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup application logging with appropriate level."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if self.debug_mode:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            
        # Create custom handler for console widget
        self.console_handler = None
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('pdf_cleanup_app.log', mode='a')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"PDF Cleanup App starting (debug={self.debug_mode}, log_level={self.log_level})")
        
    def _setup_console_logging(self):
        """Setup logging to console widget."""
        if self.main_window and self.main_window.left_panel:
            # Create custom handler that sends logs to console widget
            class ConsoleWidgetHandler(logging.Handler):
                def __init__(self, console_widget):
                    super().__init__()
                    self.console_widget = console_widget
                    
                def emit(self, record):
                    try:
                        msg = self.format(record)
                        if self.console_widget:
                            self.console_widget.append_console_output(msg)
                    except Exception:
                        pass  # Ignore errors in logging handler
            
            # Add console handler to root logger
            console_handler = ConsoleWidgetHandler(self.main_window.left_panel)
            console_handler.setLevel(getattr(logging, self.log_level.upper()))
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # Add to root logger so all modules log to console
            root_logger = logging.getLogger()
            root_logger.addHandler(console_handler)
            
            self.console_handler = console_handler
            self.logger.info("Console logging connected successfully")
        
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Handle uncaught exceptions application-wide.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            self.logger.info("Application interrupted by user")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        # Log the exception
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.critical(f"Uncaught exception: {error_msg}")
        
        # Print error to stderr instead of showing pop-up dialog
        print(f"Critical error: {error_msg}", file=sys.stderr)
        
        # Cleanup and exit
        self.cleanup()
        sys.exit(1)
        
    def initialize(self) -> bool:
        """
        Initialize the application components.
        
        Returns:
            True if initialization was successful
        """
        try:
            self.logger.info("Initializing application components")
            
            # Load configuration
            if not self.config.initialize():
                self.logger.warning("Failed to load configuration, using defaults")
                
            # Ensure data directories exist
            if not self.path_manager.ensure_all_data_directories():
                self.logger.warning("Failed to create some data directories")
                
            # Create main window
            self.main_window = MainWindow()
            self.main_window.initialize()
            
            # Connect logging to console widget
            self._setup_console_logging()
            
            self.logger.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            if self.debug_mode:
                self.logger.debug(traceback.format_exc())
            return False
            
    def run(self) -> int:
        """
        Run the application main loop.
        
        Returns:
            Application exit code
        """
        if not self.initialize():
            self.logger.error("Application initialization failed")
            return 1
            
        try:
            self.logger.info("Starting application main loop")
            self.main_window.show()
            exit_code = self.app.exec_()
            self.logger.info(f"Application exited with code: {exit_code}")
            return exit_code
            
        except Exception as e:
            self.logger.error(f"Application runtime error: {e}")
            if self.debug_mode:
                self.logger.debug(traceback.format_exc())
            return 1
            
    def cleanup(self):
        """Cleanup application resources and perform shutdown procedures."""
        try:
            self.logger.info("Starting application cleanup")
            
            if self.main_window:
                self.main_window.cleanup()
                
            # Save configuration if needed
            if self.config and self.config.settings:
                self.config.save_config()
                
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")