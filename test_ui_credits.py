#!/usr/bin/env python3
"""Tests for the UI Credit button and display"""
import os
import pygame
import tempfile
import shutil

from src.ui import UI


class DummyPlayer:
    def __init__(self):
        self._credits = 0
        self.current_album_id = 1
        self.queue = []

    def add_credit(self, n=1):
        self._credits += int(n)

    def get_credits(self):
        return self._credits

    def get_volume(self):
        return 0.5

    def is_music_playing(self):
        return False

    def get_current_track_info(self):
        return None
    def get_current_album(self):
        return None


class DummyLibrary:
    def __init__(self):
        # minimal album objects to allow draw_album_card to run
        a = type("A", (), {})()
        a.album_id = 1
        a.tracks = [{"filename": "t1.mp3", "title": "T1", "duration_formatted": "0:30"}]
        a.directory = "."
        a.artist = "Artist"
        a.title = "Album"
        # Provide multiple albums for left/right columns
        self._albums = [a, a, a, a]

    def get_albums(self):
        return self._albums


class DummyConfig:
    def __init__(self):
        self._d = {}

    def get(self, key, default=None):
        return self._d.get(key, default)

    def set(self, key, value):
        self._d[key] = value

    def save(self):
        pass

    def reset_to_defaults(self):
        self._d.clear()


class StubTheme:
    def get_background(self, w, h):
        return None

    def get_button_image(self, key):
        return None

    def get_media_button_image(self, key, state='normal'):
        return None
    def get_color(self, key, default=None):
        return default


class StubThemeManager:
    def get_current_theme(self):
        return StubTheme()

    themes = {"dark": StubTheme(), "light": StubTheme()}


def test_credit_button_adds_credit():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())

        # Draw main screen so the button gets positioned
        ui.draw_main_screen()

        # Simulate click on the credit button
        pos = ui.credit_button.rect.center
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
        ui.handle_events()

        assert player.get_credits() == 1
    finally:
        pygame.quit()
