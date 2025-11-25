# JukeBox - Professional Digital Music Library

A sophisticated, fully-themed music jukebox application built with Python, pygame, and SDL2 that provides a professional album library experience with complete customization capabilities.

## Features

### Modern Professional Interface
- **Complete Theming System**: PNG/SVG button support with automatic fallbacks
- **Rollover Highlights**: Interactive hover effects on all buttons (30% brightness increase)
- **Responsive Design**: Scales between fullscreen (1280x800) and windowed modes
- **3-Column Layout**: Browse previous, current, and next albums simultaneously
- **Enhanced Navigation**: Side navigation buttons with themed graphics
- **Real-time Feedback**: Visual feedback for all user interactions

### Album Management
- **52 Album Library**: Organize music into up to 52 numbered albums (01-52)
- **Auto-Detection**: Automatically scans numbered directories for audio files
- **ID3 Tag Reading**: Extracts artist, album name, track title, and duration from audio files
- **Multiple Formats**: Supports MP3, WAV, OGG, and FLAC files
- **Smart Text Handling**: Intelligent wrapping and truncation for long titles

### Audio Controls
- **Volume Slider**: Horizontal slider for precise volume control (0-100%)
- **Audio Fader**: Smooth fade-in/fade-out with adjustable speed
- **5-Band Equalizer**: Professional audio equalization
  - 60 Hz (Bass)
  - 250 Hz (Low Mid)
  - 1 kHz (Mid)
  - 4 kHz (High Mid)
  - 16 kHz (Treble)
  - Range: -12 dB to +12 dB per band
  - Toggle display with EQ button

### Metadata
- **Automatic Indexing**: Creates organized catalog on startup

### Playback Controls
- Play, skip, stop functionality
- Credits: playback requires credits — one credit allows one play. Use the "Add Credit" button on the main screen (right column, below the album cards) to add credits.
- Navigate between tracks within an album
- Navigate between albums in the library
- Auto-advance to next track when current finishes
- Volume control (0-100%)

### User Interface
- **Professional 3-Column Layout**: Browse albums with visual card-based design
- **Enhanced Now Playing Display**: Persistent track information with yellow highlighting
- **Themed Media Controls**: PNG/SVG play, skip, stop buttons with rollover effects
- **Responsive Number Pad**: Centered, semi-transparent border with color-coded buttons
- **Configuration Screen**: Real-time theme switching and settings management
 - **4-Digit Selection System**: Quick track selection with real-time input display
 - **Compact Track Lists**: Album cards use a smaller, denser font for track listings so more song titles fit on each card
- **Browse Position System**: Navigate 4 albums at a time with side buttons
- **Smart Layout Adaptation**:
  - Fullscreen: 1.0x scale factor with optimal spacing
  - Windowed: 0.75x scale factor maintaining proportions
- **Visual Feedback System**:
  - Rollover highlights on all interactive elements
  - Color-coded buttons (Red: CLR, Green: ENT, Blue: Backspace)
  - Themed PNG/SVG graphics with automatic fallbacks

### Keyboard Shortcuts
- `Space`: Play/Pause
- `←→`: Previous/Next track (within album)
- `N`/`P`: Previous/Next album
- `↑↓`: Increase/Decrease volume
- `C`: Toggle configuration screen
  - `Enter` / `Esc` during Exit dialog: Confirm (Enter) or cancel (Esc) when the Exit confirmation dialog appears
- `Alt+Enter`: Toggle fullscreen mode
- `0-9`: Direct number entry for track selection
- `Enter`: Execute 4-digit selection
- `Backspace`: Remove last digit from selection
- `Escape`: Clear current selection

## Requirements

- Python 3.8+
- pygame >= 2.5.0
- mutagen >= 1.45.0
- svglib >= 1.0.0 (for SVG support)
- reportlab (dependency for SVG rendering)
- SDL2 (installed automatically with pygame)

