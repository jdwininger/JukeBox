"""
Music Player Module - Handles all music playback functionality
"""
import os
from typing import List, Optional

import pygame

from src.album_library import AlbumLibrary
from src.audio_utils import is_mixer_available


class MusicPlayer:
    """Manages music playback and playlist operations"""

    def __init__(self, library: AlbumLibrary, equalizer=None):
        """
        Initialize the music player

        Args:
            library: AlbumLibrary instance
            equalizer: Equalizer instance for audio processing
        """
        self.library = library
        self.equalizer = equalizer
        self.current_album_id = None
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7

        # Queue system: list of (album_id, track_index) tuples
        self.queue = []
        self.queue_index = 0

        # Set initial volume if an audio mixer is available — otherwise warn.
        try:
            from src.audio_utils import is_mixer_available
        except Exception:
            is_mixer_available = None

        if is_mixer_available is not None and is_mixer_available():
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception:
                # If calling mixer functions fails for any reason, continue
                # but provide a helpful message later when playback is attempted.
                pass
        else:
            # Mixer not available at init — attempt a one-off safe init so the
            # app can recover in environments where libs were installed later
            # or in CI where a dummy driver is configured.
            try:
                from src.audio_utils import attempt_mixer_init

                ok, msg = attempt_mixer_init()
                if ok:
                    try:
                        pygame.mixer.music.set_volume(self.volume)
                    except Exception:
                        pass
                else:
                    print(
                        "Warning: audio mixer not available — playback disabled until mixer is provided.",
                        msg,
                    )
            except Exception:
                print(
                    "Warning: audio mixer not available — playback disabled until mixer is provided."
                )

        # Start with first available album
        albums = self.library.get_albums()
        if albums:
            self.current_album_id = albums[0].album_id

        # Credits system: number of available play credits (1 credit allows one play)
        self._credits = 0

    # ----- Credits API -----
    def add_credit(self, amount: int = 1) -> None:
        """Add credits to the player.

        Args:
            amount: Number of credits to add (must be >= 0)
        """
        try:
            amount = int(amount)
        except Exception:
            return
        if amount <= 0:
            return
        self._credits += amount

    def use_credit(self) -> bool:
        """Attempt to consume a single credit.

        Returns:
            True if a credit was available and consumed, False otherwise.
        """
        if self._credits >= 1:
            self._credits -= 1
            return True
        return False

    def get_credits(self) -> int:
        """Return the current number of available credits."""
        return self._credits

    def get_current_album(self):
        """Get the current album"""
        if self.current_album_id is None:
            return None
        return self.library.get_album(self.current_album_id)

    def get_current_track(self) -> Optional[dict]:
        """Get the current track metadata"""
        album = self.get_current_album()
        if album and 0 <= self.current_track_index < len(album.tracks):
            return album.tracks[self.current_track_index]
        return None

    def get_playlist(self) -> List[str]:
        """Get the list of track names in current album"""
        album = self.get_current_album()
        if album:
            return [track["title"] for track in album.tracks]
        return []

    def add_to_queue(self, album_id: int, track_index: int) -> None:
        """Add a track to the queue"""
        was_empty = len(self.queue) == 0
        # If adding the first track to an empty queue would immediately start
        # playback (nothing is playing), require a credit before appending.
        # Use the logical playing state (self.is_playing) as well as the
        # mixer-reported state. On systems without a mixer available the
        # mixer API may not report busy, but our logical state will still
        # indicate playback is underway — in that case we must not require
        # an extra credit to append to the queue.
        if was_empty and not (self.is_music_playing() or self.is_playing):
            if not self.use_credit():
                print("Insufficient credits to start playback")
                return
        self.queue.append((album_id, track_index))
        print(f"Added to queue: Album {album_id:02d}, Track {track_index + 1:02d}")

        # If queue was empty and nothing is playing, start playing
        if was_empty and not self.is_music_playing():
            # we've already consumed a credit above if we needed one, so
            # prevent start_queue from trying to consume again
            self.start_queue(require_credit=False)

    def get_queue(self) -> List[tuple]:
        """Get the current queue"""
        return self.queue

    def clear_queue(self) -> None:
        """Clear the entire queue"""
        self.queue = []
        self.queue_index = 0
        print("Queue cleared")

    def get_queue_info(self) -> str:
        """Get formatted queue information"""
        if not self.queue:
            return "Queue is empty"

        queue_text = f"Queue ({len(self.queue)} songs):\n"
        for i, (album_id, track_index) in enumerate(self.queue):
            album = self.library.get_album(album_id)
            if album and 0 <= track_index < len(album.tracks):
                track = album.tracks[track_index]
                status = " [PLAYING]" if i == 0 and self.is_playing else ""
                queue_text += f"{i+1:2d}. {album.artist} - {track['title']}{status}\n"
        return queue_text.strip()

    def play_from_queue(self, require_credit: bool = True) -> None:
        """Play the current track from the queue (always at index 0)

        Args:
            require_credit: If True, consume one credit to start playback. If False,
                playback will proceed without consuming credits (used for automatic
                queue progression).
        """
        if not self.queue:
            print("Queue is empty")
            return

        self.queue_index = 0
        album_id, track_index = self.queue[0]
        # If this playback is user-initiated and credits are required, try to use one
        if require_credit:
            if not self.use_credit():
                print("Insufficient credits to play from queue")
                return
        self._play_track(album_id, track_index)

    def _play_track(self, album_id: int, track_index: int) -> None:
        """Internal method to play a specific track"""
        self.current_album_id = album_id
        self.current_track_index = track_index

        album = self.get_current_album()
        if not album or not album.tracks:
            print("No album or tracks available")
            return

        if not (0 <= self.current_track_index < len(album.tracks)):
            print("Invalid track index")
            return

        try:
            track = album.tracks[self.current_track_index]
            file_path = os.path.join(album.directory, track["filename"])

            # Apply equalizer processing if available
            if self.equalizer and hasattr(self.equalizer, "process_file"):
                processed_file = self.equalizer.process_file(file_path)
                if processed_file and processed_file != file_path:
                    file_path = processed_file
                    print(f"Applied equalizer processing")

            # Ensure the mixer is available before attempting to play audio
            try:
                from src.audio_utils import is_mixer_available
            except Exception:
                is_mixer_available = None

            if is_mixer_available is None or not is_mixer_available():
                # Try a last-ditch init attempt if the mixer module exists but
                # wasn't initialised at startup. This will help in cases where
                # the system audio backend becomes available while the app runs.
                try:
                    from src.audio_utils import attempt_mixer_init

                    ok, msg = attempt_mixer_init()
                    if not ok:
                        raise RuntimeError(
                            "Audio mixer is not available. Ensure pygame was installed with SDL_mixer/system audio libs and reinstall pygame. "
                            + msg
                        )
                except Exception:
                    raise RuntimeError(
                        "Audio mixer is not available. Ensure pygame was installed with SDL_mixer/system audio libs and reinstall pygame."
                    )

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            print(f"Now playing: {album.artist} - {album.title}")
            print(f"Track: {track['title']} ({track['duration_formatted']})")
        except Exception as e:
            print(f"Error playing track: {e}")

    def play(
        self, album_id: Optional[int] = None, track_index: Optional[int] = None
    ) -> None:
        """
        Add a track to the queue instead of playing immediately

        Args:
            album_id: Album ID to add to queue. If None and queue exists, play from queue
            track_index: Track index to add to queue
        """
        if album_id is not None and track_index is not None:
            # Add to queue instead of playing immediately
            self.add_to_queue(album_id, track_index)
        elif self.queue and not self.is_music_playing():
            # If nothing is playing and we have a queue, play from queue
            self.play_from_queue(require_credit=False)
        else:
            print("No track specified or already playing")

    def next_track(self) -> None:
        """Play the next track in the queue"""
        if not self.queue:
            print("Queue is empty")
            return

        # Remove the currently playing song from the queue
        if len(self.queue) > 0:
            completed_song = self.queue.pop(0)
            print(f"Completed: {completed_song}")

        # Play the next song (now at index 0) if queue not empty
        if self.queue:
            self.queue_index = 0
            self.play_from_queue()
        else:
            print("Queue completed")
            self.is_playing = False
            # Stop only if mixer is available
            try:
                from src.audio_utils import is_mixer_available
            except Exception:
                is_mixer_available = None

            if is_mixer_available is not None and is_mixer_available():
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass

    def previous_track(self) -> None:
        """Play the previous track (restart current track since previous songs are removed)"""
        if not self.queue:
            print("Queue is empty")
            return

        # Since previous songs are removed, just restart the current track
        print("Restarting current track")
        self.queue_index = 0
        self.play_from_queue(require_credit=False)

    def update_music_state(self) -> None:
        """Update music state and advance queue if track ended.

        Safely handle the case where the mixer is not available. If the
        mixer is unavailable we cannot reliably determine playback state and
        therefore skip advancing the queue.
        """
        if not self.is_playing:
            return

        if not is_mixer_available():
            return

        try:
            if not pygame.mixer.music.get_busy():
                # Track ended, move to next in queue
                self.next_track()
        except Exception:
            # Ignore mixer errors — don't crash the app
            return

    def start_queue(self, require_credit: bool = True) -> None:
        """Start playing from the beginning of the queue"""
        if self.queue:
            self.queue_index = 0
            self.play_from_queue(require_credit=require_credit)
        else:
            print("Queue is empty")

    def pause(self) -> None:
        """Pause the current track (safe when mixer unavailable)."""
        if not self.is_playing or self.is_paused:
            return

        if not is_mixer_available():
            # Mixer not available — change logical state only
            self.is_paused = True
            return

        try:
            pygame.mixer.music.pause()
        except Exception:
            # If pause fails, keep internal state consistent
            pass
        self.is_paused = True

    def resume(self) -> None:
        """Resume the paused track (safe when mixer unavailable)."""
        if not self.is_paused:
            return

        if not is_mixer_available():
            # Mixer not available — only update logical state
            self.is_paused = False
            return

        try:
            pygame.mixer.music.unpause()
        except Exception:
            # Ignore errors coming from mixer
            pass
        self.is_paused = False

    def stop(self) -> None:
        """Stop the current track (no-op if mixer unavailable)."""
        if is_mixer_available():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.is_playing = False
        self.is_paused = False

    def next(self) -> None:
        """Play the next track in current album"""
        album = self.get_current_album()
        if album and album.tracks:
            self.current_track_index = (self.current_track_index + 1) % len(
                album.tracks
            )
            self.play()

    def previous(self) -> None:
        """Play the previous track in current album"""
        album = self.get_current_album()
        if album and album.tracks:
            self.current_track_index = (self.current_track_index - 1) % len(
                album.tracks
            )
            self.play()

    def next_album(self) -> None:
        """Play the first track of the next album"""
        albums = self.library.get_albums()
        if not albums:
            return

        current_index = next(
            (i for i, a in enumerate(albums) if a.album_id == self.current_album_id), 0
        )
        next_index = (current_index + 1) % len(albums)
        self.play(album_id=albums[next_index].album_id, track_index=0)

    def previous_album(self) -> None:
        """Play the first track of the previous album"""
        albums = self.library.get_albums()
        if not albums:
            return

        current_index = next(
            (i for i, a in enumerate(albums) if a.album_id == self.current_album_id), 0
        )
        prev_index = (current_index - 1) % len(albums)
        self.play(album_id=albums[prev_index].album_id, track_index=0)

    def set_volume(self, volume: float) -> None:
        """
        Set the volume level with equalizer adjustment

        Args:
            volume: Base volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))

        # Apply equalizer volume adjustment if available
        final_volume = self.volume
        if self.equalizer and hasattr(self.equalizer, "apply_to_volume"):
            final_volume = self.equalizer.apply_to_volume(self.volume)

        # Set mixer volume only if mixer is available; ignore errors
        if is_mixer_available():
            try:
                pygame.mixer.music.set_volume(final_volume)
            except Exception:
                pass

    def get_volume(self) -> float:
        """Get the current volume level (0.0 to 1.0)"""
        return self.volume

    def get_current_track_info(self) -> Optional[dict]:
        """Get current track information for optimization comparison"""
        track = self.get_current_track()
        if track:
            return {
                "album_id": self.current_album_id,
                "track_index": self.current_track_index,
                "title": track.get("title", ""),
                "artist": track.get("artist", ""),
            }
        return None

    def is_music_playing(self) -> bool:
        """Check if music is currently playing.

        Returns False when the mixer is unavailable or if calling the mixer
        APIs raises an exception. This avoids crashing in environments where
        pygame was built without audio support.
        """
        try:
            if not is_mixer_available():
                return False
            return bool(pygame.mixer.music.get_busy())
        except Exception:
            return False

    def export_library(self, output_file: str) -> bool:
        """Export entire library to CSV"""
        return self.library.export_to_csv(output_file)

    def export_current_album(self, output_file: str) -> bool:
        """Export current album to CSV"""
        if self.current_album_id is None:
            return False
        return self.library.export_album_to_csv(self.current_album_id, output_file)

    def cleanup(self) -> None:
        """Clean up resources including equalizer temp files."""
        if self.equalizer and hasattr(self.equalizer, "cleanup"):
            self.equalizer.cleanup()

        if is_mixer_available():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
