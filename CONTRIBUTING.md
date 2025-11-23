# Contributing & Development Guide

This document provides comprehensive instructions for setting up, running, and contributing to the JukeBox project - a professional digital music library application built with Python and pygame.

## Quick Start

The fastest way to get JukeBox running:

```bash
git clone https://github.com/jdwininger/JukeBox
cd JukeBox
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

## Development Environment Setup

### Prerequisites

- Python 3.8 or later
- macOS, Linux, or Windows with WSL
- Audio system (ALSA on Linux, CoreAudio on macOS)

### 1. Virtual Environment (Recommended)

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

Install core dependencies:

```bash
pip install -r requirements.txt
```

Core dependencies include:
- `pygame>=2.5.0` - Audio playback and UI framework
- `mutagen>=1.45.0` - ID3 tag reading and audio metadata
- `Pillow>=9.0.0` - Image processing (optional, for icon generation)

### 3. Running the Application

#### Method 1: Launch Script (Recommended)
The `run.sh` script handles virtual environment activation and proper PYTHONPATH setup:

```bash
./run.sh
```

#### Method 2: Makefile
```bash
make run
```

#### Method 3: Direct Python Execution
```bash
# With activated virtual environment
PYTHONPATH=. python3 src/main.py

# Or using venv python directly
.venv/bin/python src/main.py
```

### 4. Project Structure

```
JukeBox/
├── src/                    # Main application source code
│   ├── main.py            # Application entry point
│   ├── player.py          # Music player engine
│   ├── ui.py              # User interface components
│   ├── theme.py           # Theming system
│   ├── album_library.py   # Album management
│   └── config.py          # Configuration handling
├── themes/                 # Theme assets
│   ├── dark/              # Dark theme (default)
│   ├── light/             # Light theme
│   └── Jeremy/            # Custom theme
├── music/                  # Music library (numbered 01-52)
├── assets/                 # Application assets
├── scripts/               # Build and utility scripts
└── JukeBox.app/           # macOS app bundle
```

## Developer tooling

To help avoid accidentally committing large generated artifacts (AppImages, extracted squashfs-root, embedded venvs, etc.),
this repository includes a safety check and optional pre-commit hooks. To enable them locally run:

```bash
./scripts/install-git-hooks.sh
# (optional) install the pre-commit framework to add additional checks
python -m pip install --user pre-commit
pre-commit install --install-hooks
```

After enabling these hooks, commits will run the safety check and standard formatting checks automatically.

## Adding Music to Your Library

JukeBox organizes music into numbered albums (01-52):

1. Create numbered directories in the `music/` folder:
```bash
mkdir -p music/{01,02,03}
```

2. Add audio files to each directory:
```bash
cp /path/to/your/album1/*.mp3 music/01/
cp /path/to/your/album2/*.mp3 music/02/
```

3. Restart JukeBox to rescan the library

Supported formats: MP3, WAV, OGG, FLAC

## Theme Development

### Current Themes
- **dark** (default): Professional dark theme
- **light**: Clean light theme
- **Jeremy**: Custom theme

### Creating Custom Themes

1. Create a new theme directory:
```bash
mkdir themes/my-theme
```

2. Add theme assets (see `COMPREHENSIVE_THEMING.md` for details):
   - Button images (PNG/SVG with automatic fallbacks)
   - Background images
   - Color schemes
   - Font configurations

3. Use the theme creation utilities:
```bash
python3 create_theme_images.py
python3 create_media_buttons.py
python3 create_nav_buttons.py
```

## Asset Generation

### Application Icon
Generate or regenerate the 256×256 application icon:

```bash
python3 scripts/generate-icon.py
```

### UI Button Assets
Create theme-specific button sets:

```bash
# PNG media buttons (play, pause, stop, etc.)
python3 create_media_buttons.py

# SVG media buttons with scalable graphics
python3 create_svg_media_buttons.py

# Navigation buttons (previous, next, etc.)
python3 create_nav_buttons.py
python3 create_svg_nav_buttons.py
```

## Building and Distribution

### macOS App Bundle (Lightweight)

A pre-configured app bundle (`JukeBox.app`) is included in the repository. It provides a native macOS application experience but requires Python and dependencies to be installed on the target system.

#### Running the App Bundle
```bash
./JukeBox.app/Contents/MacOS/JukeBox
```

#### Creating a Distribution DMG
```bash
make package-macos
# or directly:
./scripts/package-macos.sh
```

### Self-Contained macOS App (Recommended for Distribution)

Create a completely self-contained macOS application that includes Python and all dependencies. This is ideal for distribution to users who don't have Python installed.

> **Note**: The macOS app bundle can only be created on macOS systems due to platform-specific requirements.

#### Creating the Standalone App
```bash
make standalone-macos
# or directly:
./scripts/create-standalone-macos.sh
```

This creates `JukeBox-Standalone.app` with:
- Embedded Python virtual environment
- All required dependencies (pygame, mutagen, Pillow)
- Complete application source code
- Pre-configured music directory structure (albums 01-52)
- No external Python installation required

#### Creating Standalone DMG for Distribution
```bash
make standalone-dmg
# or directly:
./scripts/package-standalone-macos.sh
```

This generates `JukeBox-Standalone.dmg` containing the complete self-contained application.

#### Testing the Standalone App
```bash
./JukeBox-Standalone.app/Contents/MacOS/JukeBox
```

#### Standalone App Features
- **No Dependencies**: Runs on any macOS 10.12+ system without Python installation
- **Complete Isolation**: Uses embedded Python environment, no conflicts with system Python
- **Portable**: Can be copied to any Mac and run immediately
- **Professional**: Includes proper app bundle structure and metadata

#### Code Signing (Optional)

For distribution through macOS Gatekeeper, sign the application:

```bash
# Sign the lightweight app bundle
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  JukeBox.app

# Sign the standalone app bundle
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  JukeBox-Standalone.app

# Create signed DMG (choose your preferred version)
./scripts/package-macos.sh           # Lightweight DMG
./scripts/package-standalone-macos.sh  # Standalone DMG

# Notarize for Gatekeeper (requires Apple credentials)
xcrun notarytool submit JukeBox-Standalone.dmg \
  --apple-id "your-apple-id@email.com" \
  --team-id "TEAMID" \
  --password "app-specific-password" \
  --wait

# Staple the notarization ticket
xcrun stapler staple JukeBox-Standalone.dmg
```

#### Distribution Comparison

| Feature | Lightweight DMG | Standalone DMG |
|---------|----------------|----------------|
| File Size | ~5MB | ~59MB |
| Python Required | Yes (system) | No (embedded) |
| Dependencies | User installs | Self-contained |
| Compatibility | Python users | All macOS users |
| Best For | Developers | End users |

### Linux Distribution

#### AppImage (Portable)
Create a portable Linux application:

> **Note**: AppImage builds require a Linux system and cannot be created on macOS.

```bash
make package-appimage
# or directly:
./scripts/build-appimage.sh
```

#### Manual Distribution
The `run.sh` script provides a reliable entry point for manual distribution. Package the entire repository with dependencies for deployment.

## Testing and Quality Assurance

### Manual Testing Checklist

Before submitting changes, verify:

- [ ] Application launches without errors
- [ ] All themes load correctly
- [ ] Audio playback functions (play, pause, stop)
- [ ] Volume controls respond properly
- [ ] Navigation between albums works
- [ ] Button hover effects display correctly
- [ ] Configuration screen accessible
- [ ] Album scanning detects new music
- [ ] All UI elements scale properly

### Performance Testing

Test with various music library sizes:
- Empty library (no music)
- Small library (1-5 albums)
- Large library (20+ albums)
- Maximum capacity (52 albums)

### Audio Format Testing

Verify playback with multiple formats:
- MP3 files with various bitrates
- WAV files (uncompressed)
- OGG Vorbis files
- FLAC files (lossless)

## Contributing Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all classes and functions
- Keep functions focused and modular

### Commit Messages

Use clear, descriptive commit messages:
```
feat: add rollover highlights to PNG/SVG buttons
fix: resolve album scanning for empty directories
docs: update theme development guide
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with appropriate tests
4. Update documentation as needed
5. Submit a pull request with detailed description

### Bug Reports

When reporting bugs, include:
- Operating system and version
- Python version
- Complete error messages
- Steps to reproduce the issue
- Expected vs. actual behavior

## Advanced Development

### Package Sizes and Contents

After building both distribution options:

```bash
# File sizes
JukeBox-unsigned.dmg          21KB  (lightweight, requires Python)
JukeBox-Standalone.dmg        59MB  (self-contained, embedded Python)

# App bundle contents
JukeBox.app/                  Lightweight wrapper (~1KB)
JukeBox-Standalone.app/       Complete application (~160MB)
  └── Contents/Resources/
      ├── python/             105MB (embedded Python + packages)
      └── app/                Application source code and assets
```

The standalone version includes:
- Python 3.13 runtime environment
- All required packages (pygame, mutagen, Pillow, svglib, reportlab)
- macOS-specific bindings (pyobjc-core, pyobjc-framework-Cocoa)
- Complete application source code
- All theme assets and UI components
- Pre-configured music directory structure

### Adding New Features

#### New UI Components
1. Add component class to `src/ui.py`
2. Integrate with theme system in `src/theme.py`
3. Update documentation in relevant `.md` files

#### New Audio Features
1. Extend `MusicPlayer` class in `src/player.py`
2. Add UI controls in main interface
3. Update configuration options in `src/config.py`

#### New Themes
1. Create theme directory structure
2. Generate required assets
3. Test with all UI components
4. Document theme specifications

### Performance Optimization

Key areas for optimization:
- Album scanning and indexing
- Theme asset loading
- UI rendering loops
- Audio buffer management

### Debugging

Enable debugging output:
```bash
PYTHONPATH=. python3 -m pdb src/main.py
```

Common debugging scenarios:
- Theme loading issues
- Audio playback problems
- File path resolution
- UI component positioning

## Resources

### Documentation
- `README.md` - Project overview and features
- `COMPREHENSIVE_THEMING.md` - Complete theming guide
- `MAIN_SCREEN_LAYOUT.md` - UI layout specifications
- `PERFORMANCE_OPTIMIZATIONS.md` - Optimization notes

### External Dependencies
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Mutagen Documentation](https://mutagen.readthedocs.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

### Community
- Report issues in the project repository
- Contribute improvements through pull requests
- Share custom themes with the community

---

**Note**: All commands assume execution from the project root directory. For additional help with specific components, refer to the individual documentation files or examine the source code for detailed implementation examples.
