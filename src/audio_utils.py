"""Audio-related helper functions used across the project.

This module provides a small, safe check for whether the pygame mixer
subsystem is available in the current Python environment. The function
is_mixer_available() returns a boolean and never raises an exception
on import — it only returns False when mixer support is missing.
"""
from typing import Tuple


def is_mixer_available() -> bool:
    """Return True if pygame.mixer is importable and appears available.

    The check intentionally avoids initialising audio (pygame.mixer.init())
    because that can change global state or block. Instead it tests import
    and basic attribute presence. The function returns False if the mixer
    module does not exist or raises a ModuleNotFoundError.
    """
    try:
        import pygame
    except Exception:
        return False

    try:
        # The mixer submodule may not be present if pygame was built without
        # SDL_mixer or related system libs. Accessing pygame.mixer may raise
        # ModuleNotFoundError on some systems — handle that gracefully.
        mixer = getattr(pygame, "mixer", None)
        if mixer is None:
            return False

        # Confirm at least that expected callables are available
        has_music = hasattr(mixer, "music")
        has_get_init = hasattr(mixer, "get_init")
        return bool(has_music and has_get_init)
    except ModuleNotFoundError:
        return False
