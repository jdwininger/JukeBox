"""Tiny bundled bitmap font renderer used as a guaranteed fallback.

This module implements a minimal 6x8 pixel monospace bitmap font for
ASCII characters commonly used in the UI. It purposely avoids any system
libraries and relies only on pygame.Surface and pure Python so it will work
in constrained test/CI environments.

The public class BitmappedFont mimics the subset of the pygame.font
API used by UI: .render(text, aa, color) -> Surface and .get_height().
"""
from __future__ import annotations

from typing import Tuple

import pygame

# Each glyph is 5 pixels wide, 7 pixels tall. We'll leave a 1px space
# between glyphs horizontally, for a 6px cell width.
# For simplicity we only define glyphs for a limited set of characters
# used in the UI (letters, digits, punctuation). Unknown characters
# render as a blank box.
# The bitmaps are stored as strings of '1' and '0', 5 chars per row.
_DEFAULT_GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "10000", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["01110", "10001", "00001", "00110", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
    ",": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    ":": ["00000", "00100", "00000", "00000", "00100", "00000", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
}

CELL_W = 6  # includes 1px spacing
CELL_H = 8  # glyph rows + maybe a 1px baseline


class BitmappedFont:
    """Simple bitmap font renderer compatible with (small) subset of pygame.font API."""

    def __init__(self, size: int = 8, scale: int = 1):
        # size is logical font size; we use scale to allow bigger rendering
        self._size = max(6, int(size))
        self._scale = max(1, int(scale))

    def get_height(self) -> int:
        return CELL_H * self._scale

    def render(self, text: str, aa: bool, color: Tuple[int, int, int]):
        s = str(text)
        w = max(1, len(s) * CELL_W * self._scale)
        h = CELL_H * self._scale
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        # draw each char
        for idx, ch in enumerate(s):
            glyph = _DEFAULT_GLYPHS.get(ch.upper(), None)
            if glyph is None:
                # unknown char: draw a small rectangle placeholder
                rect = pygame.Rect(idx * CELL_W * self._scale + 1, 1, 4 * self._scale, (CELL_H - 2) * self._scale)
                try:
                    pygame.draw.rect(surf, color, rect)
                except Exception:
                    pass
                continue
            # draw pixels
            for y, row in enumerate(glyph):
                for x, bit in enumerate(row):
                    if bit == "1":
                        px = idx * CELL_W * self._scale + x * self._scale
                        py = y * self._scale
                        if self._scale == 1:
                            try:
                                surf.set_at((px, py), color)
                            except Exception:
                                pass
                        else:
                            rect = pygame.Rect(px, py, self._scale, self._scale)
                            try:
                                pygame.draw.rect(surf, color, rect)
                            except Exception:
                                pass
        return surf


# Module-level convenience factory used by UI code (mimics SysFont signature)
def SysFont(name: str, size: int = 8):
    # name ignored — this is a small builtin font
    return BitmappedFont(size=size, scale=max(1, size // 8))
