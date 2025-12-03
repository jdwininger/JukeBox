import os
import pygame

import sys, types

# Provide lightweight stubs so tests don't import mutagen/scipy
if 'src.album_library' not in sys.modules:
    m = types.ModuleType('src.album_library')
    class StubAlbum:
        def __init__(self,*a,**k): pass
        def get_albums(self): return []
    m.AlbumLibrary = StubAlbum
    sys.modules['src.album_library'] = m
if 'src.audio_effects' not in sys.modules:
    m2 = types.ModuleType('src.audio_effects')
    class StubEq:
        def __init__(self,*a,**k): pass
        def get_presets(self): return {}
        def get_all_bands(self): return [0.0]*5
        def set_band(self, i, v): return None
    m2.Equalizer = StubEq
    sys.modules['src.audio_effects'] = m2

from src.album_library import AlbumLibrary
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI


def test_font_fallback_with_missing_font(monkeypatch, tmp_path):
    # Simulate pygame.font.SysFont failing and remove freetype to force DummyFont
    monkeypatch.setattr(pygame.font, 'SysFont', lambda *a, **k: (_ for _ in ()).throw(Exception('SysFont fail')))
    if hasattr(pygame, 'freetype'):
        monkeypatch.delattr(pygame, 'freetype', raising=False)

    # Create minimal objects needed to construct UI
    lib_dir = tmp_path / "music_lib"
    library = AlbumLibrary(str(lib_dir))
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    # Ensure we use a HEADLESS video driver for tests
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    ui = UI(None, library, cfg, tm)

    # The small_font should be our DummyFont and render should return a surface
    surf = ui.small_font.render("Hello", True, (255, 0, 0))
    assert getattr(surf, 'get_width', lambda: 0)() > 0
    assert getattr(surf, 'get_height', lambda: 0)() > 0

    # Also ensure get_height is consistent with the rendered surface height
    h = ui.small_font.get_height()
    r = ui.small_font.render('Hg', True, (255, 255, 255))
    # Allow small tolerances for different font backends / default bitmap fonts
    assert abs(h - r.get_height()) <= 5


def test_freetype_get_height_matches_rendered(monkeypatch, tmp_path):
    """Simulate pygame.freetype where get_sized_height is incorrect but
    render returns a surface of the true height — UI should report the
    rendered surface height, not the incorrect sized height."""
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    # Create a fake freetype font object
    class FakeFTFont:
        def __init__(self, bad_size, true_h):
            self._bad_size = bad_size
            self._true_h = true_h

        def get_sized_height(self):
            return self._bad_size

        def render(self, text, fgcolor=None):
            # Return a pygame Surface whose height is the true height
            surf = pygame.Surface((10, self._true_h), pygame.SRCALPHA)
            surf.fill((255, 255, 255, 255))
            return surf, surf.get_rect()

    # Monkeypatch pygame.freetype.SysFont to return our fake font
    # Ensure the test imports UI in an environment that uses freetype
    import sys, types
    if hasattr(pygame, 'freetype'):
        orig_ft = pygame.freetype
    else:
        orig_ft = None

    class FTMod:
        def SysFont(self, *a, **k):
            return FakeFTFont(bad_size=6, true_h=18)

    monkeypatch.setattr(pygame, 'freetype', FTMod(), raising=False)

    # Stub heavy modules
    import types as _types, sys as _sys
    if 'src.album_library' not in _sys.modules:
        m = _types.ModuleType('src.album_library')
        class StubAlbum:
            def __init__(self,*a,**k): pass
            def get_albums(self): return []
        m.AlbumLibrary = StubAlbum
        _sys.modules['src.album_library'] = m
    if 'src.audio_effects' not in _sys.modules:
        m2 = _types.ModuleType('src.audio_effects')
        class StubEq:
            def __init__(self,*a,**k): pass
            def get_presets(self): return {}
            def get_all_bands(self): return [0.0]*5
            def set_band(self, i, v): return None
        m2.Equalizer = StubEq
        _sys.modules['src.audio_effects'] = m2

    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()
    ui = UI(None, _sys.modules['src.album_library'].AlbumLibrary(), cfg, tm)
    class DummyTheme:
        def get_background(self, w, h):
            surf = pygame.Surface((w, h))
            surf.fill((16, 16, 16))
            return surf
    ui.current_theme = DummyTheme()
    # Ensure UI has a usable theme background for cached background path
    class DummyTheme:
        def get_background(self, w, h):
            surf = pygame.Surface((w, h))
            surf.fill((16, 16, 16))
            return surf

    ui.current_theme = DummyTheme()

    # Confirm small_font's get_height returns the 'true' rendered height
    h = ui.small_font.get_height()
    surf = ui.small_font.render('Hg', True, (255,255,255))
    assert h == surf.get_height()

    # Restore original freetype if present
    if orig_ft is not None:
        monkeypatch.setattr(pygame, 'freetype', orig_ft, raising=False)


