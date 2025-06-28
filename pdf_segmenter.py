#!/usr/bin/env python3
"""
PDF Segmentation Tool
Extracts table of contents and splits PDF into sections for RPG rulebooks.
Uses PyMuPDF for maximum portability.
"""

import os
import re
import fitz  # PyMuPDF
from pathlib import Path
import argparse


class PDFSegmenter:
    def __init__(self, pdf_path, output_dir="data/txt_input"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.doc = None
        self.toc = []
        
        # Get PDF name for subdirectory
        self.pdf_name = Path(pdf_path).stem
        
        # Create output subdirectory
        self.output_subdir = os.path.join(output_dir, self.pdf_name)
        os.makedirs(self.output_subdir, exist_ok=True)
    
    def open_pdf(self):
        """Open the PDF file."""
        try:
            self.doc = fitz.open(self.pdf_path)
            print(f"✅ Opened PDF: {self.pdf_path}")
            print(f"📄 Total pages: {len(self.doc)}")
            return True
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            return False
    
    def extract_toc(self):
        """Extract table of contents from PDF."""
        try:
            self.toc = self.doc.get_toc()
            print(f"📋 Found {len(self.toc)} TOC entries")
            
            if not self.toc:
                print("⚠️  No TOC found, will use page-based segmentation")
                return False
            
            print("\n📖 Table of Contents:")
            for level, title, page in self.toc:
                indent = "  " * (level - 1)
                print(f"{indent}• {title} (page {page})")
            
            return True
        except Exception as e:
            print(f"❌ Error extracting TOC: {e}")
            return False
    
    def clean_filename(self, title):
        """Clean title for use as filename."""
        # Remove special characters and replace spaces with underscores
        clean = re.sub(r'[^\w\s-]', '', title)
        clean = re.sub(r'[-\s]+', '_', clean)
        clean = clean.lower().strip('_')
        return clean
    
    def extract_text_from_page(self, page_num):
        """Extract text from a specific page using PyMuPDF."""
        try:
            page = self.doc[page_num]
            text = page.get_text()
            return text.strip()
        except Exception as e:
            print(f"❌ Error extracting text from page {page_num + 1}: {e}")
            return ""
    
    def segment_by_toc(self):
        """Segment PDF based on table of contents."""
        if not self.toc:
            print("❌ No TOC available for segmentation")
            return False
        
        print(f"\n🔄 Segmenting PDF into {len(self.toc)} sections...")
        print(f"📁 Output directory: {self.output_subdir}")
        
        for i, (level, title, page) in enumerate(self.toc):
            # Determine end page (next TOC entry or end of document)
            end_page = len(self.doc) - 1
            if i + 1 < len(self.toc):
                end_page = self.toc[i + 1][2] - 1
            
            print(f"\n📝 Processing: {title} (pages {page}-{end_page})")
            
            # Extract text from page range
            section_text = ""
            for page_num in range(page - 1, min(end_page + 1, len(self.doc))):
                page_text = self.extract_text_from_page(page_num)
                if page_text:
                    section_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
            
            if section_text.strip():
                # Create filename
                clean_title = self.clean_filename(title)
                filename = f"{clean_title}.txt"
                filepath = os.path.join(self.output_subdir, filename)
                
                # Save section
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n")
                    f.write(section_text)
                
                print(f"✅ Saved: {self.pdf_name}/{filename}")
            else:
                print(f"⚠️  No text extracted for: {title}")
        
        return True
    
    def segment_by_pages(self, pages_per_section=10):
        """Segment PDF by page ranges when no TOC is available."""
        print(f"\n🔄 Segmenting PDF by pages ({pages_per_section} pages per section)...")
        print(f"📁 Output directory: {self.output_subdir}")
        
        total_pages = len(self.doc)
        
        for start_page in range(0, total_pages, pages_per_section):
            end_page = min(start_page + pages_per_section - 1, total_pages - 1)
            
            print(f"\n📝 Processing pages {start_page + 1}-{end_page + 1}")
            
            # Extract text from page range
            section_text = ""
            for page_num in range(start_page, end_page + 1):
                page_text = self.extract_text_from_page(page_num)
                if page_text:
                    section_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
            
            if section_text.strip():
                # Create filename
                filename = f"pages_{start_page + 1:03d}-{end_page + 1:03d}.txt"
                filepath = os.path.join(self.output_subdir, filename)
                
                # Save section
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Pages {start_page + 1}-{end_page + 1}\n\n")
                    f.write(section_text)
                
                print(f"✅ Saved: {self.pdf_name}/{filename}")
            else:
                print(f"⚠️  No text extracted for pages {start_page + 1}-{end_page + 1}")
        
        return True
    
    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()


def main():
    parser = argparse.ArgumentParser(description="Segment PDF into text sections based on TOC")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", default="data/txt_input", help="Output directory for text files")
    parser.add_argument("--pages-per-section", type=int, default=10, help="Pages per section when no TOC available")
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not os.path.exists(args.pdf_path):
        print(f"❌ PDF file not found: {args.pdf_path}")
        return 1
    
    # Initialize segmenter
    segmenter = PDFSegmenter(args.pdf_path, args.output_dir)
    
    try:
        # Open PDF
        if not segmenter.open_pdf():
            return 1
        
        # Extract TOC
        has_toc = segmenter.extract_toc()
        
        # Segment PDF
        if has_toc:
            success = segmenter.segment_by_toc()
        else:
            success = segmenter.segment_by_pages(args.pages_per_section)
        
        if success:
            print(f"\n🎉 PDF segmentation complete! Check {segmenter.output_subdir} for output files.")
        else:
            print("\n❌ PDF segmentation failed.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        segmenter.close()
    
    return 0


if __name__ == "__main__":
    exit(main()) 