## Installation
## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pygame mutagen svglib reportlab
   # or use requirements.txt if available:
   pip install -r requirements.txt
   ```

## Usage
### Running the Application

Recommended ways to start the app from the command line (macOS / zsh). Run these from the project root (repository root).

- 1) Activate the virtual environment, then run (recommended)

```bash
source .venv/bin/activate
python src/main.py
# or run as a module:
python -m src.main
```

- 2) Run without activating the venv (use the venv Python directly)

```bash
.venv/bin/python src/main.py
```

- 3) If dependencies are missing, install them (inside the venv or with the venv python)

```bash
# activate venv first
source .venv/bin/activate
pip install -r requirements.txt

# or using the venv python without activating
.venv/bin/python -m pip install -r requirements.txt
```

Notes:
- Ensure you run commands from the project root directory.
- The app uses `pygame` and requires a graphical environment (macOS desktop). If running headless, additional setup is required.
- To run in background (no terminal blocking):

```bash
source .venv/bin/activate && python src/main.py & disown
```

Quickstart convenience (bootstrap venv & install)
------------------------------------------------

`quickstart.py` now provides simple bootstrapping helpers to create a virtual environment and install dependencies from `requirements.txt`.

Examples:

- Create a venv and install requirements into `.venv` (default):

```bash
bash quickstart.py --bootstrap
```

- Create a venv at a custom location and install deps:

```bash
bash quickstart.py --bootstrap --venv .myenv
```

- Only install dependencies into an existing venv (no creation):

```bash
bash quickstart.py --install-deps --venv .venv
```

- Create the virtualenv but skip installing dependencies (useful if you plan to install manually or prepare offline):

```bash
bash quickstart.py --bootstrap --venv .venv --no-install
```

These helpers are useful when distributing a minimal release tar — run them inside the extracted folder to prepare a runtime environment using the included `requirements.txt`.

### macOS App Bundle

If you prefer a clickable application on macOS, a minimal `.app` wrapper is included at the project root as `JukeBox.app`. It expects the repository layout and dependencies to be present.

- To run by double-clicking: open `JukeBox.app` in Finder.
- To run from Terminal using `open`:

```bash
open ./JukeBox.app
```

The bundle calls the same `run.sh` launcher and will attempt to use the project's virtual environment if present.

### Running on Linux

Prerequisites (Debian/Ubuntu example):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip libsdl2-2.0-0 libsdl2-image-2.0-0 libasound2
```

Create and activate the virtual environment, install dependencies, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/python src/main.py

Packaging & releases (AppImage, tar, CI)
--------------------------------------

This project now includes improved packaging and CI release automation to make building and publishing easier.

- AppImage (standalone Linux executable): use `./scripts/build-appimage.sh` (requires Linux). The builder supports an embedded Python virtualenv and a `--slim` mode to reduce size.

- Minimal release tar: `./scripts/create-release-tar.sh` produces a compact `build/release/JukeBox-<version>.tar.gz` containing runtime files (src, assets, themes) and a helper `setup_and_run.sh` to create a venv, install `requirements.txt`, and run `run.sh`. There's a `make release-tar` convenience target in the Makefile that calls the script.

- Repository safety & pre-commit: a `scripts/check-for-bloat.sh` safety checker prevents committing large artifacts (AppImages, extracted squashfs, repo venvs). A local pre-commit hook is available via `.githooks/pre-commit` and you can install it with `./scripts/install-git-hooks.sh`. Pre-commit configuration includes formatting and linting hooks (Black, isort, flake8) and the repo safety checks.

- CI & release workflow: GitHub Actions will run tests, safety checks, build full & slim AppImages, create checksums, (optionally) create .zsync metadata, produce a combined release manifest, and upload artifacts on release. The release workflow also uploads the minimal release tar and its checksum. Optional signing and AppImageHub listing automation are supported if repository secrets are configured.

See `RELEASE_NOTES.md` for a short summary of the changes to packaging, CI, and developer tooling.
```

Running diagnostics
-------------------

If the app behaves oddly on your system (no audio, missing images, themes not loading), run the built-in diagnostics which will inspect pygame, mixer, image and svg support and give distro-specific hints:

```bash
# Using quickstart
python quickstart.py --diagnose

