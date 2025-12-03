#!/usr/bin/env python3
"""Verify queue behavior when mixer API isn't available but logical playback is active."""

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


def test_add_to_queue_when_mixer_unavailable_but_playing(monkeypatch):
    lib = DummyLibrary()
    p = MusicPlayer(lib)

    # Simulate the mixer reporting not busy (False) but our logical state
    # indicates playback is active. This represents environments without
    # a working mixer but where the app still marks is_playing True.
    monkeypatch.setattr(p, "is_music_playing", lambda: False)
    p.is_playing = True

    p.clear_queue()
    p._credits = 0

    # Should append to queue even though the mixer API reports not busy
    p.add_to_queue(1, 0)
    assert len(p.get_queue()) == 1
