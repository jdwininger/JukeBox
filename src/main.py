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
    theme_name = config.get('theme', 'default')
    theme_manager.set_current_theme(theme_name)
    
    # Setup library
    music_dir = os.path.join(os.path.dirname(__file__), '..', 'music')
    library = AlbumLibrary(music_dir)
    library.scan_library()
    
    # Create the player and UI
    player = MusicPlayer(library)
    ui = UI(player, library, config, theme_manager)
    
    # Run the application
    ui.run()
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
