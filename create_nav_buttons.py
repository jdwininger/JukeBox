#!/usr/bin/env python3
"""
Create navigation button images (left/right arrows) for all themes
"""
import os
import pygame

# Initialize pygame
pygame.init()

def create_navigation_buttons():
    """Create left and right navigation button images for all themes"""
    
    # Define theme configurations
    themes = {
        'dark': {
            'bg_color': (40, 40, 40),
            'arrow_color': (200, 200, 200),
            'border_color': (80, 80, 80)
        },
        'light': {
            'bg_color': (240, 240, 240),
            'arrow_color': (60, 60, 60),
            'border_color': (180, 180, 180)
        },
        'Jeremy': {
            'bg_color': (50, 20, 80),
            'arrow_color': (255, 215, 0),
            'border_color': (150, 100, 200)
        }
    }
    
    # Button dimensions - taller than wide
    width = 60
    height = 80
    
    for theme_name, colors in themes.items():
        print(f"Creating navigation buttons for {theme_name} theme...")
        
        # Ensure theme directory exists
        theme_dir = f"themes/{theme_name}"
        os.makedirs(theme_dir, exist_ok=True)
        
        # Create left button (< arrow)
        left_surface = pygame.Surface((width, height))
        left_surface.fill(colors['bg_color'])
        
        # Draw subtle border
        pygame.draw.rect(left_surface, colors['border_color'], left_surface.get_rect(), 2)
        
        # Draw left arrow (pointing left)
        arrow_points = [
            (width * 0.65, height * 0.25),  # Top right
            (width * 0.35, height * 0.5),   # Left point
            (width * 0.65, height * 0.75)   # Bottom right
        ]
        pygame.draw.polygon(left_surface, colors['arrow_color'], arrow_points)
        
        # Add some depth with a smaller inner arrow
        inner_points = [
            (width * 0.6, height * 0.3),
            (width * 0.4, height * 0.5),
            (width * 0.6, height * 0.7)
        ]
        pygame.draw.polygon(left_surface, colors['arrow_color'], inner_points, 2)
        
        # Save left button
        pygame.image.save(left_surface, f"{theme_dir}/left_button.png")
        
        # Create right button (> arrow)
        right_surface = pygame.Surface((width, height))
        right_surface.fill(colors['bg_color'])
        
        # Draw subtle border
        pygame.draw.rect(right_surface, colors['border_color'], right_surface.get_rect(), 2)
        
        # Draw right arrow (pointing right)
        arrow_points = [
            (width * 0.35, height * 0.25),  # Top left
            (width * 0.65, height * 0.5),   # Right point
            (width * 0.35, height * 0.75)   # Bottom left
        ]
        pygame.draw.polygon(right_surface, colors['arrow_color'], arrow_points)
        
        # Add some depth with a smaller inner arrow
        inner_points = [
            (width * 0.4, height * 0.3),
            (width * 0.6, height * 0.5),
            (width * 0.4, height * 0.7)
        ]
        pygame.draw.polygon(right_surface, colors['arrow_color'], inner_points, 2)
        
        # Save right button
        pygame.image.save(right_surface, f"{theme_dir}/right_button.png")
        
        print(f"✓ Created navigation buttons for {theme_name} theme")

if __name__ == "__main__":
    create_navigation_buttons()
    print("✓ Navigation button images created for all themes")