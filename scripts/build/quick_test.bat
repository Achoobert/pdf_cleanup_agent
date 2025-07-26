@echo off
REM Quick build and test script for Windows

setlocal enabledelayedexpansion

echo 🚀 PDF Power Converter - Quick Build and Test
echo ==============================================

REM Check if we're in the right directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the project root directory
    exit /b 1
)

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Warning: No virtual environment detected
    echo    Consider activating your venv: venv\Scripts\activate.bat
)

REM Default options
set BUILD_ONLY=false
set TEST_ONLY=false
set WATCH=false
set VERBOSE=false
set PLATFORMS=source,wheel

REM Parse command line arguments
:parse_args
if "%1"=="" goto end_parse
if "%1"=="--build-only" (
    set BUILD_ONLY=true
    shift
    goto parse_args
)
if "%1"=="--test-only" (
    set TEST_ONLY=true
    shift
    goto parse_args
)
if "%1"=="--watch" (
    set WATCH=true
    shift
    goto parse_args
)
if "%1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%1"=="--platforms" (
    set PLATFORMS=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [options]
    echo.
    echo Options:
    echo   --build-only    Only build, don't run tests
    echo   --test-only     Only run tests, don't build
    echo   --watch         Watch for changes and auto-rebuild/test
    echo   --verbose       Verbose output
    echo   --platforms     Comma-separated list of platforms (source,wheel,exe)
    echo   --help          Show this help message
    echo.
    echo Examples:
    echo   %0                              # Build and test with defaults
    echo   %0 --build-only --verbose       # Only build with verbose output
    echo   %0 --watch                      # Watch mode for development
    echo   %0 --platforms source,wheel,exe # Build multiple platforms
    exit /b 0
)
echo ❌ Unknown option: %1
echo Use --help for usage information
exit /b 1

:end_parse

REM Build command
set CMD=python build_and_test.py --headless

if "%BUILD_ONLY%"=="true" (
    set CMD=!CMD! --build-only
)

if "%TEST_ONLY%"=="true" (
    set CMD=!CMD! --test-only
)

if "%WATCH%"=="true" (
    set CMD=!CMD! --watch
)

if "%VERBOSE%"=="true" (
    set CMD=!CMD! --verbose
)

REM Convert comma-separated platforms to space-separated
set PLATFORMS_FORMATTED=%PLATFORMS:,= %
set CMD=!CMD! --platforms !PLATFORMS_FORMATTED!

echo 📋 Configuration:
echo    Build only: %BUILD_ONLY%
echo    Test only: %TEST_ONLY%
echo    Watch mode: %WATCH%
echo    Verbose: %VERBOSE%
echo    Platforms: %PLATFORMS%
echo.

REM Check dependencies
echo 🔍 Checking dependencies...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ❌ PyQt5 not found. Installing dependencies...
    pip install -r requirements.txt
)

if "%WATCH%"=="true" (
    python -c "import watchdog" >nul 2>&1
    if errorlevel 1 (
        echo 📦 Installing watchdog for watch mode...
        pip install watchdog
    )
)

REM Set environment for headless testing
set QT_QPA_PLATFORM=offscreen

echo 🏃 Running: !CMD!
echo.

REM Run the command
!CMD!
if errorlevel 1 (
    echo.
    echo ❌ Build and test failed!
    echo 📄 Check build_test.log for details
    exit /b 1
)

echo.
echo ✅ Build and test completed successfully!

REM Show summary if results file exists
if exist "test_results.json" (
    echo.
    echo 📊 Quick Summary:
    python -c "import json; results = json.load(open('test_results.json')); summary = results.get('summary', {}); print(f'   Builds: {summary.get(\"successful_builds\", 0)}/{summary.get(\"total_builds\", 0)}'); print(f'   Tests: {summary.get(\"successful_tests\", 0)}/{summary.get(\"total_tests\", 0)}'); print(f'   Regressions: {summary.get(\"total_regressions\", 0)}'); print('   Status: ✅ ALL PASSED' if summary.get('overall_success') else '   Status: ❌ SOME FAILED')"
)

REM Show report location
if exist "build_test_report.md" (
    echo.
    echo 📄 Detailed report: build_test_report.md
)