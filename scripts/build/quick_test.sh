#!/bin/bash
# Quick build and test script

set -e

echo "🚀 PDF Power Converter - Quick Build and Test"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating your venv: source venv/bin/activate"
fi

# Default options
BUILD_ONLY=false
TEST_ONLY=false
WATCH=false
VERBOSE=false
PLATFORMS="source,wheel"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --build-only    Only build, don't run tests"
            echo "  --test-only     Only run tests, don't build"
            echo "  --watch         Watch for changes and auto-rebuild/test"
            echo "  --verbose       Verbose output"
            echo "  --platforms     Comma-separated list of platforms (source,wheel,exe)"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Build and test with defaults"
            echo "  $0 --build-only --verbose       # Only build with verbose output"
            echo "  $0 --watch                      # Watch mode for development"
            echo "  $0 --platforms source,wheel,exe # Build multiple platforms"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python build_and_test.py --headless"

if [ "$BUILD_ONLY" = true ]; then
    CMD="$CMD --build-only"
fi

if [ "$TEST_ONLY" = true ]; then
    CMD="$CMD --test-only"
fi

if [ "$WATCH" = true ]; then
    CMD="$CMD --watch"
fi

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

# Convert comma-separated platforms to space-separated
PLATFORMS_ARRAY=(${PLATFORMS//,/ })
CMD="$CMD --platforms ${PLATFORMS_ARRAY[@]}"

echo "📋 Configuration:"
echo "   Build only: $BUILD_ONLY"
echo "   Test only: $TEST_ONLY"
echo "   Watch mode: $WATCH"
echo "   Verbose: $VERBOSE"
echo "   Platforms: $PLATFORMS"
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."
if ! python -c "import PyQt5" 2>/dev/null; then
    echo "❌ PyQt5 not found. Installing dependencies..."
    pip install -r requirements.txt
fi

if [ "$WATCH" = true ]; then
    if ! python -c "import watchdog" 2>/dev/null; then
        echo "📦 Installing watchdog for watch mode..."
        pip install watchdog
    fi
fi

# Set environment for headless testing
export QT_QPA_PLATFORM=offscreen

echo "🏃 Running: $CMD"
echo ""

# Run the command
if eval $CMD; then
    echo ""
    echo "✅ Build and test completed successfully!"
    
    # Show summary if results file exists
    if [ -f "test_results.json" ]; then
        echo ""
        echo "📊 Quick Summary:"
        python -c "
import json
try:
    with open('test_results.json', 'r') as f:
        results = json.load(f)
    
    summary = results.get('summary', {})
    builds = summary.get('successful_builds', 0)
    total_builds = summary.get('total_builds', 0)
    tests = summary.get('successful_tests', 0)
    total_tests = summary.get('total_tests', 0)
    regressions = summary.get('total_regressions', 0)
    
    print(f'   Builds: {builds}/{total_builds}')
    print(f'   Tests: {tests}/{total_tests}')
    print(f'   Regressions: {regressions}')
    
    if summary.get('overall_success'):
        print('   Status: ✅ ALL PASSED')
    else:
        print('   Status: ❌ SOME FAILED')
        
except Exception as e:
    print(f'   Could not read results: {e}')
"
    fi
    
    # Show report location
    if [ -f "build_test_report.md" ]; then
        echo ""
        echo "📄 Detailed report: build_test_report.md"
    fi
    
else
    echo ""
    echo "❌ Build and test failed!"
    echo "📄 Check build_test.log for details"
    exit 1
fi