#!/usr/bin/env python3
"""
Portable Setup Script for PDF Power Converter

This script creates a portable distribution that users can download,
unzip, and run without installation.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def copy_data_directory(src, dst):
    """Copy data directory with better error handling."""
    if not Path(src).exists():
        return
    
    Path(dst).mkdir(parents=True, exist_ok=True)
    
    for item in Path(src).rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(src)
            dest_file = dst / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(item, dest_file)
            except PermissionError:
                print(f"Warning: Skipped {item} due to permission error")
            except Exception as e:
                print(f"Warning: Could not copy {item}: {e}")

def create_portable_structure():
    """Create the portable distribution structure."""
    
    # Define the portable directory structure
    portable_dir = Path("portable_dist")
    
    # Clean up existing portable directory with better error handling
    if portable_dir.exists():
        try:
            shutil.rmtree(portable_dir)
        except PermissionError:
            print("Warning: Could not remove existing portable_dist directory.")
            print("Trying to clean individual files...")
            # Try to remove files individually
            for item in portable_dir.rglob('*'):
                if item.is_file():
                    try:
                        item.unlink()
                    except PermissionError:
                        print(f"Warning: Could not remove {item}")
        except Exception as e:
            print(f"Warning: Error cleaning portable directory: {e}")
    
    # Create directory structure
    dirs_to_create = [
        portable_dir,
        portable_dir / "app",
        portable_dir / "app" / "scripts",
        portable_dir / "app" / "data",
        portable_dir / "logs",
        portable_dir / "output"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return portable_dir

def copy_application_files(portable_dir):
    """Copy necessary application files to portable directory."""
    
    app_dir = portable_dir / "app"
    
    # Files to copy from root
    root_files = [
        "main.py",
        "run.py", 
        "requirements.txt",
        "requirements_minimal.txt",
        "README.md",
        "LICENSE",
        ".env"  # If it exists
    ]
    
    for file_name in root_files:
        if Path(file_name).exists():
            try:
                shutil.copy2(file_name, app_dir / file_name)
                print(f"Copied: {file_name}")
            except PermissionError as e:
                print(f"Warning: Could not copy {file_name}: {e}")
    
    # Copy scripts directory, excluding cache and build files
    if Path("scripts").exists():
        def ignore_patterns(dir, files):
            return [f for f in files if f.startswith('__pycache__') or f.endswith('.pyc') or f.endswith('.pyo') or f == '.DS_Store']
        
        try:
            shutil.copytree("scripts", app_dir / "scripts", dirs_exist_ok=True, ignore=ignore_patterns)
            print("Copied: scripts directory (excluding cache files)")
        except PermissionError as e:
            print(f"Warning: Could not copy scripts directory: {e}")
    
    # Copy essential config files
    # Main config goes to app root (where code expects it)
    main_config_files = [
        "pipeline_config.yml"
    ]
    
    # Secondary config files go to data/config
    data_config_files = [
        "data-order.yml"
    ]
    
    # Copy main config to app root (where the application code expects it)
    for config_file in main_config_files:
        if Path(config_file).exists():
            try:
                shutil.copy2(config_file, app_dir / config_file)
                print(f"Copied main config: {config_file}")
            except PermissionError as e:
                print(f"Warning: Could not copy {config_file}: {e}")
    
    # Ensure data/config directory exists for secondary configs
    (app_dir / "data" / "config").mkdir(parents=True, exist_ok=True)
    
    # Copy secondary config files to data/config
    for config_file in data_config_files:
        if Path(config_file).exists():
            try:
                shutil.copy2(config_file, app_dir / "data" / "config" / config_file)
                print(f"Copied data config: {config_file}")
            except PermissionError as e:
                print(f"Warning: Could not copy {config_file}: {e}")
    
    # Also copy any existing config files from data/config (except main config)
    if Path("data/config").exists():
        try:
            for config_file in Path("data/config").glob("*.yml"):
                if config_file.name not in main_config_files:
                    dest_file = app_dir / "data" / "config" / config_file.name
                    if not dest_file.exists():
                        shutil.copy2(config_file, dest_file)
                        print(f"Copied additional config: {config_file.name}")
        except Exception as e:
            print(f"Warning: Could not copy data/config files: {e}")
    
    # Copy data directory if it exists, but handle permission errors gracefully
    if Path("data").exists():
        try:
            # Use a custom copy function that handles permission errors
            copy_data_directory("data", app_dir / "data")
            print("Copied: data directory")
        except Exception as e:
            print(f"Warning: Could not copy data directory: {e}")

def create_launcher_scripts(portable_dir):
    """Create simple launcher scripts for different platforms."""
    
    # Windows batch launcher
    windows_launcher = portable_dir / "PDF_Power_Converter.bat"
    windows_launcher.write_text("""@echo off
