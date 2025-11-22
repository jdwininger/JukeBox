"""
Music Player Module - Handles all music playback functionality
"""
import pygame
import os
from typing import List, Optional
from src.album_library import AlbumLibrary


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
            print("Warning: audio mixer not available — playback disabled until mixer is provided.")
        
        # Start with first available album
        albums = self.library.get_albums()
        if albums:
            self.current_album_id = albums[0].album_id
    
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
            return [track['title'] for track in album.tracks]
        return []
    
    def add_to_queue(self, album_id: int, track_index: int) -> None:
        """Add a track to the queue"""
        was_empty = len(self.queue) == 0
        self.queue.append((album_id, track_index))
        print(f"Added to queue: Album {album_id:02d}, Track {track_index + 1:02d}")
        
        # If queue was empty and nothing is playing, start playing
        if was_empty and not self.is_music_playing():
            self.start_queue()
    
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
    
    def play_from_queue(self) -> None:
        """Play the current track from the queue (always at index 0)"""
        if not self.queue:
            print("Queue is empty")
            return
        
        self.queue_index = 0
        album_id, track_index = self.queue[0]
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
            file_path = os.path.join(album.directory, track['filename'])
            
            # Apply equalizer processing if available
            if self.equalizer and hasattr(self.equalizer, 'process_file'):
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
                raise RuntimeError("Audio mixer is not available. Ensure pygame was installed with SDL_mixer/system audio libs and reinstall pygame.")

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            print(f"Now playing: {album.artist} - {album.title}")
            print(f"Track: {track['title']} ({track['duration_formatted']})")
        except Exception as e:
            print(f"Error playing track: {e}")
    
    def play(self, album_id: Optional[int] = None, track_index: Optional[int] = None) -> None:
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
            self.play_from_queue()
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
        self.play_from_queue()
    
    def update_music_state(self) -> None:
        """Update music state and advance queue if track ended"""
        if self.is_playing and not pygame.mixer.music.get_busy():
            # Track ended, move to next in queue
            self.next_track()
    
    def start_queue(self) -> None:
        """Start playing from the beginning of the queue"""
        if self.queue:
            self.queue_index = 0
            self.play_from_queue()
        else:
            print("Queue is empty")
    
    def pause(self) -> None:
        """Pause the current track"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
    
    def resume(self) -> None:
        """Resume the paused track"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
    
    def stop(self) -> None:
        """Stop the current track"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
    
    def next(self) -> None:
        """Play the next track in current album"""
        album = self.get_current_album()
        if album and album.tracks:
            self.current_track_index = (self.current_track_index + 1) % len(album.tracks)
            self.play()
    
    def previous(self) -> None:
        """Play the previous track in current album"""
        album = self.get_current_album()
        if album and album.tracks:
            self.current_track_index = (self.current_track_index - 1) % len(album.tracks)
            self.play()
    
    def next_album(self) -> None:
        """Play the first track of the next album"""
        albums = self.library.get_albums()
        if not albums:
            return
        
        current_index = next((i for i, a in enumerate(albums) if a.album_id == self.current_album_id), 0)
        next_index = (current_index + 1) % len(albums)
        self.play(album_id=albums[next_index].album_id, track_index=0)
    
    def previous_album(self) -> None:
        """Play the first track of the previous album"""
        albums = self.library.get_albums()
        if not albums:
            return
        
        current_index = next((i for i, a in enumerate(albums) if a.album_id == self.current_album_id), 0)
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
        if self.equalizer and hasattr(self.equalizer, 'apply_to_volume'):
            final_volume = self.equalizer.apply_to_volume(self.volume)
        
        pygame.mixer.music.set_volume(final_volume)
    
    def get_volume(self) -> float:
        """Get the current volume level (0.0 to 1.0)"""
        return self.volume
    
    def get_current_track_info(self) -> Optional[dict]:
        """Get current track information for optimization comparison"""
        track = self.get_current_track()
        if track:
            return {
                'album_id': self.current_album_id,
                'track_index': self.current_track_index,
                'title': track.get('title', ''),
                'artist': track.get('artist', '')
            }
        return None
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()
    
    def export_library(self, output_file: str) -> bool:
        """Export entire library to CSV"""
        return self.library.export_to_csv(output_file)
    
    def export_current_album(self, output_file: str) -> bool:
        """Export current album to CSV"""
        if self.current_album_id is None:
            return False
        return self.library.export_album_to_csv(self.current_album_id, output_file)
    
    def cleanup(self) -> None:
        """Clean up resources including equalizer temp files"""
        if self.equalizer and hasattr(self.equalizer, 'cleanup'):
            self.equalizer.cleanup()
        pygame.mixer.music.stop()