def test_font_debug_overlay_renders(tmp_path):
    """Ensure the debug overlay can be enabled and renders without error."""
    import os as _os, sys as _sys, types as _types
    _os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    # stub heavy modules
    if 'src.album_library' not in _sys.modules:
        m = _types.ModuleType('src.album_library')
        class StubAlbum:
            def __init__(self,*a,**k): pass
            def get_albums(self): return []
        m.AlbumLibrary = StubAlbum
        _sys.modules['src.album_library'] = m
    if 'src.audio_effects' not in _sys.modules:
        m2 = _types.ModuleType('src.audio_effects')
        class StubEq:
            def __init__(self,*a,**k): pass
            def get_presets(self): return {}
            def get_all_bands(self): return [0.0]*5
            def set_band(self, i, v): return None
        m2.Equalizer = StubEq
        _sys.modules['src.audio_effects'] = m2

    cfg = Config(config_file=str(tmp_path / "config.json"))
    cfg.set('debug_font_overlay', True)
    tm = ThemeManager()
    ui = UI(None, _sys.modules['src.album_library'].AlbumLibrary(), cfg, tm)
    # Provide a simple background so draw() can use cached background paths
    class DummyTheme:
        def get_background(self, w, h):
            surf = pygame.Surface((w, h))
            surf.fill((16, 16, 16))
            return surf
    ui.current_theme = DummyTheme()
    ui.config_screen_open = False
    # stub player methods used by draw_main_screen
    class StubPlayer:
        def get_volume(self):
            return 0.5

        def is_paused(self):
            return False

        def is_music_playing(self):
            return False

        def get_current_track_info(self):
            return None

    ui.player = StubPlayer()
    # should not raise when draw() is called
    ui.draw()


def _has_bottom_pixels(surf: pygame.Surface, rows=3) -> bool:
    """Check that the bottom `rows` rows of the surface contain any non-empty pixels.

    This helps detect cases where the surface bottom is entirely transparent
    (indicating potential clipping / truncated rendering).
    """
    w, h = surf.get_size()
    px = pygame.PixelArray(surf.copy())
    try:
        # sample a few rows from the bottom
        for ry in range(max(0, h - rows), h):
            for x in range(w):
                if px[x, ry] != surf.map_rgb((0, 0, 0)):
                    return True
        return False
    finally:
        del px


def test_rendered_surfaces_have_bottom_pixels(tmp_path):
    """Make sure font renderers produce surfaces with content at their bottom rows
    so we avoid runtime clipping where the bottom of glyphs are missing.
    """
    import os as _os, sys as _sys, types as _types
    _os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    if 'src.album_library' not in _sys.modules:
        m = _types.ModuleType('src.album_library')
        class StubAlbum:
            def __init__(self,*a,**k): pass
            def get_albums(self): return []
        m.AlbumLibrary = StubAlbum
        _sys.modules['src.album_library'] = m
    if 'src.audio_effects' not in _sys.modules:
        m2 = _types.ModuleType('src.audio_effects')
        class StubEq:
            def __init__(self,*a,**k): pass
            def get_presets(self): return {}
            def get_all_bands(self): return [0.0]*5
            def set_band(self, i, v): return None
        m2.Equalizer = StubEq
        _sys.modules['src.audio_effects'] = m2

    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()
    ui = UI(None, _sys.modules['src.album_library'].AlbumLibrary(), cfg, tm)
    # Test a few representative renderers
    samples = [
        (ui.small_font, 'Hgqyp'),
        (ui.medium_font, 'Hgqyp'),
        (ui.large_font, 'Hgqyp'),
        (ui.tiny_font, 'Hgqyp'),
    ]
    for fnt, txt in samples:
        surf = fnt.render(txt, True, (255, 255, 255))
        assert _has_bottom_pixels(surf, rows=4), f"bottom rows empty for font {fnt}"
