#!/usr/bin/env python3
"""Tests for album track list font sizing and album card rendering."""
import os
import pygame

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
        a = type("A", (), {})()
        a.album_id = 1
        # create many tracks to force truncation/display of several lines
        a.tracks = [{"filename": f"t{i}.mp3", "title": f"Track {i}", "duration_formatted": "0:30"} for i in range(1, 25)]
        a.directory = "."
        a.artist = "Artist"
        a.title = "Album"
        self._albums = [a]

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

    def get_media_button_image(self, key):
        return None

    def get_color(self, key, default=None):
        return default


class StubThemeManager:
    def get_current_theme(self):
        return StubTheme()

    themes = {"dark": StubTheme(), "light": StubTheme()}


def test_track_list_font_smaller():
    # Verify the track list font is smaller than tiny_font
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        # Expect the newly-introduced track_list_font to be smaller than tiny_font
        assert ui.track_list_font.get_height() < ui.tiny_font.get_height()
    finally:
        pygame.quit()


def test_draw_album_card_with_many_tracks_runs():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        # draw the main screen (which will call draw_album_card) and ensure it runs
        ui.draw_main_screen()
    finally:
        pygame.quit()


def test_placeholder_album_text_left():
    """Empty/placeholder album text should appear on the left side of the card."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())

        # Create a placeholder album (no tracks, explicitly marked invalid)
        a = type("A", (), {})()
        a.album_id = 5
        a.tracks = []
        a.directory = "."
        a.artist = "Empty Slot 05"
        a.title = "No Album"
        a.is_valid = False

        # Compute content and art positions used by the UI logic
        # Use the same dimensions used for draw_album_card
        x, y, w, h = 10, 10, 400, 120
        padding = 8
        content_x = x + padding
        content_y = y + padding
        content_width = w - padding * 2
        content_height = h - padding * 2
        art_size = min(content_height - 10, int(content_width // 2.2))
        art_x = x + w - padding - art_size

        # Use compute_album_text_origin to inspect the origin calculation
        text_x, text_y, computed_art_x = ui.compute_album_text_origin(a, x, y, w, h)
        assert text_x == content_x, "Placeholder text should start at content_x (left side)"
        assert text_x < art_x, "Computed left-side text origin should be left of album art area"

        # Album number overlay for placeholder should still be in the art area
        num_x, num_y = ui.compute_album_number_origin(a, x, y, w, h)
        assert num_x >= art_x and num_x < art_x + art_size, "Album number should be inside art area"
    finally:
        pygame.quit()


def test_valid_album_without_art_text_right():
    """Valid albums without album art should keep text positioned next to the art area."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())

        # Create a valid album (has tracks) but has no art files
        a = type("A", (), {})()
        a.album_id = 7
        a.tracks = [{"filename": "t1.mp3", "title": "Track 1", "duration_formatted": "0:30"}]
        a.directory = "."
        a.artist = "Some Artist"
        a.title = "Some Album"
        a.is_valid = True

        # Compute art x position (use same card dims)
        x, y, w, h = 10, 10, 400, 120
        padding = 8
        content_width = w - padding * 2
        content_height = h - padding * 2
        art_size = min(content_height - 10, int(content_width // 2.2))
        art_x = x + w - padding - art_size

        text_x, _, computed_art_x = ui.compute_album_text_origin(a, x, y, w, h)
        # For a valid album without art, text should be positioned near the art area
        assert text_x >= art_x - 5, "Computed text origin should be near the art area for valid album without art"

        # Album number for valid album without art should be in art area as well
        num_x, num_y = ui.compute_album_number_origin(a, x, y, w, h)
        assert num_x >= art_x and num_x < art_x + art_size
    finally:
        pygame.quit()


def test_volume_overlay_position():
    """The volume slider should have a semi-transparent black overlay positioned
    correctly relative to the slider rectangle."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        # Render main screen so slider layout is applied
        ui.draw_main_screen()

        vx, vy, vw, vh = ui.compute_volume_overlay_origin()

        label_h = ui.small_font.get_height()
        top_extra = label_h + 12
        assert vw == ui.volume_slider.width + 20
        # overlay was extended downward by 10px
        assert vh == ui.volume_slider.height + 12 + top_extra + 10
        assert vx == ui.volume_slider.x - 8
        assert vy == ui.volume_slider.y - top_extra
    finally:
        pygame.quit()
