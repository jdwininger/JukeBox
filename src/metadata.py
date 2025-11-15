"""
Metadata Module - Handles ID3 tag reading and metadata extraction
"""
import os
from typing import Dict, List, Optional, Tuple
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE


class MetadataReader:
    """Reads and extracts metadata from audio files"""
    
    SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac')
    
    @staticmethod
    def get_duration_seconds(duration_ms: float) -> int:
        """Convert milliseconds to seconds"""
        return int(duration_ms / 1000)
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds to MM:SS format"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    @classmethod
    def read_track_metadata(cls, file_path: str) -> Optional[Dict]:
        """
        Read metadata from a single audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with track metadata or None if reading fails
        """
        if not os.path.exists(file_path):
            return None
        
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            if ext == '.mp3':
                return cls._read_mp3(file_path)
            elif ext == '.flac':
                return cls._read_flac(file_path)
            elif ext == '.ogg':
                return cls._read_ogg(file_path)
            elif ext == '.wav':
                return cls._read_wav(file_path)
        except Exception as e:
            print(f"Error reading metadata from {filename}: {e}")
            return None
        
        return None
    
    @staticmethod
    def _read_mp3(file_path: str) -> Optional[Dict]:
        """Read MP3 metadata"""
        try:
            audio = EasyID3(file_path)
            title = audio.get('title', ['Unknown'])[0]
            artist = audio.get('artist', ['Unknown'])[0]
            album = audio.get('album', ['Unknown'])[0]
            
            # Get duration
            from mutagen.mp3 import MP3
            mp3_audio = MP3(file_path)
            duration_seconds = MetadataReader.get_duration_seconds(mp3_audio.info.length * 1000)
            
            return {
                'title': title,
                'artist': artist,
                'album': album,
                'duration_seconds': duration_seconds,
                'duration_formatted': MetadataReader.format_time(duration_seconds),
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            print(f"Error reading MP3: {e}")
            return None
    
    @staticmethod
    def _read_flac(file_path: str) -> Optional[Dict]:
        """Read FLAC metadata"""
        try:
            audio = FLAC(file_path)
            title = audio.get('title', ['Unknown'])[0] if audio.get('title') else 'Unknown'
            artist = audio.get('artist', ['Unknown'])[0] if audio.get('artist') else 'Unknown'
            album = audio.get('album', ['Unknown'])[0] if audio.get('album') else 'Unknown'
            
            duration_seconds = int(audio.info.length)
            
            return {
                'title': title,
                'artist': artist,
                'album': album,
                'duration_seconds': duration_seconds,
                'duration_formatted': MetadataReader.format_time(duration_seconds),
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            print(f"Error reading FLAC: {e}")
            return None
    
    @staticmethod
    def _read_ogg(file_path: str) -> Optional[Dict]:
        """Read OGG Vorbis metadata"""
        try:
            audio = OggVorbis(file_path)
            title = audio.get('title', ['Unknown'])[0] if audio.get('title') else 'Unknown'
            artist = audio.get('artist', ['Unknown'])[0] if audio.get('artist') else 'Unknown'
            album = audio.get('album', ['Unknown'])[0] if audio.get('album') else 'Unknown'
            
            duration_seconds = int(audio.info.length)
            
            return {
                'title': title,
                'artist': artist,
                'album': album,
                'duration_seconds': duration_seconds,
                'duration_formatted': MetadataReader.format_time(duration_seconds),
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            print(f"Error reading OGG: {e}")
            return None
    
    @staticmethod
    def _read_wav(file_path: str) -> Optional[Dict]:
        """Read WAV metadata"""
        try:
            audio = WAVE(file_path)
            
            # WAV files may not have ID3 tags, use filename as fallback
            title = 'Unknown'
            artist = 'Unknown'
            album = 'Unknown'
            
            if audio.tags:
                title = audio.tags.get('TIT2', ['Unknown'])[0].text[0] if audio.tags.get('TIT2') else 'Unknown'
                artist = audio.tags.get('TPE1', ['Unknown'])[0].text[0] if audio.tags.get('TPE1') else 'Unknown'
                album = audio.tags.get('TALB', ['Unknown'])[0].text[0] if audio.tags.get('TALB') else 'Unknown'
            
            duration_seconds = int(audio.info.length)
            
            return {
                'title': title,
                'artist': artist,
                'album': album,
                'duration_seconds': duration_seconds,
                'duration_formatted': MetadataReader.format_time(duration_seconds),
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            print(f"Error reading WAV: {e}")
            return None
