#!/usr/bin/env python3
"""
Test script for portable distribution

This script tests that the portable distribution works correctly.
"""

import sys
import os
from pathlib import Path
import subprocess

def test_python_version():
    """Test that Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is too old. Need Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def test_required_packages():
    """Test that required packages can be imported."""
    required_packages = [
        ('PyQt5', 'PyQt5.QtWidgets'),
        ('requests', 'requests'),
        ('yaml', 'yaml'),
        ('dotenv', 'dotenv'),
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is available")
        except ImportError:
            print(f"❌ {package_name} is missing")
            missing.append(package_name)
    
    return len(missing) == 0, missing

def test_portable_structure():
    """Test that portable directory structure exists."""
    portable_dir = Path("portable_dist")
    
    if not portable_dir.exists():
        print("❌ Portable distribution not found. Run create_portable.bat first.")
        return False
    
    required_files = [
        "PDF_Power_Converter.bat",
        "PDF_Power_Converter.sh", 
        "README_PORTABLE.md",
        "app/run.py",
        "app/main.py",
        "app/requirements_portable.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = portable_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} is missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_app_import():
    """Test that the main app can be imported."""
    try:
        # Add scripts to path temporarily
        scripts_path = Path("scripts")
        if scripts_path.exists():
            sys.path.insert(0, str(scripts_path))
        
        from ui.app_controller import PDFCleanupApp
        print("✅ Main application can be imported")
        return True
    except ImportError as e:
        print(f"❌ Cannot import main application: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing PDF Power Converter Portable Setup")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test Python version
    if test_python_version():
        tests_passed += 1
    
    # Test required packages
    packages_ok, missing = test_required_packages()
    if packages_ok:
        tests_passed += 1
    elif missing:
        print(f"\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing)}")
    
    # Test portable structure
    if test_portable_structure():
        tests_passed += 1
    
    # Test app import
    if test_app_import():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Portable distribution is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())