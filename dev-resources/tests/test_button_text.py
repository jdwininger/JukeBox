#!/usr/bin/env python3
"""Unit tests for Button text rendering behavior."""
import os
import pygame

from src.ui import Button, Colors


class StubThemeWithBg:
    def __init__(self, color=(10, 120, 200)):
        self._color = color

    def get_button_image(self, state='normal'):
        # Return a Surface to act as a themed background image
        surf = pygame.Surface((200, 80))
        surf.fill(self._color)
        return surf


def _init_pygame():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def test_text_button_draws_text_without_theme():
    _init_pygame()
    try:
        font = pygame.font.Font(None, 24)
        surface = pygame.Surface((200, 100))
        surface.fill((0, 0, 0))

        btn = Button(10, 10, 150, 50, "Click me", color=(64, 64, 64), theme=None)
        btn.draw(surface, font)

        # Determine text bounding rect from the rendered font
        text_surface = font.render(btn.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=btn.rect.center)

        # Sample one point inside text rect and one in the button background
        text_px = surface.get_at(text_rect.center)
        bg_px = surface.get_at((btn.rect.x + 4, btn.rect.y + 4))

        assert text_px != bg_px, "Expected text to alter pixels inside text area when no theme present"
    finally:
        pygame.quit()


def test_text_button_draws_text_with_theme_background():
    _init_pygame()
    try:
        font = pygame.font.Font(None, 24)
        surface = pygame.Surface((200, 100))
        surface.fill((0, 0, 0))

        theme = StubThemeWithBg(color=(18, 42, 99))
        btn = Button(10, 10, 150, 50, "Apply", color=(64, 64, 64), theme=theme)
        btn.draw(surface, font)

        text_surface = font.render(btn.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=btn.rect.center)

        text_px = surface.get_at(text_rect.center)
        bg_px = surface.get_at((btn.rect.x + 4, btn.rect.y + 4))

        assert text_px != bg_px, "Expected text to be drawn over themed button background"
    finally:
        pygame.quit()
