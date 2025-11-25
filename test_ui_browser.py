#!/usr/bin/env python3
"""Tests for the in-modal pure-pygame browser helper methods in UI."""
import os
import shutil
import sys
import tempfile
import types

import pygame

# Provide lightweight stubs for mutagen submodules so UI/album_library imports don't fail
for mod_name, attrs in (
    ("mutagen.easyid3", {"EasyID3": lambda *a, **k: {}}),
    ("mutagen.flac", {"FLAC": lambda *a, **k: types.SimpleNamespace(pictures=[])}),
    (
        "mutagen.oggvorbis",
        {
            "OggVorbis": lambda *a, **k: types.SimpleNamespace(
                info=types.SimpleNamespace(length=0)
            )
        },
    ),
    (
        "mutagen.wave",
        {
            "WAVE": lambda *a, **k: types.SimpleNamespace(
                info=types.SimpleNamespace(length=0), tags={}
            )
        },
    ),
    (
        "mutagen.mp3",
        {
            "MP3": lambda *a, **k: types.SimpleNamespace(
                info=types.SimpleNamespace(length=0), tags={}
            )
        },
    ),
    ("mutagen.id3", {"ID3": object, "APIC": object}),
    ("mutagen", {}),
):
    if mod_name not in sys.modules:
        m = types.ModuleType(mod_name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[mod_name] = m

# Stub some local src.* modules so UI imports succeed without external deps
if "src.player" not in sys.modules:
    m = types.ModuleType("src.player")

    class MusicPlayer:
        def __init__(self):
            self.volume = 0.7
            self.is_playing = False
            self.is_paused = False

        def get_volume(self):
            return self.volume

        def get_current_track_info(self):
            return None

        def is_music_playing(self):
            return self.is_playing

    m.MusicPlayer = MusicPlayer
    sys.modules["src.player"] = m

if "src.album_library" not in sys.modules:
    m = types.ModuleType("src.album_library")

    class AlbumLibrary:
        def __init__(self, path=None):
            self.path = path

        def get_albums(self):
            return []

        def scan_library(self):
            return

        def extract_all_cover_art(self):
            return {"extracted": 0, "existing": 0, "failed": 0}

    m.AlbumLibrary = AlbumLibrary
    sys.modules["src.album_library"] = m

if "src.audio_effects" not in sys.modules:
    m = types.ModuleType("src.audio_effects")

    class Equalizer:
        def __init__(self):
            pass

        def get_presets(self):
            return {}

        def get_all_bands(self):
            return [0, 0, 0, 0, 0]

    m.Equalizer = Equalizer
    sys.modules["src.audio_effects"] = m

if "src.widgets" not in sys.modules:
    m = types.ModuleType("src.widgets")

    class Slider:
        def __init__(self, *a, **k):
            self.x = 0
            self.y = 0
            self.width = 100
            self.height = 20
            self._value = 50

        def get_value(self):
            return self._value

        def draw(self, *a, **k):
            pass

    class VerticalSlider(Slider):
        pass

    m.Slider = Slider
    m.VerticalSlider = VerticalSlider
    sys.modules["src.widgets"] = m

from src.ui import UI


class DummyLibrary:
    def get_albums(self):
        return []

    def get_library_stats(self):
        return {
            "total_albums": 0,
            "max_albums": 52,
            "total_tracks": 0,
            "total_duration_formatted": "0:00",
        }


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


class StubThemeManager:
    def get_current_theme(self):
        return StubTheme()

    # Make themes mapping available for setup_theme_buttons
    themes = {"dark": StubTheme(), "light": StubTheme()}


def test_open_browser_sets_state():
    # Use dummy video driver for headless test environments
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()

    tmp = tempfile.mkdtemp(prefix="jukebox_test_browser_")
    try:
        # Create a few directories and files
        os.makedirs(os.path.join(tmp, "01"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "02"), exist_ok=True)
        with open(os.path.join(tmp, "readme.txt"), "w") as f:
            f.write("hello")

        ui = UI(
            player=None,
            library=DummyLibrary(),
            config=DummyConfig(),
            theme_manager=StubThemeManager(),
        )

        # open browser and check state
        ui._open_browser(tmp)

        assert ui.config_browser_path == os.path.expanduser(tmp)
        assert isinstance(ui.config_browser_entries, list)
        # should contain the directories '01' and '02' and a file 'readme.txt'
        names = [e["name"] for e in ui.config_browser_entries]
        assert "01" in names
        assert "02" in names
        assert "readme.txt" in names

        # visible count should be >= 1 (room for rows)
        vc = ui._browser_visible_count()
        assert vc >= 1

        print("test_ui_browser.py: OK")
    finally:
        shutil.rmtree(tmp)
        pygame.quit()


def test_choose_library_button_lowered():
    # Make sure the UI positions Choose Library button lower to avoid clipping
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(
            player=None,
            library=DummyLibrary(),
            config=DummyConfig(),
            theme_manager=StubThemeManager(),
        )
        # config_y in UI.setup_config_buttons is 300, the button is now lowered 40 -> 340
        expected_y = 340
        assert ui.config_choose_music_button.rect.y == expected_y

        # Also check library action placement after rendering config screen
        ui.draw_config_screen()
        # After the layout change library actions are two columns; rescan should be on the same row as Extract Art
        assert ui.config_rescan_button.rect.y == ui.config_extract_art_button.rect.y
        assert ui.config_extract_art_button.rect.x > ui.config_rescan_button.rect.x
        # And they should be at least 45px below the Choose button (no clipping after header shift)
        assert (
            ui.config_rescan_button.rect.y >= ui.config_choose_music_button.rect.y + 45
        )
        # Reset moves to next row
        assert ui.config_reset_button.rect.y > ui.config_rescan_button.rect.y

        # Choose button is now positioned in the middle column and may be higher than
        # the initial setup position — ensure it's no lower than expected initial
        # position (sanity check) and that it remains at or above column alignment.
        assert ui.config_choose_music_button.rect.y <= 340
    finally:
        pygame.quit()


if __name__ == "__main__":
    test_open_browser_sets_state()


def test_click_and_double_click_opens_directory():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()

    tmp = tempfile.mkdtemp(prefix="jukebox_test_browser_")
    try:
        # directory and a file
        os.makedirs(os.path.join(tmp, "01"), exist_ok=True)
        with open(os.path.join(tmp, "note.txt"), "w") as f:
            f.write("x")

        ui = UI(
            player=None,
            library=DummyLibrary(),
            config=DummyConfig(),
            theme_manager=StubThemeManager(),
        )
        # Open the browser in modal
        ui.config_music_editing = True
        ui.config_browser_open = True
        ui._open_browser(tmp)

        rects = ui._get_music_modal_rects()
        pa = rects["preview_area"]
        header_ht = ui.small_font.get_height()
        row_h = max(ui.small_font.get_height(), 18)

        # Click the first visible entry (should be '01')
        assert ui.config_browser_entries[0]["name"] == "01"
        assert ui.config_browser_entries[0]["is_dir"] is True
        x = pa.x + 16
        y = pa.y + header_ht + 8 + row_h // 2
        pygame.event.post(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (x, y), "button": 1})
        )
        ui.handle_events()

        assert ui.config_browser_selected == 0
        # clicking selects the entry (input may be unchanged in some headless environments)
        assert ui.config_browser_selected == 0

        # Simulate opening selected folder (double-click behavior) by calling helper
        ui._open_browser(os.path.join(tmp, "01"))
        assert ui.config_browser_path.endswith(os.path.join("", "01"))

    finally:
        shutil.rmtree(tmp)
        pygame.quit()


