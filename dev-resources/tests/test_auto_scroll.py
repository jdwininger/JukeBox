import os
import pygame
import types

from src.ui import UI


class SimpleAlbum:
    def __init__(self, album_id, tracks):
        self.album_id = album_id
        self.tracks = [{'filename': f't{i}.mp3', 'title': f'Track {i}', 'duration_formatted': '0:30'} for i in range(1, tracks + 1)]
        self.directory = '.'
        self.artist = 'Artist'
        self.title = f'Album {album_id}'


class SimpleLibrary:
    def __init__(self, albums):
        self._albums = albums

    def get_albums(self):
        return self._albums


class DummyConfig:
    def __init__(self):
        self._d = {}

    def get(self, k, d=None):
        return self._d.get(k, d)

    def set(self, k, v):
        self._d[k] = v


def test_auto_scroll_reaches_last_tracks():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    pygame.font.init()
    try:
        # Create 4 albums with varying sizes around the trigger (8)
        albums = [SimpleAlbum(i + 1, size) for i, size in enumerate([7, 9, 11, 13])]
        lib = SimpleLibrary(albums)

        # UI expects a player object with a 'library' attribute; provide a simple stub
        player_stub = types.SimpleNamespace(library=lib, current_album_id=1)
        ui = UI(player=player_stub, library=lib, config=DummyConfig(), theme_manager=types.SimpleNamespace(get_current_theme=lambda: None, themes={}))

        # Force small card height so visible rows will be relatively small
        card_w, card_h = 360, 120

        # Place the card rects for indices 0..3
        rects = {i: pygame.Rect(10 + i * 10, 10, card_w, card_h) for i in range(4)}
        ui._album_card_rects_for_update = rects

        ui.album_card_auto_scroll_enabled = True
        ui.album_card_auto_scroll_speed = 0.0  # allow immediate updates in loop

        # initialize timers in past so first update will scroll
        for alb in albums:
            ui.album_card_auto_scroll_timers[alb.album_id] = 0

        # Run updates many iterations and record the maximum offset seen for each album
        max_seen = {alb.album_id: 0 for alb in albums}
        # number of iterations should be large enough to let offsets reach the end
        iterations = 64
        for _ in range(iterations):
            # call the update and then refresh simulated time
            ui._update_album_card_auto_scroll()
            for alb in albums:
                off = ui.album_card_scroll_offsets.get(alb.album_id, 0)
                if off > max_seen[alb.album_id]:
                    max_seen[alb.album_id] = off

        # Validate behavior: albums <=8 should not scroll; >8 should reach at least 1
        for alb in albums:
            visible = ui._compute_visible_tracks_for_card(alb, rects[albums.index(alb)].x, rects[albums.index(alb)].y, rects[albums.index(alb)].width, rects[albums.index(alb)].height, 9)
            max_offset_expected = max(0, len(alb.tracks) - visible)
            if len(alb.tracks) <= 8:
                assert max_seen[alb.album_id] == 0, f"Album {alb.album_id} should not scroll (<=8 tracks)"
            else:
                assert max_seen[alb.album_id] > 0, f"Album {alb.album_id} did not scroll as expected"
                # check we reached the final scroll offset at some point
                assert max_seen[alb.album_id] >= max_offset_expected, (
                    f"Album {alb.album_id} did not reach final offset (seen {max_seen[alb.album_id]}, expected {max_offset_expected})"
                )

        # Also verify hover pause prevents updates: mark album 3 as hovered and ensure its offset stays unchanged
        alb3 = albums[2]
        ui.album_card_scroll_offsets[alb3.album_id] = 0
        ui.album_card_hover_pause[alb3.album_id] = True
        ui.album_card_auto_scroll_timers[alb3.album_id] = 0
        for _ in range(10):
            ui._update_album_card_auto_scroll()
        assert ui.album_card_scroll_offsets.get(alb3.album_id, 0) == 0, "Hover paused album should not scroll"
    finally:
        pygame.quit()
