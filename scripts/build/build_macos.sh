#!/bin/bash

# Build script for macOS with code signing
# This script builds the PDF Cleanup Agent for macOS and signs it with a self-signed certificate

set -e

APP_NAME="PDF Cleanup Agent"
APP_VERSION="1.0.0"
KEYCHAIN_NAME="pdf-cleanup-dev.keychain"

echo "Building $APP_NAME for macOS..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check if certificate exists
if [ ! -f ".codesign_identity" ]; then
    echo "No code signing identity found. Creating self-signed certificate..."
    ./scripts/build/create_macos_cert.sh
fi

# Read certificate identity
CERT_IDENTITY=$(cat .codesign_identity 2>/dev/null || echo "")

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Build with PyInstaller
echo "Building application with PyInstaller..."
pyinstaller pdf_cleanup_agent.spec --noconfirm --clean

# Check if app was built
if [ ! -d "dist/$APP_NAME.app" ]; then
    echo "Error: Application build failed"
    exit 1
fi

# Sign the application if certificate is available
if [ -n "$CERT_IDENTITY" ]; then
    echo "Signing application with identity: $CERT_IDENTITY"
    
    # Unlock keychain
    security unlock-keychain -p "dev-password" "$KEYCHAIN_NAME" || true
    
    # Sign the app bundle
    codesign --force --deep --sign "$CERT_IDENTITY" "dist/$APP_NAME.app"
    
    # Verify signature
    echo "Verifying signature..."
    codesign --verify --deep --strict "dist/$APP_NAME.app"
    
    # Check if spctl accepts it (may fail for self-signed)
    spctl --assess --type exec "dist/$APP_NAME.app" || echo "Note: Self-signed app may show security warning on first run"
    
    echo "Application signed successfully!"
else
    echo "Warning: No certificate identity found, application will not be signed"
fi

# Create DMG
echo "Creating DMG..."
if command -v create-dmg &> /dev/null; then
    create-dmg \
        --volname "$APP_NAME" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 200 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 600 185 \
        --hdiutil-quiet \
        "$APP_NAME-$APP_VERSION-macos.dmg" \
        "dist/$APP_NAME.app" || {
        echo "create-dmg failed, creating simple DMG..."
        hdiutil create -volname "$APP_NAME" -srcfolder "dist/$APP_NAME.app" -ov -format UDZO "$APP_NAME-$APP_VERSION-macos.dmg"
    }
else
    echo "create-dmg not found, creating simple DMG..."
    hdiutil create -volname "$APP_NAME" -srcfolder "dist/$APP_NAME.app" -ov -format UDZO "$APP_NAME-$APP_VERSION-macos.dmg"
fi

echo ""
echo "Build complete!"
echo "Application: dist/$APP_NAME.app"
echo "DMG: $APP_NAME-$APP_VERSION-macos.dmg"
echo ""
echo "To install create-dmg for better DMG creation:"
echo "brew install create-dmg"