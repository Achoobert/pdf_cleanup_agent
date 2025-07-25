"""Main Application Entry Point - PDF Power Converter"""
import sys, os, argparse

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.app_controller import PDFCleanupApp

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="PDF Cleanup Agent")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--log-level', choices=['DEBUG','INFO','WARNING','ERROR'], 
                       default='INFO', help='Set logging level')
    parser.add_argument('--version', action='version', version='PDF Cleanup Agent 1.0.0')
    return parser.parse_args()

def main():
    """Main entry point with command-line argument handling."""
    args = parse_arguments()
    app = PDFCleanupApp(debug_mode=args.debug, log_level=args.log_level)
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    return exit_code

if __name__ == '__main__':
    sys.exit(main())