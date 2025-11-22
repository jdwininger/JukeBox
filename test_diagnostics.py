#!/usr/bin/env python3
"""Test for diagnostics module — validates returned structure and types."""
from src.diagnostics import run_diagnostics


def test_run_diagnostics():
    res = run_diagnostics()
    assert isinstance(res, dict)
    assert 'mixer_available' in res and isinstance(res['mixer_available'], bool)
    assert 'pygame_image_extended' in res and isinstance(res['pygame_image_extended'], bool)
    assert 'svg_support' in res and isinstance(res['svg_support'], bool)
    assert 'recommendations' in res and isinstance(res['recommendations'], list)
    print('Diagnostics check OK:', res['mixer_available'], res['pygame_image_extended'], res['svg_support'])


if __name__ == '__main__':
    test_run_diagnostics()
    print('test_diagnostics.py: OK')
