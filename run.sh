#!/bin/bash
# Simple launcher for PDF Power Converter on macOS/Linux

echo "Starting PDF Power Converter..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the application
python3 main.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with error"
    read -p "Press Enter to continue..."
fi