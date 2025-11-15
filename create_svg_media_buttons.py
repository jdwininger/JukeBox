#!/usr/bin/env python3
"""
Create sample SVG media control button images for themes
"""
from pathlib import Path

def create_svg_media_buttons():
    """Create SVG versions of media control buttons"""
    # Create SVG button images for each theme
    for theme_name in ['dark', 'light', 'Jeremy']:
        theme_dir = Path(f"themes/{theme_name}")
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        create_theme_svg_buttons(theme_dir, theme_name)
    
    print("✓ SVG media control button images created for all themes")

def create_theme_svg_buttons(theme_dir: Path, theme_name: str):
    """Create SVG media control buttons for a specific theme"""
    
    # Theme-specific colors
    if theme_name == 'dark':
        bg_color = "#282828"
        icon_color = "#DCDCDC"
        border_color = "#646464"
    elif theme_name == 'light':
        bg_color = "#F0F0F0"
        icon_color = "#3C3C3C"
        border_color = "#A0A0A0"
    else:  # Jeremy theme
        bg_color = "#3C5064"
        icon_color = "#FFFFFF"
        border_color = "#788CA0"
    
    # Play button SVG
    play_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>
  <polygon points="20,16 20,48 48,32" fill="{icon_color}"/>
</svg>"""
    
    # Pause button SVG
    pause_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>
  <rect x="22" y="18" width="6" height="28" fill="{icon_color}"/>
  <rect x="36" y="18" width="6" height="28" fill="{icon_color}"/>
</svg>"""
    
    # Stop button SVG
    stop_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>
  <rect x="20" y="20" width="24" height="24" fill="{icon_color}"/>
</svg>"""
    
    # Config button SVG (gear)
    config_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>
  <g transform="translate(32,32)">
    <path d="M-18,0 L-16,-4 L-12,-4 L-14,0 L-12,4 L-16,4 Z M-12.7,-12.7 L-9.9,-15.5 L-7.1,-12.7 L-9.9,-9.9 L-12.7,-12.7 Z M0,-18 L4,-16 L4,-12 L0,-14 L-4,-12 L-4,-16 Z M12.7,-12.7 L15.5,-9.9 L12.7,-7.1 L9.9,-9.9 L12.7,-12.7 Z M18,0 L16,4 L12,4 L14,0 L12,-4 L16,-4 Z M12.7,12.7 L9.9,15.5 L7.1,12.7 L9.9,9.9 L12.7,12.7 Z M0,18 L-4,16 L-4,12 L0,14 L4,12 L4,16 Z M-12.7,12.7 L-15.5,9.9 L-12.7,7.1 L-9.9,9.9 L-12.7,12.7 Z" fill="{icon_color}"/>
    <circle cx="0" cy="0" r="8" fill="{bg_color}" stroke="{icon_color}" stroke-width="2"/>
  </g>
</svg>"""
    
    # Write SVG files
    (theme_dir / "play_button.svg").write_text(play_svg)
    (theme_dir / "pause_button.svg").write_text(pause_svg)
    (theme_dir / "stop_button.svg").write_text(stop_svg)
    (theme_dir / "config_button.svg").write_text(config_svg)
    
    print(f"✓ Created SVG media buttons for {theme_name} theme")

if __name__ == "__main__":
    create_svg_media_buttons()