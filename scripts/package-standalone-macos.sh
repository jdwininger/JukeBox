#!/usr/bin/env bash
# package-standalone-macos.sh - Create DMG for standalone macOS app
set -euo pipefail

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: macOS DMG creation can only be performed on macOS systems."
    echo "This script requires macOS-specific tools (hdiutil)."
    echo ""
    echo "For Linux distribution, use:"
    echo "  make package-appimage"
    echo "  ./scripts/build-appimage.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
APP_NAME="JukeBox-Standalone"
BUNDLE_PATH="$PROJECT_ROOT/$APP_NAME.app"
DMG_NAME="JukeBox-Standalone"
VOLUME_NAME="JukeBox Standalone"

echo "Creating DMG for standalone JukeBox app..."

# Ensure the standalone app exists
if [ ! -d "$BUNDLE_PATH" ]; then
    echo "Error: Standalone app not found at $BUNDLE_PATH"
    echo "Run ./scripts/create-standalone-macos.sh first"
    exit 1
fi

# Clean up existing DMG
if [ -f "$PROJECT_ROOT/$DMG_NAME.dmg" ]; then
    echo "Removing existing DMG..."
    rm "$PROJECT_ROOT/$DMG_NAME.dmg"
fi

# Create temporary directory for DMG contents
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Copy app bundle to temporary directory
echo "Copying app bundle..."
cp -R "$BUNDLE_PATH" "$TEMP_DIR/"

# Create Applications symlink for easy installation
ln -s /Applications "$TEMP_DIR/Applications"

# Create DMG
echo "Creating DMG..."
hdiutil create -volname "$VOLUME_NAME" \
               -srcfolder "$TEMP_DIR" \
               -ov \
               -format UDZO \
               "$PROJECT_ROOT/$DMG_NAME.dmg"

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# Get DMG size
DMG_SIZE=$(du -h "$PROJECT_ROOT/$DMG_NAME.dmg" | cut -f1)

echo ""
echo "✓ Standalone DMG created successfully!"
echo "  File: $DMG_NAME.dmg"
echo "  Size: $DMG_SIZE"
echo ""
echo "The DMG contains:"
echo "  - Self-contained JukeBox app with embedded Python"
echo "  - All required dependencies"
echo "  - No external Python installation required"
echo ""
echo "To install: Double-click the DMG and drag JukeBox to Applications"
