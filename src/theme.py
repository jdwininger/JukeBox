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

    # Default colors used when a theme doesn't override values. Kept as a
    # class-level constant so other modules (eg. ThemeManager) can reference
    # the canonical defaults without instantiating Theme objects.
    DEFAULT_COLORS = {
        "background": (32, 32, 32),
        "text": (255, 255, 255),
        "text_secondary": (200, 200, 200),
        "accent": (100, 200, 100),
        "button": (64, 64, 64),
        "button_hover": (100, 100, 100),
        "button_pressed": (50, 50, 50),
        "button_text": (255, 255, 255),
        "artist_text": (255, 255, 255),
        "album_text": (200, 200, 200),
        "track_list": (200, 200, 200),
    }

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

        # Close button paths (for modal close buttons)
        self.close_button_path = os.path.join(theme_dir, "close_button.png")
        self.close_button_svg_path = os.path.join(theme_dir, "close_button.svg")

        # Credits button paths
        self.credits_button_path = os.path.join(theme_dir, "credits_button.png")
        self.credits_button_svg_path = os.path.join(theme_dir, "credits_button.svg")

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
        # Close button image (optional)
        self.close_button: Optional[pygame.Surface] = None
        self.close_button_hover: Optional[pygame.Surface] = None
        self.close_button_pressed: Optional[pygame.Surface] = None

        # Credits button image (optional)
        self.credits_button: Optional[pygame.Surface] = None
        self.credits_button_hover: Optional[pygame.Surface] = None
        self.credits_button_pressed: Optional[pygame.Surface] = None

        # Color scheme (defaults). These keys are documented and can be
        # overridden by a theme.conf file in the theme directory. Use a copy
        # of DEFAULT_COLORS so each Theme instance can be modified safely.
        self.colors = dict(self.DEFAULT_COLORS)

        # Load any per-theme configuration (theme.conf) which can override
        # color keys above. This lets theme authors provide easily-editable
        # color and button color values without changing Python code.
        # Keep a separate per-button color map so themes may declare
        # specific colors for individual text-buttons (eg. CLR, ENT, Credits).
        # Per-button colors structure; map: button_name -> { 'normal': (r,g,b), 'hover': (...), 'pressed': (...) }
        self.button_colors = {}

        try:
            # Use the consolidated loader which reads both [colors] and
            # [button_colors]/[buttons] sections.
            self._load_theme_conf()
        except Exception:
            # Keep defaults on any error reading/parsing the file.
            pass

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

        # Load close button variants if provided
        self._load_media_button(
            "close", self.close_button_path, self.close_button_svg_path
        )

        # Load navigation buttons (PNG first, then SVG)
        self._load_media_button(
            "left", self.left_button_path, self.left_button_svg_path, size=(60, 80)
        )
        self._load_media_button(
            "right", self.right_button_path, self.right_button_svg_path, size=(60, 80)
        )

        # Load exit button and its variants (PNG first then SVG)
        self._load_media_button(
            "exit", self.exit_button_path, self.exit_button_svg_path
        )

        # Load credits button and its variants (PNG first then SVG). Use
        # the requested 65x85 size so the artwork maps to the credit button
        # dimensions used throughout the UI and avoids runtime scaling.
        self._load_media_button(
            "credits", self.credits_button_path, self.credits_button_svg_path, size=(65, 85)
        )

    def _load_media_button(
        self, button_type: str, png_path: str, svg_path: str, size: Tuple[int, int] = (50, 50)
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
                    surf = load_image_surface(png_path, size=size)
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
                # Render SVG at the UI's target media control size
                svg_surface = self.load_svg_as_surface(svg_path, size[0], size[1])
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
                    surf = load_image_surface(png_hover, size=size)
                else:
                    surf = pygame.image.load(png_hover)

                setattr(self, hover_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} hover PNG: {e}")
        elif SVG_SUPPORT and os.path.exists(svg_hover):
            try:
                surf = self.load_svg_as_surface(svg_hover, size[0], size[1])
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
                    surf = load_image_surface(png_pressed, size=size)
                else:
                    surf = pygame.image.load(png_pressed)

                setattr(self, pressed_attr, surf)
            except Exception as e:
                print(f"Error loading {button_type} pressed PNG: {e}")
        elif SVG_SUPPORT and os.path.exists(svg_pressed):
            try:
                surf = self.load_svg_as_surface(svg_pressed, size[0], size[1])
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
        """Get media button image by type and state (normal | hover | pressed).

        If a state-specific asset isn't present, fall back to the 'normal' state so
        a theme that only provides a single static image still works.

        Returns the pygame.Surface for the requested button (or None if none exists).
        """
        if state not in ("normal", "hover", "pressed"):
            state = "normal"

        if state == "normal":
            attr = f"{button_type}_button"
        elif state == "hover":
            attr = f"{button_type}_button_hover"
        else:
            attr = f"{button_type}_button_pressed"

        img = getattr(self, attr, None)

        # If hover/pressed requested but not available, fall back to normal
        if img is None and state != "normal":
            img = getattr(self, f"{button_type}_button", None)

        return img

    # Theme config helpers (moved inside Theme): parsing & loader
    def _parse_color_value(self, s: str):
        """Parse color value from theme.conf.

        Accepts hex (#RRGGBB) or comma-separated r,g,b integers.
        Returns a (r,g,b) tuple or None on parse failure.
        """
        s = s.strip()
        if not s:
            return None
        if s.startswith("#") and len(s) == 7:
            try:
                return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))
            except Exception:
                return None
        parts = [p.strip() for p in s.split(',') if p.strip()]
        if len(parts) == 3:
            try:
                return (int(parts[0]), int(parts[1]), int(parts[2]))
            except Exception:
                return None
        return None

    def _load_theme_conf(self) -> None:
        """Load theme colors from theme.conf (INI) inside theme_dir.

        Supported section: [colors]
        """
        import configparser

        conf_file = os.path.join(self.theme_dir, "theme.conf")
        if not os.path.exists(conf_file):
            return
        parser = configparser.ConfigParser()
        try:
            parser.read(conf_file)
        except Exception:
            return
        # Parse the colors section if present
        if "colors" in parser:
            for key, val in parser.items("colors"):
                if key in self.colors:
                    parsed = self._parse_color_value(val)
                    if parsed:
                        self.colors[key] = parsed

        # Parse per-button color overrides: support either [button_colors]
        # or a legacy [buttons] section to be flexible.
        for section_name in ("button_colors", "buttons"):
            if section_name in parser:
                for key, val in parser.items(section_name):
                    # Normalize key to lowercase to make lookups case-insensitive
                    raw = key.strip().lower()
                    parsed = self._parse_color_value(val)
                    if not parsed:
                        continue

                    # Support keys with suffixes: _hover, _pressed. Otherwise normal.
                    state = "normal"
                    base = raw
                    if raw.endswith("_hover"):
                        base = raw[: -len("_hover")]
                        state = "hover"
                    elif raw.endswith("_pressed"):
                        base = raw[: -len("_pressed")]
                        state = "pressed"

                    if base not in self.button_colors:
                        self.button_colors[base] = {}

                    self.button_colors[base][state] = parsed

        return

    def get_button_color(
        self, button_name: str, default: Tuple[int, int, int] = None, state: str = "normal"
    ) -> Tuple[int, int, int]:
        """Get a color for a specific button name.

        Looks up per-button color overrides defined in theme.conf (case-insensitive).
        Falls back to the theme's general `button` color or the optional `default`.
        """
        if default is None:
            default = self.get_color("button")

        if not button_name:
            return default

        name = button_name.strip().lower()

        entry = self.button_colors.get(name)
        if isinstance(entry, dict):
            # Prefer requested state, fallback to normal, then default
            if state in entry:
                return entry[state]
            if "normal" in entry:
                return entry["normal"]

        # Support legacy flat mapping where entry was a tuple
        if entry and isinstance(entry, tuple):
            return entry

        return default

    # ---------- theme.conf helpers (move into Theme) ----------

    

    
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
            # Create a simple theme.conf so themes are editable and install
            # with sensible color keys for users to customize. Use the
            # canonical Theme.DEFAULT_COLORS rather than referencing
            # ThemeManager.self.colors which doesn't exist.
            conf_path = os.path.join(default_dir, "theme.conf")
            try:
                with open(conf_path, "w", encoding="utf-8") as f:
                    f.write("[colors]\n")
                    # Use Theme.DEFAULT_COLORS to avoid relying on instance state
                    for k, v in Theme.DEFAULT_COLORS.items():
                        f.write(f"{k} = {v[0]},{v[1]},{v[2]}\n")

                    # Provide an example section for per-button colors. This
                    # allows theme authors to give specific colors for named
                    # text buttons (eg. CLR, ENT, Credits) using [button_colors]
                    f.write("\n[button_colors]\n")
                    f.write("credits = 255,215,0\n")
                    f.write("credits_hover = 255,230,128\n")
                    f.write("credits_pressed = 200,150,0\n")
                    f.write("clr = 200,50,50\n")
                    f.write("clr_hover = 230,100,100\n")
                    f.write("ent = 100,200,100\n")
            except Exception:
                pass

            self.discover_themes()

    def create_theme(
        self,
        name: str,
        colors: Dict[str, Tuple[int, int, int]] = None,
        button_colors: Dict[str, Tuple[int, int, int]] = None,
    ) -> bool:
        """Create a new theme directory with placeholder assets and a theme.conf.

        Args:
            name: The directory name for the new theme inside themes_dir
            colors: Optional mapping of color keys -> (r,g,b) to write in [colors]
            button_colors: Optional mapping of button name -> (r,g,b) for [button_colors]

        Returns True on success, False if the theme already existed or creation failed.
        """
        if not name:
            return False

        theme_dir = os.path.join(self.themes_dir, name)
        if os.path.exists(theme_dir):
            # don't overwrite existing theme
            return False

        try:
            os.makedirs(theme_dir, exist_ok=False)

            # Create simple placeholder images (same shapes as default)
            try:
                bg_surface = pygame.Surface((1000, 700))
                bg_surface.fill(Theme.DEFAULT_COLORS.get("background", (32, 32, 32)))
                pygame.image.save(bg_surface, os.path.join(theme_dir, "background.png"))

                btn_surface = pygame.Surface((100, 50))
                btn_surface.fill(Theme.DEFAULT_COLORS.get("button", (64, 64, 64)))
                pygame.image.save(btn_surface, os.path.join(theme_dir, "button.png"))

                btn_hover_surface = pygame.Surface((100, 50))
                btn_hover_surface.fill(Theme.DEFAULT_COLORS.get("button_hover", (100, 100, 100)))
                pygame.image.save(btn_hover_surface, os.path.join(theme_dir, "button_hover.png"))

                btn_pressed_surface = pygame.Surface((100, 50))
                btn_pressed_surface.fill(Theme.DEFAULT_COLORS.get("button_pressed", (50, 50, 50)))
                pygame.image.save(btn_pressed_surface, os.path.join(theme_dir, "button_pressed.png"))
            except Exception:
                # If writing images fails, continue — theme.conf is most important
                pass

            # Write theme.conf
            conf_path = os.path.join(theme_dir, "theme.conf")
            with open(conf_path, "w", encoding="utf-8") as f:
                # Colors section: use provided colors overriding defaults
                f.write("[colors]\n")
                base_colors = dict(Theme.DEFAULT_COLORS)
                if colors:
                    # replace only known keys
                    for k, v in colors.items():
                        if k in base_colors and isinstance(v, (tuple, list)) and len(v) == 3:
                            base_colors[k] = (int(v[0]), int(v[1]), int(v[2]))

                for k, v in base_colors.items():
                    f.write(f"{k} = {v[0]},{v[1]},{v[2]}\n")

                # button_colors section: support either simple tuple (normal) or
                # nested dicts { 'normal':(...), 'hover':(...), 'pressed':(...) }
                if button_colors:
                    f.write("\n[button_colors]\n")
                    for btn, col in button_colors.items():
                        if isinstance(col, (tuple, list)) and len(col) == 3:
                            f.write(f"{btn} = {int(col[0])},{int(col[1])},{int(col[2])}\n")
                        elif isinstance(col, dict):
                            # write known states if provided
                            for st in ("normal", "hover", "pressed"):
                                if st in col and isinstance(col[st], (tuple, list)) and len(col[st]) == 3:
                                    keyname = btn if st == "normal" else f"{btn}_{st}"
                                    f.write(f"{keyname} = {int(col[st][0])},{int(col[st][1])},{int(col[st][2])}\n")

            # refresh discovery
            self.discover_themes()
            return True
        except Exception:
            # Fail quietly and return False on any error
            return False

    

    
