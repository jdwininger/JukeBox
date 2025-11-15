#!/usr/bin/env bash
# build-appimage.sh - Build an AppImage for JukeBox (Linux/x86_64)
# Notes:
# - This script packages the repository files into an AppDir and runs appimagetool to produce an AppImage.
# - The resulting AppImage will include the application code but not system Python or binary dependencies.
#   The host must provide a compatible `python3` and required Python packages (or you must vendor them into the AppDir).
# - Tested on x86_64 Linux systems.

set -euo pipefail

# Check if running on Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Error: AppImage builds can only be created on Linux systems."
    echo "AppImage is a Linux-specific packaging format."
    echo ""
    echo "For macOS distribution, use:"
    echo "  make standalone-macos"
    echo "  ./scripts/create-standalone-macos.sh"
    exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
APPDIR_NAME="JukeBox.AppDir"
APPDIR="$BUILD_DIR/$APPDIR_NAME"
OUT_NAME="JukeBox-x86_64.AppImage"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/jukebox"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/applications"

# Copy application files into AppDir share
rsync -a --exclude='.git' --exclude='build' --exclude='music' --exclude='JukeBox.app' --exclude='*.AppImage' "$ROOT_DIR/" "$APPDIR/usr/share/jukebox/"

# Add a small launcher that uses system python3
cat > "$APPDIR/usr/bin/jukebox" <<'EOF'
#!/usr/bin/env bash
# Launcher inside AppImage - runs the packaged app with system python3
HERE="$(dirname "$(readlink -f "$0")")/.."
APPDIR_ROOT="$HERE/usr/share/jukebox"
export PYTHONUNBUFFERED=1
exec /usr/bin/env python3 "$APPDIR_ROOT/src/main.py" "$@"
EOF
chmod +x "$APPDIR/usr/bin/jukebox"

# Add a desktop file
cat > "$APPDIR/usr/share/applications/jukebox.desktop" <<'EOF'
[Desktop Entry]
Name=JukeBox
Exec=jukebox
Icon=jukebox
Type=Application
Categories=Audio;Player;
EOF

# Add icon (placeholder 256x256 PNG if not present in repo)
ICON_TARGET="$APPDIR/usr/share/icons/hicolor/256x256/apps/jukebox.png"
if [ -f "$ROOT_DIR/assets/icon.png" ]; then
  cp "$ROOT_DIR/assets/icon.png" "$ICON_TARGET"
else
  # Create a tiny placeholder PNG (1x1 transparent) and scale won't be ideal, but works.
  cat > "$ICON_TARGET" <<'PNG'
\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82
PNG
fi

# Ensure appimagetool exists; try to download it if missing
APPIMAGETOOL="$(command -v appimagetool || true)"
if [ -z "$APPIMAGETOOL" ]; then
  echo "appimagetool not found in PATH. Attempting to download appimagetool (x86_64)..."
  TOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
  DL="$BUILD_DIR/appimagetool-x86_64.AppImage"
  mkdir -p "$BUILD_DIR"
  if command -v curl >/dev/null 2>&1; then
    curl -L -o "$DL" "$TOOL_URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$DL" "$TOOL_URL"
  else
    echo "Please install curl or wget to download appimagetool, or install appimagetool manually." >&2
    exit 1
  fi
  chmod +x "$DL"
  APPIMAGETOOL="$DL"
fi

# Build AppImage
echo "Building AppImage..."
"$APPIMAGETOOL" "$APPDIR" -n -u
# appimagetool may output the AppImage to the current directory; move it to project root
# Try to find the created AppImage in build dir
CREATED=$(ls -1t "$BUILD_DIR"/*.AppImage 2>/dev/null || true)
if [ -n "$CREATED" ]; then
  mv -f $CREATED "$ROOT_DIR/$OUT_NAME"
  echo "Created AppImage: $ROOT_DIR/$OUT_NAME"
else
  # appimagetool may have created it in cwd
  if [ -f "$APPDIR/$OUT_NAME" ]; then
    mv -f "$APPDIR/$OUT_NAME" "$ROOT_DIR/"
    echo "Created AppImage: $ROOT_DIR/$OUT_NAME"
  else
    echo "Could not find the created AppImage. Please run appimagetool manually:" >&2
    echo "  appimagetool $APPDIR" >&2
    exit 1
  fi
fi

echo "AppImage build complete. Note: the AppImage uses system python3 and expects dependencies to be installed on the target host, or you must vendor them into the AppDir."
