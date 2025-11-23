#!/usr/bin/env python3
"""
generate-icon.py - Generate a JukeBox icon (256x256 PNG) using PIL.
Usage: python3 scripts/generate-icon.py [output_path]
Default output: assets/icon.png
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)

def generate_icon(output_path="assets/icon.png"):
    """Generate a colorful JukeBox icon."""
    size = 256
    img = Image.new("RGBA", (size, size), (30, 30, 40, 255))  # Dark blue-gray background
    draw = ImageDraw.Draw(img)

    # Draw a stylized speaker/jukebox shape
    # Speaker cone (left)
    cone_x, cone_y = 50, 80
    cone_size = 60
    draw.ellipse([cone_x, cone_y, cone_x + cone_size, cone_y + cone_size],
                 fill=(100, 150, 255), outline=(50, 100, 200), width=3)

    # Speaker cone 2 (right)
    cone_x2 = 150
    draw.ellipse([cone_x2, cone_y, cone_x2 + cone_size, cone_y + cone_size],
                 fill=(100, 150, 255), outline=(50, 100, 200), width=3)

    # Center display (music wave visualization)
    display_y = 160
    for i in range(0, 30, 5):
        bar_height = 15 + (i * 2)
        x = 70 + i
        y_center = display_y + 20
        draw.rectangle([x, y_center - bar_height // 2, x + 3, y_center + bar_height // 2],
                       fill=(0, 255, 100), outline=(0, 200, 80), width=1)

    # Text label
    try:
        draw.text((size // 2, size - 30), "JukeBox", fill=(200, 200, 200), anchor="mm")
    except Exception:
        # Font not available on some systems; skip text
        pass

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    img.save(output_file, "PNG")
    print(f"Generated icon: {output_path}")

if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "assets/icon.png"
    generate_icon(output)
