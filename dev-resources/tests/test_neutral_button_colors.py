#!/usr/bin/env python3
"""Tests for neutral default button colors coming from theme."""
import os
import pygame

from src.ui import Button


class StubTheme:
    def get_color(self, key, default=None):
        if key == "button":
            return (10, 10, 10)
        return default


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def _quit():
    pygame.quit()


def test_button_defaults_to_theme_button_color():
    _init()
    try:
        theme = StubTheme()
        btn = Button(0, 0, 50, 50, "Test", color=None, theme=theme)
        assert btn.color == (10, 10, 10)
    finally:
        _quit()


def test_media_buttons_in_ui_use_neutral_color():
    _init()
    try:
        from src.ui import UI
        from src.config import Config
        from src.album_library import AlbumLibrary

        class DummyConfig(Config):
            def __init__(self):
                self._d = {}
            def get(self, k, default=None):
                return default
            def set(self, k, v):
                pass
            def save(self):
                pass

        class DummyLibrary:
            def get_albums(self):
                return []

        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=type("TM", (), {"get_current_theme": lambda self: StubTheme(), "themes": {}})())
        assert ui.play_button.color == (10, 10, 10)
        assert ui.pause_button.color == (10, 10, 10)
        assert ui.stop_button.color == (10, 10, 10)
    finally:
        _quit()
