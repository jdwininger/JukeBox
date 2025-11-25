"""
Theme Manager Module - Handles application theming with images
"""
import io
import os
from typing import Dict, Optional, Tuple

import pygame

try:
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg

    SVG_SUPPORT = True
    print("SVG support enabled with svglib/reportlab")
except ImportError as e:
    SVG_SUPPORT = False
    print(f"SVG support not available. Error: {e}")
    print("Install with: pip install svglib reportlab")
except OSError as e:
    SVG_SUPPORT = False
    print(f"SVG support disabled due to library issue: {e}")
    print("To fix: pip install svglib reportlab")


class Theme:
    """Represents a single theme with images and colors"""

    def __init__(self, theme_name: str, theme_dir: str):
        """
        Initialize a theme

        Args:
            theme_name: Name of the theme
            theme_dir: Path to the theme directory
        """
        self.name = theme_name
        self.theme_dir = theme_dir

        # Image paths
        self.background_path = os.path.join(theme_dir, "background.png")
        self.background_svg_path = os.path.join(theme_dir, "background.svg")
        self.button_path = os.path.join(theme_dir, "button.png")
        self.button_hover_path = os.path.join(theme_dir, "button_hover.png")
        self.button_pressed_path = os.path.join(theme_dir, "button_pressed.png")
        self.slider_track_path = os.path.join(theme_dir, "slider_track.png")
        self.slider_track_svg_path = os.path.join(theme_dir, "slider_track.svg")
        self.slider_track_vertical_path = os.path.join(
            theme_dir, "slider_track_vertical.png"
        )
        self.slider_track_vertical_svg_path = os.path.join(
            theme_dir, "slider_track_vertical.svg"
        )
        self.slider_knob_path = os.path.join(theme_dir, "slider_knob.png")

        # Media control button paths
        self.play_button_path = os.path.join(theme_dir, "play_button.png")
        self.play_button_svg_path = os.path.join(theme_dir, "play_button.svg")
        self.pause_button_path = os.path.join(theme_dir, "pause_button.png")
        self.pause_button_svg_path = os.path.join(theme_dir, "pause_button.svg")
        self.stop_button_path = os.path.join(theme_dir, "stop_button.png")
        self.stop_button_svg_path = os.path.join(theme_dir, "stop_button.svg")
        self.config_button_path = os.path.join(theme_dir, "config_button.png")
        self.config_button_svg_path = os.path.join(theme_dir, "config_button.svg")

        # Exit button paths (icon support)
        self.exit_button_path = os.path.join(theme_dir, "exit_button.png")
        self.exit_button_svg_path = os.path.join(theme_dir, "exit_button.svg")

        # Navigation button paths
        self.left_button_path = os.path.join(theme_dir, "left_button.png")
        self.left_button_svg_path = os.path.join(theme_dir, "left_button.svg")
        self.right_button_path = os.path.join(theme_dir, "right_button.png")
        self.right_button_svg_path = os.path.join(theme_dir, "right_button.svg")

        # Loaded images
        self.background: Optional[pygame.Surface] = None
        self.button: Optional[pygame.Surface] = None
        self.button_hover: Optional[pygame.Surface] = None
        self.button_pressed: Optional[pygame.Surface] = None
        self.slider_track: Optional[pygame.Surface] = None
        self.slider_track_vertical: Optional[pygame.Surface] = None
        self.slider_knob: Optional[pygame.Surface] = None

        # Media control button images
        self.play_button: Optional[pygame.Surface] = None
        self.play_button_hover: Optional[pygame.Surface] = None
        self.play_button_pressed: Optional[pygame.Surface] = None
        self.pause_button: Optional[pygame.Surface] = None
        self.pause_button_hover: Optional[pygame.Surface] = None
        self.pause_button_pressed: Optional[pygame.Surface] = None
        self.stop_button: Optional[pygame.Surface] = None
        self.stop_button_hover: Optional[pygame.Surface] = None
        self.stop_button_pressed: Optional[pygame.Surface] = None
        self.config_button: Optional[pygame.Surface] = None
        self.config_button_hover: Optional[pygame.Surface] = None
        self.config_button_pressed: Optional[pygame.Surface] = None
        # Exit button image (optional)
        self.exit_button: Optional[pygame.Surface] = None

        # Color scheme
        self.colors = {
            "background": (32, 32, 32),
            "text": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "accent": (100, 200, 100),
            "button": (64, 64, 64),
            "button_hover": (100, 100, 100),
            "button_pressed": (50, 50, 50),
        }

        # Load images
        self.load_images()

    def load_images(self) -> None:
        """Load theme images"""
        # Try to load background (PNG first, then SVG)
        # Use a robust loader that falls back to Pillow if pygame can't load PNGs
        try:
            from src.image_utils import load_image_surface
        except Exception:
            load_image_surface = None

        if load_image_surface is not None and os.path.exists(self.background_path):
            try:
                self.background = load_image_surface(self.background_path)
                if self.background is None:
                    raise RuntimeError("failed to load background via robust loader")
            except Exception as e:
                print(f"Error loading background image: {e}")
        elif SVG_SUPPORT and os.path.exists(self.background_svg_path):
            try:
                self.background = self.load_svg_as_surface(self.background_svg_path)
                print(f"Loaded SVG background: {self.background_svg_path}")
            except Exception as e:
                print(f"Error loading background SVG: {e}")

        if os.path.exists(self.button_path) and load_image_surface is not None:
            try:
                self.button = load_image_surface(self.button_path)
                if self.button is None:
                    raise RuntimeError("failed to load button image")
            except Exception as e:
                print(f"Error loading button image: {e}")

        if os.path.exists(self.button_hover_path) and load_image_surface is not None:
            try:
                self.button_hover = load_image_surface(self.button_hover_path)
                if self.button_hover is None:
                    raise RuntimeError("failed to load button_hover image")
            except Exception as e:
                print(f"Error loading button_hover image: {e}")

        if os.path.exists(self.button_pressed_path) and load_image_surface is not None:
            try:
                self.button_pressed = load_image_surface(self.button_pressed_path)
                if self.button_pressed is None:
                    raise RuntimeError("failed to load button_pressed image")
            except Exception as e:
                print(f"Error loading button_pressed image: {e}")

        # Load slider track (horizontal)
        if os.path.exists(self.slider_track_path) and load_image_surface is not None:
            try:
                self.slider_track = load_image_surface(self.slider_track_path)
                if self.slider_track is None:
                    raise RuntimeError("failed to load slider_track image")
            except Exception as e:
                print(f"Error loading slider_track image: {e}")
        elif os.path.exists(self.slider_track_svg_path) and SVG_SUPPORT:
            try:
                self.slider_track = self.load_svg_as_surface(self.slider_track_svg_path)
                print(f"Loaded SVG slider track: {self.slider_track_svg_path}")
            except Exception as e:
                print(f"Error loading slider_track SVG: {e}")

        # Load vertical slider track
        if (
            os.path.exists(self.slider_track_vertical_path)
            and load_image_surface is not None
        ):
            try:
                self.slider_track_vertical = load_image_surface(
                    self.slider_track_vertical_path
                )
                if self.slider_track_vertical is None:
                    raise RuntimeError("failed to load slider_track_vertical image")
            except Exception as e:
                print(f"Error loading slider_track_vertical image: {e}")
        elif os.path.exists(self.slider_track_vertical_svg_path) and SVG_SUPPORT:
            try:
                self.slider_track_vertical = self.load_svg_as_surface(
                    self.slider_track_vertical_svg_path
                )
                print(
                    f"Loaded vertical SVG slider track: {self.slider_track_vertical_svg_path}"
                )
            except Exception as e:
                print(f"Error loading slider_track_vertical SVG: {e}")

        if os.path.exists(self.slider_knob_path) and load_image_surface is not None:
            try:
                self.slider_knob = load_image_surface(self.slider_knob_path)
                if self.slider_knob is None:
                    raise RuntimeError("failed to load slider_knob image")
            except Exception as e:
                print(f"Error loading slider_knob image: {e}")

        # Load media control buttons (PNG first, then SVG)
        self._load_media_button("play", self.play_button_path, self.play_button_svg_path)
        self._load_media_button(
            "pause", self.pause_button_path, self.pause_button_svg_path
        )
        self._load_media_button(
            "stop", self.stop_button_path, self.stop_button_svg_path
        )
        self._load_media_button(
            "config", self.config_button_path, self.config_button_svg_path
        )

        # Load exit button if provided by the theme
        self._load_media_button(
            "exit", self.exit_button_path, self.exit_button_svg_path
        )

        # Load navigation buttons (PNG first, then SVG)
        self._load_media_button(
            "left", self.left_button_path, self.left_button_svg_path
        )
        self._load_media_button(
            "right", self.right_button_path, self.right_button_svg_path
        )

        # Load exit button and its variants (PNG first then SVG)
        self._load_media_button(
            "exit", self.exit_button_path, self.exit_button_svg_path
        )

    def _load_media_button(
        self, button_type: str, png_path: str, svg_path: str
    ) -> None:
        """Load media button image (PNG first, then SVG)"""
        button_attr = f"{button_type}_button"
        hover_attr = f"{button_type}_button_hover"
        pressed_attr = f"{button_type}_button_pressed"

        # Try PNG first for normal state
        if os.path.exists(png_path):
            try:
                # Import the robust loader locally (this method may be called
                # from a different scope where load_image_surface isn't defined)
                try:
                    from src.image_utils import load_image_surface
                except Exception:
                    load_image_surface = None

                if load_image_surface is not None:
                    # Load media assets at the UI's intended media control size
                    # to avoid rescaling at render-time and preserve crispness.
                    surf = load_image_surface(png_path, size=(50, 50))
                else:
                    surf = pygame.image.load(png_path)

                if surf is None:
                    raise RuntimeError("failed to load PNG for button")

                setattr(self, button_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} button PNG: {e}")

        # Try SVG if PNG failed or doesn't exist
        # Try SVG for normal state
        if SVG_SUPPORT and os.path.exists(svg_path):
            try:
                # Load SVG at standard button size (64x64)
                # Render SVG at the UI's target media control size (50x50)
                svg_surface = self.load_svg_as_surface(svg_path, 50, 50)
                setattr(self, button_attr, svg_surface)
            except Exception as e:
                print(f"Error loading {button_type} button SVG: {e}")

        # Hover/pressed variants: look for PNG/SVG with _hover/_pressed suffixes
        # Hover PNG
        png_hover = png_path.replace('.png', '_hover.png')
        svg_hover = svg_path.replace('.svg', '_hover.svg')
        if os.path.exists(png_hover):
            try:
                try:
                    from src.image_utils import load_image_surface
                except Exception:
                    load_image_surface = None

                if load_image_surface is not None:
                    surf = load_image_surface(png_hover, size=(50, 50))
                else:
                    surf = pygame.image.load(png_hover)

                setattr(self, hover_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} hover PNG: {e}")
        elif SVG_SUPPORT and os.path.exists(svg_hover):
            try:
                surf = self.load_svg_as_surface(svg_hover, 50, 50)
                setattr(self, hover_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} hover SVG: {e}")

        # Pressed PNG
        png_pressed = png_path.replace('.png', '_pressed.png')
        svg_pressed = svg_path.replace('.svg', '_pressed.svg')
        if os.path.exists(png_pressed):
            try:
                try:
                    from src.image_utils import load_image_surface
                except Exception:
                    load_image_surface = None

                if load_image_surface is not None:
                    surf = load_image_surface(png_pressed, size=(50, 50))
                else:
                    surf = pygame.image.load(png_pressed)

                setattr(self, pressed_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} pressed PNG: {e}")
        elif SVG_SUPPORT and os.path.exists(svg_pressed):
            try:
                surf = self.load_svg_as_surface(svg_pressed, 50, 50)
                setattr(self, pressed_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} pressed SVG: {e}")

    def load_svg_as_surface(
        self, svg_path: str, width: int = None, height: int = None
    ) -> pygame.Surface:
        """Convert SVG to pygame surface using svglib"""
        if not SVG_SUPPORT:
            raise ImportError("svglib/reportlab not available for SVG support")

        try:
            # Parse SVG file
            drawing = svg2rlg(svg_path)

            # Set dimensions if provided
            if width and height:
                # Scale drawing to desired size
                scale_x = width / drawing.width if drawing.width else 1
                scale_y = height / drawing.height if drawing.height else 1
                drawing.scale(scale_x, scale_y)
                drawing.width = width
                drawing.height = height

            # Render to PIL image
            pil_image = renderPM.drawToPIL(drawing)

            # Convert PIL image to pygame surface
            mode = pil_image.mode
            size = pil_image.size
            raw = pil_image.tobytes()

            return pygame.image.fromstring(raw, size, mode)
        except Exception as e:
            print(f"Failed to convert SVG to surface: {e}")
            raise

    def is_complete(self) -> bool:
        """Check if theme has all essential images"""
        return self.background is not None

    def get_background(
        self, width: int = None, height: int = None
    ) -> Optional[pygame.Surface]:
        """Get background image, optionally scaled from SVG"""
        # If we have SVG and specific dimensions requested, reload at that size
        if (
            SVG_SUPPORT
            and os.path.exists(self.background_svg_path)
            and width is not None
            and height is not None
        ):
            try:
                return self.load_svg_as_surface(self.background_svg_path, width, height)
            except Exception as e:
                print(f"Error loading scaled SVG background: {e}")

        return self.background

    def get_button_image(self, state: str = "normal") -> Optional[pygame.Surface]:
        """Get button image for a given state"""
        if state == "hover" and self.button_hover:
            return self.button_hover
        elif state == "pressed" and self.button_pressed:
            return self.button_pressed
        return self.button

    def get_color(
        self, color_key: str, default: Tuple[int, int, int] = None
    ) -> Tuple[int, int, int]:
        """Get color from theme"""
        if default is None:
            default = (128, 128, 128)
        return self.colors.get(color_key, default)

    def get_media_button_image(self, button_type: str, state: str = "normal") -> Optional[pygame.Surface]:
        """Get media button image by type and state (normal | hover | pressed)

        If a state-specific asset is not present, fall back to the 'normal' state where
        possible. This makes the UI resilient when themes only provide a single
        static image for a media control.

        Returns None if no asset is available for the requested type.
        """
        if state not in ("normal", "hover", "pressed"):
            state = "normal"

        # Map the requested state to an attribute name
        if state == "normal":
            attr = f"{button_type}_button"
        elif state == "hover":
            attr = f"{button_type}_button_hover"
        else:
            attr = f"{button_type}_button_pressed"

        # Try to return the state-specific image first
        img = getattr(self, attr, None)

        # If a hover/pressed state was requested but isn't available, fall back
        # to the normal variant so the UI still has an icon to display.
        if img is None and state != "normal":
            img = getattr(self, f"{button_type}_button", None)

        return img


