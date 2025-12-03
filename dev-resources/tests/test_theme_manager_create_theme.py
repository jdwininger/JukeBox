#!/usr/bin/env python3
"""Tests for ThemeManager.create_theme to ensure new themes get created and theme.conf contains the provided colors and per-button entries."""
import os
import tempfile

from src.theme import ThemeManager


def test_create_theme_writes_theme_conf(monkeypatch):
    td = tempfile.TemporaryDirectory()
    themes_root = td.name

    # Stub pygame operations used by create_theme
    class DummySurface:
        def __init__(self, size):
            self.size = size

        def fill(self, c):
            self.color = c

    def fake_save(surf, path):
        # ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(b"PNGDATA")

    monkeypatch.setattr("pygame.Surface", lambda size: DummySurface(size))
    monkeypatch.setattr("pygame.image.save", fake_save)

    mgr = ThemeManager(themes_dir=themes_root)

    # create a theme with custom colors
    name = "custom_theme"
    colors = {"background": (10, 20, 30), "button": (40, 50, 60)}
    button_colors = {
        "credits": {"normal": (1, 2, 3), "hover": (2, 3, 4), "pressed": (5, 6, 7)},
        "clr": (4, 5, 6),
    }

    ok = mgr.create_theme(name, colors=colors, button_colors=button_colors)
    assert ok

    theme_dir = os.path.join(themes_root, name)
    assert os.path.isdir(theme_dir)
    conf_path = os.path.join(theme_dir, "theme.conf")
    assert os.path.exists(conf_path)

    text = open(conf_path, "r", encoding="utf-8").read()
    assert "background = 10,20,30" in text
    assert "button = 40,50,60" in text
    # button_colors entries
    assert "credits = 1,2,3" in text
    assert "credits_hover = 2,3,4" in text
    assert "credits_pressed = 5,6,7" in text
    assert "clr = 4,5,6" in text
