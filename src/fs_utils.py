"""Filesystem helper utilities used by the UI.

This module provides a small, testable function to preview a music directory
without touching global UI state. It returns a summary dict with basic
information used by the config preview modal.
"""
import os
from typing import Dict, List


SUPPORTED = ('.mp3', '.wav', '.ogg', '.flac')


def preview_music_directory(path: str, max_items: int = 10) -> Dict:
    """Return a small summary of the given path.

    Summary keys:
      - exists: bool - whether path exists
      - is_dir: bool - whether path is a directory
      - album_slots: list[str] - numbered album directories found (01..52)
      - sample_files: list[str] - first `max_items` audio or other files
      - audio_files_count: int - total number of audio files in path (recursive)
    """
    result: Dict = {
        'exists': False,
        'is_dir': False,
        'album_slots': [],
        'sample_files': [],
        'audio_files_count': 0,
    }

    if not path:
        return result

    path = os.path.expanduser(path)
    result['exists'] = os.path.exists(path)
    result['is_dir'] = os.path.isdir(path)

    if not result['exists'] or not result['is_dir']:
        return result

    # Check for numbered album slots 01..52
    slots = []
    for i in range(1, 53):
        sub = os.path.join(path, f"{i:02d}")
        if os.path.isdir(sub):
            slots.append(f"{i:02d}")
    result['album_slots'] = slots

    # Gather first-level files (non-recursive) and count audio files recursively
    sample = []
    audio_count = 0
    try:
        for root, dirs, files in os.walk(path):
            # Count audio files
            for fn in files:
                if fn.lower().endswith(SUPPORTED):
                    audio_count += 1

            # Collect up to max_items sample files from top-level directory only
            if root == path:
                for fn in files:
                    sample.append(fn)
                    if len(sample) >= max_items:
                        break

            # Stop further deep walking if we've counted far enough
            # (but we still want accurate counts; keep walking)

        result['audio_files_count'] = audio_count
        result['sample_files'] = sample[:max_items]
    except Exception:
        # On any error, return partial results
        pass

    return result


def list_directory(path: str) -> Dict:
    """Return a listing summary used by the in-app pure-pygame browser.

    Returns a dict with keys:
      - path: the absolute expanded path
      - exists: bool
      - is_dir: bool
      - entries: list of dicts {name, is_dir, size, mtime}
    The entries list sorts directories first (alphabetical) then files.
    """
    out = {'path': os.path.expanduser(path), 'exists': False, 'is_dir': False, 'entries': []}

    p = out['path']
    if not os.path.exists(p):
        return out
    out['exists'] = True
    out['is_dir'] = os.path.isdir(p)
    if not out['is_dir']:
        return out

    try:
        items = []
        for name in sorted(os.listdir(p)):
            try:
                fp = os.path.join(p, name)
                is_dir = os.path.isdir(fp)
                size = os.path.getsize(fp) if os.path.isfile(fp) else 0
                mtime = os.path.getmtime(fp)
                items.append({'name': name, 'is_dir': is_dir, 'size': size, 'mtime': mtime})
            except Exception:
                # skip unreadable entries
                continue

        # Sort directories first, then files, both alphabetically
        items.sort(key=lambda e: (not e['is_dir'], e['name'].lower()))
        out['entries'] = items
    except Exception:
        # On error, return what we have
        pass

    return out
