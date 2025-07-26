"""
Integration tests for Progress and Status Management

Tests the integration between status manager, progress widgets, and handlers.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.ui.utils.status_manager import StatusManager, StatusLevel, ProgressType
from scripts.ui.components.progress_widgets import ProgressPanel, ProgressWidget, BusyWidget
from scripts.ui.components.right_panel import RightPanel
from scripts.ui.components.main_window import MainWindow


class TestStatusManager(unittest.TestCase):
    """Test the StatusManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.status_manager = StatusManager()
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.status_manager.cleanup()
        
    def test_add_status_message(self):
        """Test adding status messages."""
        message_id = self.status_manager.add_status_message(
            "Test message", StatusLevel.INFO, "TestSource"
        )
        
        self.assertIsNotNone(message_id)
        self.assertIn(message_id, self.status_manager.status_messages)
        
        message = self.status_manager.status_messages[message_id]
        self.assertEqual(message.message, "Test message")
        self.assertEqual(message.level, StatusLevel.INFO)
        self.assertEqual(message.source, "TestSource")
        
    def test_update_status_message(self):
        """Test updating status messages."""
        message_id = self.status_manager.add_status_message("Original message")
        
        success = self.status_manager.update_status_message(
            message_id, "Updated message", StatusLevel.SUCCESS
        )
        
        self.assertTrue(success)
        message = self.status_manager.status_messages[message_id]
        self.assertEqual(message.message, "Updated message")
        self.assertEqual(message.level, StatusLevel.SUCCESS)
        
    def test_remove_status_message(self):
        """Test removing status messages."""
        message_id = self.status_manager.add_status_message("Test message")
        
        success = self.status_manager.remove_status_message(message_id)
        
        self.assertTrue(success)
        self.assertNotIn(message_id, self.status_manager.status_messages)
        
    def test_start_progress(self):
        """Test starting progress indicators."""
        progress_id = self.status_manager.start_progress(
            "Test Progress", ProgressType.DETERMINATE, 100, "Starting..."
        )
        
        self.assertIsNotNone(progress_id)
        self.assertIn(progress_id, self.status_manager.active_progress)
        
        progress = self.status_manager.active_progress[progress_id]
        self.assertEqual(progress.title, "Test Progress")
        self.assertEqual(progress.progress_type, ProgressType.DETERMINATE)
        self.assertEqual(progress.maximum, 100)
        self.assertEqual(progress.message, "Starting...")
        
    def test_update_progress(self):
        """Test updating progress indicators."""
        progress_id = self.status_manager.start_progress("Test Progress")
        
        success = self.status_manager.update_progress(
            progress_id, current=50, message="Half way done"
        )
        
        self.assertTrue(success)
        progress = self.status_manager.active_progress[progress_id]
        self.assertEqual(progress.current, 50)
        self.assertEqual(progress.message, "Half way done")
        
    def test_finish_progress(self):
        """Test finishing progress indicators."""
        progress_id = self.status_manager.start_progress("Test Progress")
        
        success = self.status_manager.finish_progress(progress_id, "Completed!")
        
        self.assertTrue(success)
        self.assertNotIn(progress_id, self.status_manager.active_progress)
        self.assertEqual(len(self.status_manager.progress_history), 1)
        
    def test_start_busy_indicator(self):
        """Test starting busy indicators."""
        busy_id = self.status_manager.start_busy_indicator(
            "Processing", "Please wait..."
        )
        
        self.assertIsNotNone(busy_id)
        self.assertIn(busy_id, self.status_manager.busy_indicators)
        
        busy = self.status_manager.busy_indicators[busy_id]
        self.assertEqual(busy.operation, "Processing")
        self.assertEqual(busy.message, "Please wait...")
        
    def test_finish_busy_indicator(self):
        """Test finishing busy indicators."""
        busy_id = self.status_manager.start_busy_indicator("Processing")
        
        success = self.status_manager.finish_busy_indicator(busy_id)
        
        self.assertTrue(success)
        self.assertNotIn(busy_id, self.status_manager.busy_indicators)
        
    def test_is_busy(self):
        """Test checking if system is busy."""
        self.assertFalse(self.status_manager.is_busy())
        
        # Add progress indicator
        progress_id = self.status_manager.start_progress("Test")
        self.assertTrue(self.status_manager.is_busy())
        
        # Finish progress
        self.status_manager.finish_progress(progress_id)
        self.assertFalse(self.status_manager.is_busy())
        
        # Add busy indicator
        busy_id = self.status_manager.start_busy_indicator("Test")
        self.assertTrue(self.status_manager.is_busy())
        
        # Finish busy
        self.status_manager.finish_busy_indicator(busy_id)
        self.assertFalse(self.status_manager.is_busy())


