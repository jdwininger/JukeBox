#!/usr/bin/env python3
"""
Create sample media control button images for themes
"""
import pygame
import os
from pathlib import Path
import math

def create_media_button_images():
    """Create sample media control button images"""
    pygame.init()

    # Create button image directories
    for theme_name in ['dark', 'light', 'Jeremy']:
        theme_dir = Path(f"themes/{theme_name}")
        theme_dir.mkdir(parents=True, exist_ok=True)

        create_theme_media_buttons(theme_dir, theme_name)

    pygame.quit()
    print("✓ Media control button images created for all themes")

def create_theme_media_buttons(theme_dir: Path, theme_name: str):
    """Create media control buttons for a specific theme"""
    button_size = (64, 64)

    # Theme-specific colors
    if theme_name == 'dark':
        bg_color = (40, 40, 40)
        icon_color = (220, 220, 220)
        border_color = (100, 100, 100)
    elif theme_name == 'light':
        bg_color = (240, 240, 240)
        icon_color = (60, 60, 60)
        border_color = (160, 160, 160)
    else:  # Jeremy theme
        bg_color = (60, 80, 100)
        icon_color = (255, 255, 255)
        border_color = (120, 140, 160)

    # Play button (triangle pointing right)
    play_surface = pygame.Surface(button_size, pygame.SRCALPHA)
    play_surface.fill((0, 0, 0, 0))  # Transparent background

    # Background circle
    pygame.draw.circle(play_surface, bg_color, (32, 32), 30)
    pygame.draw.circle(play_surface, border_color, (32, 32), 30, 2)

    # Play triangle
    triangle_points = [(20, 16), (20, 48), (48, 32)]
    pygame.draw.polygon(play_surface, icon_color, triangle_points)

    pygame.image.save(play_surface, str(theme_dir / "play_button.png"))

    # Pause button (two vertical bars)
    pause_surface = pygame.Surface(button_size, pygame.SRCALPHA)
    pause_surface.fill((0, 0, 0, 0))  # Transparent background

    # Background circle
    pygame.draw.circle(pause_surface, bg_color, (32, 32), 30)
    pygame.draw.circle(pause_surface, border_color, (32, 32), 30, 2)

    # Pause bars
    bar1 = pygame.Rect(22, 18, 6, 28)
    bar2 = pygame.Rect(36, 18, 6, 28)
    pygame.draw.rect(pause_surface, icon_color, bar1)
    pygame.draw.rect(pause_surface, icon_color, bar2)

    pygame.image.save(pause_surface, str(theme_dir / "pause_button.png"))

    # Stop button (square)
    stop_surface = pygame.Surface(button_size, pygame.SRCALPHA)
    stop_surface.fill((0, 0, 0, 0))  # Transparent background

    # Background circle
    pygame.draw.circle(stop_surface, bg_color, (32, 32), 30)
    pygame.draw.circle(stop_surface, border_color, (32, 32), 30, 2)

    # Stop square
    stop_rect = pygame.Rect(20, 20, 24, 24)
    pygame.draw.rect(stop_surface, icon_color, stop_rect)

    pygame.image.save(stop_surface, str(theme_dir / "stop_button.png"))

    # Config button (gear)
    config_surface = pygame.Surface(button_size, pygame.SRCALPHA)
    config_surface.fill((0, 0, 0, 0))  # Transparent background

    # Background circle
    pygame.draw.circle(config_surface, bg_color, (32, 32), 30)
    pygame.draw.circle(config_surface, border_color, (32, 32), 30, 2)

    # Draw gear
    center_x, center_y = 32, 32
    radius = 18

    # Draw gear teeth (8 teeth)
    teeth_points = []
    for i in range(16):  # 8 teeth, 2 points each
        angle = i * math.pi / 8
        if i % 2 == 0:
            # Outer tooth point
            tooth_radius = radius + 4
        else:
            # Inner tooth point
            tooth_radius = radius
        x = center_x + tooth_radius * math.cos(angle)
        y = center_y + tooth_radius * math.sin(angle)
        teeth_points.append((x, y))

    # Draw gear outline
    if len(teeth_points) > 2:
        pygame.draw.polygon(config_surface, icon_color, teeth_points)

    # Draw inner circle
    inner_radius = radius // 2
    pygame.draw.circle(config_surface, bg_color, (center_x, center_y), inner_radius)
    pygame.draw.circle(config_surface, icon_color, (center_x, center_y), inner_radius, 2)

    pygame.image.save(config_surface, str(theme_dir / "config_button.png"))

    print(f"✓ Created media buttons for {theme_name} theme")

if __name__ == "__main__":
    create_media_button_images()
