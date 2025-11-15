# JukeBox Theming Guide

## Overview

The JukeBox application now includes a complete theming system that allows you to customize the visual appearance using background images and themed UI elements. Themes are stored in the `themes/` directory with a simple, organized structure.

## Built-in Themes

### Dark Theme (Default)
- **Location**: `themes/dark/`
- **Description**: Dark gradient background with gray controls
- **Best for**: Low-light environments, reduced eye strain

### Light Theme
- **Location**: `themes/light/`
- **Description**: Light gradient background with light gray controls
- **Best for**: Bright environments, high contrast reading

## Theme Directory Structure

Each theme requires the following structure:

```
themes/
└── theme_name/
    ├── background.png       # Main background (1000x700 recommended)
    ├── button.png           # Normal button state
    ├── button_hover.png     # Button when mouse hovers over it
    ├── button_pressed.png   # Button when clicked/pressed
    ├── slider_track.png     # Slider background/track
    └── slider_knob.png      # Slider handle/control point
```

## Creating a Custom Theme

### Step 1: Create Theme Directory

```bash
mkdir themes/mytheme
```

### Step 2: Create Theme Images

Create PNG images for each component:

1. **background.png** (1000x700 pixels)
   - Main application background
   - Used as the foundation for the UI
   - Larger images will be scaled down

2. **button.png** (recommended 90x40 pixels)
   - Normal button appearance
   - Used for most UI buttons

3. **button_hover.png** (90x40 pixels)
   - Button appearance when mouse hovers over it
   - Should be visually distinct from normal state

4. **button_pressed.png** (90x40 pixels)
   - Button appearance when clicked
   - Should indicate pressed/active state

5. **slider_track.png** (200x4 pixels)
   - Background for slider controls
   - Used for volume, equalizer, etc.

6. **slider_knob.png** (20x20 pixels)
   - Handle/control point for sliders
   - Should be clearly visible on slider track

### Step 3: Use Your Theme

#### Option A: Set as Default Theme

Edit `~/.jukebox_config.json`:

```json
{
  "theme": "mytheme",
  "volume": 0.7,
  "auto_play_next": true
}
```

#### Option B: Switch Themes Via Config Screen

1. Run JukeBox
2. Click the "Config" button
3. Select your theme (future enhancement)

## Image Design Tips

### Color Scheme Recommendations

#### Dark Theme Colors
- Background: Dark grays (#1a1a1a to #4a4a4a)
- Buttons: Medium gray (#646464) with lighter hover (#969696)
- Text: White (#ffffff)
- Accents: Bright greens/blues for active elements

#### Light Theme Colors
- Background: Light grays (#c8c8c8 to #f0f0f0)
- Buttons: Light gray (#c8c8c8) with lighter hover (#dcdcdc)
- Text: Dark (#333333)
- Accents: Blues/purples for active elements

### Design Guidelines

1. **Consistency**: Maintain consistent visual style across all images
2. **Contrast**: Ensure sufficient contrast between background and text
3. **Visibility**: Make interactive elements clearly distinguishable
4. **Size**: Follow recommended sizes for proper scaling
5. **Format**: Use PNG format for transparency support

### Image Creation Tools

Popular tools for creating theme images:

- **GIMP** (Free, cross-platform)
- **Aseprite** (Pixel art focused)
- **Photoshop** (Professional)
- **Krita** (Open source, drawing focused)
- **Online editors**: Pixlr, Photopea

## Technical Details

### Image Loading

The ThemeManager automatically:
1. Discovers themes in the `themes/` directory
2. Loads theme images on demand
3. Provides fallback colors if images fail to load
4. Caches images in memory

### Fallback Colors

If theme images are unavailable, JukeBox uses fallback colors:

- Slider track: RGB(100, 100, 100)
- Slider knob: RGB(200, 200, 200)
- Accent color: RGB(100, 200, 100)

### Supported Image Formats

- PNG (recommended, supports transparency)
- JPG (supported, no transparency)
- BMP (supported)
- GIF (supported)

## Example: Creating a "Cyberpunk" Theme

### 1. Create directory
```bash
mkdir themes/cyberpunk
```

### 2. Design images with:
- Neon colors (bright cyan, magenta, yellow)
- Dark black background with neon accents
- Geometric, angular button designs
- High contrast for visibility

### 3. Save images to `themes/cyberpunk/`

### 4. Configure (optional):
```json
{
  "theme": "cyberpunk"
}
```

## Troubleshooting

### Theme Not Loading

1. Verify directory name is correct: `themes/theme_name/`
2. Check all required files exist and are PNG format
3. Ensure no spaces in directory name (use underscores instead)
4. Check file permissions

### Images Look Distorted

1. Verify background.png is PNG format
2. Check background size (1000x700 or larger)
3. Try recreating images with correct dimensions

### Theme Not Switching

1. Ensure theme directory exists with all required files
2. Restart application to apply new theme
3. Check `~/.jukebox_config.json` has correct theme name

## File Size Optimization

Keep images small for faster loading:

- **background.png**: 3-5 KB (1000x700)
- **button.png**: 150-200 bytes (90x40)
- **slider_track.png**: 100 bytes (200x4)
- **slider_knob.png**: 150 bytes (20x20)

Typical total theme size: ~4-6 KB

## Advanced: Theme Configuration

Future enhancement: Additional theme settings file (`theme.json`)

```json
{
  "name": "Cyberpunk",
  "author": "Your Name",
  "version": "1.0",
  "description": "A neon-themed cyberpunk interface",
  "colors": {
    "primary": "#FF00FF",
    "secondary": "#00FFFF",
    "background": "#0A0E27"
  }
}
```

## Sharing Your Theme

To share your theme with others:

1. Create a theme following guidelines above
2. Test thoroughly on different systems
3. Create a README with:
   - Theme name and description
   - Color scheme information
   - Installation instructions
   - Screenshots
4. Share via GitHub or forums

## Contributing Themes

To contribute themes to the JukeBox project:

1. Create your theme directory
2. Include all required image files
3. Submit as a GitHub pull request
4. Include proper attribution and license

---

**For more information**, see the main [README.md](README.md) file.
