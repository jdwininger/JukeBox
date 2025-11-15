"""
Theme Manager Module - Handles application theming with images
"""
import os
import pygame
from typing import Dict, Optional, Tuple


class Theme:
    """Represents a single theme with images and colors"""
    
    def __init__(self, theme_name: str, theme_dir: str):
        """
        Initialize a theme
        
        Args:
            theme_name: Name of the theme
            theme_dir: Path to the theme directory
        """
        self.name = theme_name
        self.theme_dir = theme_dir
        
        # Image paths
        self.background_path = os.path.join(theme_dir, 'background.png')
        self.button_path = os.path.join(theme_dir, 'button.png')
        self.button_hover_path = os.path.join(theme_dir, 'button_hover.png')
        self.button_pressed_path = os.path.join(theme_dir, 'button_pressed.png')
        self.slider_track_path = os.path.join(theme_dir, 'slider_track.png')
        self.slider_track_svg_path = os.path.join(theme_dir, 'slider_track.svg')
        self.slider_track_vertical_path = os.path.join(theme_dir, 'slider_track_vertical.png')
        self.slider_track_vertical_svg_path = os.path.join(theme_dir, 'slider_track_vertical.svg')
        self.slider_knob_path = os.path.join(theme_dir, 'slider_knob.png')
        
        # Loaded images
        self.background: Optional[pygame.Surface] = None
        self.button: Optional[pygame.Surface] = None
        self.button_hover: Optional[pygame.Surface] = None
        self.button_pressed: Optional[pygame.Surface] = None
        self.slider_track: Optional[pygame.Surface] = None
        self.slider_track_vertical: Optional[pygame.Surface] = None
        self.slider_knob: Optional[pygame.Surface] = None
        
        # Color scheme
        self.colors = {
            'background': (32, 32, 32),
            'text': (255, 255, 255),
            'text_secondary': (200, 200, 200),
            'accent': (100, 200, 100),
            'button': (64, 64, 64),
            'button_hover': (100, 100, 100),
            'button_pressed': (50, 50, 50),
        }
        
        # Load images
        self.load_images()
    
    def load_images(self) -> None:
        """Load theme images"""
        if os.path.exists(self.background_path):
            try:
                self.background = pygame.image.load(self.background_path)
            except Exception as e:
                print(f"Error loading background image: {e}")
        
        if os.path.exists(self.button_path):
            try:
                self.button = pygame.image.load(self.button_path)
            except Exception as e:
                print(f"Error loading button image: {e}")
        
        if os.path.exists(self.button_hover_path):
            try:
                self.button_hover = pygame.image.load(self.button_hover_path)
            except Exception as e:
                print(f"Error loading button_hover image: {e}")
        
        if os.path.exists(self.button_pressed_path):
            try:
                self.button_pressed = pygame.image.load(self.button_pressed_path)
            except Exception as e:
                print(f"Error loading button_pressed image: {e}")
        
        # Load slider track (horizontal)
        if os.path.exists(self.slider_track_path):
            try:
                self.slider_track = pygame.image.load(self.slider_track_path)
            except Exception as e:
                print(f"Error loading slider_track image: {e}")
        elif os.path.exists(self.slider_track_svg_path):
            try:
                # For SVG support, you'd need to install pygame-ce or use cairosvg
                # For now, we'll skip SVG loading but keep the structure
                print(f"SVG slider track found but SVG support not implemented: {self.slider_track_svg_path}")
            except Exception as e:
                print(f"Error loading slider_track SVG: {e}")
        
        # Load vertical slider track
        if os.path.exists(self.slider_track_vertical_path):
            try:
                self.slider_track_vertical = pygame.image.load(self.slider_track_vertical_path)
            except Exception as e:
                print(f"Error loading slider_track_vertical image: {e}")
        elif os.path.exists(self.slider_track_vertical_svg_path):
            try:
                # For SVG support, you'd need to install pygame-ce or use cairosvg
                print(f"Vertical SVG slider track found but SVG support not implemented: {self.slider_track_vertical_svg_path}")
            except Exception as e:
                print(f"Error loading slider_track_vertical SVG: {e}")
        
        if os.path.exists(self.slider_knob_path):
            try:
                self.slider_knob = pygame.image.load(self.slider_knob_path)
            except Exception as e:
                print(f"Error loading slider_knob image: {e}")
    
    def is_complete(self) -> bool:
        """Check if theme has all essential images"""
        return self.background is not None
    
    def get_background(self) -> Optional[pygame.Surface]:
        """Get background image"""
        return self.background
    
    def get_button_image(self, state: str = 'normal') -> Optional[pygame.Surface]:
        """Get button image for a given state"""
        if state == 'hover' and self.button_hover:
            return self.button_hover
        elif state == 'pressed' and self.button_pressed:
            return self.button_pressed
        return self.button
    
    def get_color(self, color_key: str, default: Tuple[int, int, int] = None) -> Tuple[int, int, int]:
        """Get color from theme"""
        if default is None:
            default = (128, 128, 128)
        return self.colors.get(color_key, default)


