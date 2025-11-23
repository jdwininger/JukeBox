#!/usr/bin/env python3
"""Test that AlbumLibrary ensures numbered album directories are created."""
import os
import shutil
import tempfile

from src.album_library import AlbumLibrary


def test_album_slots_created():
    tmp = tempfile.mkdtemp(prefix='jukebox_test_')
    try:
        # initialize library at tmp path
        lib = AlbumLibrary(tmp)

        # Ensure the base path exists
        assert os.path.exists(tmp)

        # Check the expected numbered directories exist
        expected = [os.path.join(tmp, f"{i:02d}") for i in range(1, AlbumLibrary.MAX_ALBUMS + 1)]
        missing = [p for p in expected if not os.path.isdir(p)]
        assert not missing, f"Missing album slot directories: {missing}"

        print('Album slot directories found OK')
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    test_album_slots_created()
    print('test_album_dirs.py: OK')
