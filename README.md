# PDF Cleanup Agent

python scripts/pdf_process_pipeline.py <pdf_path>
python scripts/postprocess_pipeline.py <markdown_dir>

## Project Structure

```
pdf_cleanup_agent/
├── agent.py              # Main processing script
├── agent_stream.py       # Streaming version for large documents
├── pdf_segmenter.py      # PDF segmentation tool
├── hello_world.py        # Test script for Ollama connection
├── run_tests.py          # Test runner script
├── prompt.txt            # AI prompt template
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_agent.py     # Tests for main agent
│   ├── test_agent_stream.py  # Tests for streaming agent
│   ├── test_hello_world.py   # Tests for connectivity
│   └── test_pdf_segmenter.py # Tests for PDF segmentation
├── data/
│   ├── txt_input/        # Input text files 
│   ├── pdf/              # Input PDF files 
│   ├── markdown/         # Input markdown files 
│   └── output/           # Generated output files 
```

## Setup

1. Install Python dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Install and start Ollama:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull deepseek-r1
   ollama serve
   ```

3. Test the connection:
   ```bash
   python hello_world.py
   ```

## Usage

### PDF Segmentation

Segment RPG rulebooks into sections based on table of contents:

```bash
# Basic segmentation using TOC
python pdf_segmenter.py data/pdf/your_rulebook.pdf

# Custom output directory
python pdf_segmenter.py data/pdf/your_rulebook.pdf --output-dir data/txt_input

# Fallback to page-based segmentation (if no TOC)
python pdf_segmenter.py data/pdf/your_rulebook.pdf --pages-per-section 15
```

The script will:
- Extract the table of contents from your PDF
- Split the PDF into sections based on TOC entries
- Convert each section to text using PyMuPDF (works with most modern PDFs)
- Save each section as a separate `.txt` file in `data/txt_input/`

**Note:** This tool works best with PDFs that have embedded text (most modern PDFs). For scanned/image-only PDFs, you may need to use a different tool with OCR capabilities.

### Text Processing

1. Place your input text file in `data/txt_input/input.txt` (or use segmented files)
2. Create a `prompt.txt` file with your AI instructions
3. Run the processing script:
   ```bash
   # For regular processing
   python agent.py
   
   # For large documents (streaming)
   python agent_stream.py
   ```

4. Find your output in `data/output/output.md`

## Testing

The project includes a comprehensive test suite to ensure reliability:

### Running Tests Locally

```bash
# Run all tests
python run_tests.py

# Run specific test modules
python -m unittest tests.test_agent -v
python -m unittest tests.test_agent_stream -v
python -m unittest tests.test_hello_world -v
python -m unittest tests.test_pdf_segmenter -v
```

### Test Coverage

The test suite covers:
- ✅ API connectivity and error handling
- ✅ File operations and directory creation
- ✅ Text chunking and streaming functionality
- ✅ Prompt processing and formatting
- ✅ PDF segmentation functionality
- ✅ Error scenarios and edge cases

### Continuous Integration

Tests automatically run on:
- Every push to main/master branch
- Every pull request
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

## Copyright Protection

This repository is configured to prevent accidental commits of copyrighted content:
- All `.txt`, `.pdf`, and `.md` files are excluded from git
- Data directories are preserved with `.gitkeep` files
- Only the directory structure is tracked, not the content

## Configuration

- **Model**: Change `MODEL = "deepseek-r1"` in the scripts to use a different Ollama model
- **Chunk Size**: Adjust `CHUNK_SIZE = 3000` in `agent_stream.py` for different document sizes
- **API Endpoint**: Modify `OLLAMA_API` if using a remote Ollama instance 