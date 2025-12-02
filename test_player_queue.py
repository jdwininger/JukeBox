#!/usr/bin/env python3
"""Tests for MusicPlayer queue behaviour"""
from types import SimpleNamespace

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


def test_add_to_queue_while_playing(monkeypatch):
    """When music is playing and the queue is empty, adding should append without needing credits."""
    lib = DummyLibrary()
    p = MusicPlayer(lib)

    # avoid touching audio
    monkeypatch.setattr(p, "_play_track", lambda a, b: None)
    # Simulate that a track is currently playing (mixer busy)
    monkeypatch.setattr(p, "is_music_playing", lambda: True)

    p.clear_queue()
    p._credits = 0

    # Should add even though credits are zero because playback is active
    p.add_to_queue(1, 0)
    assert len(p.get_queue()) == 1