class ThemeManager:
    """Manages application themes"""

    def __init__(self, themes_dir: str = None):
        """
        Initialize theme manager

        Args:
            themes_dir: Path to themes directory
        """
        if themes_dir is None:
            themes_dir = os.path.join(os.path.dirname(__file__), "..", "themes")

        self.themes_dir = themes_dir
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None

        self._ensure_themes_directory()
        self.discover_themes()

    def _ensure_themes_directory(self) -> None:
        """Ensure themes directory exists"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
            print(f"Created themes directory: {self.themes_dir}")

    def discover_themes(self) -> None:
        """Discover available themes"""
        self.themes = {}

        if not os.path.exists(self.themes_dir):
            print(f"Themes directory not found: {self.themes_dir}")
            return

        try:
            for item in os.listdir(self.themes_dir):
                theme_path = os.path.join(self.themes_dir, item)
                if os.path.isdir(theme_path):
                    theme = Theme(item, theme_path)
                    self.themes[item] = theme
                    print(f"Found theme: {item}")
        except Exception as e:
            print(f"Error discovering themes: {e}")

    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get a theme by name"""
        return self.themes.get(theme_name)

    def set_current_theme(self, theme_name: str) -> bool:
        """
        Set the current active theme

        Args:
            theme_name: Name of theme to activate

        Returns:
            True if theme was set, False otherwise
        """
        theme = self.get_theme(theme_name)
        if theme:
            self.current_theme = theme
            print(f"Theme changed to: {theme_name}")
            return True
        else:
            print(f"Theme not found: {theme_name}")
            return False

    def get_current_theme(self) -> Optional[Theme]:
        """Get the current active theme"""
        return self.current_theme

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return sorted(list(self.themes.keys()))

    def create_default_theme(self) -> None:
        """Create a default theme with placeholder images"""
        default_dir = os.path.join(self.themes_dir, "default")
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)

            # Create a simple background surface
            bg_surface = pygame.Surface((1000, 700))
            bg_surface.fill((32, 32, 32))
            pygame.image.save(bg_surface, os.path.join(default_dir, "background.png"))

            # Create simple button surface
            btn_surface = pygame.Surface((100, 50))
            btn_surface.fill((64, 64, 64))
            pygame.image.save(btn_surface, os.path.join(default_dir, "button.png"))

            # Create button hover surface
            btn_hover_surface = pygame.Surface((100, 50))
            btn_hover_surface.fill((100, 100, 100))
            pygame.image.save(
                btn_hover_surface, os.path.join(default_dir, "button_hover.png")
            )

            # Create button pressed surface
            btn_pressed_surface = pygame.Surface((100, 50))
            btn_pressed_surface.fill((50, 50, 50))
            pygame.image.save(
                btn_pressed_surface, os.path.join(default_dir, "button_pressed.png")
            )

            print(f"Created default theme in: {default_dir}")
            self.discover_themes()
