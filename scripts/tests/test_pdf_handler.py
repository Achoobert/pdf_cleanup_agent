"""
Unit tests for PDF Handler

Tests the PDF processing workflow and state management.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtCore import QObject
from PyQt5.QtTest import QTest

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.ui.handlers.pdf_handler import PDFHandler, ProcessingState
from scripts.ui.handlers.process_handler import ProcessManager


class TestProcessingState(unittest.TestCase):
    """Test the ProcessingState dataclass."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = ProcessingState()
        
    def test_initial_state(self):
        """Test initial state values."""
        self.assertIsNone(self.state.current_pdf)
        self.assertEqual(len(self.state.processing_queue), 0)
        self.assertEqual(len(self.state.active_processes), 0)
        self.assertIsNone(self.state.last_output_path)
        self.assertEqual(len(self.state.processing_history), 0)
        self.assertEqual(len(self.state.failed_pdfs), 0)
        
    def test_add_to_queue(self):
        """Test adding PDFs to processing queue."""
        pdf_path = "/test/path/test.pdf"
        self.state.add_to_queue(pdf_path)
        
        self.assertIn(pdf_path, self.state.processing_queue)
        self.assertEqual(len(self.state.processing_queue), 1)
        
        # Adding same PDF again should not duplicate
        self.state.add_to_queue(pdf_path)
        self.assertEqual(len(self.state.processing_queue), 1)
        
    def test_remove_from_queue(self):
        """Test removing PDFs from processing queue."""
        pdf_path = "/test/path/test.pdf"
        self.state.add_to_queue(pdf_path)
        self.state.remove_from_queue(pdf_path)
        
        self.assertNotIn(pdf_path, self.state.processing_queue)
        self.assertEqual(len(self.state.processing_queue), 0)
        
    def test_start_processing(self):
        """Test starting processing for a PDF."""
        pdf_path = "/test/path/test.pdf"
        process_id = "test_process_1"
        
        self.state.add_to_queue(pdf_path)
        self.state.start_processing(pdf_path, process_id)
        
        self.assertEqual(self.state.current_pdf, pdf_path)
        self.assertIn(process_id, self.state.active_processes)
        self.assertEqual(self.state.active_processes[process_id], pdf_path)
        self.assertNotIn(pdf_path, self.state.processing_queue)
        
    def test_finish_processing_success(self):
        """Test finishing processing successfully."""
        pdf_path = "/test/path/test.pdf"
        process_id = "test_process_1"
        output_path = "/test/output/test"
        
        self.state.start_processing(pdf_path, process_id)
        self.state.finish_processing(process_id, True, output_path)
        
        self.assertNotIn(process_id, self.state.active_processes)
        self.assertEqual(self.state.last_output_path, output_path)
        self.assertEqual(len(self.state.processing_history), 1)
        self.assertNotIn(pdf_path, self.state.failed_pdfs)
        
        history_entry = self.state.processing_history[0]
        self.assertEqual(history_entry['pdf_path'], pdf_path)
        self.assertEqual(history_entry['process_id'], process_id)
        self.assertTrue(history_entry['success'])
        self.assertEqual(history_entry['output_path'], output_path)
        
    def test_finish_processing_failure(self):
        """Test finishing processing with failure."""
        pdf_path = "/test/path/test.pdf"
        process_id = "test_process_1"
        
        self.state.start_processing(pdf_path, process_id)
        self.state.finish_processing(process_id, False)
        
        self.assertNotIn(process_id, self.state.active_processes)
        self.assertIn(pdf_path, self.state.failed_pdfs)
        self.assertEqual(len(self.state.processing_history), 1)
        
        history_entry = self.state.processing_history[0]
        self.assertFalse(history_entry['success'])
        self.assertIsNone(history_entry['output_path'])
        
    def test_is_processing(self):
        """Test checking if a PDF is being processed."""
        pdf_path = "/test/path/test.pdf"
        process_id = "test_process_1"
        
        self.assertFalse(self.state.is_processing(pdf_path))
        
        self.state.start_processing(pdf_path, process_id)
        self.assertTrue(self.state.is_processing(pdf_path))
        
        self.state.finish_processing(process_id, True)
        self.assertFalse(self.state.is_processing(pdf_path))
        
    def test_get_queue_position(self):
        """Test getting queue position for a PDF."""
        pdf1 = "/test/path/test1.pdf"
        pdf2 = "/test/path/test2.pdf"
        pdf3 = "/test/path/test3.pdf"
        
        self.state.add_to_queue(pdf1)
        self.state.add_to_queue(pdf2)
        self.state.add_to_queue(pdf3)
        
        self.assertEqual(self.state.get_queue_position(pdf1), 0)
        self.assertEqual(self.state.get_queue_position(pdf2), 1)
        self.assertEqual(self.state.get_queue_position(pdf3), 2)
        self.assertEqual(self.state.get_queue_position("/nonexistent.pdf"), -1)
        
    def test_clear_failed(self):
        """Test clearing failed PDFs list."""
        pdf_path = "/test/path/test.pdf"
        process_id = "test_process_1"
        
        self.state.start_processing(pdf_path, process_id)
        self.state.finish_processing(process_id, False)
        
        self.assertIn(pdf_path, self.state.failed_pdfs)
        
        self.state.clear_failed()
        self.assertEqual(len(self.state.failed_pdfs), 0)


