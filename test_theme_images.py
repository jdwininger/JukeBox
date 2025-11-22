#!/usr/bin/env python3
"""Simple theme image loading test.

This test checks that the project's robust image loader can load one
PNG and that Theme can load an SVG background (if svg support is available).
"""
from src.image_utils import load_image_surface
from src.theme import Theme, SVG_SUPPORT


def test_load_some_images():
    png = 'themes/dark/play_button.png'
    s = load_image_surface(png)
    assert s is not None
    print('PNG loader OK')

    if SVG_SUPPORT:
        t = Theme('dark','themes/dark')
        bg = t.get_background(64,64)
        assert bg is not None
        print('SVG background loader OK')


if __name__ == '__main__':
    test_load_some_images()
    print('test_theme_images.py: OK')
