"""
Music Player Module - Handles all music playback functionality
"""
import pygame
import os
from typing import List, Optional
from src.album_library import AlbumLibrary


class MusicPlayer:
    """Manages music playback and playlist operations"""
    
    def __init__(self, library: AlbumLibrary):
        """
        Initialize the music player
        
        Args:
            library: AlbumLibrary instance
        """
        self.library = library
        self.current_album_id = None
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.volume)
        
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
    
    def play(self, album_id: Optional[int] = None, track_index: Optional[int] = None) -> None:
        """
        Play a track from the library
        
        Args:
            album_id: Album ID to play from. If None, uses current album
            track_index: Track index. If None, plays from current index
        """
        if album_id is not None:
            self.current_album_id = album_id
            self.current_track_index = 0
        
        if track_index is not None:
            self.current_track_index = track_index
        
        album = self.get_current_album()
        if not album or not album.tracks:
            print("No album or tracks available")
            return
        
        if not (0 <= self.current_track_index < len(album.tracks)):
            self.current_track_index = 0
        
        try:
            track = album.tracks[self.current_track_index]
            file_path = os.path.join(album.directory, track['filename'])
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            print(f"Now playing: {album.artist} - {album.title}")
            print(f"Track: {track['title']} ({track['duration_formatted']})")
        except Exception as e:
            print(f"Error playing track: {e}")
    
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
        Set the volume level
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
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
