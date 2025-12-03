#!/usr/bin/env python3
"""
Create SVG navigation button images (left/right arrows) for all themes
"""
import os


def create_svg_navigation_buttons():
    """Create SVG left and right navigation button images for all themes"""

    # Define theme configurations
    themes = {
        "dark": {
            "bg_color": "#282828",
            "arrow_color": "#C8C8C8",
            "border_color": "#505050",
        },
        "light": {
            "bg_color": "#F0F0F0",
            "arrow_color": "#3C3C3C",
            "border_color": "#B4B4B4",
        },
        "Jeremy": {
            "bg_color": "#321450",
            "arrow_color": "#FFD700",
            "border_color": "#9664C8",
        },
    }

    # Button dimensions - taller than wide
    width = 60
    height = 80

    for theme_name, colors in themes.items():
        print(f"Creating SVG navigation buttons for {theme_name} theme...")

        # Ensure theme directory exists
        theme_dir = f"themes/{theme_name}"
        os.makedirs(theme_dir, exist_ok=True)

        # Create left button SVG (< arrow)
        left_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="{colors['bg_color']}" stroke="{colors['border_color']}" stroke-width="2"/>
  <polygon points="{width * 0.65},{height * 0.25} {width * 0.35},{height * 0.5} {width * 0.65},{height * 0.75}"
           fill="{colors['arrow_color']}"/>
  <polygon points="{width * 0.6},{height * 0.3} {width * 0.4},{height * 0.5} {width * 0.6},{height * 0.7}"
           fill="none" stroke="{colors['arrow_color']}" stroke-width="2"/>
</svg>"""

        with open(f"{theme_dir}/left_button.svg", "w") as f:
            f.write(left_svg)

        # Create right button SVG (> arrow)
        right_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="{colors['bg_color']}" stroke="{colors['border_color']}" stroke-width="2"/>
  <polygon points="{width * 0.35},{height * 0.25} {width * 0.65},{height * 0.5} {width * 0.35},{height * 0.75}"
           fill="{colors['arrow_color']}"/>
  <polygon points="{width * 0.4},{height * 0.3} {width * 0.6},{height * 0.5} {width * 0.4},{height * 0.7}"
           fill="none" stroke="{colors['arrow_color']}" stroke-width="2"/>
</svg>"""

        with open(f"{theme_dir}/right_button.svg", "w") as f:
            f.write(right_svg)

        print(f"✓ Created SVG navigation buttons for {theme_name} theme")


if __name__ == "__main__":
    create_svg_navigation_buttons()
    print("✓ SVG navigation button images created for all themes")
