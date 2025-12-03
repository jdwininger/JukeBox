#!/usr/bin/env python3
"""Tests per-button colors from theme.conf are parsed correctly.

Verifies RGB and hex formats and fallback behavior.
"""
import os
import tempfile
import pygame

from src.theme import Theme


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()


def _quit():
    pygame.quit()


def test_button_colors_parsing_and_fallback():
    _init()
    try:
        td = tempfile.TemporaryDirectory()
        d = td.name

        cfg = os.path.join(d, "theme.conf")
        with open(cfg, "w", encoding="utf-8") as f:
            f.write("[button_colors]\n")
            f.write("clr = 1,2,3\n")
            f.write("clr_hover = 4,5,6\n")
            f.write("credits = #112233\n")
            f.write("credits_pressed = 77,88,99\n")
            # Also include a generic button color to validate fallback
            f.write("\n[colors]\n")
            f.write("button = 10,20,30\n")

        t = Theme("tmp", d)
        assert t.get_button_color("CLR") == (1, 2, 3)
        assert t.get_button_color("CLR", state="hover") == (4, 5, 6)
        assert t.get_button_color("credits") == (17, 34, 51)
        assert t.get_button_color("credits", state="pressed") == (77, 88, 99)
        # Non-existent button falls back to the generic button color
        assert t.get_button_color("ent") == (10, 20, 30)
    finally:
        _quit()