# Using main app
python -m src.main --diagnose

# Or run directly
python -m src.diagnostics
```

The command prints a short human-readable report and recommendations for resolving missing dependencies.

Automatic fixer helper
----------------------

If you want JukeBox to *attempt* to install missing system packages for you, use the `--fix` or `--autofix` options.

- `--fix` will run diagnostics then interactively prompt you which suggested commands to run.
- `--autofix` will run diagnostics and attempt all suggested fixes without prompting.

Example (interactive):

```bash
python quickstart.py --fix
```

Example (automatic — requires confirmation):

```bash
# Run suggested fixes, but you'll be asked to confirm before any commands run
python quickstart.py --autofix

# Skip the confirmation prompt (runs immediately - use with care):
python quickstart.py --autofix --autofix-yes
```

Notes:
- The fixer helper prints the commands it will run; most are distro package manager commands (apt-get / dnf) and require sudo.
- The helper runs commands using the shell; confirm you understand the commands before allowing them.

Preview-only mode
-----------------

If you want to *see* exactly what commands would be run without executing anything, use the `--preview-fix` flag. This is the safest way to inspect the OS commands the fixer would run.

```bash
python quickstart.py --preview-fix
```

This prints the list of commands grouped by area (audio/image/svg) and exits — no system changes are made.

Notes for Linux:
- Ensure SDL2 and related system libraries are installed for `pygame` to initialize the display and audio.
- On headless servers, run within an X/Wayland session or use a virtual framebuffer (e.g., `Xvfb`).

Additional diagnostics & improvements:

- The app now includes a more robust image loader that falls back to Pillow (Pillow must be installed) when pygame can't load a PNG. This resolves cases where SDL_image isn't available or built without PNG support.

- The `music/` library directory is created automatically (if missing) and the app now also seeds the expected 01..52 album slot directories so the UI shows placeholders and you can drop music files into numbered folders.

- If you don't see your music, verify the repo's music directory (project-root/music) or set up your own by putting audio files into `music/01/`, `music/02/`, etc. Supported formats: mp3, wav, ogg, flac.

Default music location on macOS / Linux
--------------------------------------

On macOS and Linux the application now defaults the music library to the user's Music folder at:

```
~/Music/JukeBox
```

If this directory doesn't exist the app will create it and ensure the expected numbered album slots (01–52) are present so you can drop files directly into the numbered folders. This keeps your music in a conventional, user-visible location instead of buried inside the project directory.

If you prefer the repo-local `music/` folder, start the program from the repo root or update config to point elsewhere (future enhancement: configurable via CLI/config file).

Note: The app now automatically prefers an existing ~/Music/JukeBox-like folder (for example `~/Music/Jukebox` or `~/Music/jukebox`) when no `music_dir` is configured. This avoids creating a new `~/Music/JukeBox` directory if you already have a similarly-named folder in your Music directory.

Configuring library from the app (GUI)
------------------------------------

You can now change the music library location from inside the application:

1. Open the Configuration screen (press `C` or click the gear icon).
2. Click the `Choose Library` button in the Library Actions column.
3. A native folder selection dialog will appear (via tkinter) — pick a folder or create a new one.

If you pick a folder, the app will persist your choice to `~/.jukebox_config.json` as `music_dir`, create the numbered album slots (01–52) if they don't exist, and update the library immediately.
If you cancel the dialog, the app will keep using the current library location (which defaults to `~/Music/JukeBox` on macOS/Linux).

Compact Track List setting:
- Toggle compact track listings on album cards from the Settings section in the Configuration screen. When enabled, album cards use a denser font and tighter spacing so more track titles fit on each card.

Density slider:
- Fine-tune how densely track lists are drawn using the new "Density" slider in the Configuration screen (range: 0.5 = very dense, 1.0 = normal). Changes apply immediately across the UI.

#### Common Linux troubleshooting: missing audio / mixer

If the app starts but later fails with errors about `pygame.mixer` or audio missing ("mixer module not available" or "No module named 'pygame.mixer'"), it usually means system audio libraries (SDL_mixer / libsndfile) were not present when pygame was installed.

Quick fixes for most distros (run as root or with sudo):

Debian / Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y libsdl2-dev libsdl2-mixer-dev libsndfile1-dev
```

