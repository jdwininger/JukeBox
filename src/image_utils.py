"""Image loading helpers used by the UI and theming code.

This module provides robust loading of raster images into pygame surfaces.
It prefers pygame.image.load but falls back to Pillow (PIL) if SDL_image
support is missing or the file cannot be opened by pygame for any reason.

Functions are designed to never crash on import and return None on failure.
"""
from typing import Optional, Tuple
import os


def _pil_image_to_pygame_surface(pil_image) -> 'pygame.Surface':
    """Convert a PIL Image to a pygame Surface.

    Import pygame locally to avoid importing it at module import-time for simple
    tools that don't need full pygame initialization.
    """
    try:
        import pygame
    except Exception:
        raise

    mode = pil_image.mode
    size = pil_image.size
    raw = pil_image.tobytes()

    surface = pygame.image.fromstring(raw, size, mode)
    # Convert to a display-friendly format if possible
    try:
        surface = surface.convert_alpha() if mode in ('RGBA', 'LA') else surface.convert()
    except Exception:
        pass
    return surface


def load_image_surface(path: str, size: Tuple[int, int] = None) -> Optional['pygame.Surface']:
    """Load an image file into a pygame Surface.

    - Tries pygame.image.load first.
    - If that fails and Pillow is available, uses PIL.Image to load/convert the file
      and create a pygame surface.
    - If `size` is provided (width, height) the PIL result is resized to that size.

    Returns a pygame.Surface or None on failure.
    """
    if not os.path.exists(path):
        return None

    try:
        import pygame
        surf = pygame.image.load(path)
        if size and hasattr(surf, 'get_size'):
            try:
                surf = pygame.transform.smoothscale(surf, size)
            except Exception:
                pass
        return surf
    except Exception:
        # Try Pillow fallback
        try:
            from PIL import Image
        except Exception:
            return None

        try:
            pil = Image.open(path)
            if size:
                pil = pil.resize(size, Image.LANCZOS)

            # Ensure we have a mode pygame understands
            if pil.mode not in ('RGBA', 'RGB'):
                pil = pil.convert('RGBA')

            return _pil_image_to_pygame_surface(pil)
        except Exception:
            return None
