#!/usr/bin/env python3
"""Simple test for mixer availability helper.

This test only verifies that the helper returns a boolean value.
It intentionally does not assume the presence of audio hardware.
"""
from src.audio_utils import is_mixer_available


def test_mixer_returns_bool():
    result = is_mixer_available()
    print(f"is_mixer_available() -> {result}")
    assert isinstance(result, bool)


if __name__ == '__main__':
    test_mixer_returns_bool()
    print('test_mixer.py: OK')