class TestProgressWidgets(unittest.TestCase):
    """Test the progress widget components."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.ui.utils.status_manager import ProgressInfo, BusyIndicator, StatusMessage
        
        # Create test data
        self.progress_info = ProgressInfo(
            id="test_progress",
            title="Test Progress",
            progress_type=ProgressType.DETERMINATE,
            current=25,
            maximum=100,
            message="Processing..."
        )
        
        self.busy_info = BusyIndicator(
            id="test_busy",
            operation="Test Operation",
            message="Please wait..."
        )
        
        self.status_message = StatusMessage(
            id="test_status",
            message="Test status message",
            level=StatusLevel.INFO,
            timestamp=None  # Will be set automatically
        )
        
    def test_progress_widget_creation(self):
        """Test creating progress widgets."""
        widget = ProgressWidget(self.progress_info)
        widget.initialize()
        
        self.assertEqual(widget.progress_info.id, "test_progress")
        self.assertEqual(widget.progress_info.title, "Test Progress")
        
        widget.cleanup()
        
    def test_busy_widget_creation(self):
        """Test creating busy widgets."""
        widget = BusyWidget(self.busy_info)
        widget.initialize()
        
        self.assertEqual(widget.busy_info.id, "test_busy")
        self.assertEqual(widget.busy_info.operation, "Test Operation")
        
        widget.cleanup()
        
    def test_progress_panel_management(self):
        """Test progress panel widget management."""
        panel = ProgressPanel()
        panel.initialize()
        
        # Add progress widget
        panel.add_progress_widget(self.progress_info)
        self.assertIn(self.progress_info.id, panel.progress_widgets)
        
        # Add busy widget
        panel.add_busy_widget(self.busy_info)
        self.assertIn(self.busy_info.id, panel.busy_widgets)
        
        # Add status widget
        panel.add_status_widget(self.status_message)
        self.assertIn(self.status_message.id, panel.status_widgets)
        
        # Remove widgets
        panel.remove_progress_widget(self.progress_info.id)
        self.assertNotIn(self.progress_info.id, panel.progress_widgets)
        
        panel.remove_busy_widget(self.busy_info.id)
        self.assertNotIn(self.busy_info.id, panel.busy_widgets)
        
        panel.remove_status_widget(self.status_message.id)
        self.assertNotIn(self.status_message.id, panel.status_widgets)
        
        panel.cleanup()


class TestRightPanelIntegration(unittest.TestCase):
    """Test right panel integration with status management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.right_panel = RightPanel()
        self.right_panel.initialize()
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.right_panel.cleanup()
        
    def test_status_manager_integration(self):
        """Test status manager integration."""
        status_manager = self.right_panel.get_status_manager()
        self.assertIsNotNone(status_manager)
        
        # Add status message
        message_id = self.right_panel.add_status_message(
            "Test message", StatusLevel.INFO, "TestSource"
        )
        self.assertIsNotNone(message_id)
        
        # Check that message was added to status manager
        messages = status_manager.get_status_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Test message")
        
    def test_progress_indicator_integration(self):
        """Test progress indicator integration."""
        # Start progress
        progress_id = self.right_panel.start_progress_indicator(
            "Test Progress", ProgressType.DETERMINATE, 100, "Starting..."
        )
        self.assertIsNotNone(progress_id)
        
        # Update progress
        success = self.right_panel.update_progress_indicator(
            progress_id, current=50, message="Half done"
        )
        self.assertTrue(success)
        
        # Finish progress
        success = self.right_panel.finish_progress_indicator(
            progress_id, "Completed!"
        )
        self.assertTrue(success)
        
    def test_busy_indicator_integration(self):
        """Test busy indicator integration."""
        # Start busy indicator
        busy_id = self.right_panel.start_busy_indicator(
            "Test Operation", "Processing..."
        )
        self.assertIsNotNone(busy_id)
        
        # Check system is busy
        self.assertTrue(self.right_panel.is_system_busy())
        
        # Finish busy indicator
        success = self.right_panel.finish_busy_indicator(busy_id)
        self.assertTrue(success)
        
        # Check system is no longer busy
        self.assertFalse(self.right_panel.is_system_busy())


class TestMainWindowIntegration(unittest.TestCase):
    """Test main window integration with progress system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the PDF handler to avoid file system dependencies
        with patch('scripts.ui.handlers.PDFHandler') as mock_handler_class:
            self.mock_pdf_handler = Mock()
            mock_handler_class.return_value = self.mock_pdf_handler
            
            # Configure mock methods
            self.mock_pdf_handler.initialize.return_value = None
            self.mock_pdf_handler.set_status_manager.return_value = None
            
            self.main_window = MainWindow()
            self.main_window.initialize()
            
    def tearDown(self):
        """Clean up test fixtures."""
        self.main_window.cleanup()
        
    def test_status_manager_access(self):
        """Test accessing status manager through main window."""
        status_manager = self.main_window.get_status_manager()
        self.assertIsNotNone(status_manager)
        
    def test_enhanced_status_message(self):
        """Test adding enhanced status messages."""
        message_id = self.main_window.add_enhanced_status_message(
            "Test message", "info", "TestSource"
        )
        self.assertIsNotNone(message_id)
        
        status_manager = self.main_window.get_status_manager()
        messages = status_manager.get_status_messages()
        self.assertEqual(len(messages), 1)
        
    def test_progress_operation_lifecycle(self):
        """Test complete progress operation lifecycle."""
        # Start progress operation
        progress_id = self.main_window.start_progress_operation(
            "Test Operation", "Starting...", 100
        )
        self.assertIsNotNone(progress_id)
        
        # Update progress
        success = self.main_window.update_progress_operation(
            progress_id, 50, "Half done"
        )
        self.assertTrue(success)
        
        # Finish progress
        success = self.main_window.finish_progress_operation(
            progress_id, "Completed!"
        )
        self.assertTrue(success)
        
    def test_busy_operation_lifecycle(self):
        """Test complete busy operation lifecycle."""
        # Start busy operation
        busy_id = self.main_window.start_busy_operation(
            "Test Operation", "Processing..."
        )
        self.assertIsNotNone(busy_id)
        
        # Check system is busy
        self.assertTrue(self.main_window.is_system_busy())
        
        # Finish busy operation
        success = self.main_window.finish_busy_operation(busy_id)
        self.assertTrue(success)
        
        # Check system is no longer busy
        self.assertFalse(self.main_window.is_system_busy())
        
    def test_pdf_handler_status_manager_connection(self):
        """Test that PDF handler gets status manager reference."""
        # Verify that set_status_manager was called on the PDF handler
        self.mock_pdf_handler.set_status_manager.assert_called_once()


if __name__ == '__main__':
    # Set up Qt application for testing
    app = QApplication([])
    
    # Run tests
    unittest.main()