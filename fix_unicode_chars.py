#!/usr/bin/env python3
"""
Replace Unicode emoji characters with ASCII equivalents for Windows compatibility.
"""

import os
from pathlib import Path

# Unicode to ASCII replacements
REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '📄': '[PAGES]',
    '📋': '[TOC]',
    '⚠️': '[WARNING]',
    '🎉': '[SUCCESS]',
}

def fix_file(file_path):
    """Fix Unicode characters in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for unicode_char, ascii_replacement in REPLACEMENTS.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix Unicode characters in portable distribution."""
    portable_scripts = Path("portable_dist/app/scripts")
    if not portable_scripts.exists():
        print("Portable distribution not found. Run portable_setup.py first.")
        return
    
    fixed_count = 0
    for py_file in portable_scripts.rglob("*.py"):
        if fix_file(py_file):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files in portable distribution")

if __name__ == "__main__":
    main()