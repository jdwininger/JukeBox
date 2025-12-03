#!/usr/bin/env bash
# package-macos.sh - Create an unsigned .dmg containing JukeBox.app
# Requires macOS (hdiutil) and the app bundle at ./JukeBox.app
# This script creates a temporary DMG and copies the app into it.

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

APP_NAME="JukeBox.app"
DMG_NAME="JukeBox-unsigned.dmg"
TEMP_DIR="build_dmg_temp"

if [ ! -d "$APP_NAME" ]; then
  echo "Error: $APP_NAME not found in project root. Build or copy the app bundle first."
  exit 1
fi

rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
cp -R "$APP_NAME" "$TEMP_DIR/"

# Use hdiutil to create dmg (macOS-only)
if command -v hdiutil >/dev/null 2>&1; then
  echo "Creating unsigned dmg: $DMG_NAME"
  hdiutil create -srcfolder "$TEMP_DIR" -volname "JukeBox" -fs HFS+ -format UDZO "$DMG_NAME"
  echo "Created $DMG_NAME"
  rm -rf "$TEMP_DIR"
  echo "Unsigned dmg ready. To sign and notarize, use Apple Developer tools (codesign & altool/notarytool)."
else
  echo "hdiutil not found. This script must be run on macOS."
  exit 1
fi