Fedora / RHEL / CentOS:

```bash
sudo dnf install -y SDL2-devel SDL2_mixer SDL2_mixer-devel libsndfile-devel
```

After installing system deps, reinstall pygame inside your virtualenv to ensure mixer is built/available there:

```bash
source .venv/bin/activate
python -m pip install --upgrade --force-reinstall --no-cache-dir pygame
```

If you still see audio issues, check that your system audio stack (PulseAudio or PipeWire) is running and that the user has permission to access the sound devices.

### Setting Up Your Album Library

1. Create numbered album directories in the `music/` folder:
   ```
   music/
   ├── 01/
   ├── 02/
   ├── 03/
   ...
   ├── 52/
   ```

2. Copy complete albums into each numbered directory:
   ```
   music/
   ├── 01/
   │   ├── track01.mp3
   │   ├── track02.mp3
   │   └── track03.mp3
   ├── 02/
   │   ├── song1.flac
   │   ├── song2.flac
   │   └── song3.flac
   ```

3. Run the application - it automatically scans and indexes all albums

## Professional Theming System

Release tar (minimal runtime tar.gz)
----------------------------------

If you'd like a minimal, portable source archive for distribution (contains only the runtime files needed to run JukeBox), use the provided helper which produces a compressed tarball in `build/release/`.

From the repository root you can build it manually:

```bash
bash scripts/create-release-tar.sh
```

Or use the convenience Makefile target:

```bash
make release-tar
```

What the tar contains:
- Selected runtime files: `src/`, `assets/`, `themes/`, plus `run.sh`, `requirements.txt`, `setup.py`, `README.md` and `LICENSE`.
- A tiny helper `setup_and_run.sh` is included in the archive — it will create a `venv` in the extracted folder, install dependencies from `requirements.txt` and launch `run.sh` for you.

Notes:
- The tarball intentionally excludes tests, `.git`, `__pycache__`, and other development-only files to keep the archive small.
- The archive does not include a pre-built virtualenv or Python binary. If you want a completely standalone release (with embedded venv), tell me and I can add an option to include it — note this substantially increases the archive size.

To clean generated release artifacts (tar files, checksums):

```bash
make clean-release
```


JukeBox features a comprehensive theming system with complete PNG/SVG button support, automatic fallbacks, and real-time theme switching.

### Current Themes

**Available Built-in Themes:**
- **dark** (default): Professional dark gradient with themed controls
- **light**: Clean light gradient with light themed controls
- **matrix**: Green matrix-style digital theme
- **neon**: Vibrant neon cyberpunk theme
- **wood**: Warm wooden jukebox aesthetic
- **metal**: Industrial metallic design
- **retro**: Classic vintage jukebox styling

### Theme Components

Each theme includes:

#### Background Images
- **Main Background**: Full 1280x800 themed background with scaling support

#### Button Graphics (PNG/SVG with Fallbacks)
- **Media Controls**:
  - `play_button.png/svg` - Play button with theme styling
  - `pause_button.png/svg` - Skip button with theme styling
  - `stop_button.png/svg` - Stop button with theme styling
  - `config_button.png/svg` - Configuration gear icon
- **Navigation Controls**:
  - `nav_left_button.png/svg` - Left navigation arrow (60x80px)
  - `nav_right_button.png/svg` - Right navigation arrow (60x80px)
- **Interactive Elements**:
  - Automatic fallback to solid colors if images missing
  - Rollover highlights (30% brightness increase) on all buttons
  - Responsive scaling for fullscreen/windowed modes

#### Theme Selection Interface
- **Real-time Switching**: Instant theme changes via Configuration screen
- **Theme Discovery**: Automatic detection of all available themes
- **Persistent Settings**: Theme choice saved to user configuration
- **Preview Capability**: See themes immediately when selected

### Theme Directory Structure

Themes are stored in the `themes/` directory with the following structure:

