#!/usr/bin/env python3
"""Verify themed close_button assets are used by Close-labeled buttons."""
import os
import tempfile
import pygame

from src.theme import Theme
from src.ui import Button, Colors


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def _quit():
    pygame.quit()


def test_close_button_uses_theme_asset():
    _init()
    try:
        td = tempfile.TemporaryDirectory()
        d = td.name

        # Save a close_button.png at a larger size (will be loaded and resized by Theme)
        surf = pygame.Surface((100, 100))
        surf.fill((250, 10, 10))
        path = os.path.join(d, "close_button.png")
        pygame.image.save(surf, path)

        theme = Theme("tmp", d)

        # Ensure Theme loaded the close button
        assert getattr(theme, "close_button", None) is not None

        surface = pygame.Surface((200, 120))
        surface.fill((0, 0, 0))

        btn = Button(10, 10, 50, 50, "Close", color=Colors.RED, theme=theme)
        btn.draw(surface, pygame.font.Font(None, 24))

        center_px = surface.get_at(btn.rect.center)
        assert center_px != (0, 0, 0, 255), "Expected themed close_button to be drawn"
    finally:
        _quit()
