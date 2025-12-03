#!/usr/bin/env python3
"""Tests for keypad/4-digit selection handling (keyboard + keypad + backspace)."""
import os
import pygame

from src.ui import UI


class DummyConfig:
    def __init__(self):
        self._d = {}

    def get(self, key, default=None):
        return self._d.get(key, default)

    def set(self, k, v):
        self._d[k] = v

    def save(self):
        pass


class DummyAlbum:
    def __init__(self, album_id, tracks):
        self.album_id = album_id
        self.tracks = tracks


class DummyLibrary:
    def __init__(self):
        # album 1 exists with 4 tracks
        self._albums = {1: DummyAlbum(1, ["t1", "t2", "t3", "t4"])}

    def get_album(self, album_id: int):
        return self._albums.get(album_id)

    def get_albums(self):
        return list(self._albums.values())


class StubThemeManager:
    def get_current_theme(self):
        return None

    themes = {}


def _init():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def _quit():
    pygame.quit()


def test_numpad_keys_do_not_auto_execute():
    _init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())

        # Simulate keypad keys: kp0, kp1, kp0, kp3 -> 0103 should auto-execute
        for k in [pygame.K_KP0, pygame.K_KP1, pygame.K_KP0]:
            evt = pygame.event.Event(pygame.KEYDOWN, {"key": k})
            ui.handle_number_input(evt)
        assert ui.selection_buffer == "010"

        # 4th digit should NOT auto-execute — buffer should remain and
        # selection_mode should still be True until Enter is pressed.
        evt = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_KP3})
        ui.handle_number_input(evt)
        assert ui.selection_buffer == "0103"
        assert ui.selection_mode is True
    finally:
        _quit()


def test_backspace_key_removes_last_digit():
    _init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())

        # Insert two digits via keyboard
        ui.handle_number_input(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_1}))
        ui.handle_number_input(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_2}))
        assert ui.selection_buffer == "12"

        # Post a backspace key event and run handle_events()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_BACKSPACE}))
        ui.handle_events()
        assert ui.selection_buffer == "1"
    finally:
        _quit()


def test_keypad_enter_executes_selection():
    _init()
    try:
        ui = UI(player=None, library=DummyLibrary(), config=DummyConfig(), theme_manager=StubThemeManager())

        # Directly set a 4-digit selection and press keypad Enter
        ui.selection_buffer = "0103"
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_KP_ENTER}))
        ui.handle_events()

        # After execute_selection buffer should be cleared
        assert ui.selection_buffer == ""
        assert ui.selection_mode is False
    finally:
        _quit()
