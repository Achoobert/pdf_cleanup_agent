"""
Unit tests for PDFDropWidget

Tests drag and drop functionality, file validation, and visual feedback.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QUrl, QMimeData, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QDragLeaveEvent
from PyQt5.QtTest import QTest

from ui.components.pdf_drop_widget import PDFDropWidget


class TestPDFDropWidget(unittest.TestCase):
    """Test cases for PDFDropWidget drag and drop functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """Set up test fixtures."""
        self.widget = PDFDropWidget()
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf_path = os.path.join(self.temp_dir, "test.pdf")
        self.test_non_pdf_path = os.path.join(self.temp_dir, "test.txt")
        
        # Create test files
        self._create_test_pdf()
        self._create_test_non_pdf()
        
        # Mock the PDF directory to use temp directory
        self.original_get_pdf_dir = self.widget._get_pdf_directory
        self.widget._get_pdf_directory = lambda: os.path.join(self.temp_dir, "pdf")
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.widget._get_pdf_directory = self.original_get_pdf_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.widget.deleteLater()
        
    def _create_test_pdf(self):
        """Create a minimal test PDF file."""
        # Create a minimal PDF file (simplified PDF structure)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
229
%%EOF"""
        with open(self.test_pdf_path, 'wb') as f:
            f.write(pdf_content)
            
    def _create_test_non_pdf(self):
        """Create a test non-PDF file."""
        with open(self.test_non_pdf_path, 'w') as f:
            f.write("This is not a PDF file")
            
    def _create_mime_data(self, file_paths):
        """Create QMimeData with file URLs."""
        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(path) for path in file_paths]
        mime_data.setUrls(urls)
        return mime_data
        
    def _create_drag_event(self, mime_data, event_type='enter'):
        """Create a drag event for testing."""
        pos = QPoint(10, 10)
        
        if event_type == 'enter':
            return QDragEnterEvent(pos, Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
        elif event_type == 'move':
            return QDragMoveEvent(pos, Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
        elif event_type == 'drop':
            return QDropEvent(pos, Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)
        elif event_type == 'leave':
            return QDragLeaveEvent()
            
    def test_initialization(self):
        """Test widget initialization."""
        self.assertFalse(self.widget._drag_active)
        self.assertTrue(self.widget.acceptDrops())
        self.assertIsNotNone(self.widget._mime_db)
        
    def test_pdf_file_validation_valid_pdf(self):
        """Test validation of valid PDF file."""
        result = self.widget._is_valid_pdf_file(self.test_pdf_path)
        self.assertTrue(result)
        
    def test_pdf_file_validation_invalid_file(self):
        """Test validation of non-PDF file."""
        result = self.widget._is_valid_pdf_file(self.test_non_pdf_path)
        self.assertFalse(result)
        
    def test_pdf_file_validation_nonexistent_file(self):
        """Test validation of nonexistent file."""
        result = self.widget._is_valid_pdf_file("/nonexistent/file.pdf")
        self.assertFalse(result)
        
    def test_comprehensive_pdf_validation_valid(self):
        """Test comprehensive PDF validation with valid file."""
        result = self.widget._validate_pdf_file(self.test_pdf_path)
        self.assertTrue(result['valid'])
        self.assertEqual(result['reason'], 'Valid PDF file')
        
    def test_comprehensive_pdf_validation_invalid(self):
        """Test comprehensive PDF validation with invalid file."""
        result = self.widget._validate_pdf_file(self.test_non_pdf_path)
        self.assertFalse(result['valid'])
        self.assertEqual(result['reason'], 'Not a valid PDF file')
        
    def test_comprehensive_pdf_validation_empty_path(self):
        """Test comprehensive PDF validation with empty path."""
        result = self.widget._validate_pdf_file("")
        self.assertFalse(result['valid'])
        self.assertEqual(result['reason'], 'Empty file path')
        
    def test_comprehensive_pdf_validation_nonexistent(self):
        """Test comprehensive PDF validation with nonexistent file."""
        result = self.widget._validate_pdf_file("/nonexistent/file.pdf")
        self.assertFalse(result['valid'])
        self.assertEqual(result['reason'], 'File does not exist')
        
    def test_drag_enter_valid_pdf(self):
        """Test drag enter event with valid PDF file."""
        mime_data = self._create_mime_data([self.test_pdf_path])
        event = self._create_drag_event(mime_data, 'enter')
        
        # Mock the event to track if it was accepted
        event.acceptProposedAction = Mock()
        
        self.widget.dragEnterEvent(event)
        
        self.assertTrue(self.widget._drag_active)
        event.acceptProposedAction.assert_called_once()
        
    def test_drag_enter_invalid_file(self):
        """Test drag enter event with invalid file."""
        mime_data = self._create_mime_data([self.test_non_pdf_path])
        event = self._create_drag_event(mime_data, 'enter')
        
        # Mock the event to track if it was ignored
        event.ignore = Mock()
        
        self.widget.dragEnterEvent(event)
        
        self.assertFalse(self.widget._drag_active)
        event.ignore.assert_called_once()
        
    def test_drag_enter_no_urls(self):
        """Test drag enter event with no URLs."""
        mime_data = QMimeData()  # Empty mime data
        event = self._create_drag_event(mime_data, 'enter')
        
        event.ignore = Mock()
        
        self.widget.dragEnterEvent(event)
        
        self.assertFalse(self.widget._drag_active)
        event.ignore.assert_called_once()
        
    def test_drag_move_active(self):
        """Test drag move event when drag is active."""
        # First activate drag
        self.widget._drag_active = True
        
        mime_data = self._create_mime_data([self.test_pdf_path])
        event = self._create_drag_event(mime_data, 'move')
        
        event.acceptProposedAction = Mock()
        
        self.widget.dragMoveEvent(event)
        
        event.acceptProposedAction.assert_called_once()
        
    def test_drag_move_inactive(self):
        """Test drag move event when drag is not active."""
        self.widget._drag_active = False
        
        mime_data = self._create_mime_data([self.test_pdf_path])
        event = self._create_drag_event(mime_data, 'move')
        
        event.ignore = Mock()
        
        self.widget.dragMoveEvent(event)
        
        event.ignore.assert_called_once()
        
    def test_drag_leave(self):
        """Test drag leave event."""
        # First activate drag
        self.widget._drag_active = True
        
        event = self._create_drag_event(None, 'leave')
        
        self.widget.dragLeaveEvent(event)
        
        self.assertFalse(self.widget._drag_active)
        
    def test_drop_event_valid_pdf(self):
        """Test drop event with valid PDF file."""
        mime_data = self._create_mime_data([self.test_pdf_path])
        event = self._create_drag_event(mime_data, 'drop')
        
        # Mock signals
        self.widget.pdf_dropped = Mock()
        self.widget.pdf_preprocess_requested = Mock()
        
        event.acceptProposedAction = Mock()
        
        self.widget.dropEvent(event)
        
        self.assertFalse(self.widget._drag_active)
        event.acceptProposedAction.assert_called_once()
        self.widget.pdf_dropped.emit.assert_called_once()
        self.widget.pdf_preprocess_requested.emit.assert_called_once()
        
    def test_drop_event_invalid_file(self):
        """Test drop event with invalid file."""
        mime_data = self._create_mime_data([self.test_non_pdf_path])
        event = self._create_drag_event(mime_data, 'drop')
        
        # Mock signals
        self.widget.pdf_drop_rejected = Mock()
        
        event.acceptProposedAction = Mock()
        
        self.widget.dropEvent(event)
        
        self.widget.pdf_drop_rejected.emit.assert_called_once()
        
    def test_drop_event_multiple_files(self):
        """Test drop event with multiple files (mixed valid/invalid)."""
        # Create another test PDF
        test_pdf_2 = os.path.join(self.temp_dir, "test2.pdf")
        shutil.copy2(self.test_pdf_path, test_pdf_2)
        
        mime_data = self._create_mime_data([
            self.test_pdf_path, 
            self.test_non_pdf_path, 
            test_pdf_2
        ])
        event = self._create_drag_event(mime_data, 'drop')
        
        # Mock signals
        self.widget.pdf_dropped = Mock()
        self.widget.pdf_drop_rejected = Mock()
        self.widget.pdf_preprocess_requested = Mock()
        
        event.acceptProposedAction = Mock()
        
        self.widget.dropEvent(event)
        
        # Should have 2 successful drops and 1 rejection
        self.assertEqual(self.widget.pdf_dropped.emit.call_count, 2)
        self.assertEqual(self.widget.pdf_drop_rejected.emit.call_count, 1)
        self.assertEqual(self.widget.pdf_preprocess_requested.emit.call_count, 2)
        
    def test_copy_pdf_to_data_dir(self):
        """Test copying PDF to data directory."""
        result_path = self.widget._copy_pdf_to_data_dir(self.test_pdf_path)
        
        self.assertTrue(os.path.exists(result_path))
        self.assertTrue(result_path.endswith("test.pdf"))
        
    def test_copy_pdf_duplicate_handling(self):
        """Test handling of duplicate filenames when copying."""
        # Copy the same file twice
        result_path_1 = self.widget._copy_pdf_to_data_dir(self.test_pdf_path)
        result_path_2 = self.widget._copy_pdf_to_data_dir(self.test_pdf_path)
        
        self.assertTrue(os.path.exists(result_path_1))
        self.assertTrue(os.path.exists(result_path_2))
        self.assertNotEqual(result_path_1, result_path_2)
        self.assertTrue(result_path_2.endswith("test_1.pdf"))
        
    def test_copy_pdf_invalid_source(self):
        """Test copying with invalid source path."""
        with self.assertRaises(ValueError):
            self.widget._copy_pdf_to_data_dir("/nonexistent/file.pdf")
            
    def test_refresh_pdf_list(self):
        """Test refreshing the PDF list."""
        # Copy a PDF to the data directory
        self.widget._copy_pdf_to_data_dir(self.test_pdf_path)
        
        self.widget.refresh_pdf_list()
        
        self.assertEqual(self.widget.count(), 1)
        self.assertEqual(self.widget.item(0).text(), "test.pdf")
        
    def test_get_selected_pdf(self):
        """Test getting selected PDF path."""
        # Copy a PDF and refresh list
        self.widget._copy_pdf_to_data_dir(self.test_pdf_path)
        self.widget.refresh_pdf_list()
        
        # Select the first item
        self.widget.setCurrentRow(0)
        
        selected_path = self.widget.get_selected_pdf()
        self.assertTrue(selected_path.endswith("test.pdf"))
        self.assertTrue(os.path.exists(selected_path))
        
    def test_get_selected_pdf_no_selection(self):
        """Test getting selected PDF when nothing is selected."""
        selected_path = self.widget.get_selected_pdf()
        self.assertEqual(selected_path, "")
        
    def test_add_pdf_programmatically_valid(self):
        """Test adding PDF programmatically with valid file."""
        # Mock signals
        self.widget.pdf_dropped = Mock()
        self.widget.pdf_preprocess_requested = Mock()
        
        result = self.widget.add_pdf_programmatically(self.test_pdf_path)
        
        self.assertTrue(result)
        self.widget.pdf_dropped.emit.assert_called_once()
        self.widget.pdf_preprocess_requested.emit.assert_called_once()
        
    def test_add_pdf_programmatically_invalid(self):
        """Test adding PDF programmatically with invalid file."""
        # Mock signals
        self.widget.pdf_drop_rejected = Mock()
        
        result = self.widget.add_pdf_programmatically(self.test_non_pdf_path)
        
        self.assertFalse(result)
        self.widget.pdf_drop_rejected.emit.assert_called_once()
        
    def test_visual_feedback_properties(self):
        """Test that visual feedback properties are set correctly."""
        # Test drag active state
        self.widget._drag_active = True
        self.widget.setProperty("dragActive", True)
        
        # Check that property is set (actual styling test would require more complex setup)
        self.assertTrue(self.widget.property("dragActive"))
        
        # Test drag inactive state
        self.widget._drag_active = False
        self.widget.setProperty("dragActive", False)
        
        self.assertFalse(self.widget.property("dragActive"))
        
    @patch('os.path.getsize')
    def test_validate_pdf_file_size_limits(self, mock_getsize):
        """Test PDF validation with file size limits."""
        # Test empty file
        mock_getsize.return_value = 0
        result = self.widget._validate_pdf_file(self.test_pdf_path)
        self.assertFalse(result['valid'])
        self.assertEqual(result['reason'], 'File is empty')
        
        # Test file too large
        mock_getsize.return_value = 101 * 1024 * 1024  # 101MB
        result = self.widget._validate_pdf_file(self.test_pdf_path)
        self.assertFalse(result['valid'])
        self.assertEqual(result['reason'], 'File too large (>100MB)')
        
    def test_error_handling_in_drag_events(self):
        """Test error handling in drag events."""
        # Test with None event
        self.widget.dragEnterEvent(None)
        self.assertFalse(self.widget._drag_active)
        
        # Test with event that has no mimeData
        event = Mock()
        event.mimeData.return_value = None
        event.ignore = Mock()
        
        self.widget.dragEnterEvent(event)
        event.ignore.assert_called_once()


if __name__ == '__main__':
    unittest.main()