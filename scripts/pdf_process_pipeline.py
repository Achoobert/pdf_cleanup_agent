import sys
import os
from pathlib import Path
import yaml

# Fix console encoding for Unicode support on Windows
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# Ensure project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_segmenter import PDFSegmenter
import agent_stream

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/pdf_process_pipeline.py <pdf_path>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    pdf_stem = Path(pdf_path).stem

    # Output directories from config
    config_path = os.path.join(os.path.dirname(__file__), '../pipeline_config.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    txt_output_dir = config['directories']['txt_output']
    markdown_output_dir = config['directories']['markdown_output']
    prompt_file = os.path.join(os.path.dirname(__file__), '..', config['settings']['prompt'])

    # 1. Segment PDF to text
    segmenter = PDFSegmenter(pdf_path, txt_output_dir)
    if not segmenter.open_pdf():
        print(f"❌ Failed to open PDF: {pdf_path}")
        sys.exit(1)
    has_toc = segmenter.extract_toc()
    if has_toc:
        segmenter.segment_by_toc()
    else:
        segmenter.segment_by_pages()
    segmenter.close()
    print(f"✅ PDF segmented: {pdf_path}")

    # 2. Run LLM on all .txt files in the output dir for this PDF
    input_dir = os.path.join(txt_output_dir, pdf_stem)
    if not os.path.exists(input_dir):
        print(f"❌ No segmented text found at {input_dir}")
        sys.exit(1)
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    # Find all .txt files recursively
    txt_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    print(f"Found {len(txt_files)} .txt files to process with LLM.")
    for input_path in txt_files:
        agent_stream.process_file(input_path, prompt)
    print(f"✅ LLM processing complete. Markdown output in {markdown_output_dir}/{pdf_stem}")

if __name__ == "__main__":
    main() 