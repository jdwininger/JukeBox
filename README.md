# JukeBox - Python Album Library Music Player

A sophisticated music jukebox application built with Python, pygame, and SDL2 that manages up to 50 albums with full ID3 tag metadata extraction.

## Features

### Album Management
- **50 Album Limit**: Organize music into up to 50 numbered albums (01-50)
- **Auto-Detection**: Automatically scans numbered directories for audio files
- **ID3 Tag Reading**: Extracts artist, album name, track title, and duration from audio files
- **Multiple Formats**: Supports MP3, WAV, OGG, and FLAC files

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
- Play, pause, stop functionality
- Navigate between tracks within an album
- Navigate between albums in the library
- Auto-advance to next track when current finishes
- Volume control (0-100%)

### User Interface
- **Album Library View**: Display of all available albums
- **Current Album Display**: Shows artist, album title, track list
- **Status Display**: Real-time playback status and volume
- **Library Statistics**: Total albums, tracks, and duration
- **Configuration Screen**: Manage settings, rescan library, export data
- **4-Digit Selection System**: Quick track selection by album/track number
- **Clickable Number Pad**: GUI-based number entry
  - Access via Configuration screen (Equalizer button)
  - Dark theme (default) - Dark gradient background with gray controls
  - Light theme - Light gradient background with light gray controls
  - Extensible theme directory structure for custom themes

### Keyboard Shortcuts
- `Space`: Play/Pause
- `←→`: Previous/Next track (within album)
- `N`/`P`: Previous/Next album
- `↑↓`: Increase/Decrease volume
- `E`: Export library to CSV
- `C`: Toggle configuration screen

## Requirements

- Python 3.8+
- pygame >= 2.5.0
- mutagen >= 1.45.0
- SDL2 (installed automatically with pygame)


1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
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
```

Notes for Linux:
- Ensure SDL2 and related system libraries are installed for `pygame` to initialize the display and audio.
- On headless servers, run within an X/Wayland session or use a virtual framebuffer (e.g., `Xvfb`).

### Setting Up Your Album Library

1. Create numbered album directories in the `music/` folder:
   ```
   music/
   ├── 01/
   ├── 02/
   ├── 03/
   ...
   ├── 50/
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

### (Removed Feature)

Previous versions included CSV export functionality. This feature has been removed to simplify the interface.

## Theme System

JukeBox includes a flexible theming system that allows you to customize the application's appearance with background images and themed button/slider designs.

### Theme Directory Structure

Themes are stored in the `themes/` directory with the following structure:

```
themes/
├── dark/                       # Dark theme
│   ├── background.png         # Main background image
│   ├── button.png             # Normal button appearance
│   ├── button_hover.png       # Button when hovered
│   ├── button_pressed.png     # Button when pressed
│   ├── slider_track.png       # Slider track/background
│   └── slider_knob.png        # Slider knob/handle
├── light/                      # Light theme
│   ├── background.png
│   ├── button.png
│   ├── button_hover.png
│   ├── button_pressed.png
│   ├── slider_track.png
│   └── slider_knob.png
└── custom/                     # Create your own themes here
    ├── background.png
    ├── button.png
    ├── button_hover.png
    ├── button_pressed.png
    ├── slider_track.png
    └── slider_knob.png
```

### Available Themes

- **dark** (default): Dark gradient background with gray controls
- **light**: Light gradient background with light gray controls

### Creating Custom Themes

1. Create a new directory in `themes/` with your theme name:
   ```bash
   mkdir themes/mytheme
   ```

2. Add theme images (PNG format recommended):
  - `background.png`: 1280x800 pixels (current default window size; larger images will be scaled)
   - `button.png`: Button appearance (any size, will be scaled)
   - `button_hover.png`: Button hover state
   - `button_pressed.png`: Button pressed state
   - `slider_track.png`: Slider background track
   - `slider_knob.png`: Slider handle/knob

3. (Optional) Edit `~/.jukebox_config.json` to set your theme as default:
   ```json
   {
     "theme": "mytheme"
   }
   ```

### Theme Image Guidelines

