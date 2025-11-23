"""
Configuration Module - Handles application settings and configuration
"""
import json
import os
from typing import Dict, Any


class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        'auto_play_next': True,
        'shuffle_enabled': False,
        'repeat_mode': 'off',  # 'off', 'all', 'one'
        'volume': 0.7,
        'max_albums': 50,
        'show_album_art': True,
        'export_format': 'csv',
        'theme': 'dark',
        # If set, this path will be used as the music library root
        # (e.g. '/home/user/Music/JukeBox'). If None the app falls back
        # to platform defaults (~/Music/JukeBox on macOS/Linux).
        'music_dir': None,
        'keyboard_shortcut_enabled': True,
    }
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration
        
        Args:
            config_file: Path to config JSON file
        """
        if config_file is None:
            config_file = os.path.join(os.path.expanduser('~'), '.jukebox_config.json')
        
        self.config_file = config_file
        self.settings = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Update with loaded values, keeping defaults for missing keys
                    self.settings.update(loaded)
                print(f"Configuration loaded from: {self.config_file}")
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Configuration saved to: {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.settings[key] = value
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
