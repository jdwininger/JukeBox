#!/usr/bin/env python3
"""Test for fs_utils.preview_music_directory."""
import os
import tempfile
import shutil

from src.fs_utils import preview_music_directory


def test_preview_tmpdir():
    tmp = tempfile.mkdtemp(prefix='jukebox_test_')
    try:
        # create numbered directories and some files
        os.makedirs(os.path.join(tmp, '01'), exist_ok=True)
        with open(os.path.join(tmp, '01', 'track1.mp3'), 'wb') as f:
            f.write(b'\x00' * 100)
        # top-level file
        with open(os.path.join(tmp, 'note.txt'), 'w') as f:
            f.write('hello')

        res = preview_music_directory(tmp)
        assert res['exists'] is True
        assert res['is_dir'] is True
        assert '01' in res['album_slots']
        assert res['audio_files_count'] >= 1
        assert 'note.txt' in res['sample_files']

        print('test_fs_preview.py: OK')
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    test_preview_tmpdir()
