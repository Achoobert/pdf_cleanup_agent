@echo off
REM Simple Windows launcher for PDF Power Converter

echo Starting PDF Power Converter...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the application
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)