#!/bin/bash

# Create self-signed certificate for macOS code signing
# This script creates a development certificate for local builds

set -e

CERT_NAME="PDF Cleanup Agent Developer"
KEYCHAIN_NAME="pdf-cleanup-dev.keychain"
KEYCHAIN_PASSWORD="dev-password"

echo "Creating self-signed certificate for macOS code signing..."

# Create keychain
echo "Creating keychain: $KEYCHAIN_NAME"
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_NAME" || true
security default-keychain -s "$KEYCHAIN_NAME"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_NAME"

# Set keychain timeout (optional)
security set-keychain-settings -t 3600 -l "$KEYCHAIN_NAME"

# Create certificate configuration
cat > /tmp/cert.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = $CERT_NAME
O = PDF Cleanup Agent Development
OU = Development
C = US
ST = Development
L = Development

[v3_req]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = codeSigning
basicConstraints = CA:false
EOF

# Generate private key and certificate
echo "Generating certificate..."
openssl req -new -x509 -days 365 -nodes -config /tmp/cert.conf \
  -keyout /tmp/codesign.key -out /tmp/codesign.crt

# Import certificate and key to keychain
echo "Importing certificate to keychain..."
security import /tmp/codesign.crt -k "$KEYCHAIN_NAME" -T /usr/bin/codesign
security import /tmp/codesign.key -k "$KEYCHAIN_NAME" -T /usr/bin/codesign

# Set certificate trust settings
echo "Setting certificate trust..."
security set-key-partition-list -S apple-tool:,apple: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN_NAME"

# Find and display certificate identity
echo "Certificate created successfully!"
echo "Available code signing identities:"
security find-identity -v -p codesigning "$KEYCHAIN_NAME"

# Get the certificate identity for use in build scripts
CERT_IDENTITY=$(security find-identity -v -p codesigning "$KEYCHAIN_NAME" | grep "$CERT_NAME" | head -1 | sed 's/.*) \(.*\) ".*/\1/')

if [ -n "$CERT_IDENTITY" ]; then
    echo ""
    echo "Certificate Identity: $CERT_IDENTITY"
    echo "You can use this identity for code signing with:"
    echo "codesign --force --deep --sign \"$CERT_IDENTITY\" \"path/to/your.app\""
    
    # Save identity to file for build scripts
    echo "$CERT_IDENTITY" > .codesign_identity
    echo "Certificate identity saved to .codesign_identity"
else
    echo "Warning: Could not find certificate identity"
fi

# Cleanup temporary files
rm -f /tmp/cert.conf /tmp/codesign.key /tmp/codesign.crt

echo ""
echo "Setup complete! You can now build and sign macOS applications."
echo "Note: This is a self-signed certificate for development only."
echo "Users will see a security warning when running the app for the first time."