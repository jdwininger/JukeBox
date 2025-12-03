#!/usr/bin/env python3
"""
Create default theme images for JukeBox
"""
import os
from pathlib import Path

import pygame


def create_dark_theme():
    """Create dark theme images"""
    # Initialize pygame for image creation
    pygame.init()

    theme_dir = Path("themes/dark")
    theme_dir.mkdir(parents=True, exist_ok=True)

    # Background image (dark gradient)
    background = pygame.Surface((1000, 700))
    for y in range(700):
        # Gradient from dark gray to black
        color_val = int(64 * (1 - y / 700))
        pygame.draw.line(
            background, (color_val, color_val, color_val), (0, y), (1000, y)
        )
    pygame.image.save(background, str(theme_dir / "background.png"))
    print(f"✓ Created {theme_dir / 'background.png'}")

    # Button image (gray rectangle)
    button = pygame.Surface((90, 40))
    button.fill((100, 100, 100))
    pygame.draw.rect(button, (255, 255, 255), button.get_rect(), 2)
    pygame.image.save(button, str(theme_dir / "button.png"))
    print(f"✓ Created {theme_dir / 'button.png'}")

    # Button hover image (lighter gray)
    button_hover = pygame.Surface((90, 40))
    button_hover.fill((150, 150, 150))
    pygame.draw.rect(button_hover, (255, 255, 255), button_hover.get_rect(), 2)
    pygame.image.save(button_hover, str(theme_dir / "button_hover.png"))
    print(f"✓ Created {theme_dir / 'button_hover.png'}")

    # Button pressed image (darker)
    button_pressed = pygame.Surface((90, 40))
    button_pressed.fill((80, 80, 80))
    pygame.draw.rect(button_pressed, (200, 200, 200), button_pressed.get_rect(), 2)
    pygame.image.save(button_pressed, str(theme_dir / "button_pressed.png"))
    print(f"✓ Created {theme_dir / 'button_pressed.png'}")

    # Slider track image (horizontal line)
    slider_track = pygame.Surface((200, 4))
    slider_track.fill((80, 80, 80))
    pygame.image.save(slider_track, str(theme_dir / "slider_track.png"))
    print(f"✓ Created {theme_dir / 'slider_track.png'}")

    # Slider knob image (small circle)
    slider_knob = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(slider_knob, (200, 200, 200), (10, 10), 8)
    pygame.draw.circle(slider_knob, (255, 255, 255), (10, 10), 8, 2)
    pygame.image.save(slider_knob, str(theme_dir / "slider_knob.png"))
    print(f"✓ Created {theme_dir / 'slider_knob.png'}")

    pygame.quit()
    print(f"\n✓ Dark theme created successfully in {theme_dir}")


def create_light_theme():
    """Create light theme images"""
    # Initialize pygame for image creation
    pygame.init()

    theme_dir = Path("themes/light")
    theme_dir.mkdir(parents=True, exist_ok=True)

    # Background image (light gradient)
    background = pygame.Surface((1000, 700))
    for y in range(700):
        # Gradient from light gray to white
        color_val = int(200 + 55 * (y / 700))
        pygame.draw.line(
            background, (color_val, color_val, color_val), (0, y), (1000, y)
        )
    pygame.image.save(background, str(theme_dir / "background.png"))
    print(f"✓ Created {theme_dir / 'background.png'}")

    # Button image (light button)
    button = pygame.Surface((90, 40))
    button.fill((200, 200, 200))
    pygame.draw.rect(button, (100, 100, 100), button.get_rect(), 2)
    pygame.image.save(button, str(theme_dir / "button.png"))
    print(f"✓ Created {theme_dir / 'button.png'}")

    # Button hover image (lighter)
    button_hover = pygame.Surface((90, 40))
    button_hover.fill((220, 220, 220))
    pygame.draw.rect(button_hover, (80, 80, 80), button_hover.get_rect(), 2)
    pygame.image.save(button_hover, str(theme_dir / "button_hover.png"))
    print(f"✓ Created {theme_dir / 'button_hover.png'}")

    # Button pressed image (darker)
    button_pressed = pygame.Surface((90, 40))
    button_pressed.fill((180, 180, 180))
    pygame.draw.rect(button_pressed, (100, 100, 100), button_pressed.get_rect(), 2)
    pygame.image.save(button_pressed, str(theme_dir / "button_pressed.png"))
    print(f"✓ Created {theme_dir / 'button_pressed.png'}")

    # Slider track image (horizontal line)
    slider_track = pygame.Surface((200, 4))
    slider_track.fill((180, 180, 180))
    pygame.image.save(slider_track, str(theme_dir / "slider_track.png"))
    print(f"✓ Created {theme_dir / 'slider_track.png'}")

    # Slider knob image (small circle)
    slider_knob = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(slider_knob, (100, 100, 100), (10, 10), 8)
    pygame.draw.circle(slider_knob, (50, 50, 50), (10, 10), 8, 2)
    pygame.image.save(slider_knob, str(theme_dir / "slider_knob.png"))
    print(f"✓ Created {theme_dir / 'slider_knob.png'}")

    pygame.quit()
    print(f"\n✓ Light theme created successfully in {theme_dir}")


if __name__ == "__main__":
    os.chdir("/Users/jeremy/Source/JukeBox/JukeBox")
    print("Creating JukeBox theme images...\n")
    create_dark_theme()
    create_light_theme()
    print("\n✓ All themes created successfully!")
