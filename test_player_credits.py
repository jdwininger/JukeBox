#!/usr/bin/env python3
"""Tests for the MusicPlayer credit system"""
from types import SimpleNamespace

import pytest

from src.player import MusicPlayer


class DummyAlbum:
    def __init__(self):
        self.album_id = 1
        self.tracks = [{"filename": "t1.mp3", "title": "T1", "duration_formatted": "0:30"}]
        self.directory = "."
        self.artist = "Artist"
        self.title = "Album"


class DummyLibrary:
    def __init__(self):
        self._albums = [DummyAlbum()]

    def get_albums(self):
        return self._albums

    def get_album(self, album_id):
        return self._albums[0]


def test_add_and_use_credit_basic():
    lib = DummyLibrary()
    p = MusicPlayer(lib)

    # initial credits = 0
    assert p.get_credits() == 0

    p.add_credit(2)
    assert p.get_credits() == 2

    assert p.use_credit() is True
    assert p.get_credits() == 1

    # using until zero
    assert p.use_credit() is True
    assert p.get_credits() == 0
    assert p.use_credit() is False


def test_add_to_queue_requires_credit(monkeypatch):
    lib = DummyLibrary()
    p = MusicPlayer(lib)

    # stub out playback (_play_track) so test doesn't touch audio
    monkeypatch.setattr(p, "_play_track", lambda a, b: None)
    # avoid pygame mixer calls in is_music_playing for headless tests
    monkeypatch.setattr(p, "is_music_playing", lambda: False)

    # queue empty and no credits -> attempting to add should fail (nothing added)
    p.clear_queue()
    p._credits = 0
    p.add_to_queue(1, 0)
    assert p.get_queue() == []

    # add a credit, then adding to queue should succeed and consume the credit
    p.add_credit(1)
    assert p.get_credits() == 1
    p.add_to_queue(1, 0)
    assert len(p.get_queue()) == 1
    # credit consumed by adding first item that triggers playback
    assert p.get_credits() == 0