```
themes/
├── dark/                       # Dark theme
│   ├── background.png         # Main background image (1280x800)
│   ├── play_button.png        # Play button (50x50)
│   ├── play_button.svg        # Play button SVG (vector)
│   ├── pause_button.png       # Skip button (50x50)
│   ├── pause_button.svg       # Skip button SVG (vector)
│   ├── stop_button.png        # Stop button (50x50)
│   ├── stop_button.svg        # Stop button SVG (vector)
│   ├── config_button.png      # Configuration gear (50x50)
│   ├── config_button.svg      # Configuration gear SVG (vector)
│   ├── nav_left_button.png    # Left navigation arrow (60x80)
│   ├── nav_left_button.svg    # Left navigation arrow SVG (vector)
│   ├── nav_right_button.png   # Right navigation arrow (60x80)
│   ├── nav_right_button.svg   # Right navigation arrow SVG (vector)
│   ├── slider_track.png       # Legacy: Slider track/background
│   └── slider_knob.png        # Legacy: Slider knob/handle
├── light/                      # Light theme
│   ├── background.png         # All same files as dark theme
│   ├── play_button.png        # with light theme styling
│   ├── play_button.svg
│   ├── pause_button.png
│   ├── pause_button.svg
│   ├── stop_button.png
│   ├── stop_button.svg
│   ├── config_button.png
│   ├── config_button.svg
│   ├── nav_left_button.png
│   ├── nav_left_button.svg
│   ├── nav_right_button.png
│   ├── nav_right_button.svg
│   ├── slider_track.png
│   └── slider_knob.png
└── custom/                     # Create your own themes here
│   ├── background.png
│   ├── play_button.png
│   ├── play_button.svg
│   ├── pause_button.png
│   ├── pause_button.svg
│   ├── stop_button.png
│   ├── stop_button.svg
│   ├── config_button.png
│   ├── config_button.svg
│   ├── nav_left_button.png
│   ├── nav_left_button.svg
│   ├── nav_right_button.png
│   ├── nav_right_button.svg
│   ├── slider_track.png
│   └── slider_knob.png
```

### Available Themes

- **dark** (default): Dark gradient background with gray controls
- **light**: Light gradient background with light gray controls

### Creating Custom Themes

1. Create a new directory in `themes/` with your theme name:
   ```bash
   mkdir themes/mytheme
   ```

2. Add theme images (PNG or SVG format):
   - `background.png`: 1280x800 pixels main background
   - **Media Button Graphics** (PNG/SVG):
     - `play_button.png` or `play_button.svg`: 50x50 pixels
    - `pause_button.png` or `pause_button.svg`: 50x50 pixels (used as the Skip control)
     - `stop_button.png` or `stop_button.svg`: 50x50 pixels
     - `config_button.png` or `config_button.svg`: 50x50 pixels
   - **Navigation Button Graphics**:
     - `nav_left_button.png` or `nav_left_button.svg`: 60x80 pixels
     - `nav_right_button.png` or `nav_right_button.svg`: 60x80 pixels
   - **Legacy Support** (optional):
     - `slider_track.png`: Slider background track
     - `slider_knob.png`: Slider handle/knob

3. Theme auto-discovery: Restart application to see new theme in Configuration

### Advanced Theme Features

- **SVG Support**: Vector graphics scale perfectly at any resolution
- **PNG Fallbacks**: Automatic fallback to PNG if SVG unavailable
- **Color Fallbacks**: System defaults if no graphics found
- **Responsive Scaling**:
  - Fullscreen mode: Full-size graphics (1.0x scale)
  - Windowed mode: Proportional scaling (0.75x scale)
- **Real-time Switching**: No application restart required

### Theme Image Guidelines

- **Background**: Should be 1280x800 pixels or larger (auto-scaled to fit)
- **Media Buttons**: 50x50 pixels for consistency (PNG or SVG)
- **Navigation Buttons**: 60x80 pixels (taller than wide, PNG or SVG)
- **Format**: PNG with transparency or SVG for vector scaling
- **Colors**: Ensure good contrast for text visibility over backgrounds
- **SVG Benefits**: Perfect scaling, smaller file sizes, crisp at any resolution
- **Fallback Strategy**: Include both SVG and PNG versions for maximum compatibility