class TestPDFHandler(unittest.TestCase):
    """Test the PDFHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create PDF handler with mocked process manager
        with patch('scripts.ui.handlers.pdf_handler.ProcessManager') as mock_pm_class:
            self.mock_process_manager = Mock(spec=ProcessManager)
            mock_pm_class.return_value = self.mock_process_manager
            
            self.pdf_handler = PDFHandler()
            
            # Configure mock methods
            self.mock_process_manager.initialize.return_value = None
            self.mock_process_manager.get_python_executable.return_value = "python"
            self.mock_process_manager.start_process.return_value = True
            self.mock_process_manager.stop_process.return_value = True
            self.mock_process_manager.stop_all_processes.return_value = None
            
            # Initialize the handler
            self.pdf_handler.initialize()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.pdf_handler.cleanup()
        
    def test_initialization(self):
        """Test PDF handler initialization."""
        self.assertTrue(self.pdf_handler.is_initialized)
        self.assertIsNotNone(self.pdf_handler.processing_state)
        self.assertIsNotNone(self.pdf_handler.process_manager)
        
    def test_validate_pdf_file_valid(self):
        """Test PDF file validation with valid file."""
        # Create a temporary PDF file
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
            
        result = self.pdf_handler._validate_pdf_file(pdf_path)
        self.assertTrue(result)
        
    def test_validate_pdf_file_invalid_extension(self):
        """Test PDF file validation with invalid extension."""
        # Create a temporary non-PDF file
        txt_path = os.path.join(self.temp_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("dummy content")
            
        result = self.pdf_handler._validate_pdf_file(txt_path)
        self.assertFalse(result)
        
    def test_validate_pdf_file_nonexistent(self):
        """Test PDF file validation with nonexistent file."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.pdf")
        
        result = self.pdf_handler._validate_pdf_file(nonexistent_path)
        self.assertFalse(result)
        
    @patch('scripts.ui.handlers.pdf_handler.os.makedirs')
    @patch('scripts.ui.handlers.pdf_handler.shutil.copy2')
    def test_copy_pdf_to_data_dir_success(self, mock_copy, mock_makedirs):
        """Test successful PDF copying to data directory."""
        # Create source PDF
        source_path = os.path.join(self.temp_dir, "source.pdf")
        with open(source_path, 'w') as f:
            f.write("dummy pdf content")
            
        # Mock the copy operation
        mock_copy.return_value = None
        
        with patch.object(self.pdf_handler, '_get_pdf_directory', return_value=self.temp_dir):
            # Mock os.path.exists to return False so no duplicate handling occurs
            with patch('scripts.ui.handlers.pdf_handler.os.path.exists', return_value=False):
                result = self.pdf_handler._copy_pdf_to_data_dir(source_path)
            
        expected_dest = os.path.join(self.temp_dir, "source.pdf")
        self.assertEqual(result, expected_dest)
        mock_copy.assert_called_once_with(source_path, expected_dest)
        
    @patch('scripts.ui.handlers.pdf_handler.shutil.copy2')
    def test_copy_pdf_to_data_dir_failure(self, mock_copy):
        """Test PDF copying failure."""
        source_path = os.path.join(self.temp_dir, "source.pdf")
        with open(source_path, 'w') as f:
            f.write("dummy pdf content")
            
        # Mock copy failure
        mock_copy.side_effect = Exception("Copy failed")
        
        with patch.object(self.pdf_handler, '_get_pdf_directory', return_value=self.temp_dir):
            result = self.pdf_handler._copy_pdf_to_data_dir(source_path)
            
        self.assertIsNone(result)
        
    def test_handle_pdf_drop_success(self):
        """Test successful PDF drop handling."""
        # Create source PDF
        source_path = os.path.join(self.temp_dir, "test.pdf")
        with open(source_path, 'w') as f:
            f.write("dummy pdf content")
            
        # Mock the copy operation
        with patch.object(self.pdf_handler, '_copy_pdf_to_data_dir') as mock_copy:
            mock_copy.return_value = os.path.join(self.temp_dir, "test.pdf")
            
            with patch.object(self.pdf_handler, '_start_pdf_segmentation') as mock_segment:
                mock_segment.return_value = True
                
                result = self.pdf_handler.handle_pdf_drop(source_path)
                
        self.assertTrue(result)
        mock_copy.assert_called_once_with(source_path)
        mock_segment.assert_called_once()
        
    def test_handle_pdf_drop_invalid_file(self):
        """Test PDF drop handling with invalid file."""
        invalid_path = os.path.join(self.temp_dir, "test.txt")
        with open(invalid_path, 'w') as f:
            f.write("dummy content")
            
        result = self.pdf_handler.handle_pdf_drop(invalid_path)
        self.assertFalse(result)
        
    def test_start_pdf_segmentation(self):
        """Test starting PDF segmentation."""
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        
        with patch.object(self.pdf_handler, '_get_segmenter_script_path') as mock_script:
            mock_script.return_value = "/path/to/segmenter.py"
            
            with patch.object(self.pdf_handler, '_get_txt_output_directory') as mock_dir:
                mock_dir.return_value = "/path/to/txt"
                
                result = self.pdf_handler._start_pdf_segmentation(pdf_path)
                
        self.assertTrue(result)
        self.mock_process_manager.start_process.assert_called_once()
        
        # Check that PDF was added to processing state
        process_id = f"pdf_segment_{os.path.basename(pdf_path)}"
        self.assertIn(process_id, self.pdf_handler.processing_state.active_processes)
        
    def test_start_full_processing(self):
        """Test starting full processing pipeline."""
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
            
        with patch.object(self.pdf_handler, '_start_processing_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            result = self.pdf_handler.start_full_processing(pdf_path)
            
        self.assertTrue(result)
        mock_pipeline.assert_called_once_with(pdf_path)
        self.assertIn(pdf_path, self.pdf_handler.processing_state.processing_queue)
        
    def test_cancel_processing(self):
        """Test cancelling processing for a specific PDF."""
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        process_id = f"pdf_segment_{os.path.basename(pdf_path)}"
        
        # Add to processing state
        self.pdf_handler.processing_state.start_processing(pdf_path, process_id)
        
        result = self.pdf_handler.cancel_processing(pdf_path)
        
        self.assertTrue(result)
        self.mock_process_manager.stop_process.assert_called_once_with(process_id, force=True)
        
    def test_cancel_all_processing(self):
        """Test cancelling all processing."""
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        self.pdf_handler.processing_state.add_to_queue(pdf_path)
        
        result = self.pdf_handler.cancel_all_processing()
        
        self.assertTrue(result)
        self.mock_process_manager.stop_all_processes.assert_called_once()
        self.assertEqual(len(self.pdf_handler.processing_state.processing_queue), 0)
        self.assertEqual(len(self.pdf_handler.processing_state.active_processes), 0)
        self.assertIsNone(self.pdf_handler.processing_state.current_pdf)
        
    def test_get_processing_state(self):
        """Test getting processing state."""
        state = self.pdf_handler.get_processing_state()
        self.assertIsInstance(state, ProcessingState)
        self.assertEqual(state, self.pdf_handler.processing_state)
        
    @patch('scripts.ui.handlers.pdf_handler.os.path.exists')
    @patch('scripts.ui.handlers.pdf_handler.os.listdir')
    def test_get_pdf_list(self, mock_listdir, mock_exists):
        """Test getting list of PDF files."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['test1.pdf', 'test2.PDF', 'test.txt', 'test3.pdf']
        
        with patch.object(self.pdf_handler, '_get_pdf_directory') as mock_dir:
            mock_dir.return_value = "/test/pdf/dir"
            
            pdf_list = self.pdf_handler.get_pdf_list()
            
        expected_pdfs = [
            "/test/pdf/dir/test1.pdf",
            "/test/pdf/dir/test2.PDF", 
            "/test/pdf/dir/test3.pdf"
        ]
        self.assertEqual(len(pdf_list), 3)
        for pdf in expected_pdfs:
            self.assertIn(pdf, pdf_list)
            
    @patch('scripts.ui.handlers.pdf_handler.os.path.exists')
    @patch('scripts.ui.handlers.pdf_handler.os.listdir')
    def test_is_pdf_processed(self, mock_listdir, mock_exists):
        """Test checking if PDF has been processed."""
        pdf_path = "/test/path/test.pdf"
        
        # Test when processed (directory exists and has files)
        mock_exists.return_value = True
        mock_listdir.return_value = ['test.md']
        
        result = self.pdf_handler.is_pdf_processed(pdf_path)
        self.assertTrue(result)
        
        # Test when not processed (directory doesn't exist)
        mock_exists.return_value = False
        
        result = self.pdf_handler.is_pdf_processed(pdf_path)
        self.assertFalse(result)
        
        # Test when directory exists but is empty
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        result = self.pdf_handler.is_pdf_processed(pdf_path)
        self.assertFalse(result)
        
    def test_retry_failed_pdf(self):
        """Test retrying a failed PDF."""
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        with open(pdf_path, 'w') as f:
            f.write("dummy pdf content")
            
        # Add to failed list
        self.pdf_handler.processing_state.failed_pdfs.append(pdf_path)
        
        with patch.object(self.pdf_handler, 'start_full_processing') as mock_start:
            mock_start.return_value = True
            
            result = self.pdf_handler.retry_failed_pdf(pdf_path)
            
        self.assertTrue(result)
        self.assertNotIn(pdf_path, self.pdf_handler.processing_state.failed_pdfs)
        mock_start.assert_called_once_with(pdf_path)


if __name__ == '__main__':
    # Set up Qt application for testing
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Run tests
    unittest.main()