import os
import pygame

from src.album_library import AlbumLibrary
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI


def test_ui_uses_bundled_font_when_everything_missing(monkeypatch, tmp_path):
    # Force all usual font paths to fail
    monkeypatch.setattr(pygame.font, 'SysFont', lambda *a, **k: (_ for _ in ()).throw(Exception('SysFont fail')))
    if hasattr(pygame, 'freetype'):
        monkeypatch.delattr(pygame, 'freetype', raising=False)

    # Remove PIL if present
    try:
        import sys

        if 'PIL' in sys.modules:
            del sys.modules['PIL']
        # also remove pillow modules if present
        if 'PIL.Image' in sys.modules:
            del sys.modules['PIL.Image']
    except Exception:
        pass

    # Create minimal objects needed to construct UI
    lib_dir = tmp_path / "music_lib"
    library = AlbumLibrary(str(lib_dir))
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    ui = UI(None, library, cfg, tm)

    # Render a text surface using the small_font (should be bundled font)
    surf = ui.small_font.render("Hello", True, (255, 255, 255))
    # Ensure a non-empty surface with visible drawn pixels exists
    assert surf.get_width() > 0 and surf.get_height() > 0
    # check at least one non-transparent pixel exists (indicating glyphs drawn)
    # Verify at least one pixel is non-transparent by sampling the surface.
    w, h = surf.get_width(), surf.get_height()
    found = False
    for y in range(h):
        for x in range(w):
            try:
                a = surf.get_at((x, y))[3]
            except Exception:
                a = 255
            if a != 0:
                found = True
                break
        if found:
            break
    assert found, "No visible pixels found on rendered surface"
