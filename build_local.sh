#!/bin/bash

# Local build script for PDF Cleanup Agent
# Builds the application into ./dist without code signing

set -e

APP_NAME="PDF Cleanup Agent"
APP_VERSION="1.0.0"

echo "Building $APP_NAME locally..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Installing/updating dependencies..."
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
if [ -d "dist" ]; then
    rm -rf dist/*
else
    mkdir -p dist
fi

# Build with PyInstaller
echo "Building application with PyInstaller..."
pyinstaller pdf_cleanup_agent.spec --noconfirm --clean

# Check if app was built
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [ ! -d "dist/$APP_NAME.app" ]; then
        echo "Error: macOS application build failed"
        exit 1
    fi
    echo ""
    echo "✅ Build complete!"
    echo "📱 macOS App: dist/$APP_NAME.app"
    echo ""
    echo "To run the app:"
    echo "open \"dist/$APP_NAME.app\""
else
    # Linux/Windows
    if [ ! -f "dist/PDFCleanupAgent/PDFCleanupAgent" ] && [ ! -f "dist/PDFCleanupAgent/PDFCleanupAgent.exe" ]; then
        echo "Error: Application build failed"
        exit 1
    fi
    echo ""
    echo "✅ Build complete!"
    echo "📁 Application: dist/PDFCleanupAgent/"
    echo ""
    echo "To run the app:"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "dist/PDFCleanupAgent/PDFCleanupAgent.exe"
    else
        echo "./dist/PDFCleanupAgent/PDFCleanupAgent"
    fi
fi

echo ""
echo "📂 Build output directory: ./dist"
echo ""
echo "Note: This is an unsigned build for local development/testing."