REM Set console to UTF-8 for Unicode character support
chcp 65001 >nul 2>&1
echo Starting PDF Power Converter...
cd /d "%~dp0\\app"
python run.py
if errorlevel 1 (
    echo.
    echo Error: Python not found or application failed to start.
    echo Please ensure Python 3.8+ is installed and in your PATH.
    echo.
    pause
)
""")
    
    # Linux/Mac shell launcher
    unix_launcher = portable_dir / "PDF_Power_Converter.sh"
    unix_launcher.write_text("""#!/bin/bash
echo "Starting PDF Power Converter..."
cd "$(dirname "$0")/app"
python3 run.py
if [ $? -ne 0 ]; then
    echo
    echo "Error: Python not found or application failed to start."
    echo "Please ensure Python 3.8+ is installed."
    echo
    read -p "Press Enter to continue..."
fi
""")
    
    # Make shell script executable
    os.chmod(unix_launcher, 0o755)
    
    print("Created launcher scripts")

def create_requirements_minimal(portable_dir):
    """Create a minimal requirements file for portable distribution."""
    
    minimal_requirements = """# PDF Power Converter - Minimal Requirements
# Core GUI Framework
PyQt5>=5.15.0

# PDF Processing
PyPDF2>=3.0.0
pdfplumber>=0.9.0

# AI/LLM Integration
openai>=1.0.0
anthropic>=0.7.0
tiktoken>=0.5.0

# Essential Utilities
requests>=2.28.0
python-dotenv>=1.0.0
pyyaml>=6.0
colorlog>=6.7.0
"""
    
    req_file = portable_dir / "app" / "requirements_portable.txt"
    req_file.write_text(minimal_requirements)
    print("Created portable requirements file")

def create_setup_instructions(portable_dir):
    """Create setup instructions for users."""
    
    instructions = """# PDF Power Converter - Portable Version

## Quick Start

### Windows Users:
1. Double-click `PDF_Power_Converter.bat` to start the application

### Mac/Linux Users:
1. Open terminal in this folder
2. Run: `./PDF_Power_Converter.sh`

## First Time Setup

If you get errors about missing Python packages, install them:

```bash
# Navigate to the app folder
cd app

# Install required packages
pip install -r requirements_portable.txt
```

## Requirements

- Python 3.8 or higher
- Internet connection (for AI features)

## Configuration

1. Copy your `.env` file to the `app` folder with your API keys
2. Modify `app/pipeline_config.yml` if needed (main configuration)
3. Additional configs are in `app/data/config/` if needed

## Folder Structure

- `app/` - Main application files
- `app/pipeline_config.yml` - Main configuration file
- `app/data/config/` - Additional configuration files (data-order.yml, etc.)
- `app/data/prompts/` - AI prompts and templates
- `logs/` - Application logs (created automatically)
- `output/` - Processed files will be saved here

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure Python is in your system PATH

### "Module not found" errors
- Run: `pip install -r app/requirements_portable.txt`

### GUI doesn't start
- Check that you have a display/desktop environment
- Try running: `python app/run.py --debug` for more information

## Support

For issues and updates, visit: [Your GitHub Repository]
"""
    
    readme_file = portable_dir / "README_PORTABLE.md"
    readme_file.write_text(instructions)
    print("Created setup instructions")

def create_env_template(portable_dir):
    """Create a template .env file."""
    
    env_template = """# PDF Power Converter Configuration
# Copy this file to .env and fill in your API keys

# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
DEBUG=false
LOG_LEVEL=INFO

# Output Settings
OUTPUT_DIR=../output
"""
    
    env_file = portable_dir / "app" / ".env.template"
    env_file.write_text(env_template)
    print("Created .env template")

def main():
    """Main setup function."""
    print("Creating PDF Power Converter Portable Distribution...")
    print("=" * 50)
    
    try:
        # Create directory structure
        portable_dir = create_portable_structure()
        
        # Copy application files
        copy_application_files(portable_dir)
        
        # Create launcher scripts
        create_launcher_scripts(portable_dir)
        
        # Create minimal requirements
        create_requirements_minimal(portable_dir)
        
        # Create setup instructions
        create_setup_instructions(portable_dir)
        
        # Create env template
        create_env_template(portable_dir)
        
        print("\n" + "=" * 50)
        print("Portable distribution created successfully!")
        print(f"Location: {portable_dir.absolute()}")
        print("\nNext steps:")
        print("1. Test the portable version")
        print("2. Create a ZIP file for distribution")
        print("3. Share with users!")
        
    except Exception as e:
        print(f"ERROR: Error creating portable distribution: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())