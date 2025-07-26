#!/bin/bash

# Test script to verify the local build works

echo "Testing PDF Cleanup Agent build..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    APP_PATH="dist/PDF Cleanup Agent.app"
    
    if [ ! -d "$APP_PATH" ]; then
        echo "❌ Build not found: $APP_PATH"
        echo "Run ./build_local.sh first"
        exit 1
    fi
    
    echo "✅ macOS app bundle found: $APP_PATH"
    
    # Check if executable exists
    EXEC_PATH="$APP_PATH/Contents/MacOS/PDFCleanupAgent"
    if [ ! -f "$EXEC_PATH" ]; then
        echo "❌ Executable not found: $EXEC_PATH"
        exit 1
    fi
    
    echo "✅ Executable found: $EXEC_PATH"
    
    # Check app bundle structure
    if [ -f "$APP_PATH/Contents/Info.plist" ]; then
        echo "✅ Info.plist found"
    else
        echo "❌ Info.plist missing"
    fi
    
    if [ -d "$APP_PATH/Contents/Resources" ]; then
        echo "✅ Resources directory found"
    else
        echo "❌ Resources directory missing"
    fi
    
    echo ""
    echo "🚀 To run the app:"
    echo "   open \"$APP_PATH\""
    echo ""
    echo "🚀 To run from command line (for debugging):"
    echo "   \"$EXEC_PATH\""
    
else
    # Linux/Windows
    APP_PATH="dist/PDFCleanupAgent"
    
    if [ ! -d "$APP_PATH" ]; then
        echo "❌ Build not found: $APP_PATH"
        echo "Run ./build_local.sh first"
        exit 1
    fi
    
    echo "✅ Application directory found: $APP_PATH"
    
    # Check executable
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        EXEC_PATH="$APP_PATH/PDFCleanupAgent.exe"
    else
        EXEC_PATH="$APP_PATH/PDFCleanupAgent"
    fi
    
    if [ ! -f "$EXEC_PATH" ]; then
        echo "❌ Executable not found: $EXEC_PATH"
        exit 1
    fi
    
    echo "✅ Executable found: $EXEC_PATH"
    
    echo ""
    echo "🚀 To run the app:"
    echo "   \"$EXEC_PATH\""
fi

echo ""
echo "📊 Build size:"
du -sh dist/

echo ""
echo "✅ Build test completed successfully!"