## Interface Layout - Professional 3-Column Design

### Main Screen Components

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                         JukeBox - Album Library                                   ║
║ Volume: [████████░░] [▶][⏸][⏹]                              [⚙]                  ║
├────────────────────┬────────────────────────┬────────────────────┤
│   LEFT COLUMN      │     CENTER COLUMN      │   RIGHT COLUMN     │
│  (Browse Albums)   │   (Now Playing Box)    │  (Browse Albums)   │
├────────────────────┤                        ├────────────────────┤
│ ┌───────────────┐  │  ┌──────────────────┐  │ ┌───────────────┐  │
│ │ [📀] Album 01 │  │  │ ♪ Now Playing    │  │ │ [📀] Album 03 │  │
│ │ Artist Name   │  │  │ ┌──────────────┐ │  │ │ Artist Name   │  │
│ │ Album Title   │  │  │ │ [Album Art]  │ │  │ │ Album Title   │  │
│ │ 13 tracks     │  │  │ │ with Number  │ │  │ │ 18 tracks     │  │
│ │ 1. Track...   │  │  │ └──────────────┘ │  │ │ 1. Track...   │  │
│ │ 2. Track...   │  │  │ ♫ Current Track  │  │ │ 2. Track...   │  │
│ └───────────────┘  │  │ Selection XX YY  │  │ └───────────────┘  │
│                    │  └──────────────────┘  │                    │
│ ┌───────────────┐  │                        │ ┌───────────────┐  │
│ │ [📀] Album 02 │  │     Browse Controls    │ │ [📀] Album 04 │  │
│ │ Artist Name   │  │                        │ │ Artist Name   │  │
│ │ Album Title   │  │                        │ │ Album Title   │  │
│ └───────────────┘  │                        │ └───────────────┘  │
├────────────────────┴────────────────────────┴────────────────────┤
│                   [<] 4-Digit Selection Pad [>]                   │
│                      ┌─────────────────────┐                      │
│                      │  Selection: ____    │                      │
│                      │ ┌─────────────────┐ │                      │
│                      │ │ [7] [8] [9]     │ │                      │
│                      │ │ [4] [5] [6]     │ │                      │
│                      │ │ [1] [2] [3]     │ │                      │
│                      │ │ [0] [<]         │ │                      │
│                      │ │ [CLR] [ENT]     │ │                      │
│                      │ └─────────────────┘ │                      │
│                      └─────────────────────┘                      │
├──────────────────────────────────────────────────────────────────┤
│ 4-digit: Album(2)+Track(2) | C: Config | Space: Play/Pause | Alt+Enter: Fullscreen │
╚══════════════════════════════════════════════════════════════════════════════════╝

