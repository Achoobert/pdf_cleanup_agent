#!/usr/bin/env python3
"""
Simple launcher script for PDF Power Converter

This is a simplified entry point that just launches the main application.
Use this if you want a simple way to start the app without command-line options.
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the Python path
project_root = Path(__file__).parent.absolute()
scripts_path = project_root / 'scripts'
sys.path.insert(0, str(scripts_path))

# Set up output directory for portable version
output_dir = project_root.parent / 'output' if (project_root.parent / 'output').exists() else project_root / 'output'
output_dir.mkdir(exist_ok=True)

# Set environment variable for output directory
os.environ.setdefault('PDF_CONVERTER_OUTPUT_DIR', str(output_dir))

def main():
    """Launch the PDF Power Converter application."""
    try:
        from ui.app_controller import PDFCleanupApp
        
        # Create and run the application with default settings
        app = PDFCleanupApp(debug_mode=False, log_level="INFO")
        exit_code = app.run()
        
        # Cleanup
        app.cleanup()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 130
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all required dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())