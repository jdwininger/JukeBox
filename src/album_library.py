"""
Album Manager Module - Manages albums in numbered directories and exports metadata to CSV
"""
import os
import csv
from typing import Dict, List, Optional
from src.metadata import MetadataReader


class Album:
    """Represents a single album"""
    
    def __init__(self, album_id: int, directory: str):
        """
        Initialize an album
        
        Args:
            album_id: Album ID (1-50)
            directory: Path to the album directory
        """
        self.album_id = album_id
        self.directory = directory
        self.artist = "Unknown"
        self.title = "Unknown"
        self.tracks: List[Dict] = []
        self.is_valid = False
    
    def scan(self) -> bool:
        """
        Scan the album directory for audio files and extract metadata
        
        Returns:
            True if album is valid (has audio files), False otherwise
        """
        if not os.path.isdir(self.directory):
            return False
        
        self.tracks = []
        audio_files = []
        
        # Find all audio files in the directory
        try:
            for file in sorted(os.listdir(self.directory)):
                if file.lower().endswith(MetadataReader.SUPPORTED_FORMATS):
                    file_path = os.path.join(self.directory, file)
                    audio_files.append(file_path)
        except Exception as e:
            print(f"Error scanning directory {self.directory}: {e}")
            return False
        
        if not audio_files:
            return False
        
        # Read metadata from each file
        for file_path in audio_files:
            metadata = MetadataReader.read_track_metadata(file_path)
            if metadata:
                self.tracks.append(metadata)
                
                # Use first track to set album artist if not set
                if self.artist == "Unknown":
                    self.artist = metadata['artist']
        
        # Set album title from first track if available
        if self.tracks and self.title == "Unknown":
            self.title = self.tracks[0].get('album', 'Unknown')
        
        self.is_valid = len(self.tracks) > 0
        return self.is_valid
    
    def extract_cover_art(self) -> bool:
        """
        Extract album art from the first track and save as cover.jpg
        
        Returns:
            True if art was extracted and saved, False otherwise
        """
        if not self.tracks:
            return False
        
        # Get the first track file path
        first_track = self.tracks[0]
        track_path = os.path.join(self.directory, first_track['filename'])
        cover_path = os.path.join(self.directory, 'cover.jpg')
        
        # Skip if cover.jpg already exists
        if os.path.exists(cover_path):
            print(f"Album {self.album_id:02d}: cover.jpg already exists")
            return True
        
        # Try to extract embedded art
        if MetadataReader.extract_album_art(track_path, cover_path):
            print(f"Album {self.album_id:02d}: Extracted cover art from {first_track['filename']}")
            return True
        else:
            print(f"Album {self.album_id:02d}: No embedded art found in {first_track['filename']}")
            return False
    
    def to_csv_rows(self) -> List[List[str]]:
        """
        Convert album data to CSV rows
        
        Returns:
            List of rows: first is header, rest are tracks
        """
        rows = [
            ['Artist', self.artist],
            ['Album', self.title],
            ['Track #', 'Title', 'Duration']
        ]
        
        for i, track in enumerate(self.tracks, 1):
            rows.append([
                str(i),
                track['title'],
                track['duration_formatted']
            ])
        
        return rows


class AlbumLibrary:
    """Manages the entire album library (1-50 albums)"""
    
    MAX_ALBUMS = 50
    
    def __init__(self, library_directory: str):
        """
        Initialize the album library
        
        Args:
            library_directory: Path to the main music directory
        """
        self.library_directory = library_directory
        self.albums: Dict[int, Album] = {}
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self) -> None:
        """Create the music directory if it doesn't exist"""
        if not os.path.exists(self.library_directory):
            os.makedirs(self.library_directory)
            print(f"Created library directory: {self.library_directory}")
    
    def scan_library(self) -> None:
        """Scan all numbered directories (01-50) for albums"""
        self.albums = {}
        
        for i in range(1, self.MAX_ALBUMS + 1):
            album_dir = os.path.join(self.library_directory, f"{i:02d}")
            album = Album(i, album_dir)
            
            if album.scan():
                self.albums[i] = album
                print(f"Album {i:02d}: {album.artist} - {album.title} ({len(album.tracks)} tracks)")
    
    def get_album(self, album_id: int) -> Optional[Album]:
        """
        Get an album by ID
        
        Args:
            album_id: Album ID (1-50)
            
        Returns:
            Album object or None if not found
        """
        return self.albums.get(album_id)
    
    def get_albums(self) -> List[Album]:
        """Get all valid albums"""
        return sorted(self.albums.values(), key=lambda a: a.album_id)
    
    def export_to_csv(self, output_file: str) -> bool:
        """
        Export all album metadata to a CSV file
        
        Args:
            output_file: Path to the output CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for album in self.get_albums():
                    rows = album.to_csv_rows()
                    for row in rows:
                        writer.writerow(row)
                    # Add blank row between albums
                    writer.writerow([])
            
            print(f"Library exported to: {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting library: {e}")
            return False
    
    def export_album_to_csv(self, album_id: int, output_file: str) -> bool:
        """
        Export a single album to CSV
        
        Args:
            album_id: Album ID (1-50)
            output_file: Path to the output CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        album = self.get_album(album_id)
        if not album:
            print(f"Album {album_id:02d} not found")
            return False
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                rows = album.to_csv_rows()
                for row in rows:
                    writer.writerow(row)
            
            print(f"Album exported to: {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting album: {e}")
            return False
    
    def get_library_stats(self) -> Dict:
        """Get library statistics"""
        total_tracks = sum(len(album.tracks) for album in self.albums.values())
        total_duration = sum(
            sum(track['duration_seconds'] for track in album.tracks)
            for album in self.albums.values()
        )
        
        return {
            'total_albums': len(self.albums),
            'max_albums': self.MAX_ALBUMS,
            'total_tracks': total_tracks,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': self._format_duration(total_duration)
        }
    
    def extract_all_cover_art(self) -> Dict[str, int]:
        """
        Extract cover art for all albums from their first tracks
        
        Returns:
            Dictionary with extraction statistics
        """
        stats = {'extracted': 0, 'existing': 0, 'failed': 0, 'total': 0}
        
        for album in self.get_albums():
            stats['total'] += 1
            cover_path = os.path.join(album.directory, 'cover.jpg')
            
            if os.path.exists(cover_path):
                stats['existing'] += 1
            elif album.extract_cover_art():
                stats['extracted'] += 1
            else:
                stats['failed'] += 1
        
        print(f"Cover art extraction complete:")
        print(f"  Total albums: {stats['total']}")
        print(f"  Already had cover.jpg: {stats['existing']}")
        print(f"  Successfully extracted: {stats['extracted']}")
        print(f"  Failed to extract: {stats['failed']}")
        
        return stats
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
