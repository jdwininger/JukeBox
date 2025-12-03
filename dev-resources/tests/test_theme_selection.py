import os
import pytest
import pygame

from src.album_library import AlbumLibrary
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI, Colors


def test_clicking_theme_button_changes_theme(tmp_path):
    # Ensure headless mode for pygame display
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    # Prepare library/config and theme manager
    library = AlbumLibrary(str(tmp_path / "music_lib"))
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    available = tm.get_available_themes()
    if not available:
        # Create a default theme if none exist
        tm.create_default_theme()
        available = tm.get_available_themes()

    assert available, "No themes available to test with"

    # Ensure we pick a theme different from the config default
    current_pref = cfg.get('theme', 'dark')
    pick = next((n for n in available if n != current_pref), None)
    if pick is None:
        # Make a new theme so we can switch to it
        pick = 'test_theme_switch'
        ok = tm.create_theme(pick)
        assert ok, "Failed to create temporary test theme"

    # Create the UI and locate the corresponding theme button
    ui = UI(None, library, cfg, tm)

    btn = None
    for name, b in ui.theme_buttons:
        if name == pick:
            btn = b
            break

    assert btn is not None, f"Theme button for '{pick}' not found in UI"

    # Simulate click in the center of the theme button
    pos = btn.rect.center
    ui.handle_theme_selection(pos)

    # ThemeManager and UI should now reflect the chosen theme
    assert tm.get_current_theme() is not None
    assert tm.get_current_theme().name == pick
    assert ui.current_theme is not None
    assert ui.current_theme.name == pick

    # Config should have been updated and saved to the file
    assert cfg.get('theme') == pick

    # setup_theme_buttons should have updated the button colors — find the theme button again
    ui.setup_theme_buttons()
    found = False
    for name, b in ui.theme_buttons:
        if name == pick:
            found = True
            assert b.color == Colors.GREEN
            break

    assert found, "Theme button disappeared after selection"
