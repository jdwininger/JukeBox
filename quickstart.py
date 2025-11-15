#!/usr/bin/env python3
"""
Quick Start Example - Demonstrates library usage
"""
from src.album_library import AlbumLibrary
import os


def main():
    """Run quick start example"""
    # Setup library directory
    music_dir = os.path.join(os.path.dirname(__file__), 'music')
    
    # Create library instance
    library = AlbumLibrary(music_dir)
    
    # Scan for albums
    print("Scanning library...")
    library.scan_library()
    
    # Display statistics
    stats = library.get_library_stats()
    print(f"\n{'='*60}")
    print(f"Library Statistics")
    print(f"{'='*60}")
    print(f"Albums Found: {stats['total_albums']}/{stats['max_albums']}")
    print(f"Total Tracks: {stats['total_tracks']}")
    print(f"Total Duration: {stats['total_duration_formatted']}")
    print()
    
    # Display albums
    albums = library.get_albums()
    if albums:
        print(f"{'='*60}")
        print(f"Albums in Library")
        print(f"{'='*60}")
        for album in albums:
            print(f"\n[Album {album.album_id:02d}] {album.artist} - {album.title}")
            print(f"  Tracks: {len(album.tracks)}")
            for i, track in enumerate(album.tracks[:5], 1):
                print(f"    {i}. {track['title']} ({track['duration_formatted']})")
            if len(album.tracks) > 5:
                print(f"    ... and {len(album.tracks) - 5} more tracks")
    else:
        print("\nNo albums found!")
        print("Please add music files to the 'music/' directory in numbered folders (01-50)")
    
    # Export library
    print(f"\n{'='*60}")
    export_path = os.path.join(os.path.dirname(__file__), 'library_export.csv')
    if library.export_to_csv(export_path):
        print(f"✓ Library exported to: {export_path}")
    else:
        print("✗ Export failed")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