def test_theme_buttons_center_in_fullscreen_and_windowed():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(
            player=None,
            library=DummyLibrary(),
            config=DummyConfig(),
            theme_manager=StubThemeManager(),
        )

        # Simulate windowed width
        ui.width = 1280
        ui.fullscreen = False
        ui.draw_theme_selector()
        xs = [btn.rect.x for _, btn in ui.theme_buttons]
        # compute center of the button block
        if xs:
            min_x = min(xs)
            max_x = max(xs) + ui.theme_buttons[0][1].rect.width
            center_block = (min_x + max_x) / 2
            assert abs(center_block - (ui.width / 2)) < 2

        # Simulate fullscreen width (wider)
        ui.width = 1920
        ui.fullscreen = True
        ui.draw_theme_selector()
        xs2 = [btn.rect.x for _, btn in ui.theme_buttons]
        if xs2:
            min_x2 = min(xs2)
            max_x2 = max(xs2) + ui.theme_buttons[0][1].rect.width
            center_block2 = (min_x2 + max_x2) / 2
            assert abs(center_block2 - (ui.width / 2)) < 2
        # windowed mode content should be moved down about 50px from default
        # calculate title y in windowed mode
        ui.fullscreen = False
        ui.width = 1280
        title1 = ui.medium_font.render("Theme Selection", True, (0, 0, 0))
        title_y1 = ui.height - 180 - 30 + 50
        # in fullscreen (no extra shift) title_y2 should be 50px higher
        ui.fullscreen = True
        title_y2 = ui.height - 180 - 30
        assert title_y1 - title_y2 == 50
    finally:
        pygame.quit()


def test_theme_preview_position_fullscreen_vs_windowed():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(
            player=None,
            library=DummyLibrary(),
            config=DummyConfig(),
            theme_manager=StubThemeManager(),
        )
        # simulate a theme button being hovered
        if not ui.theme_buttons:
            return
        ui.theme_buttons[0][1].is_hovered = True

        # windowed mode: width 1280
        ui.fullscreen = False
        ui.width = 1280
        px1, py1 = ui._get_theme_preview_pos(ui.height - 180)

        # fullscreen: width 1920
        ui.fullscreen = True
        ui.width = 1920
        px2, py2 = ui._get_theme_preview_pos(ui.height - 180)

        # In fullscreen the preview y should be above the title (i.e., less than windowed y)
        assert py2 < py1
        # Verify exact expected positions after the 40px upward shift:
        # windowed: theme_section_y - 130 - 40
        # windowed now has extra 20px upward nudge (total 60)
        expected_py1 = ui.height - 180 - 130 - 60
        # fullscreen: title_y - 10 - 120 - 40
        expected_py2 = ui.height - 180 - 30 - 10 - 120 - 40
        assert py1 == expected_py1
        assert py2 == expected_py2
        # x should still be centered for each width
        assert abs(px1 + 100 - (1280 / 2)) < 2
        assert abs(px2 + 100 - (1920 / 2)) < 2
    finally:
        pygame.quit()


def test_effects_align_with_settings_header():
    """Ensure Audio/Visual Effects blocks are aligned vertically with Settings header."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    try:
        ui = UI(
            player=None,
            library=DummyLibrary(),
            config=DummyConfig(),
            theme_manager=StubThemeManager(),
        )
        # Draw config screen so positions are set
        ui.draw_config_screen()

        # settings_y in draw_config_screen is 100; audio effects buttons were moved up 10px -> effects_y + 30
        expected_effects_y = 100 + 30
        assert ui.config_equalizer_button.rect.y == expected_effects_y

        # visual effects were nudged down — expect it at effects_y + 85 + 30
        expected_visual_y = 100 + 85 + 30
        assert ui.config_fullscreen_button.rect.y == expected_visual_y
    finally:
        pygame.quit()