- **Background**: Should be 1280x800 pixels or larger (will be scaled)
- **Buttons**: Suggest 90x40 pixels for consistency
- **Sliders**: Track around 200x4 pixels, knob around 20x20 pixels
- **Format**: PNG with transparency support recommended
- **Colors**: Ensure good contrast for button text visibility

## Project Structure

```
JukeBox/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── player.py            # MusicPlayer - playback logic
│   ├── album_library.py     # Album/Library management
│   ├── metadata.py          # ID3 tag reading
│   ├── ui.py                # User interface
│   ├── config.py            # Configuration management
│   ├── theme.py             # Theme system
│   ├── audio_effects.py     # Equalizer and audio fading
│   └── widgets.py           # UI widgets (sliders)
├── themes/                  # Theme directories
│   ├── dark/                # Default dark theme
│   └── light/               # Light theme
├── music/                   # Album directories (01-50)
│   ├── 01/
│   ├── 02/
│   └── ...
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE

## Helpers

- `run.sh` — a small launcher script that activates the `.venv` (if present) and runs the app.
- `Makefile` — includes a `make run` target that invokes `./run.sh`.
- `scripts/package-macos.sh` — helper script to create an unsigned `.dmg` from the included `JukeBox.app` (macOS only).
- `CONTRIBUTING.md` — contains run & packaging instructions.
```

## Module Overview

### `metadata.py` - MetadataReader Class
- Reads ID3 tags from MP3, FLAC, OGG, and WAV files
- Extracts artist, album, title, and duration
- Formats duration to MM:SS
- Handles missing or incomplete metadata gracefully

### `album_library.py` - Album Management
- **Album Class**: Represents a single album with tracks
- **AlbumLibrary Class**: Manages all 50 album slots
  - Scans numbered directories
  - Tracks valid albums
  - Exports to CSV format
  - Provides library statistics

### `player.py` - MusicPlayer
- Manages playback state
- Handles album and track navigation
- Volume control
- Export functionality

### `ui.py` - User Interface
- Pygame-based graphical interface
- Button controls and keyboard shortcuts
- Album and track listing
- Library statistics display
- Theme integration for background and button images

### `theme.py` - Theme System
- **Theme Class**: Represents a single theme with images and colors
  - Loads PNG images for backgrounds and controls
  - Provides fallback colors when images unavailable
  - Image types: background, button, button_hover, button_pressed, slider_track, slider_knob
- **ThemeManager Class**: Manages theme discovery and switching
  - Automatically discovers themes in `themes/` directory
  - Switches themes dynamically
  - Persists theme preference to configuration

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

- **Organize by Album**: Keep complete albums in each directory for best results
- **Consistent Tagging**: Ensure MP3/audio files have proper ID3 tags for accurate metadata
- **Directory Naming**: Albums must be in numbered directories (01-50) to be recognized

## Troubleshooting

### Albums not showing?
- Verify audio files are in numbered directories (01, 02, etc.)
- Check that files use supported formats (MP3, WAV, OGG, FLAC)
- Ensure directory names are exactly 2 digits with leading zero if needed

### No metadata showing?
- Check that audio files have proper ID3 tags (especially MP3 files)
- Some formats may need correct metadata encoding
- Files without tags will show as "Unknown"

### No sound playing?
- Verify system audio is working
- Check file permissions on audio files
- Try a different audio format to isolate the issue

### Removed Export Feature
If you are looking for CSV export present in earlier versions, retrieve it from a prior commit or re-implement using the `AlbumLibrary` class.

## Future Enhancements

- [ ] Album artwork display (ID3v2 embedded artwork)
- [ ] Shuffle and repeat modes
- [ ] Seek/progress bar visualization
- [ ] Playlist creation and management
- [ ] Search and filter functionality
- [ ] Now Playing indicators
- [ ] Track time display (current/total)
- [ ] Drag-and-drop album management
- [ ] Theme preview in configuration screen
- [ ] Preset equalizer profiles (Rock, Jazz, Classical, etc.)

## License

See LICENSE file for details.
A jukebox written with pygame
