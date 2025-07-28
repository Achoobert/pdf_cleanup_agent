#!/usr/bin/env python3
"""
Fix console encoding for Unicode support on Windows.

This script adds proper UTF-8 encoding setup to Python scripts
so they can display Unicode characters correctly on Windows.
"""

import os
import re
from pathlib import Path

def add_encoding_fix(file_path):
    """Add UTF-8 encoding fix to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if encoding fix is already present
        if 'import sys' in content and 'utf-8' in content and 'reconfigure' in content:
            return False
        
        # Find the imports section
        lines = content.split('\n')
        import_end_idx = 0
        
        # Find where imports end
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_end_idx = i + 1
            elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                if import_end_idx > 0:
                    break
        
        # Add encoding fix after imports
        encoding_fix = [
            "",
            "# Fix console encoding for Unicode support on Windows",
            "import sys",
            "if hasattr(sys.stdout, 'reconfigure'):",
            "    sys.stdout.reconfigure(encoding='utf-8')",
            "if hasattr(sys.stderr, 'reconfigure'):",
            "    sys.stderr.reconfigure(encoding='utf-8')",
            ""
        ]
        
        # Insert the fix
        lines[import_end_idx:import_end_idx] = encoding_fix
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Added encoding fix to: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_main_scripts():
    """Fix the main entry point scripts."""
    scripts_to_fix = [
        "scripts/pdf_segmenter.py",
        "scripts/pdf_process_pipeline.py", 
        "scripts/postprocess_pipeline.py",
        "scripts/markdown_to_fvtt.py",
        "scripts/hello_world.py",
        "scripts/post_processing.py"
    ]
    
    fixed_count = 0
    for script_path in scripts_to_fix:
        if Path(script_path).exists():
            if add_encoding_fix(script_path):
                fixed_count += 1
    
    return fixed_count

def main():
    """Main function to add encoding fixes."""
    print("Adding UTF-8 console encoding support...")
    print("=" * 50)
    
    fixed_count = fix_main_scripts()
    print(f"Added encoding fix to {fixed_count} files")
    
    print("\n" + "=" * 50)
    print("✅ Console encoding fix complete!")
    print("Unicode characters should now display properly on Windows.")

if __name__ == "__main__":
    main()