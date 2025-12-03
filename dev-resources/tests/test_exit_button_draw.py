#!/usr/bin/env python3
"""Tests to ensure exit button is visible when no theme asset exists."""
import os
import pygame

from src.ui import Button, Colors


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def _quit():
    pygame.quit()


def test_exit_button_draws_default_icon_without_theme():
    _init()
    try:
        surface = pygame.Surface((200, 100))
        surface.fill((0, 0, 0))

        btn = Button(10, 10, 50, 50, "Exit", color=Colors.RED, theme=None, icon_type="exit")
        btn.draw(surface, pygame.font.Font(None, 24))

        # The button center should not match the background (black)
        center_px = surface.get_at(btn.rect.center)
        assert center_px != (0, 0, 0, 255)
    finally:
        _quit()
