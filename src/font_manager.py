"""
Font Manager Module - Handles font initialization with multiple backends
"""
import os
from typing import Dict, Optional

import pygame


class FontManager:
    """Manages font initialization with fallback backends for robustness"""

    def __init__(self, bundled_font_path: Optional[str] = None):
        self.bundled_font_path = bundled_font_path
        self.font_file_used: Optional[str] = None

    def init_fonts(self) -> Dict[str, object]:
        """Initialize and return all UI fonts with appropriate fallbacks"""
        fonts = {}

        try:
            # When available, prefer pygame.freetype (more robust on some platforms)
            if hasattr(pygame, "freetype"):
                ft = pygame.freetype

                class _FTWrapper:
                    def __init__(self, ftfont):
                        self._ft = ftfont

                    def render(self, text, aa, color):
                            surf, _ = self._ft.render(str(text), fgcolor=color)
                            # Some freetype implementations can render glyphs right
                            # at the bottom edge. Add a tiny vertical padding to the
                            # returned surface to avoid half-glyph clipping when
                            # downstream code composites or scales the surface.
                            try:
                                h = surf.get_height()
                                pad_v = max(2, int(h * 0.12)) + 4  # Increased padding to prevent compositor clipping
                                if pad_v > 0:
                                    out = pygame.Surface((surf.get_width(), h + pad_v), pygame.SRCALPHA)
                                    out.fill((0, 0, 0, 0))
                                    out.blit(surf, (0, 0))
                                    return out
                            except Exception:
                                pass
                            return surf

                    def get_height(self):
                        """Return a reliable height for this freetype-based font.

                        Some pygame.freetype implementations can return a sized
                        height that doesn't match the actual returned surface.
                        To avoid text clipping, render a short sample and use
                        the surface height which will match what render() draws.
                        Cache the size on the ftfont object if possible.
                        """
                        try:
                            # Prefer a direct sized height when available
                            sized = int(self._ft.get_sized_height())
                        except Exception:
                            sized = None

                        try:
                            # Render a sample glyph to get the actual surface height
                            surf, _ = self._ft.render("Hg", fgcolor=(0, 0, 0))
                            actual = surf.get_height()
                        except Exception:
                            actual = None

                        # If both are present and equal-ish prefer actual surface
                        # but include the same small padding we apply when
                        # rendering so get_height mirrors the surface height.
                        if actual is not None:
                            pad_v = max(2, int(actual * 0.12)) + 4  # Match increased padding in render
                            return int(actual + pad_v)
                        if sized is not None:
                            return int(sized)
                        # fallback conservative default
                        return 12

                # If a bundled TTF exists, prefer loading it directly
                # via pygame.freetype.Font to ensure we use the same font
                # everywhere. Fall back to SysFont when the bundled font
                # isn't available or the load fails.
                try:
                    if self.bundled_font_path and os.path.exists(self.bundled_font_path):
                        fonts['large_font'] = _FTWrapper(ft.Font(self.bundled_font_path, 36))
                        fonts['medium_font'] = _FTWrapper(ft.Font(self.bundled_font_path, 20))
                        fonts['small_medium_font'] = _FTWrapper(ft.Font(self.bundled_font_path, 20))
                        fonts['small_font'] = _FTWrapper(ft.Font(self.bundled_font_path, 14))
                        fonts['tiny_font'] = _FTWrapper(ft.Font(self.bundled_font_path, 10))
                        fonts['track_list_font'] = _FTWrapper(ft.Font(self.bundled_font_path, 9))
                        fonts['track_list_font_fullscreen'] = _FTWrapper(ft.Font(self.bundled_font_path, 12))
                        # record which file we loaded so tests can assert it
                        self.font_file_used = self.bundled_font_path
                    else:
                        raise RuntimeError("bundled freetype font not available")
                except Exception:
                    # fallback to system freetype fonts
                    fonts['large_font'] = _FTWrapper(ft.SysFont("Arial", 36))
                    fonts['medium_font'] = _FTWrapper(ft.SysFont("Arial", 20))
                    fonts['small_medium_font'] = _FTWrapper(ft.SysFont("Arial", 20))
                    fonts['small_font'] = _FTWrapper(ft.SysFont("Arial", 14))
                    fonts['tiny_font'] = _FTWrapper(ft.SysFont("Arial", 10))
                    fonts['track_list_font'] = _FTWrapper(ft.SysFont("Arial", 9))
                    fonts['track_list_font_fullscreen'] = _FTWrapper(ft.SysFont("Arial", 12))
            else:
                # Try a bundled TTF first (assets/fonts/DejaVuSans.ttf)
                bundled_font_path = self.bundled_font_path

                loaded = False

                # 1) Try Pillow (ImageFont.truetype) — works even when pygame.font
                #    is partially broken. Prefer this as it uses the actual TTF.
                if bundled_font_path and os.path.exists(bundled_font_path):
                    try:
                        from PIL import ImageFont, Image, ImageDraw

                        def _make_pil_wrapper(size):
                            pil_font = ImageFont.truetype(bundled_font_path, size)

                            class _PILWrap:
                                def __init__(self, pf):
                                    self._pf = pf

                                def render(self, text, aa, color):
                                    s = str(text)
                                    tmp_img = Image.new("RGBA", (1, 1))
                                    draw = ImageDraw.Draw(tmp_img)
                                    # textbbox is available in newer Pillow versions
                                    try:
                                        bbox = draw.textbbox((0, 0), s, font=self._pf)
                                        w = bbox[2] - bbox[0]
                                        h = bbox[3] - bbox[1]
                                    except Exception:
                                        try:
                                            w, h = draw.textsize(s, font=self._pf)
                                        except Exception:
                                            # Last-resort fallback
                                            w, h = self._pf.getsize(s)
                                    # Add a small vertical padding so glyphs with
                                    # descenders or odd render offsets are not
                                    # accidentally clipped when converted into a
                                    # pygame Surface or later composited/scaled.
                                    pad_v = max(2, int(h * 0.12)) + 4  # Increased padding to prevent compositor clipping
                                    img = Image.new("RGBA", (max(1, w), max(1, h + pad_v)), (0, 0, 0, 0))
                                    draw = ImageDraw.Draw(img)
                                    # Draw with a tiny top offset so there is
                                    # always some spare space beneath glyphs.
                                    draw.text((0, 2), s, font=self._pf, fill=tuple(color))
                                    data = img.tobytes()
                                    surf = pygame.image.fromstring(data, img.size, img.mode)
                                    return surf

                                def get_height(self):
                                    """Return a reliable height for this font.

                                    Pillow's FreeTypeFont may not expose a stable getsize
                                    API in all versions, so we compute the height by
                                    measuring a short sample string using an
                                    ImageDraw instance — this mirrors render() and
                                    avoids AttributeError or mismatches between
                                    get_height() and the actual rendered surface.
                                    """
                                    try:
                                        # Prefer textbbox (newer Pillow) for accurate metrics
                                        tmp = Image.new("RGBA", (1, 1))
                                        draw = ImageDraw.Draw(tmp)
                                        try:
                                            # use a representative glyph pair ('Hg') which
                                            # includes ascender and descender to better
                                            # match the surface produced by render().
                                            bbox = draw.textbbox((0, 0), "Hg", font=self._pf)
                                            base_h = bbox[3] - bbox[1]
                                        except Exception:
                                            # Fallback to textsize if textbbox unavailable
                                            try:
                                                w, h = draw.textsize("Hg", font=self._pf)
                                                base_h = h
                                            except Exception:
                                                # Best-effort: some PIL font objects provide getsize
                                                if hasattr(self._pf, "getsize"):
                                                    base_h = self._pf.getsize("Hg")[1]
                                                else:
                                                    # As a last resort pick a conservative value
                                                    base_h = int(0.6 * max(8, getattr(self._pf, 'size', 12)))

                                        # Add the same vertical padding we use in render()
                                        pad_v = max(2, int(base_h * 0.12)) + 4  # Match increased padding in render
                                        return base_h + pad_v
                                    except Exception:
                                        # Never raise from a font height helper — return a sane default
                                        return 12

                            return _PILWrap(pil_font)

                        fonts['large_font'] = _make_pil_wrapper(36)
                        fonts['medium_font'] = _make_pil_wrapper(20)
                        fonts['small_medium_font'] = _make_pil_wrapper(20)
                        fonts['small_font'] = _make_pil_wrapper(14)
                        fonts['tiny_font'] = _make_pil_wrapper(10)
                        fonts['track_list_font'] = _make_pil_wrapper(9)
                        fonts['track_list_font_fullscreen'] = _make_pil_wrapper(12)
                        loaded = True
                        # record that we're using the bundled font file
                        if bundled_font_path:
                            self.font_file_used = bundled_font_path
                    except Exception:
                        loaded = False

                # 2) Try pygame.font.Font pointing at the bundled TTF
                if not loaded and bundled_font_path and os.path.exists(bundled_font_path):
                    try:
                        fonts['large_font'] = pygame.font.Font(bundled_font_path, 36)
                        fonts['medium_font'] = pygame.font.Font(bundled_font_path, 20)
                        fonts['small_medium_font'] = pygame.font.Font(bundled_font_path, 20)
                        fonts['small_font'] = pygame.font.Font(bundled_font_path, 14)
                        fonts['tiny_font'] = pygame.font.Font(bundled_font_path, 10)
                        fonts['track_list_font'] = pygame.font.Font(bundled_font_path, 9)
                        fonts['track_list_font_fullscreen'] = pygame.font.Font(bundled_font_path, 12)
                        loaded = True
                        # record that we used the bundled font file
                        self.font_file_used = bundled_font_path
                    except Exception:
                        loaded = False

                # 3) Try system SysFont as a final attempt before outer fallback
                if not loaded:
                    try:
                        fonts['large_font'] = pygame.font.SysFont("Arial", 36)
                        fonts['medium_font'] = pygame.font.SysFont("Arial", 20)
                        fonts['small_medium_font'] = pygame.font.SysFont("Arial", 20)
                        fonts['small_font'] = pygame.font.SysFont("Arial", 14)
                        fonts['tiny_font'] = pygame.font.SysFont("Arial", 10)
                        fonts['track_list_font'] = pygame.font.SysFont("Arial", 9)
                        fonts['track_list_font_fullscreen'] = pygame.font.SysFont("Arial", 12)
                        loaded = True
                    except Exception:
                        loaded = False

                if not loaded:
                    raise RuntimeError("No font backend available")

        except Exception:
            # Minimal fallback when all font backends fail
            from src.bundled_font import SysFont as _BundledSysFont

            class _DummyFont:
                def __init__(self, size=14):
                    self._size = size
                    # SysFont bundled fallback expects a (name, size) signature
                    # so pass a dummy name and the size to match the expected
                    # constructor and avoid TypeError in tests.
                    try:
                        self._font = _BundledSysFont("_bundled", self._size)
                    except TypeError:
                        # Conservative fallback for unexpected signatures
                        self._font = _BundledSysFont(self._size)

                def render(self, text, aa, color):
                    return self._font.render(text, aa, color)

                def get_height(self):
                    return self._font.get_height()

            fonts['large_font'] = _DummyFont(36)
            fonts['medium_font'] = _DummyFont(20)
            fonts['small_medium_font'] = _DummyFont(20)
            fonts['small_font'] = _DummyFont(14)
            fonts['tiny_font'] = _DummyFont(10)
            fonts['track_list_font'] = _DummyFont(9)
            fonts['track_list_font_fullscreen'] = _DummyFont(12)

        return fonts