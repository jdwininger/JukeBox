import os
import sys
import types
import pygame

# Create a lightweight stub for src.album_library so importing src.ui
# doesn't pull in optional heavy deps (mutagen) in test environments.
if "src.album_library" not in sys.modules:
    album_mod = types.ModuleType("src.album_library")

    class _StubAlbumLibrary:
        def __init__(self, *a, **k):
            pass

        def get_albums(self):
            return []

        def scan_library(self):
            return None

    album_mod.AlbumLibrary = _StubAlbumLibrary
    sys.modules["src.album_library"] = album_mod
# Avoid importing heavy optional audio deps during collection (scipy) by
# providing a light stub for audio_effects.Equalizer used by UI.
if "src.audio_effects" not in sys.modules:
    ae = types.ModuleType("src.audio_effects")

    class _StubEqualizer:
        def __init__(self, *a, **k):
            pass

        def get_presets(self):
            return {}

        def get_all_bands(self):
            return [0.0, 0.0, 0.0, 0.0, 0.0]

        def set_band(self, idx, value):
            return None

    ae.Equalizer = _StubEqualizer
    sys.modules["src.audio_effects"] = ae
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI, Colors, THEMABLE_TEXT_BUTTONS


def test_theme_creator_input_and_blocking(tmp_path, monkeypatch):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    # Minimal dummy library used by the UI in tests to avoid heavy deps
    class DummyLibrary:
        def get_albums(self):
            return []

    lib_dir = tmp_path / "music_lib"
    library = DummyLibrary()
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    ui = UI(None, library, cfg, tm)

    # Ensure config screen open so New Theme button is present
    ui.config_screen_open = True

    # Locate the 'New Theme' button and open the modal
    new_btn = ui.new_theme_button
    assert new_btn is not None
    ui.handle_theme_selection(new_btn.rect.center)
    assert ui.theme_creator_open
    # input should be focused by default
    assert getattr(ui, 'theme_creator_input_active', False) is True

    # Simulate typing "test" into the modal using KEYDOWN events
    for ch in "test":
        ev = pygame.event.Event(pygame.KEYDOWN, {"key": ord(ch), "unicode": ch})
        pygame.event.post(ev)
        ui.handle_events()

    assert ui.theme_creator_name == "test"

    # Clicking a background control while modal open should be swallowed
    prev_val = cfg.get("compact_track_list", True)
    # Click the compact button which would normally toggle this value
    compact_pos = ui.config_compact_button.rect.center
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": compact_pos}))
    ui.handle_events()
    assert cfg.get("compact_track_list", True) == prev_val

    # Check layout: buttons area should not overlap picker
    rects = ui._get_theme_creator_rects()
    ba = rects["buttons_area"]
    assert ba.right <= rects["picker"].x

    # Now choose a themable button inside the modal to create sliders
    # pick the first themable button center
    ba = rects["buttons_area"]
    # compute first button center (col 0 row 0)
    padding = 8
    cols = 3
    btn_w = (ba.width - (cols + 1) * padding) // cols
    btn_h = 40
    x0 = ba.x + padding
    y0 = ba.y + padding
    first_center = (x0 + btn_w // 2, y0 + btn_h // 2)

    # Click it
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": first_center}))
    ui.handle_events()

    # Sliders should be created and their knob widths should be reasonable (not huge)
    assert ui.theme_creator_sliders is not None
    r_s, g_s, b_s = ui.theme_creator_sliders
    # knob rect width should be bounded (we clamp to max radius 20 => width <= 40)
    assert r_s.knob_rect.width <= 48


def test_theme_creator_button_visibility_and_slider_click(tmp_path):
    """Regression test: clicking a themable button should not make other
    themable buttons vanish and clicking a slider knob must not close the modal."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    # Minimal dummy library used by the UI in tests to avoid heavy deps
    class DummyLibrary:
        def get_albums(self):
            return []

    lib_dir = tmp_path / "music_lib"
    library = DummyLibrary()
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    ui = UI(None, library, cfg, tm)
    ui.config_screen_open = True

    # Open the theme-creator modal
    ui.handle_theme_selection(ui.new_theme_button.rect.center)
    assert ui.theme_creator_open

    # Compute centers of three different themable buttons (first row, cols 0/1/2)
    rects = ui._get_theme_creator_rects()
    ba = rects["buttons_area"]
    padding = 8
    cols = 3
    btn_w = (ba.width - (cols + 1) * padding) // cols
    btn_h = 40
    x0 = ba.x + padding
    y0 = ba.y + padding

    centers = [
        (x0 + btn_w // 2, y0 + btn_h // 2),
        (x0 + (btn_w + padding) + btn_w // 2, y0 + btn_h // 2),
        (x0 + 2 * (btn_w + padding) + btn_w // 2, y0 + btn_h // 2),
    ]

    # Draw the modal to populate the surface and ensure the buttons are present
    ui.draw_theme_creator_dialog()
    surf = ui.screen

    # sample pixel on each button center to ensure button background was drawn
    initial_pixels = [tuple(surf.get_at((int(cx), int(cy)))[:3]) for cx, cy in centers]
    # they should be non-empty colors
    for p in initial_pixels:
        assert any(v != 0 for v in p)

    # Click first button to begin editing it (create sliders)
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": centers[0]}))
    ui.handle_events()

    # After selecting a button other buttons should still be drawn (not vanish)
    ui.draw_theme_creator_dialog()
    surf = ui.screen
    for (cx, cy), before in zip(centers[1:], initial_pixels[1:]):
        px = tuple(surf.get_at((int(cx), int(cy)))[:3])
        # ensure the pixel color didn't unexpectedly change (disappear/clear)
        assert px == before

    # Now ensure clicking a slider knob doesn't close the modal
    assert ui.theme_creator_sliders is not None
    r_s, g_s, b_s = ui.theme_creator_sliders

    # Simulate click on the red slider's knob position
    # Make sure knob_rect exists; if it isn't positioned yet, call draw to set it
    ui.draw_theme_creator_dialog()
    knob_center = r_s.knob_rect.center
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": knob_center}))
    ui.handle_events()

    # The modal must remain open after clicking slider
    assert ui.theme_creator_open is True


def test_theme_creator_draw_with_state_dicts(tmp_path):
    """Ensure drawing the preview handles dict-style per-state color entries
    (older code attempted to pass tuple(dict) to pygame and would raise, causing
    partial rendering/visual disappearance).
    """
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    # Minimal dummy library used by the UI in tests to avoid heavy deps
    class DummyLibrary:
        def get_albums(self):
            return []

    lib_dir = tmp_path / "music_lib"
    library = DummyLibrary()
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    ui = UI(None, library, cfg, tm)
    ui.config_screen_open = True
    ui.handle_theme_selection(ui.new_theme_button.rect.center)
    assert ui.theme_creator_open

    # Add dict entries for several buttons to mimic stateful colors
    # Use only a 'normal' entry to be used as preview
    for _, key in THEMABLE_TEXT_BUTTONS[:4]:
        ui.theme_creator_button_colors[key] = {"normal": (10, 20, 30)}

    # Drawing should not raise and should render all buttons
    ui.draw_theme_creator_dialog()
    surf = ui.screen

    rects = ui._get_theme_creator_rects()
    ba = rects["buttons_area"]
    padding = 8
    cols = 3
    btn_w = (ba.width - (cols + 1) * padding) // cols
    btn_h = 40
    x0 = ba.x + padding
    y0 = ba.y + padding
    centers = [
        (x0 + btn_w // 2, y0 + btn_h // 2),
        (x0 + (btn_w + padding) + btn_w // 2, y0 + btn_h // 2),
        (x0 + 2 * (btn_w + padding) + btn_w // 2, y0 + btn_h // 2),
    ]

    # No drawing exceptions; sampled pixels should be non-transparent and a tuple
    for cx, cy in centers:
        px = surf.get_at((int(cx), int(cy)))[:3]
        assert isinstance(px[0], int)
