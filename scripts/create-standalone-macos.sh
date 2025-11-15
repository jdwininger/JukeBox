#!/usr/bin/env bash
# create-standalone-macos.sh - Create a self-contained macOS app bundle
# This bundles Python, dependencies, and the complete application
set -euo pipefail

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: macOS app bundles can only be created on macOS systems."
    echo "This script requires macOS-specific tools and frameworks."
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

echo "Creating self-contained macOS app bundle: $BUNDLE_PATH"

# Clean up existing bundle
if [ -d "$BUNDLE_PATH" ]; then
    echo "Removing existing bundle..."
    rm -rf "$BUNDLE_PATH"
fi

# Create bundle structure
echo "Creating bundle structure..."
mkdir -p "$BUNDLE_PATH/Contents/MacOS"
mkdir -p "$BUNDLE_PATH/Contents/Resources"
mkdir -p "$BUNDLE_PATH/Contents/Frameworks"

# Copy Info.plist and update for standalone app
cat > "$BUNDLE_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>JukeBox Standalone</string>
  <key>CFBundleDisplayName</key>
  <string>JukeBox</string>
  <key>CFBundleIdentifier</key>
  <string>com.jdwininger.jukebox.standalone</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundleExecutable</key>
  <string>JukeBox</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.12</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>CFBundleShortVersionString</key>
  <string>1.0.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleSignature</key>
  <string>JUKE</string>
</dict>
</plist>
EOF

# Create Python virtual environment inside bundle
echo "Creating embedded Python environment..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
EMBEDDED_PYTHON_DIR="$BUNDLE_PATH/Contents/Resources/python"
mkdir -p "$EMBEDDED_PYTHON_DIR"

# Create virtual environment in bundle
python3 -m venv "$EMBEDDED_PYTHON_DIR"

# Activate the embedded environment and install dependencies
source "$EMBEDDED_PYTHON_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"

# Install additional dependencies that might be needed for standalone operation
pip install pyobjc-core pyobjc-framework-Cocoa svglib reportlab

echo "Installed packages in embedded Python:"
pip list

deactivate

# Copy application source code
echo "Copying application source..."
mkdir -p "$BUNDLE_PATH/Contents/Resources/app"
cp -r "$PROJECT_ROOT/src" "$BUNDLE_PATH/Contents/Resources/app/"
cp -r "$PROJECT_ROOT/themes" "$BUNDLE_PATH/Contents/Resources/app/"
cp -r "$PROJECT_ROOT/assets" "$BUNDLE_PATH/Contents/Resources/app/"

# Create music directory structure
mkdir -p "$BUNDLE_PATH/Contents/Resources/app/music"
for i in $(seq -w 1 52); do
    mkdir -p "$BUNDLE_PATH/Contents/Resources/app/music/$i"
done

# Copy configuration files
cp "$PROJECT_ROOT/requirements.txt" "$BUNDLE_PATH/Contents/Resources/app/"
if [ -f "$PROJECT_ROOT/config.json" ]; then
    cp "$PROJECT_ROOT/config.json" "$BUNDLE_PATH/Contents/Resources/app/"
fi

# Create standalone launcher script
cat > "$BUNDLE_PATH/Contents/MacOS/JukeBox" << 'EOF'
#!/usr/bin/env bash
# Standalone JukeBox launcher with embedded Python
set -euo pipefail

# Get bundle paths
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_DIR="$BUNDLE_DIR/Resources/python"
APP_DIR="$BUNDLE_DIR/Resources/app"
PYTHON_BIN="$PYTHON_DIR/bin/python"

# Change to app directory
cd "$APP_DIR"

# Set up environment
export PYTHONPATH="$APP_DIR"
export PYGAME_HIDE_SUPPORT_PROMPT=1

# Verify Python exists
if [ ! -x "$PYTHON_BIN" ]; then
    echo "Error: Embedded Python not found at $PYTHON_BIN"
    exit 1
fi

# Launch application
echo "Starting JukeBox with embedded Python..."
exec "$PYTHON_BIN" src/main.py
EOF

# Make launcher executable
chmod +x "$BUNDLE_PATH/Contents/MacOS/JukeBox"

# Copy icon if it exists
if [ -f "$PROJECT_ROOT/assets/icon.png" ]; then
    echo "Adding application icon..."
    cp "$PROJECT_ROOT/assets/icon.png" "$BUNDLE_PATH/Contents/Resources/"
    
    # Update Info.plist to include icon
    /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string icon.png" "$BUNDLE_PATH/Contents/Info.plist" 2>/dev/null || true
fi

echo "Self-contained app bundle created successfully!"
echo "Location: $BUNDLE_PATH"
echo ""
echo "To test the standalone app:"
echo "  ./\"$APP_NAME.app/Contents/MacOS/JukeBox\""
echo ""
echo "To create a DMG for distribution:"
echo "  ./scripts/package-standalone-macos.sh"