Note: A new "Add Credit" button is displayed beneath the right-column album cards on the main screen. Each press adds one credit; starting playback consumes one credit (one press to play a song).
```

### Interactive Elements

#### Themed Controls (No Borders)
- **Media Buttons**: Play, Pause, Stop with PNG/SVG graphics
 - **Media Buttons**: Play, Skip, Stop with PNG/SVG graphics
- **Configuration Button**: Gear icon with theme styling
  - **Exit Button**: An "Exit" control sits to the right of the Config (gear) button on the top-right — it opens a confirmation dialog to make sure you want to quit the program.
- **Navigation Arrows**: Side buttons for album browsing

#### Bordered Controls (Text-based)
- **Number Pad**: Color-coded buttons with white borders
  - Numbers (0-9): Gray background
  - CLR: Red background (clear function)
  - ENT: Green background (enter function)
  - <: Blue background (backspace function)

#### Responsive Features
- **Hover Effects**: All buttons brighten 30% on mouse hover
- **Scaling**: Interface scales proportionally between fullscreen/windowed
- **Smart Layout**: 3-column design adapts to screen size
- **Real-time Feedback**: Immediate visual response to all interactions

## Current Status: ✅ PRODUCTION READY

### ✅ **Complete Feature Set**
- Professional 3-column album browsing interface
- Complete theming system with PNG/SVG support and real-time switching
- Rollover highlights and visual feedback on all interactive elements
- Responsive design scaling for fullscreen/windowed modes
- 4-digit selection system with real-time input display
- Enhanced Now Playing display with persistent track information
- Browse position system for efficient album navigation

### ✅ **Professional Polish**
- Themed media controls with automatic fallbacks
- Smart text wrapping and truncation for long titles
- Color-coded number pad with visual button states
- Semi-transparent interface borders for professional appearance
- Comprehensive keyboard shortcuts for all functions

## Project Structure

```
JukeBox/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point with enhanced UI
│   ├── player.py            # MusicPlayer - playback logic
│   ├── album_library.py     # Album/Library management (52 albums)
│   ├── metadata.py          # ID3 tag reading
│   ├── ui.py                # Enhanced user interface with theming
│   ├── config.py            # Configuration management
│   ├── theme.py             # Complete theme system (PNG/SVG support)
│   ├── audio_effects.py     # Equalizer and audio fading
│   └── widgets.py           # UI widgets (sliders, buttons)
├── themes/                  # Theme directories with graphics
│   ├── dark/                # Default dark theme
│   │   ├── background.png
│   │   ├── play_button.png
│   │   ├── pause_button.png
│   │   ├── stop_button.png
│   │   ├── config_button.png
│   │   ├── nav_left_button.png
│   │   └── nav_right_button.png
│   ├── light/               # Light theme
│   ├── matrix/              # Matrix digital theme
│   ├── neon/                # Neon cyberpunk theme
│   ├── wood/                # Wooden jukebox theme
│   ├── metal/               # Industrial metal theme
│   └── retro/               # Vintage jukebox theme
├── music/                   # Album directories (01-52)
│   ├── 01/
│   ├── 02/
│   └── ...
├── COMPREHENSIVE_THEMING.md # Complete theming documentation
├── MAIN_SCREEN_LAYOUT.md    # Interface layout documentation
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE

## Helpers

