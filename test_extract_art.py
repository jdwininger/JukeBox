#!/usr/bin/env python3
"""
Test script to extract album art from all albums
"""

import os
import sys

# Add src to path
sys.path.append("src")

from album_library import AlbumLibrary


def main():
    print("Album Art Extraction Test")
    print("=" * 40)

    # Initialize library
    library = AlbumLibrary("music")

    # Scan for albums
    print("Scanning library...")
    library.scan_library()

    albums = library.get_albums()
    print(f"Found {len(albums)} albums")

    # Extract album art for all albums
    print("\nExtracting album art...")
    stats = library.extract_all_cover_art()

    print(f"\nExtraction complete!")
    print(f"Results: {stats}")


if __name__ == "__main__":
    main()
