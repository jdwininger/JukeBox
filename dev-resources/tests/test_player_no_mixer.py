import tempfile
import os
from src.album_library import AlbumLibrary
from src.player import MusicPlayer


def test_player_methods_safe_when_mixer_unavailable(monkeypatch, tmp_path):
    # Ensure the player module uses our monkeypatched function
    monkeypatch.setattr('src.player.is_mixer_available', lambda: False)

    # Create a temporary library dir (AlbumLibrary will create subdirs)
    library_dir = tmp_path / "music_lib"
    library_dir = str(library_dir)
    library = AlbumLibrary(library_dir)

    player = MusicPlayer(library)

    # Setting volume should not raise and state should update
    player.set_volume(0.3)
    assert abs(player.get_volume() - 0.3) < 1e-6

    # When mixer unavailable, is_music_playing should be False
    assert player.is_music_playing() is False

    # Pause/resume/stop/cleanup should not raise even when mixer is missing
    # Simulate that playback was active so pause will have an effect
    player.is_playing = True
    player.pause()
    assert player.is_paused is True

    player.resume()
    assert player.is_paused is False

    # stop should set playing flags appropriately
    player.is_playing = True
    player.stop()
    assert player.is_playing is False and player.is_paused is False

    # cleanup should not raise
    player.cleanup()

    # Adding to queue when mixer is missing and no credits should not add
    before = len(player.get_queue())
    player.add_to_queue(1, 0)
    assert len(player.get_queue()) == before
