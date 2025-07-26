#!/usr/bin/env python3
"""
Simple wrapper for build and test automation

This provides an easy entry point at the project root.
"""

import sys
import os
from pathlib import Path

# Add scripts to path
project_root = Path(__file__).parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))

# Import and run the main build and test script
from build.build_and_test import main

if __name__ == '__main__':
    main()