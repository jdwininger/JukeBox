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
        # ModuleNotFoundError or pygame's NotImplementedError on some systems —
        # handle any exception gracefully and report mixer as unavailable.
        mixer = getattr(pygame, "mixer", None)
        if mixer is None:
            return False

        # Confirm at least that expected callables are available
        # Some pygame builds raise NotImplementedError when accessing missing
        # submodules, so guard has_attr checks with try/except.
        try:
            has_music = hasattr(mixer, "music")
            has_get_init = hasattr(mixer, "get_init")
            return bool(has_music and has_get_init)
        except Exception:
            return False
    except Exception:
        return False


def mixer_status() -> Tuple[bool, str]:
    """Return (available, message) about mixer state.

    Provides a short explanation string useful for diagnostics and logs.
    """
    try:
        import importlib
        import pygame
    except Exception as e:
        return False, f"pygame import failed: {type(e).__name__} {e}"

    try:
        # try to import the mixer submodule explicitly — this can raise
        # ModuleNotFoundError if the pygame build lacks mixer support
        importlib.import_module("pygame.mixer")
    except Exception as e:
        return False, f"pygame.mixer import failed: {type(e).__name__} {e}"

    try:
        # Finally, check init state
        if getattr(pygame.mixer, "get_init", None) is None:
            return False, "pygame.mixer present but missing get_init()"
        if pygame.mixer.get_init() is None:
            return True, "pygame.mixer present but not initialized"
        return True, "pygame.mixer available and initialized"
    except Exception as e:
        return False, f"pygame.mixer check failed: {type(e).__name__} {e}"


def attempt_mixer_init(frequency=44100, size=-16, channels=2, buffer=4096) -> Tuple[bool, str]:
    """Attempt to initialise the pygame mixer and return (success, message).

    This is defensive — it will not raise, only return a tuple describing
    the outcome. Callers can try to re-run this if system libs become
    available while the app is running.
    """
    try:
        import importlib
        import pygame
    except Exception as e:
        return False, f"pygame import failed: {type(e).__name__} {e}"

    try:
        importlib.import_module("pygame.mixer")
    except Exception as e:
        return False, f"pygame.mixer import failed: {type(e).__name__} {e}"

    # Try to init if not already
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency, size, channels, buffer)
            return True, "pygame.mixer.initialized"
        return True, "pygame.mixer already initialized"
    except Exception as e:
        return False, f"pygame.mixer.init() failed: {type(e).__name__} {e}"

    try:
        # The mixer submodule may not be present if pygame was built without
        # SDL_mixer or related system libs. Accessing pygame.mixer may raise
        # ModuleNotFoundError or pygame's NotImplementedError on some systems —
        # handle any exception gracefully and report mixer as unavailable.
        mixer = getattr(pygame, "mixer", None)
        if mixer is None:
            return False

        # Confirm at least that expected callables are available
        # Some pygame builds raise NotImplementedError when accessing missing
        # submodules, so guard has_attr checks with try/except.
        try:
            has_music = hasattr(mixer, "music")
            has_get_init = hasattr(mixer, "get_init")
            return bool(has_music and has_get_init)
        except Exception:
            return False
    except Exception:
        return False
