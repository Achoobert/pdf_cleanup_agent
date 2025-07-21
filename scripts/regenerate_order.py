import sys
from pdf_segmenter import PDFSegmenter

def main():
    if len(sys.argv) < 2:
        print("Usage: python regenerate_order.py <pdf_path>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    segmenter = PDFSegmenter(pdf_path)
    if segmenter.open_pdf():
        segmenter.extract_toc()

if __name__ == "__main__":
    main() 