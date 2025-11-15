# Contributing & Running

This file documents how to run the app locally, create a macOS app bundle, and package an unsigned DMG for distribution.

## Running locally (recommended)

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
./run.sh
# or via Makefile
make run
```

3. If you prefer not to activate the venv, use the interpreter directly:

```bash
.venv/bin/python src/main.py
```

## macOS: app bundle & DMG

A minimal app bundle (`JukeBox.app`) is included in the repo root. It is a thin wrapper that runs the `run.sh` launcher and will prefer the project's `.venv` if present.

To create an unsigned DMG (macOS only), use the packaging script:

```bash
# Ensure you are on macOS and have JukeBox.app present
chmod +x scripts/package-macos.sh
./scripts/package-macos.sh
```

This creates `JukeBox-unsigned.dmg`. Signing and notarization require an Apple Developer account and Xcode tools. Example steps (manual):

```bash
# Sign the app (replace with your identity):
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name (TEAMID)" JukeBox.app

# Create dmg, then notarize with altool/notarytool, then staple the ticket
xcrun altool --notarize-app -f JukeBox.dmg --primary-bundle-id com.yourcompany.jukebox -u '<APPLE_ID>' -p '<APP_SPECIFIC_PASSWORD>'
# Wait for notarization to complete, then:
xcrun stapler staple JukeBox.dmg
```

Notarization and signing are OS X / Apple-specific and cannot be performed inside this repository automatically.

## Linux packaging

On Linux, you can distribute the repository alongside a small launcher script. A Debian package (`.deb`) or AppImage is a common approach; packaging is outside the scope of this document but the `run.sh` script provides a reliable entrypoint.

## Notes

- All suggested commands assume you run from the project root.
- If you need help creating a signed macOS release, provide the signing credentials and I can provide the exact commands you should run locally.
