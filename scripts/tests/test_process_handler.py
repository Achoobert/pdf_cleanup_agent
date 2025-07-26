"""
Unit tests for ProcessManager class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from PyQt5.QtCore import QProcess, QTimer
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QApplication

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.handlers.process_handler import ProcessManager, ProcessState, ProcessInfo


class TestProcessManager(unittest.TestCase):
    """Test cases for ProcessManager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test case."""
        self.process_manager = ProcessManager(auto_process_queue=False)
        
    def tearDown(self):
        """Clean up test case."""
        self.process_manager.cleanup()
        
    def test_initialization(self):
        """Test ProcessManager initialization."""
        self.assertEqual(len(self.process_manager.active_processes), 0)
        self.assertEqual(len(self.process_manager.process_queue), 0)
        self.assertEqual(len(self.process_manager.process_info), 0)
        self.assertEqual(self.process_manager.max_concurrent_processes, 1)
        self.assertIsInstance(self.process_manager.queue_timer, QTimer)
        
    def test_queue_process(self):
        """Test process queuing."""
        # Test queuing a process
        process_id = self.process_manager.queue_process("echo", ["test"])
        
        self.assertIsNotNone(process_id)
        self.assertEqual(len(self.process_manager.process_queue), 1)
        self.assertIn(process_id, self.process_manager.process_info)
        self.assertEqual(self.process_manager.process_info[process_id].state, ProcessState.QUEUED)
        
    def test_queue_process_with_custom_id(self):
        """Test queuing a process with custom ID."""
        custom_id = "test_process_123"
        process_id = self.process_manager.queue_process("echo", ["test"], process_id=custom_id)
        
        self.assertEqual(process_id, custom_id)
        self.assertIn(custom_id, self.process_manager.process_info)
        
    @patch('ui.handlers.process_handler.QProcess')
    def test_start_process_success(self, mock_qprocess_class):
        """Test successful process start."""
        # Mock QProcess instance
        mock_process = Mock()
        mock_process.waitForStarted.return_value = True
        mock_qprocess_class.return_value = mock_process
        
        # Start process
        success = self.process_manager.start_process("test_id", "echo", ["test"])
        
        self.assertTrue(success)
        self.assertIn("test_id", self.process_manager.active_processes)
        self.assertIn("test_id", self.process_manager.process_info)
        self.assertEqual(self.process_manager.process_info["test_id"].state, ProcessState.RUNNING)
        
    @patch('ui.handlers.process_handler.QProcess')
    def test_start_process_failure(self, mock_qprocess_class):
        """Test process start failure."""
        # Mock QProcess instance
        mock_process = Mock()
        mock_process.waitForStarted.return_value = False
        mock_qprocess_class.return_value = mock_process
        
        # Start process
        success = self.process_manager.start_process("test_id", "echo", ["test"])
        
        self.assertFalse(success)
        self.assertNotIn("test_id", self.process_manager.active_processes)
        
    def test_start_process_duplicate_id(self):
        """Test starting process with duplicate ID."""
        # Add a mock process to active processes
        mock_process = Mock()
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Try to start another process with same ID
        success = self.process_manager.start_process("test_id", "echo", ["test"])
        
        self.assertFalse(success)
        
    def test_max_concurrent_processes(self):
        """Test maximum concurrent processes limit."""
        # Set max to 1
        self.process_manager.max_concurrent_processes = 1
        
        # Add a mock process to active processes
        mock_process = Mock()
        self.process_manager.active_processes["existing"] = mock_process
        
        # Try to start another process
        success = self.process_manager.start_process("test_id", "echo", ["test"])
        
        self.assertFalse(success)
        
    def test_cancel_queued_process(self):
        """Test cancelling a queued process."""
        # Queue a process
        process_id = self.process_manager.queue_process("echo", ["test"])
        
        # Cancel it
        success = self.process_manager.cancel_process(process_id)
        
        self.assertTrue(success)
        self.assertEqual(len(self.process_manager.process_queue), 0)
        self.assertEqual(self.process_manager.process_info[process_id].state, ProcessState.CANCELLED)
        
    def test_cancel_running_process(self):
        """Test cancelling a running process."""
        # Add a mock process to active processes
        mock_process = Mock()
        mock_process.terminate.return_value = None
        mock_process.waitForFinished.return_value = True
        self.process_manager.active_processes["test_id"] = mock_process
        self.process_manager.process_info["test_id"] = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.RUNNING
        )
        
        # Cancel it
        success = self.process_manager.cancel_process("test_id")
        
        self.assertTrue(success)
        mock_process.terminate.assert_called_once()
        
    def test_stop_process(self):
        """Test stopping a process."""
        # Add a mock process to active processes
        mock_process = Mock()
        mock_process.terminate.return_value = None
        mock_process.waitForFinished.return_value = True
        self.process_manager.active_processes["test_id"] = mock_process
        self.process_manager.process_info["test_id"] = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.RUNNING
        )
        
        # Stop it
        success = self.process_manager.stop_process("test_id")
        
        self.assertTrue(success)
        mock_process.terminate.assert_called_once()
        self.assertEqual(self.process_manager.process_info["test_id"].state, ProcessState.CANCELLED)
        
    def test_stop_process_force(self):
        """Test force stopping a process."""
        # Add a mock process to active processes
        mock_process = Mock()
        mock_process.kill.return_value = None
        self.process_manager.active_processes["test_id"] = mock_process
        self.process_manager.process_info["test_id"] = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.RUNNING
        )
        
        # Force stop it
        success = self.process_manager.stop_process("test_id", force=True)
        
        self.assertTrue(success)
        mock_process.kill.assert_called_once()
        
    def test_stop_all_processes(self):
        """Test stopping all processes."""
        # Add mock processes
        mock_process1 = Mock()
        mock_process1.terminate.return_value = None
        mock_process1.waitForFinished.return_value = True
        mock_process1.kill.return_value = None
        
        mock_process2 = Mock()
        mock_process2.terminate.return_value = None
        mock_process2.waitForFinished.return_value = True
        mock_process2.kill.return_value = None
        
        self.process_manager.active_processes["test1"] = mock_process1
        self.process_manager.active_processes["test2"] = mock_process2
        
        # Add queued process
        self.process_manager.queue_process("echo", ["test"])
        
        # Stop all
        self.process_manager.stop_all_processes()
        
        self.assertEqual(len(self.process_manager.process_queue), 0)
        mock_process1.kill.assert_called_once()
        mock_process2.kill.assert_called_once()
        
    def test_get_process_info(self):
        """Test getting process information."""
        # Add process info
        process_info = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.QUEUED
        )
        self.process_manager.process_info["test_id"] = process_info
        
        # Get info
        retrieved_info = self.process_manager.get_process_info("test_id")
        
        self.assertEqual(retrieved_info, process_info)
        
        # Test non-existent process
        non_existent = self.process_manager.get_process_info("non_existent")
        self.assertIsNone(non_existent)
        
    def test_get_all_process_info(self):
        """Test getting all process information."""
        # Add process info
        process_info = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.QUEUED
        )
        self.process_manager.process_info["test_id"] = process_info
        
        # Get all info
        all_info = self.process_manager.get_all_process_info()
        
        self.assertEqual(len(all_info), 1)
        self.assertIn("test_id", all_info)
        self.assertEqual(all_info["test_id"], process_info)
        
    def test_get_queue_length(self):
        """Test getting queue length."""
        self.assertEqual(self.process_manager.get_queue_length(), 0)
        
        # Add processes to queue
        self.process_manager.queue_process("echo", ["test1"])
        self.process_manager.queue_process("echo", ["test2"])
        
        self.assertEqual(self.process_manager.get_queue_length(), 2)
        
    def test_get_active_process_count(self):
        """Test getting active process count."""
        self.assertEqual(self.process_manager.get_active_process_count(), 0)
        
        # Add mock processes
        mock_process = Mock()
        self.process_manager.active_processes["test1"] = mock_process
        self.process_manager.active_processes["test2"] = mock_process
        
        self.assertEqual(self.process_manager.get_active_process_count(), 2)
        
    def test_is_process_running(self):
        """Test checking if process is running."""
        # Test non-existent process
        self.assertFalse(self.process_manager.is_process_running("non_existent"))
        
        # Add mock process
        mock_process = Mock()
        mock_process.state.return_value = QProcess.Running
        self.process_manager.active_processes["test_id"] = mock_process
        
        self.assertTrue(self.process_manager.is_process_running("test_id"))
        
        # Test not running process
        mock_process.state.return_value = QProcess.NotRunning
        self.assertFalse(self.process_manager.is_process_running("test_id"))
        
    def test_clear_completed_processes(self):
        """Test clearing completed processes."""
        # Add completed process info
        completed_info = ProcessInfo(
            process_id="completed",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.FINISHED
        )
        
        running_info = ProcessInfo(
            process_id="running",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.RUNNING
        )
        
        self.process_manager.process_info["completed"] = completed_info
        self.process_manager.process_info["running"] = running_info
        
        # Add running process to active processes
        mock_process = Mock()
        self.process_manager.active_processes["running"] = mock_process
        
        # Clear completed
        self.process_manager.clear_completed_processes()
        
        self.assertNotIn("completed", self.process_manager.process_info)
        self.assertIn("running", self.process_manager.process_info)
        
    def test_handle_stdout(self):
        """Test handling stdout."""
        # Create signal spy
        spy = QSignalSpy(self.process_manager.process_output)
        
        # Add mock process
        mock_process = Mock()
        mock_output = Mock()
        mock_output.data.return_value = b"test output\nline 2\n"
        mock_process.readAllStandardOutput.return_value = mock_output
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Handle stdout
        self.process_manager._handle_stdout("test_id")
        
        # Check signal was emitted
        self.assertEqual(len(spy), 2)  # Two lines of output
        
    def test_handle_stderr(self):
        """Test handling stderr."""
        # Create signal spy
        spy = QSignalSpy(self.process_manager.process_error)
        
        # Add mock process
        mock_process = Mock()
        mock_error = Mock()
        mock_error.data.return_value = b"error message\n"
        mock_process.readAllStandardError.return_value = mock_error
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Handle stderr
        self.process_manager._handle_stderr("test_id")
        
        # Check signal was emitted
        self.assertEqual(len(spy), 1)
        
    def test_handle_finished_success(self):
        """Test handling successful process completion."""
        # Create signal spy
        spy = QSignalSpy(self.process_manager.process_finished)
        
        # Add process info
        process_info = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.RUNNING
        )
        self.process_manager.process_info["test_id"] = process_info
        
        # Add mock process
        mock_process = Mock()
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Handle finished
        self.process_manager._handle_finished("test_id", 0)
        
        # Check signal was emitted
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], "test_id")
        self.assertEqual(spy[0][1], 0)
        
        # Check process info updated
        self.assertEqual(self.process_manager.process_info["test_id"].state, ProcessState.FINISHED)
        self.assertEqual(self.process_manager.process_info["test_id"].exit_code, 0)
        
    def test_handle_finished_failure(self):
        """Test handling failed process completion."""
        # Add process info
        process_info = ProcessInfo(
            process_id="test_id",
            command="echo",
            args=["test"],
            working_dir=None,
            state=ProcessState.RUNNING
        )
        self.process_manager.process_info["test_id"] = process_info
        
        # Add mock process
        mock_process = Mock()
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Handle finished with error
        self.process_manager._handle_finished("test_id", 1)
        
        # Check process info updated
        self.assertEqual(self.process_manager.process_info["test_id"].state, ProcessState.FAILED)
        self.assertEqual(self.process_manager.process_info["test_id"].exit_code, 1)
        
    def test_cleanup_process(self):
        """Test process cleanup."""
        # Add mock process
        mock_process = Mock()
        mock_process.readyReadStandardOutput.disconnect.return_value = None
        mock_process.readyReadStandardError.disconnect.return_value = None
        mock_process.finished.disconnect.return_value = None
        mock_process.deleteLater.return_value = None
        
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Cleanup
        self.process_manager._cleanup_process("test_id")
        
        # Check process was removed and cleaned up
        self.assertNotIn("test_id", self.process_manager.active_processes)
        mock_process.deleteLater.assert_called_once()
        
    def test_get_python_executable(self):
        """Test getting Python executable."""
        executable = self.process_manager.get_python_executable()
        self.assertIsInstance(executable, str)
        self.assertTrue(len(executable) > 0)
        
    def test_queue_processing_with_auto_enabled(self):
        """Test automatic queue processing."""
        # Create process manager with auto processing enabled
        auto_manager = ProcessManager(auto_process_queue=True)
        
        try:
            # Mock the start_process method to avoid actual process execution
            with patch.object(auto_manager, 'start_process', return_value=True) as mock_start:
                # Queue a process
                process_id = auto_manager.queue_process("echo", ["test"])
                
                # Give some time for the timer to trigger
                QTest.qWait(200)
                
                # Check that start_process was called
                mock_start.assert_called_once()
                
        finally:
            auto_manager.cleanup()
            
    def test_process_info_timestamps(self):
        """Test that process info includes timestamps."""
        # Mock time function
        with patch('time.time', return_value=1234567890.0):
            # Add process info
            process_info = ProcessInfo(
                process_id="test_id",
                command="echo",
                args=["test"],
                working_dir=None,
                state=ProcessState.RUNNING
            )
            self.process_manager.process_info["test_id"] = process_info
            
            # Mock process
            mock_process = Mock()
            self.process_manager.active_processes["test_id"] = mock_process
            
            # Handle finished
            self.process_manager._handle_finished("test_id", 0)
            
            # Check timestamps were set
            self.assertIsNotNone(self.process_manager.process_info["test_id"].end_time)
            self.assertEqual(self.process_manager.process_info["test_id"].end_time, 1234567890.0)
            
    def test_process_states(self):
        """Test all process states are handled correctly."""
        states = [ProcessState.QUEUED, ProcessState.RUNNING, ProcessState.FINISHED, 
                 ProcessState.FAILED, ProcessState.CANCELLED]
        
        for state in states:
            self.assertIsInstance(state.value, str)
            
    def test_empty_queue_signal(self):
        """Test queue empty signal emission."""
        # Create signal spy
        spy = QSignalSpy(self.process_manager.queue_empty)
        
        # Process empty queue
        self.process_manager._process_queue()
        
        # Check signal was emitted
        self.assertEqual(len(spy), 1)
        
    def test_process_output_line_splitting(self):
        """Test that multi-line output is split correctly."""
        # Create signal spy
        spy = QSignalSpy(self.process_manager.process_output)
        
        # Add mock process with multi-line output
        mock_process = Mock()
        mock_output = Mock()
        mock_output.data.return_value = b"line 1\nline 2\nline 3\n"
        mock_process.readAllStandardOutput.return_value = mock_output
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Handle stdout
        self.process_manager._handle_stdout("test_id")
        
        # Check that 3 signals were emitted (one for each line)
        self.assertEqual(len(spy), 3)
        
    def test_process_error_line_splitting(self):
        """Test that multi-line error output is split correctly."""
        # Create signal spy
        spy = QSignalSpy(self.process_manager.process_error)
        
        # Add mock process with multi-line error
        mock_process = Mock()
        mock_error = Mock()
        mock_error.data.return_value = b"error 1\nerror 2\n"
        mock_process.readAllStandardError.return_value = mock_error
        self.process_manager.active_processes["test_id"] = mock_process
        
        # Handle stderr
        self.process_manager._handle_stderr("test_id")
        
        # Check that 2 signals were emitted (one for each line)
        self.assertEqual(len(spy), 2)


if __name__ == '__main__':
    unittest.main()