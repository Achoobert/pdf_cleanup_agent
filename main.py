#!/usr/bin/env python3
"""
PDF Power Converter - Main Entry Point

This is the main entry point for the PDF Power Converter application.
Run this file to start the application.

Usage:
    python main.py [options]
    
Options:
    --debug         Enable debug mode with verbose logging
    --log-level     Set logging level (DEBUG, INFO, WARNING, ERROR)
    --version       Show version information
    --help          Show this help message
"""

import sys
import os
import argparse

# Add the scripts directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="PDF Power Converter - Convert PDFs to structured markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Start with default settings
    python main.py --debug            # Start with debug logging
    python main.py --log-level DEBUG  # Set specific log level
        """
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO', 
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='PDF Power Converter 1.0.0'
    )
    
    return parser.parse_args()

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'PyQt5',
        'requests',  # If you use HTTP requests
        # Add other required packages here
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Error: Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main entry point for the application."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Import and run the application
        from ui.app_controller import PDFCleanupApp
        
        # Create and run the application
        app = PDFCleanupApp(debug_mode=args.debug, log_level=args.log_level)
        exit_code = app.run()
        
        # Cleanup
        app.cleanup()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 130  # Standard exit code for Ctrl+C
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all required dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.debug if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())