class ThemeManager:
    """Manages application themes"""
    
    def __init__(self, themes_dir: str = None):
        """
        Initialize theme manager
        
        Args:
            themes_dir: Path to themes directory
        """
        if themes_dir is None:
            themes_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
        
        self.themes_dir = themes_dir
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        
        self._ensure_themes_directory()
        self.discover_themes()
    
    def _ensure_themes_directory(self) -> None:
        """Ensure themes directory exists"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
            print(f"Created themes directory: {self.themes_dir}")
    
    def discover_themes(self) -> None:
        """Discover available themes"""
        self.themes = {}
        
        if not os.path.exists(self.themes_dir):
            print(f"Themes directory not found: {self.themes_dir}")
            return
        
        try:
            for item in os.listdir(self.themes_dir):
                theme_path = os.path.join(self.themes_dir, item)
                if os.path.isdir(theme_path):
                    theme = Theme(item, theme_path)
                    self.themes[item] = theme
                    print(f"Found theme: {item}")
        except Exception as e:
            print(f"Error discovering themes: {e}")
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get a theme by name"""
        return self.themes.get(theme_name)
    
    def set_current_theme(self, theme_name: str) -> bool:
        """
        Set the current active theme
        
        Args:
            theme_name: Name of theme to activate
            
        Returns:
            True if theme was set, False otherwise
        """
        theme = self.get_theme(theme_name)
        if theme:
            self.current_theme = theme
            print(f"Theme changed to: {theme_name}")
            return True
        else:
            print(f"Theme not found: {theme_name}")
            return False
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get the current active theme"""
        return self.current_theme
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return sorted(list(self.themes.keys()))
    
    def create_default_theme(self) -> None:
        """Create a default theme with placeholder images"""
        default_dir = os.path.join(self.themes_dir, 'default')
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)
            
            # Create a simple background surface
            bg_surface = pygame.Surface((1000, 700))
            bg_surface.fill((32, 32, 32))
            pygame.image.save(bg_surface, os.path.join(default_dir, 'background.png'))
            
            # Create simple button surface
            btn_surface = pygame.Surface((100, 50))
            btn_surface.fill((64, 64, 64))
            pygame.image.save(btn_surface, os.path.join(default_dir, 'button.png'))
            
            # Create button hover surface
            btn_hover_surface = pygame.Surface((100, 50))
            btn_hover_surface.fill((100, 100, 100))
            pygame.image.save(btn_hover_surface, os.path.join(default_dir, 'button_hover.png'))
            
            # Create button pressed surface
            btn_pressed_surface = pygame.Surface((100, 50))
            btn_pressed_surface.fill((50, 50, 50))
            pygame.image.save(btn_pressed_surface, os.path.join(default_dir, 'button_pressed.png'))
            
            print(f"Created default theme in: {default_dir}")
            self.discover_themes()
