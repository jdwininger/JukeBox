"""
JukeBox - A music player application using pygame and SDL2
"""
import pygame
import sys
import os
from src.player import MusicPlayer
from src.album_library import AlbumLibrary
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI


def main():
    """Main entry point for the JukeBox application"""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Load configuration
    config = Config()
    
    # Initialize theme system
    theme_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
    theme_manager = ThemeManager(theme_dir)
    theme_manager.discover_themes()
    theme_name = config.get('theme', 'dark')  # Default to 'dark' theme
    if not theme_manager.set_current_theme(theme_name):
        # Fallback to first available theme if configured theme not found
        available = theme_manager.get_available_themes()
        if available:
            theme_manager.set_current_theme(available[0])
        else:
            print("Warning: No themes available")
    
    # Setup library
    music_dir = os.path.join(os.path.dirname(__file__), '..', 'music')
    library = AlbumLibrary(music_dir)
    library.scan_library()
    
    # Create the UI first (which creates the equalizer)
    ui = UI(None, library, config, theme_manager)  # Pass None for player initially
    
    # Create the player with the equalizer from UI
    player = MusicPlayer(library, ui.equalizer)
    
    # Now set the player in the UI
    ui.player = player
    
    # Run the application
    ui.run()
    
    # Cleanup
    player.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
