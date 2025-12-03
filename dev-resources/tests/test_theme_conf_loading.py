#!/usr/bin/env python3
"""Tests for theme.conf parsing and color overrides."""
import os
import tempfile
import pygame

from src.theme import Theme


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()


def _quit():
    pygame.quit()


def test_theme_conf_parsing_rgb_and_hex():
    _init()
    try:
        td = tempfile.TemporaryDirectory()
        d = td.name

        # create a theme.conf
        cfg = os.path.join(d, "theme.conf")
        with open(cfg, "w", encoding="utf-8") as f:
            f.write("[colors]\n")
            f.write("background = 1,2,3\n")
            f.write("text = #FFEE00\n")

        t = Theme("tmp", d)
        assert t.get_color("background") == (1, 2, 3)
        assert t.get_color("text") == (255, 238, 0)
    finally:
        _quit()
