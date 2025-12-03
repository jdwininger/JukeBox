#!/usr/bin/env python3
"""Verify theme media assets are loaded at 50x50 to match UI media button size."""
import os
import tempfile
import pygame

from src.theme import Theme


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def _quit():
    pygame.quit()


def test_media_assets_loaded_at_50x50():
    _init()
    try:
        td = tempfile.TemporaryDirectory()
        d = td.name

        # Create placeholder PNGs for play/pause/stop at arbitrary size
        surf = pygame.Surface((100, 100))
        surf.fill((50, 100, 200))
        for name in ("play_button.png", "pause_button.png", "stop_button.png"):
            path = os.path.join(d, name)
            pygame.image.save(surf, path)

        # Instantiate Theme pointing to temp dir
        theme = Theme("tmp", d)

        # Check loaded surfaces are 50x50
        for key in ("play_button", "pause_button", "stop_button"):
            img = getattr(theme, key, None)
            assert img is not None, f"expected {key} to be loaded"
            assert img.get_width() == 50 and img.get_height() == 50, f"{key} not 50x50"
    finally:
        _quit()