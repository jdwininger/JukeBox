#!/usr/bin/env python3
"""Tests for ThemeManager.create_default_theme to make sure it writes theme.conf
and doesn't reference missing instance state."""
import os
import tempfile

from src.theme import ThemeManager, Theme


def test_create_default_theme_writes_conf(monkeypatch):
    td = tempfile.TemporaryDirectory()
    themes_root = td.name

    # Avoid relying on pygame internals in CI/test environment by stubbing
    # the parts used by create_default_theme
    class DummySurface:
        def __init__(self, size):
            self.size = size

        def fill(self, color):
            self.color = color

    def fake_save(surf, path):
        # Create an empty file so the code believes the images exist later
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr("pygame.Surface", lambda size: DummySurface(size))
    monkeypatch.setattr("pygame.image.save", fake_save)

    mgr = ThemeManager(themes_dir=themes_root)

    default_dir = os.path.join(themes_root, "default")
    assert not os.path.exists(default_dir)

    # Create the default theme
    mgr.create_default_theme()

    # Files should exist
    assert os.path.isdir(default_dir)
    conf_path = os.path.join(default_dir, "theme.conf")
    assert os.path.exists(conf_path)

    # Validate the content uses the Theme.DEFAULT_COLORS values
    text = open(conf_path, "r", encoding="utf-8").read()
    for k, v in Theme.DEFAULT_COLORS.items():
        assert f"{k} = {v[0]},{v[1]},{v[2]}" in text

    # Ensure the sample [button_colors] section was written
    assert "[button_colors]" in text
    assert "credits = 255,215,0" in text
    assert "clr = 200,50,50" in text
    assert "ent = 100,200,100" in text
