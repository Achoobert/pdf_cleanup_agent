# PDF Cleanup Agent

A Python-based tool for processing and cleaning up PDF documents using Ollama AI models.

## Project Structure

```
pdf_cleanup_agent/
├── agent.py              # Main processing script
├── agent_stream.py       # Streaming version for large documents
├── hello_world.py        # Test script for Ollama connection
├── run_tests.py          # Test runner script
├── prompt.txt            # AI prompt template
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_agent.py     # Tests for main agent
│   ├── test_agent_stream.py  # Tests for streaming agent
│   └── test_hello_world.py   # Tests for connectivity
├── data/
│   ├── txt_input/        # Input text files (gitignored)
│   ├── pdf/              # Input PDF files (gitignored)
│   ├── markdown/         # Input markdown files (gitignored)
│   └── output/           # Generated output files (gitignored)
└── venv/                 # Python virtual environment
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

1. Place your input text file in `data/txt_input/input.txt`
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
```

### Test Coverage

The test suite covers:
- ✅ API connectivity and error handling
- ✅ File operations and directory creation
- ✅ Text chunking and streaming functionality
- ✅ Prompt processing and formatting
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