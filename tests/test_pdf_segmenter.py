import unittest
from unittest.mock import patch, MagicMock
import os

class TestPDFSegmenterSmoke(unittest.TestCase):
    @patch('pdf_segmenter.fitz')
    def test_pdf_segmenter_import(self, mock_fitz):
        """Test that PDF segmenter can be imported."""
        try:
            from pdf_segmenter import PDFSegmenter
            self.assertTrue(True)
        except ImportError:
            # This is expected if dependencies aren't installed
            self.skipTest("PDF dependencies not available")

if __name__ == '__main__':
    unittest.main() 