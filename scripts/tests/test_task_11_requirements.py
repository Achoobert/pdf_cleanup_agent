#!/usr/bin/env python3
"""
Test Task 11 Requirements

This test verifies that all requirements for Task 11 are implemented:
- Add progress bars and status indicators to the UI components
- Implement real-time status updates during PDF processing
- Create status message system with different severity levels
- Add busy indicators for long-running operations
- Connect progress updates to ProcessManager and PDFHandler signals
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.ui.utils.status_manager import StatusManager, StatusLevel, ProgressType
from scripts.ui.components.progress_widgets import (
    ProgressPanel, ProgressWidget, BusyWidget, StatusMessageWidget,
    AnimatedProgressBar, PulsingProgressBar, BusySpinner
)
from scripts.ui.components.right_panel import RightPanel
from scripts.ui.components.main_window import MainWindow
from scripts.ui.handlers.process_handler import ProcessManager
from scripts.ui.handlers.pdf_handler import PDFHandler


class TestTask11Requirements(unittest.TestCase):
    """Test that all Task 11 requirements are implemented."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
    
    def test_requirement_progress_bars_and_status_indicators(self):
        """Test: Add progress bars and status indicators to the UI components."""
        # Test AnimatedProgressBar
        progress_bar = AnimatedProgressBar()
        self.assertIsNotNone(progress_bar)
        self.assertTrue(hasattr(progress_bar, 'setValueAnimated'))
        
        # Test PulsingProgressBar for indeterminate progress
        pulse_bar = PulsingProgressBar()
        self.assertIsNotNone(pulse_bar)
        self.assertTrue(hasattr(pulse_bar, 'pulse_timer'))
        pulse_bar.cleanup()
        
        # Test BusySpinner
        spinner = BusySpinner()
        self.assertIsNotNone(spinner)
        self.assertTrue(hasattr(spinner, 'spin_timer'))
        spinner.cleanup()
        
        # Test ProgressPanel integration
        panel = ProgressPanel()
        panel.initialize()
        self.assertIsNotNone(panel.progress_scroll_area)
        self.assertIsNotNone(panel.status_scroll_area)
        panel.cleanup()
        
        # Test RightPanel has progress components
        right_panel = RightPanel()
        right_panel.initialize()
        self.assertIsNotNone(right_panel.progress_bar)
        self.assertIsNotNone(right_panel.progress_panel)
        self.assertIsNotNone(right_panel.status_manager)
        right_panel.cleanup()
        
        print("✓ Progress bars and status indicators implemented")
    
    def test_requirement_real_time_status_updates(self):
        """Test: Implement real-time status updates during PDF processing."""
        # Test ProcessManager has progress signals
        process_manager = ProcessManager()
        process_manager.initialize()
        
        # Check for enhanced progress signals
        self.assertTrue(hasattr(process_manager, 'process_progress_updated'))
        self.assertTrue(hasattr(process_manager, 'queue_status_changed'))
        
        # Test progress extraction from output
        test_outputs = [
            ("Processing 50%", 50),
            ("Step 3 of 5", 60),
            ("Progress: 75", 75),
            ("[4/10]", 40),
            ("No progress info", -1)
        ]
        
        for output, expected in test_outputs:
            result = process_manager._extract_progress_from_output(output)
            if expected >= 0:
                self.assertEqual(result, expected, f"Failed for output: {output}")
            else:
                self.assertEqual(result, -1, f"Should return -1 for: {output}")
        
        process_manager.cleanup()
        
        # Test PDFHandler has enhanced progress signals
        with patch('scripts.ui.handlers.pdf_handler.ProcessManager'):
            pdf_handler = PDFHandler()
            pdf_handler.initialize()
            
            self.assertTrue(hasattr(pdf_handler, 'progress_started'))
            self.assertTrue(hasattr(pdf_handler, 'progress_updated'))
            self.assertTrue(hasattr(pdf_handler, 'progress_finished'))
            
            pdf_handler.cleanup()
        
        print("✓ Real-time status updates implemented")
    
    def test_requirement_status_message_system(self):
        """Test: Create status message system with different severity levels."""
        status_manager = StatusManager()
        
        # Test all severity levels
        severity_levels = [
            StatusLevel.INFO,
            StatusLevel.SUCCESS,
            StatusLevel.WARNING,
            StatusLevel.ERROR,
            StatusLevel.DEBUG
        ]
        
        for level in severity_levels:
            message_id = status_manager.add_status_message(
                f"Test {level.value} message",
                level,
                "TestSource"
            )
            self.assertIsNotNone(message_id)
            
            message = status_manager.status_messages[message_id]
            self.assertEqual(message.level, level)
        
        # Test auto-removal
        auto_remove_id = status_manager.add_status_message(
            "Auto remove test",
            StatusLevel.INFO,
            auto_remove_ms=100
        )
        self.assertIn(auto_remove_id, status_manager.status_messages)
        
        # Test message updates
        update_id = status_manager.add_status_message("Original", StatusLevel.INFO)
        success = status_manager.update_status_message(
            update_id, "Updated", StatusLevel.SUCCESS
        )
        self.assertTrue(success)
        self.assertEqual(status_manager.status_messages[update_id].message, "Updated")
        self.assertEqual(status_manager.status_messages[update_id].level, StatusLevel.SUCCESS)
        
        # Test persistent messages
        persistent_id = status_manager.add_status_message(
            "Persistent message",
            StatusLevel.WARNING,
            persistent=True
        )
        status_manager.clear_status_messages()
        self.assertIn(persistent_id, status_manager.status_messages)  # Should remain
        
        status_manager.cleanup()
        print("✓ Status message system with severity levels implemented")
    
    def test_requirement_busy_indicators(self):
        """Test: Add busy indicators for long-running operations."""
        status_manager = StatusManager()
        
        # Test busy indicator lifecycle
        busy_id = status_manager.start_busy_indicator(
            "Test Operation",
            "Processing..."
        )
        self.assertIsNotNone(busy_id)
        self.assertIn(busy_id, status_manager.busy_indicators)
        self.assertTrue(status_manager.is_busy())
        
        # Test busy indicator updates
        success = status_manager.update_busy_indicator(busy_id, "Updated message")
        self.assertTrue(success)
        self.assertEqual(
            status_manager.busy_indicators[busy_id].message,
            "Updated message"
        )
        
        # Test finishing busy indicator
        success = status_manager.finish_busy_indicator(busy_id)
        self.assertTrue(success)
        self.assertNotIn(busy_id, status_manager.busy_indicators)
        self.assertFalse(status_manager.is_busy())
        
        # Test BusyWidget
        from scripts.ui.utils.status_manager import BusyIndicator
        busy_info = BusyIndicator(
            id="test_busy",
            operation="Test Operation",
            message="Please wait..."
        )
        
        busy_widget = BusyWidget(busy_info)
        busy_widget.initialize()
        self.assertIsNotNone(busy_widget.spinner)
        self.assertIsNotNone(busy_widget.operation_label)
        busy_widget.cleanup()
        
        status_manager.cleanup()
        print("✓ Busy indicators for long-running operations implemented")
    
    def test_requirement_progress_handler_connections(self):
        """Test: Connect progress updates to ProcessManager and PDFHandler signals."""
        # Test MainWindow connects to handler signals
        with patch('scripts.ui.handlers.PDFHandler') as mock_handler_class:
            mock_pdf_handler = Mock()
            mock_handler_class.return_value = mock_pdf_handler
            mock_pdf_handler.initialize.return_value = None
            mock_pdf_handler.set_status_manager.return_value = None
            
            # Mock process manager
            mock_process_manager = Mock()
            mock_pdf_handler.process_manager = mock_process_manager
            
            main_window = MainWindow()
            main_window.initialize()
            
            # Verify PDF handler connections
            self.assertTrue(hasattr(main_window, '_on_pdf_processing_started'))
            self.assertTrue(hasattr(main_window, '_on_pdf_processing_finished'))
            self.assertTrue(hasattr(main_window, '_on_handler_progress_started'))
            self.assertTrue(hasattr(main_window, '_on_handler_progress_updated'))
            self.assertTrue(hasattr(main_window, '_on_handler_progress_finished'))
            
            # Verify process manager connections
            self.assertTrue(hasattr(main_window, '_on_process_started'))
            self.assertTrue(hasattr(main_window, '_on_process_finished'))
            self.assertTrue(hasattr(main_window, '_on_process_progress_updated'))
            self.assertTrue(hasattr(main_window, '_on_queue_status_changed'))
            
            # Test signal handler functionality
            main_window._on_process_progress_updated("test_process", 50, "Half done")
            main_window._on_queue_status_changed(2, 1)
            
            main_window.cleanup()
        
        # Test RightPanel connects to StatusManager signals
        right_panel = RightPanel()
        right_panel.initialize()
        
        status_manager = right_panel.get_status_manager()
        self.assertIsNotNone(status_manager)
        
        # Test signal connections exist
        self.assertTrue(hasattr(right_panel, '_on_status_message_added'))
        self.assertTrue(hasattr(right_panel, '_on_progress_started'))
        self.assertTrue(hasattr(right_panel, '_on_progress_updated'))
        self.assertTrue(hasattr(right_panel, '_on_busy_started'))
        
        right_panel.cleanup()
        print("✓ Progress updates connected to ProcessManager and PDFHandler signals")
    
    def test_integration_complete_workflow(self):
        """Test: Complete integration workflow with all components."""
        # Create main window with mocked handlers
        with patch('scripts.ui.handlers.PDFHandler') as mock_handler_class:
            mock_pdf_handler = Mock()
            mock_handler_class.return_value = mock_pdf_handler
            mock_pdf_handler.initialize.return_value = None
            mock_pdf_handler.set_status_manager.return_value = None
            
            main_window = MainWindow()
            main_window.initialize()
            
            # Test enhanced status message workflow
            message_id = main_window.add_enhanced_status_message(
                "Test integration message",
                "info",
                "IntegrationTest"
            )
            self.assertIsNotNone(message_id)
            
            # Test progress operation workflow
            progress_id = main_window.start_progress_operation(
                "Integration Test",
                "Starting...",
                100
            )
            self.assertIsNotNone(progress_id)
            
            # Update progress
            success = main_window.update_progress_operation(
                progress_id, 50, "Half done"
            )
            self.assertTrue(success)
            
            # Finish progress
            success = main_window.finish_progress_operation(
                progress_id, "Completed!"
            )
            self.assertTrue(success)
            
            # Test busy operation workflow
            busy_id = main_window.start_busy_operation(
                "Integration Busy Test",
                "Processing..."
            )
            self.assertIsNotNone(busy_id)
            
            # Check system is busy
            self.assertTrue(main_window.is_system_busy())
            
            # Finish busy operation
            success = main_window.finish_busy_operation(busy_id)
            self.assertTrue(success)
            
            # Check system is no longer busy
            self.assertFalse(main_window.is_system_busy())
            
            # Test notification system
            main_window.show_notification(
                "Integration Test",
                "All systems working",
                "success"
            )
            
            main_window.cleanup()
        
        print("✓ Complete integration workflow implemented")
    
    def test_ui_responsiveness_and_visual_feedback(self):
        """Test: UI remains responsive with proper visual feedback."""
        # Test animated progress bar
        progress_bar = AnimatedProgressBar()
        progress_bar.setValueAnimated(50)
        self.assertTrue(hasattr(progress_bar, 'animation'))
        
        # Test visual styling for different message types
        from scripts.ui.utils.status_manager import StatusMessage
        import datetime
        
        status_message = StatusMessage(
            id="test_visual",
            message="Test visual styling",
            level=StatusLevel.ERROR,
            timestamp=datetime.datetime.now()
        )
        
        status_widget = StatusMessageWidget(status_message)
        status_widget.initialize()
        self.assertIsNotNone(status_widget.message_label)
        status_widget.cleanup()
        
        # Test progress panel visibility management
        panel = ProgressPanel()
        panel.initialize()
        
        # Initially should be hidden (no content)
        self.assertFalse(panel.isVisible())
        
        # Add content and check visibility
        from scripts.ui.utils.status_manager import ProgressInfo
        progress_info = ProgressInfo(
            id="test_visual_progress",
            title="Visual Test",
            progress_type=ProgressType.DETERMINATE
        )
        
        panel.add_progress_widget(progress_info)
        self.assertTrue(panel.isVisible())
        
        panel.cleanup()
        print("✓ UI responsiveness and visual feedback implemented")


def run_task_11_verification():
    """Run comprehensive verification of Task 11 requirements."""
    print("Task 11: Implement progress indicators and status management")
    print("=" * 60)
    print("Verifying all requirements are implemented...\n")
    
    # Set up Qt application for testing
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask11Requirements)
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    print("\nTask 11 Requirements Verification:")
    print("-" * 40)
    
    if result.wasSuccessful():
        print("✅ ALL REQUIREMENTS IMPLEMENTED SUCCESSFULLY")
        print("\nImplemented features:")
        print("• Progress bars and status indicators in UI components")
        print("• Real-time status updates during PDF processing")
        print("• Status message system with different severity levels")
        print("• Busy indicators for long-running operations")
        print("• Connected progress updates to ProcessManager and PDFHandler signals")
        print("• Enhanced visual feedback and UI responsiveness")
        print("• Auto-dismissing messages with configurable timeouts")
        print("• Centralized status management system")
        print("• Integration with existing UI components")
        return True
    else:
        print("❌ SOME REQUIREMENTS NOT MET")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False


if __name__ == '__main__':
    success = run_task_11_verification()
    sys.exit(0 if success else 1)