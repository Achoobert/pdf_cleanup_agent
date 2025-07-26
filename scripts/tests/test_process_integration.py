"""
Integration tests for ProcessManager with real processes.
"""

import unittest
import sys
import os
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtWidgets import QApplication

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.handlers.process_handler import ProcessManager, ProcessState


class TestProcessManagerIntegration(unittest.TestCase):
    """Integration test cases for ProcessManager with real processes."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test case."""
        self.process_manager = ProcessManager()
        
    def tearDown(self):
        """Clean up test case."""
        self.process_manager.cleanup()
        
    def test_real_process_execution(self):
        """Test executing a real process."""
        # Create signal spies
        started_spy = QSignalSpy(self.process_manager.process_started)
        finished_spy = QSignalSpy(self.process_manager.process_finished)
        output_spy = QSignalSpy(self.process_manager.process_output)
        
        # Start a simple echo process
        process_id = "echo_test"
        success = self.process_manager.start_process(process_id, "echo", ["Hello World"])
        
        self.assertTrue(success)
        
        # Wait for process to complete
        timeout = 5000  # 5 seconds
        start_time = time.time()
        
        while len(finished_spy) == 0 and (time.time() - start_time) * 1000 < timeout:
            QTest.qWait(100)
            
        # Check that process completed
        self.assertEqual(len(started_spy), 1)
        self.assertEqual(len(finished_spy), 1)
        self.assertGreater(len(output_spy), 0)
        
        # Check exit code
        self.assertEqual(finished_spy[0][1], 0)  # Exit code should be 0
        
        # Check process info
        process_info = self.process_manager.get_process_info(process_id)
        self.assertIsNotNone(process_info)
        self.assertEqual(process_info.state, ProcessState.FINISHED)
        self.assertEqual(process_info.exit_code, 0)
        
    def test_queue_processing_integration(self):
        """Test queue processing with real processes."""
        # Create signal spies
        started_spy = QSignalSpy(self.process_manager.process_started)
        finished_spy = QSignalSpy(self.process_manager.process_finished)
        queue_empty_spy = QSignalSpy(self.process_manager.queue_empty)
        
        # Queue multiple processes
        process_ids = []
        for i in range(3):
            process_id = self.process_manager.queue_process("echo", [f"Process {i}"])
            process_ids.append(process_id)
            
        # Check that processes are queued
        self.assertEqual(self.process_manager.get_queue_length(), 3)
        
        # Wait for all processes to complete
        timeout = 10000  # 10 seconds
        start_time = time.time()
        
        while len(finished_spy) < 3 and (time.time() - start_time) * 1000 < timeout:
            QTest.qWait(100)
            
        # Wait a bit more for queue_empty signal
        QTest.qWait(200)
            
        # Check that all processes completed
        self.assertEqual(len(started_spy), 3)
        self.assertEqual(len(finished_spy), 3)
        
        # Check that queue is empty
        self.assertEqual(self.process_manager.get_queue_length(), 0)
        
        # Check all process info
        for process_id in process_ids:
            process_info = self.process_manager.get_process_info(process_id)
            self.assertIsNotNone(process_info)
            self.assertEqual(process_info.state, ProcessState.FINISHED)
            self.assertEqual(process_info.exit_code, 0)
            
    def test_process_cancellation_integration(self):
        """Test process cancellation with real processes."""
        # Test cancelling a queued process (this should work reliably)
        process_id = self.process_manager.queue_process("echo", ["test"])
        
        # Verify it's queued
        self.assertEqual(self.process_manager.get_queue_length(), 1)
        
        # Cancel before it starts
        success = self.process_manager.cancel_process(process_id)
        self.assertTrue(success)
        
        # Verify it's removed from queue
        self.assertEqual(self.process_manager.get_queue_length(), 0)
        
        # Check process info
        process_info = self.process_manager.get_process_info(process_id)
        self.assertIsNotNone(process_info)
        self.assertEqual(process_info.state, ProcessState.CANCELLED)
        
    def test_python_executable_integration(self):
        """Test using Python executable to run a script."""
        # Create signal spies
        started_spy = QSignalSpy(self.process_manager.process_started)
        finished_spy = QSignalSpy(self.process_manager.process_finished)
        
        # Get Python executable
        python_exe = self.process_manager.get_python_executable()
        
        # Start a Python process
        process_id = "python_test"
        success = self.process_manager.start_process(
            process_id, 
            python_exe, 
            ["-c", "print('Hello from Python')"]
        )
        
        self.assertTrue(success)
        
        # Wait for process to complete
        timeout = 5000  # 5 seconds
        start_time = time.time()
        
        while len(finished_spy) == 0 and (time.time() - start_time) * 1000 < timeout:
            QTest.qWait(100)
            
        # Check that process completed successfully
        self.assertEqual(len(started_spy), 1)
        self.assertEqual(len(finished_spy), 1)
        self.assertEqual(finished_spy[0][1], 0)  # Exit code should be 0


if __name__ == '__main__':
    unittest.main()