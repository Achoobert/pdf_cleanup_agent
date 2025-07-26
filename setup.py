"""
Setup script for PDF Power Converter

This script allows the application to be installed as a Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PDF Power Converter - Convert PDFs to structured markdown"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Filter out comments and empty lines
        requirements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements
    return []

setup(
    name="pdf-power-converter",
    version="1.0.0",
    author="PDF Power Converter Team",
    author_email="contact@pdfpowerconverter.com",
    description="Convert PDFs to structured markdown using AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf-power-converter",
    
    # Package configuration
    packages=find_packages(where="scripts"),
    package_dir={"": "scripts"},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "ui": ["icons/*.png", "styles/*.qss"],
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "pdf-power-converter=main:main",
            "ppc=main:main",  # Short alias
        ],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "Environment :: X11 Applications :: Qt",
    ],
    
    # Keywords for PyPI
    keywords="pdf converter markdown ai llm document processing",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pdf-power-converter/issues",
        "Source": "https://github.com/yourusername/pdf-power-converter",
        "Documentation": "https://github.com/yourusername/pdf-power-converter/wiki",
    },
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "cx_Freeze>=6.0.0",
        ],
    },
)