- `run.sh` — launcher script that activates `.venv` and runs the app
- `Makefile` — includes `make run` target
- `scripts/package-macos.sh` — creates unsigned `.dmg` (macOS only)
- `CONTRIBUTING.md` — run & packaging instructions
```

## Module Overview

### `metadata.py` - MetadataReader Class
- Reads ID3 tags from MP3, FLAC, OGG, and WAV files
- Extracts artist, album, title, and duration
- Formats duration to MM:SS
- Handles missing or incomplete metadata gracefully

### `album_library.py` - Enhanced Album Management
- **Album Class**: Represents individual albums with complete metadata
- **AlbumLibrary Class**: Manages all 52 album slots with advanced features
  - Scans numbered directories (01-52)
  - Smart metadata extraction and caching
  - Browse position system for efficient navigation
  - Real-time album discovery and indexing

### `player.py` - MusicPlayer
- Manages playback state
- Handles album and track navigation
- Volume control
- Export functionality

### `ui.py` - Enhanced User Interface
- Professional 3-column layout with responsive design
- Complete PNG/SVG button integration with rollover highlights
- Theme-aware rendering with automatic fallbacks
- Responsive scaling for fullscreen/windowed modes
- Real-time visual feedback for all user interactions
- Smart text handling with wrapping and truncation
- Browse position system with side navigation controls

### `theme.py` - Complete Theme System
- **Theme Class**: Comprehensive theme support with PNG/SVG graphics
  - Loads background images, media buttons, navigation controls
  - SVG support with automatic PNG fallbacks
  - Real-time theme switching without restart
  - Responsive button scaling for different screen modes
- **ThemeManager Class**: Advanced theme management
  - Auto-discovery of all themes in themes/ directory
  - Real-time theme switching via Configuration screen
  - Persistent theme preferences in user configuration
  - Support for custom user themes with automatic integration

### `config.py` - Configuration Management
- Loads/saves settings to JSON file
- Default location: `~/.jukebox_config.json`
- Stores: volume, theme, repeat mode, shuffle state, etc.

### `audio_effects.py` - Audio Processing
- **Equalizer Class**: 5-band audio equalization
  - Bands: 60Hz, 250Hz, 1kHz, 4kHz, 16kHz
  - Range: -12dB to +12dB per band
  - Built-in presets (flat, bass_boost, treble_boost, vocal)
- **AudioFader Class**: Smooth volume transitions
  - Fade-in/fade-out over specified duration
  - Smooth ramp from current to target volume

### `widgets.py` - UI Components
- **Slider**: Horizontal value adjustment widget
  - Drag-to-adjust with mouse
  - Visual feedback with hover/press states
  - Configurable min/max values
  - Theme color support
- **VerticalSlider**: Vertical slider for equalizer bands
  - Inherits from Slider with inverted Y-axis
  - Used for 5-band equalizer display

## Tips & Best Practices

### Album Organization
- **Complete Albums**: Keep full albums in numbered directories for best experience
- **Consistent Metadata**: Ensure audio files have proper ID3 tags for accurate display
- **Directory Naming**: Albums must be in numbered directories (01-52) for recognition
- **Smart Browsing**: Use side navigation buttons to browse 4 albums at a time

### Theme Customization
- **Graphics Format**: Use SVG for scalable vector graphics or PNG for pixel-perfect images
- **Consistent Sizing**: Follow recommended button sizes for professional appearance
- **Visual Testing**: Test themes in both fullscreen and windowed modes
- **Contrast Checking**: Ensure text remains readable over theme backgrounds

### Performance Tips
- **Theme Caching**: Themes are automatically cached for faster switching
- **Responsive Design**: Interface optimizes for current screen mode automatically
- **Memory Management**: Only current theme graphics loaded in memory

## Troubleshooting

### Albums not showing?
- Verify audio files are in numbered directories (01-52 with leading zeros)
- Check supported formats (MP3, WAV, OGG, FLAC)
- Ensure proper directory permissions for scanning

### Themed buttons not loading?
- Check theme directory structure matches requirements
- Verify PNG/SVG files are not corrupted
- System falls back to colored rectangles if graphics unavailable
- Check file permissions on theme directories

### Interface scaling issues?
- Toggle fullscreen mode with `Alt+Enter` to test both modes
- Interface automatically scales between 1.0x (fullscreen) and 0.75x (windowed)
- All elements maintain proportional scaling

### Theme switching problems?
- Restart application if themes not appearing in Configuration
- Check themes/ directory for proper subdirectory structure
- Verify theme files follow naming conventions (background.png, play_button.png, etc.)

### No metadata showing?
- Check audio files have proper ID3 tags (especially MP3 files)
- Some formats may need correct metadata encoding
- Files without tags display as "Unknown Artist/Album"

### Performance issues?
- Clear theme cache by restarting application
- Reduce background image size if experiencing slow loading
- Check system memory usage with large theme collections

## Future Enhancements

### Planned Features
- [ ] Embedded album artwork display (ID3v2 artwork extraction)
- [ ] Shuffle and repeat modes with visual indicators
- [ ] Seek/progress bar with click-to-seek functionality
- [ ] Playlist creation and management system
- [ ] Advanced search and filter capabilities
- [ ] Drag-and-drop album organization
- [ ] Theme preview without switching in Configuration screen

### Theme System Expansions
- [ ] Animated SVG button support
- [ ] Custom color scheme editor
- [ ] Theme marketplace integration
- [ ] Advanced theme validation tools
- [ ] Theme export/import functionality

### Interface Enhancements
- [ ] Customizable column layout options
- [ ] Advanced keyboard navigation
- [ ] Touch screen support optimization
- [ ] Multi-monitor support
- [ ] Accessibility features (screen reader support)

### Audio Features
- [ ] Advanced equalizer presets (Rock, Jazz, Classical, Electronic)
- [ ] Audio visualization effects
- [ ] Crossfade between tracks
- [ ] Volume normalization
- [ ] Audio format conversion tools

## License

See LICENSE file for details.
