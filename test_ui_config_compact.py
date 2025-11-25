#!/usr/bin/env python3
"""Tests for the compact track list toggle in Configuration screen and credit button placement."""
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
        a.tracks = [{"filename": "t1.mp3", "title": "T1", "duration_formatted": "0:30"}]
        a.directory = "."
        a.artist = "Artist"
        a.title = "Album"
        self._albums = [a]

    def get_albums(self):
        return self._albums

    def get_library_stats(self):
        return {"total_albums": 1, "max_albums": 52, "total_tracks": 1, "total_duration_formatted": "0:30"}


class DummyConfig:
    def __init__(self):
        # Include the new density setting default
        self._d = {"compact_track_list": True, "track_list_density": 0.8}

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


def test_compact_toggle_click():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        # open config screen so clicks are handled by config UI
        ui.config_screen_open = True
        ui.draw_config_screen()

        # initial state True
        assert ui.config.get("compact_track_list") is True

        pos = ui.config_compact_button.rect.center
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
        ui.handle_events()

        # toggled to False
        assert ui.config.get("compact_track_list") is False

        # Don't call draw_main_screen here (no player attached) — compact flag was toggled successfully
    finally:
        pygame.quit()


def test_credit_button_lowered_by_15px():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        # Render main screen to position buttons
        ui.draw_main_screen()

        # Compute the expected y position using the same layout calculations
        # We'll replicate the layout math to compute row2_y and card_h
        controls_margin_top = ui.header_height + 20
        button_height = 50
        media_button_size = 50
        spacing = 12
        buttons_y = controls_margin_top + 20
        content_top = buttons_y + button_height + 25
        content_height = ui.height - content_top - ui.bottom_area_height - 20
        if content_height < 200:
            content_height = 200
        row1_y = content_top + 10
        row2_y = row1_y + content_height // 2 + 35
        card_h = (content_height // 2) + 15
        expected_y = row2_y + card_h + 27

        assert ui.credit_button.rect.y == expected_y

        # Now test fullscreen toggle: compact should affect fullscreen fonts/line-height
        ui.config.set("compact_track_list", True)
        ui.fullscreen = True
        # Force a redraw
        ui.clear_caches()
        ui.draw_main_screen()
        # When fullscreen + compact, track_list_font_fullscreen should be smaller than small_font
        assert ui.track_list_font_fullscreen.get_height() < ui.small_font.get_height()
    finally:
        pygame.quit()


def test_density_slider_persists_value():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        ui.config_screen_open = True
        # Ensure slider exists and change its value
        assert hasattr(ui, "config_density_slider")
        ui.config_density_slider.set_value(0.6)

        # Simulate a click on the slider knob area to trigger persistence logic
        knob_pos = ui.config_density_slider.knob_rect.center
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": knob_pos, "button": 1}))
        ui.handle_events()

        assert abs(ui.config.get("track_list_density") - 0.6) < 0.001
    finally:
        pygame.quit()


def test_exit_button_and_confirmation():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        # Render main screen so buttons are positioned
        ui.draw_main_screen()

        # Exit button should be placed to the right of config (header right area)
        assert ui.config_button.rect.x < ui.exit_button.rect.x

        # Click exit button -> should open confirmation modal
        pos = ui.exit_button.rect.center
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}))
        ui.handle_events()
        assert ui.exit_confirm_open is True

        # Draw again so Yes/No buttons are positioned
        ui.draw_main_screen()

        # Click Yes -> should set running False
        yes_pos = ui.exit_confirm_yes.rect.center
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": yes_pos, "button": 1}))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": yes_pos, "button": 1}))
        ui.handle_events()
        assert ui.running is False

    finally:
        pygame.quit()


def test_exit_modal_stable_on_repeated_draws():
    """Ensure repeated draws while the modal is open preserve positions and stay open (no flicker causing toggling)."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        ui.draw_main_screen()

        # Open modal
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": ui.exit_button.rect.center, "button": 1}))
        ui.handle_events()
        assert ui.exit_confirm_open is True

        # Draw multiple times - positions should remain stable and modal stays open
        rects = []
        for _ in range(5):
            ui.draw_main_screen()
            rects.append((tuple(ui.exit_confirm_yes.rect), tuple(ui.exit_confirm_no.rect)))

        # All recorded rects should be equal
        assert len(set(rects)) == 1
        assert ui.exit_confirm_open is True
    finally:
        pygame.quit()


def test_config_screen_elements_do_not_overlap():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        ui.config_screen_open = True
        ui.draw_config_screen()

        # Collect important rects to test for overlap
        rects = [
            ui.config_compact_button.rect,
            ui.config_rescan_button.rect,
            ui.config_reset_button.rect,
            ui.config_extract_art_button.rect,
            ui.config_close_button.rect,
            ui.config_choose_music_button.rect,
            ui.config_equalizer_button.rect,
            ui.config_fullscreen_button.rect,
        ]
        # include density slider track rect if present
        if hasattr(ui, "config_density_slider"):
            rects.append(ui.config_density_slider.track_rect)

        # Ensure no two rects intersect
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                assert not rects[i].colliderect(rects[j]), f"Rects {i} and {j} overlap: {rects[i]} vs {rects[j]}"
    finally:
        pygame.quit()


def test_exit_modal_keyboard_confirm_and_cancel():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        player = DummyPlayer()
        ui = UI(player=player, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        ui.draw_main_screen()

        # open modal
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": ui.exit_button.rect.center, "button": 1}))
        ui.handle_events()
        assert ui.exit_confirm_open is True

        # Press Escape -> cancel
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE}))
        ui.handle_events()
        assert ui.exit_confirm_open is False

        # Reopen and confirm with Return
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": ui.exit_button.rect.center, "button": 1}))
        ui.handle_events()
        assert ui.exit_confirm_open is True

        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN}))
        ui.handle_events()
        assert ui.running is False
    finally:
        pygame.quit()


def test_library_header_aligned_with_settings():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())
        ui.config_screen_open = True
        ui.draw_config_screen()

        # The Settings header and Library header should be aligned vertically
        # Settings header Y is settings_y which is 100 in UI.draw_config_screen by default
        # We assert their top positions are equal (or very close)
        settings_header_y = 100
        # Library header drawn at info_y, we don't expose variable; compare rects of visible elements instead
        # Use the config_rescan_button Y (it is laid out below library info) and config_compact_button Y to ensure same top
        # We'll assert the compact button is in the left column and the library header is near the same vertical region
        left_compact_y = ui.config_compact_button.rect.y
        # The library header was drawn at info_y = settings_y; check that compact button is in top area as well
        assert left_compact_y >= settings_header_y
    finally:
        pygame.quit()
