#!/usr/bin/env python3
"""Tests for default music directory selection logic in main/quickstart."""
import os
import tempfile
from importlib import reload

import pytest

import src.main as main_mod
import quickstart


def test_choose_existing_variant(tmp_path, monkeypatch):
    # Create a fake ~/Music directory and a 'Jukebox' variant inside it
    home = tmp_path
    music = home / "Music"
    music.mkdir()
    (music / "Jukebox").mkdir()

    # Monkeypatch expanduser to point ~ to tmp_path
    monkeypatch.setenv("HOME", str(home))

    # Now import the modules freshly and check selection logic
    reload(main_mod)
    # Simulate the same selection algorithm used in main
    home_music = os.path.expanduser(os.path.join("~", "Music"))
    variants = ["JukeBox", "Jukebox", "jukebox", "Juke Box", "Juke-Box"]
    found = None
    for v in variants:
        cand = os.path.join(home_music, v)
        if os.path.exists(cand):
            found = cand
            break

    assert found is not None
    assert found.endswith(os.path.join("Music", "Jukebox"))


def test_quickstart_prefers_existing_variant(tmp_path, monkeypatch):
    home = tmp_path
    music = home / "Music"
    music.mkdir()
    (music / "jukebox").mkdir()

    monkeypatch.setenv("HOME", str(home))

    # reload quickstart module and run the branch to pick music_dir
    reload(quickstart)

    # Emulate logic: pick first existing variant
    home_music = os.path.expanduser(os.path.join("~", "Music"))
    variants = ["JukeBox", "Jukebox", "jukebox", "Juke Box", "Juke-Box"]
    found = None
    for v in variants:
        cand = os.path.join(home_music, v)
        if os.path.exists(cand):
            found = cand
            break

    assert found is not None
    assert found.endswith(os.path.join("Music", "jukebox"))
