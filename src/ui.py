"""
UI Module - Handles the graphical user interface
"""
import os
import sys
from typing import List, Optional, Tuple

import pygame

from src.album_library import AlbumLibrary
from src.audio_effects import Equalizer
from src.config import Config
from src.font_manager import FontManager
from src.fs_utils import list_directory
from src.player import MusicPlayer
from src.widgets import Slider, VerticalSlider


class Colors:
    """Color constants for the UI"""

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (64, 64, 64)
    DARK_GRAY = (32, 32, 32)
    LIGHT_GRAY = (200, 200, 200)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    BLUE = (0, 100, 255)
    YELLOW = (255, 200, 0)

# Labels that will be available in the Theme Creator dialog for per-button colors.
# Each entry is (display_label, config_key) where config_key is what gets written in
# theme.conf under [button_colors]. Keys are lower-case and underscore-separated.
THEMABLE_TEXT_BUTTONS = [
    ("Credits", "credits"),
    ("CLR", "clr"),
    ("ENT", "ent"),
    ("Rescan", "rescan"),
    ("Reset", "reset"),
    ("Close", "close"),
    ("Extract Art", "extract_art"),
    ("Choose Library", "choose_library"),
    ("Equalizer", "equalizer"),
    ("Fullscreen", "fullscreen"),
    ("Compact Track List", "compact_track_list"),
]


class Button:
    """Simple button class for UI controls"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        color: Tuple[int, int, int] = None,
        theme=None,
        is_gear_icon: bool = False,
        icon_type: str = None,
    ):
        """
        Initialize a button

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button label
            color: Button color (fallback if theme not available)
            theme: Optional Theme object for theming
            is_gear_icon: If True, draws a gear icon instead of text
            icon_type: Icon type ('play', 'pause', 'stop') for media control icons
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        # If color is not explicitly provided, prefer a per-button theme color
        # (eg. CLR, ENT, Credits) if provided, otherwise fall back to the
        # theme's 'button' color or a sensible default.
        if color is None:
            try:
                if theme is not None:
                    # Use the button label as the lookup key (case-insensitive).
                    self_text = text or ""
                    # Prefer a per-button color API if available, otherwise
                    # fall back to the general theme color.
                    if hasattr(theme, 'get_button_color'):
                        color = theme.get_button_color(self_text, Colors.GRAY, state="normal")
                        hover = theme.get_button_color(self_text, tuple(min(c + 50, 255) for c in color), state="hover")
                        pressed = theme.get_button_color(self_text, tuple(max(c - 20, 0) for c in color), state="pressed")
                        self.hover_color = hover
                        self.pressed_color = pressed
                    else:
                        # Theme only exposes get_color; use the generic button key
                        color = theme.get_color("button", Colors.GRAY)
                        # Hover/pressed variants can be synthesized from base color
                        self.hover_color = tuple(min(c + 50, 255) for c in color)
                        self.pressed_color = tuple(max(c - 20, 0) for c in color)
                else:
                    color = Colors.GRAY
            except Exception:
                color = Colors.GRAY

        self.color = color
        # If hover_color wasn't set above, synthesize from base color
        if not hasattr(self, "hover_color"):
            self.hover_color = tuple(min(c + 50, 255) for c in color)
        if not hasattr(self, "pressed_color"):
            # pressed default is slightly darker
            self.pressed_color = tuple(max(c - 20, 0) for c in color)
        self.is_hovered = False
        self.theme = theme
        self.is_gear_icon = is_gear_icon
        self.icon_type = icon_type

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button on the surface"""
        # Draw button visuals depending on theme availability and button type.
        state = "hover" if self.is_hovered else "normal"

        # If this is a media/icon button, try to draw the themed icon first
        if self.icon_type or self.is_gear_icon:
            if self.theme:
                # Prefer state-specific media/icon image if present
                if self.is_gear_icon:
                    img = self.theme.get_media_button_image("config", state=state)
                else:
                    img = self.theme.get_media_button_image(self.icon_type, state=state)

                if img is not None:
                    # Only scale if the image size doesn't match the button size
                    if img.get_width() != self.rect.width or img.get_height() != self.rect.height:
                        scaled_img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
                    else:
                        scaled_img = img
                    surface.blit(scaled_img, self.rect)
                else:
                    # Fallback to normal-state image if available
                    if self.is_gear_icon:
                        base_img = self.theme.get_media_button_image("config", state="normal")
                    else:
                        base_img = self.theme.get_media_button_image(self.icon_type, state="normal")

                    if base_img is not None:
                        # Only scale if the image size doesn't match the button size
                        if base_img.get_width() != self.rect.width or base_img.get_height() != self.rect.height:
                            scaled_img = pygame.transform.scale(base_img, (self.rect.width, self.rect.height))
                        else:
                            scaled_img = base_img
                        if self.is_hovered and not self.is_gear_icon:
                            scaled_img = self.apply_brightness_filter(scaled_img, 1.3)
                        surface.blit(scaled_img, self.rect)
                    else:
                        # No themed asset: draw the default icon/gear
                        if self.is_gear_icon:
                            self.draw_gear_icon(surface)
                        else:
                            self.draw_media_icon(surface)
            else:
                # No theme: draw default icon
                if self.is_gear_icon:
                    self.draw_gear_icon(surface)
                else:
                    self.draw_media_icon(surface)

            # Icon buttons do not render text labels, done.
            return

        # For text-based buttons: draw background (theme image if available) and always render text
        if self.theme:
            # Special-case: allow a themed `close_button` image to be used for
            # text-labeled Close buttons (some themes provide a specific close
            # artwork rather than the generic button background).
            if self.text and self.text.strip().lower() == "close":
                button_img = self.theme.get_media_button_image("close", state=state)
                # fall back to generic button image if there is no close-specific asset
                if button_img is None:
                    button_img = self.theme.get_button_image(state)
            else:
                button_img = self.theme.get_button_image(state)
            if button_img is not None:
                scaled_img = pygame.transform.scale(button_img, (self.rect.width, self.rect.height))
                surface.blit(scaled_img, self.rect)
            else:
                color = self.hover_color if self.is_hovered else self.color
                pygame.draw.rect(surface, color, self.rect)
                pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)
        else:
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)

        # Now draw the text label on top for text-based buttons
        if self.theme:
            text_color = self.theme.get_color("button_text", Colors.WHITE)
        else:
            text_color = Colors.WHITE
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def draw_gear_icon(self, surface: pygame.Surface) -> None:
        """Draw a gear icon in the button center"""
        center_x, center_y = self.rect.center
        radius = min(self.rect.width, self.rect.height) // 3

        # Draw outer gear teeth (8 teeth)
        import math

        teeth_points = []
        for i in range(16):  # 8 teeth, 2 points each
            angle = i * math.pi / 8
            if i % 2 == 0:
                # Outer tooth point
                tooth_radius = radius + 4
            else:
                # Inner tooth point
                tooth_radius = radius
            x = center_x + tooth_radius * math.cos(angle)
            y = center_y + tooth_radius * math.sin(angle)
            teeth_points.append((x, y))

        # Use different colors for hover effect
        if self.is_hovered:
            gear_color = Colors.BLACK
            inner_color = self.hover_color
        else:
            gear_color = Colors.LIGHT_GRAY
            inner_color = self.color

        # Draw gear outline
        if len(teeth_points) > 2:
            pygame.draw.polygon(surface, gear_color, teeth_points)

        # Draw inner circle
        inner_radius = radius // 2
        pygame.draw.circle(surface, inner_color, (center_x, center_y), inner_radius)
        pygame.draw.circle(surface, gear_color, (center_x, center_y), inner_radius, 2)

    def draw_media_icon(self, surface: pygame.Surface) -> None:
        """Draw play, pause, or stop icon based on icon_type"""
        center_x, center_y = self.rect.center
        icon_size = min(self.rect.width, self.rect.height) // 3

        # Draw a visible button background so icon-only buttons are readable
        bg_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)

        color = Colors.WHITE if self.is_hovered else Colors.LIGHT_GRAY

        if self.icon_type == "play":
            # Draw play triangle (pointing right)
            triangle_points = [
                (center_x - icon_size // 2, center_y - icon_size // 2),
                (center_x - icon_size // 2, center_y + icon_size // 2),
                (center_x + icon_size // 2, center_y),
            ]
            pygame.draw.polygon(surface, color, triangle_points)

        elif self.icon_type == "pause":
            # Draw pause (two vertical bars)
            bar_width = icon_size // 4
            bar_height = icon_size
            left_bar = pygame.Rect(
                center_x - icon_size // 3,
                center_y - bar_height // 2,
                bar_width,
                bar_height,
            )
            right_bar = pygame.Rect(
                center_x + icon_size // 6,
                center_y - bar_height // 2,
                bar_width,
                bar_height,
            )
            pygame.draw.rect(surface, color, left_bar)
            pygame.draw.rect(surface, color, right_bar)

        elif self.icon_type == "stop":
            # Draw stop (square)
            stop_rect = pygame.Rect(
                center_x - icon_size // 2,
                center_y - icon_size // 2,
                icon_size,
                icon_size,
            )
            pygame.draw.rect(surface, color, stop_rect)

        elif self.icon_type == "exit":
            # Draw a simple 'X' exit symbol centered inside the button
            thickness = max(2, icon_size // 3)
            # Coordinates for X lines
            x1, y1 = center_x - icon_size // 2, center_y - icon_size // 2
            x2, y2 = center_x + icon_size // 2, center_y + icon_size // 2
            x3, y3 = center_x - icon_size // 2, center_y + icon_size // 2
            x4, y4 = center_x + icon_size // 2, center_y - icon_size // 2
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), thickness)
            pygame.draw.line(surface, color, (x3, y3), (x4, y4), thickness)

        else:
            # Fallback: draw a simple centered dot so the button isn't empty
            dot_radius = max(2, icon_size // 4)
            pygame.draw.circle(surface, color, (center_x, center_y), dot_radius)

    def update(self, pos: Tuple[int, int]) -> None:
        """Update button hover state"""
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button is clicked"""
        return self.rect.collidepoint(pos)

    def apply_brightness_filter(
        self, image: pygame.Surface, brightness: float
    ) -> pygame.Surface:
        """Apply brightness filter to an image for hover effects

        Args:
            image: Source pygame surface
            brightness: Brightness multiplier (1.0 = normal, >1.0 = brighter)

        Returns:
            New surface with brightness applied
        """
        # Create a copy of the image
        bright_image = image.copy()

        # Create a white overlay surface with alpha for brightness
        overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)

        # Calculate alpha value for brightness effect (30% white overlay for 1.3x brightness)
        alpha = min(255, int((brightness - 1.0) * 255 * 0.3))
        overlay.fill((255, 255, 255, alpha))

        # Blend the overlay with the original image
        bright_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

        return bright_image


class NumberPadButton(Button):
    """Number pad button with digit value"""

    def __init__(self, x: int, y: int, width: int, height: int, digit: str, theme=None):
        """
        Initialize a number pad button

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            digit: Digit value (0-9 or special like 'CLR', 'ENT')
            theme: Optional Theme object for theming
        """
        super().__init__(x, y, width, height, digit, Colors.GRAY, theme=theme)
        self.digit = digit

        # Special colors for special buttons
        if digit == "CLR":
            self.color = Colors.RED
            self.hover_color = (255, 100, 100)
        elif digit == "ENT":
            self.color = Colors.GREEN
            self.hover_color = (100, 255, 100)
        elif digit == "<":
            self.color = Colors.BLUE
            self.hover_color = (100, 150, 255)


class UI:
    """Main UI class for the JukeBox application"""

    def __init__(
        self,
        player: Optional[MusicPlayer],
        library: AlbumLibrary,
        config: Config,
        theme_manager,
    ):
        """
        Initialize the UI

        Args:
            player: MusicPlayer instance (can be None initially)
            library: AlbumLibrary instance
            config: Config instance
            theme_manager: ThemeManager instance
        """
        self.player = player
        self.library = library
        self.config = config
        self.theme_manager = theme_manager
        self.current_theme = theme_manager.get_current_theme()

        # Helper methods for theme-aware colors
        self.text_color = lambda: self.current_theme.get_color("text", Colors.WHITE)
        self.text_secondary_color = lambda: self.current_theme.get_color("text_secondary", Colors.LIGHT_GRAY)
        self.accent_color = lambda: self.current_theme.get_color("accent", Colors.GREEN)
        self.button_text_color = lambda: self.current_theme.get_color("button_text", Colors.WHITE)
        self.artist_text_color = lambda: self.current_theme.get_color("artist_text", Colors.WHITE)
        self.album_text_color = lambda: self.current_theme.get_color("album_text", Colors.LIGHT_GRAY)
        self.track_text_color = lambda: self.current_theme.get_color("track_list", Colors.LIGHT_GRAY)

        # Window setup (dynamic resolution via config; defaults 1280x800)
        self.width = int(self.config.get("window_width", 1280))
        self.height = int(self.config.get("window_height", 800))
        self.fullscreen = self.config.get("fullscreen", False)

        # Set display mode based on fullscreen setting
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual fullscreen dimensions
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
        else:
            self.screen = pygame.display.set_mode(
                (self.width, self.height), pygame.RESIZABLE
            )
        pygame.display.set_caption("JukeBox - Album Library")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60

        # Layout metrics
        self.margin = 20
        self.header_height = 40
        self.controls_height = 50
        self.top_area_height = self.header_height + self.controls_height + 10
        # Reserve area at bottom for number pad + audio controls
        self.bottom_area_height = 230

        # Fonts - attempt to use pygame fonts, but provide a minimal fallback
        # when pygame.font is not available (some builds / test environments
        # omit font support). The fallback exposes render() and get_height().
        # Prefer a bundled DejaVuSans.ttf shipped with the app if present.
        try:
            self.bundled_font_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "DejaVuSans.ttf"
            )
        except Exception:
            self.bundled_font_path = None

        # When a bundled font exists on disk we'll prefer it for all
        self.font_file_used = None

        font_manager = FontManager(self.bundled_font_path)
        font_dict = font_manager.init_fonts()
        self.large_font = font_dict['large_font']
        self.medium_font = font_dict['medium_font']
        self.small_medium_font = font_dict['small_medium_font']
        self.small_font = font_dict['small_font']
        # Create a slightly larger credits font (small_font size + 5px) so
        # the credits counter stands out. Fall back gracefully if font
        # construction fails in test environments.
        try:
            # Prefer pygame.font.SysFont (works in most test envs)
            desired_h = max(8, int(self.small_font.get_height()) + 5)
            try:
                self.credits_font = pygame.font.SysFont(None, desired_h)
            except Exception:
                # If SysFont isn't available, use medium_font as a fallback
                self.credits_font = self.medium_font
        except Exception:
            self.credits_font = self.small_font
        # Add a dedicated font for the 4-digit album/track selection display
        # The user requested a DS-DIGIT.TTF at 72pt for that display. Load it
        # if present and fall back gracefully to a large system font.
        try:
            sel_font_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'DS-DIGIT.TTF')
            sel_font_path = os.path.normpath(sel_font_path)
            if os.path.exists(sel_font_path):
                try:
                    self.selection_digits_font = pygame.font.Font(sel_font_path, 72)
                except Exception:
                    self.selection_digits_font = pygame.font.SysFont(None, 72)
            else:
                try:
                    self.selection_digits_font = pygame.font.SysFont(None, 72)
                except Exception:
                    self.selection_digits_font = self.large_font
        except Exception:
            self.selection_digits_font = self.large_font
        self.tiny_font = font_dict['tiny_font']
        self.track_list_font = font_dict['track_list_font']
        self.track_list_font_fullscreen = font_dict['track_list_font_fullscreen']
        self.font_file_used = font_manager.font_file_used

        # Performance optimizations
        self._cached_background = None
        self._last_bg_size = (0, 0)
        self._text_cache = {}
        self._text_cache_size = 0
        self._max_cache_size = 100
        self._dirty_rects = []
        self._last_volume = -1
        self._last_track_info = None
        self._needs_full_redraw = True

        # 4-digit selection system (AATT: Album Album Track Track)
        self.selection_buffer = ""
        self.selection_mode = False
        # Optional override position for the selection overlay. If set to a
        # tuple (x,y) the selection text will be centered at that screen
        # coordinate instead of being placed relative to the Now Playing box.
        # This allows independent placement of the selection display.
        self.selection_center_override = None
        # When the Now Playing box is moved independently we may want the
        # selection overlay to stay where it was. `selection_anchor_shift`
        # is a vertical shift (in px) applied to selection placement so it
        # can remain fixed while the Now Playing card moves. Positive means
        # the Now Playing card moved down and selection should stay up.
        # Default set to 25 for the current layout change.
        self.selection_anchor_shift = 25
        # Temporary selection overlay state: when a selection is executed
        # we keep it visible for a short period (default 10s) before
        # reverting to the current playing selection.
        # no temporary selection buffer by default (previous behavior)

        # Configuration screen state
        self.config_screen_open = False
        self.config_message = ""
        self.config_message_timer = 0
        # In-app music folder editor / preview modal
        self.config_music_editing = False
        self.config_music_input = ""
        self.config_music_preview = None
        # Hover state for modal buttons ('browse','preview','apply','cancel')
        self.config_music_hover = None
        # Pure-pygame browser state
        self.config_browser_open = False
        self.config_browser_path = None
        self.config_browser_entries = []
        self.config_browser_selected = 0
        self.config_browser_scroll = 0
        # Double-click and mouse handling for browser
        self._browser_last_click_time = 0
        self._browser_last_click_idx = -1
        self._double_click_threshold_ms = 400

        # Audio effects
        self.equalizer = Equalizer()

        # UI state for effects
        self.show_equalizer = False
        # Persistent now playing track info; retains last track details between stops
        self.last_track_info = None

        # Album view offset for side navigation
        self.browse_position = (
            0  # Absolute position when browsing, starts showing albums 1-4
        )

        # Album card track scrolling state - maps album_id to track offset
        self.album_card_scroll_offsets = {}

        # Auto-scroll state for album cards
        self.album_card_auto_scroll_enabled = bool(self.config.get("album_auto_scroll", True))
        self.album_card_auto_scroll_speed = float(self.config.get("album_auto_scroll_speed", 2.0))  # seconds per scroll
        self.album_card_auto_scroll_timers = {}  # maps album_id to last scroll time
        self.album_card_auto_scroll_directions = {}  # maps album_id to scroll direction (1=down, -1=up)
        self.album_card_hover_pause = {}  # maps album_id to hover state

        # Keypad layout choice: False == old (calculator-style), True == new (telephone/image-style)
        self.use_new_keypad_layout = bool(self.config.get("use_new_keypad_layout", False))

        # Screen mode: 'main', 'equalizer', 'config'
        self.screen_mode = "main"
        # Album art cache
        self.album_art_cache = {}

        # Create buttons
        self.setup_buttons()

        # Helpful startup diagnostics for font backend & metrics — this
        # makes it easier to troubleshoot display problems like clipped
        # or half-rendered characters. The output is intentionally
        # concise so it can be read in logs when running the app.
        try:
            def _detect_backend(fnt):
                if hasattr(fnt, '_ft'):
                    return 'freetype'
                if hasattr(fnt, '_pf'):
                    return 'Pillow'
                # pygame.font.Font surface-like objects usually expose get_ascent
                if hasattr(fnt, 'get_ascent'):
                    return 'pygame.font'
                # bundled bitmap font has get_height and no render inconsistencies
                return fnt.__class__.__name__

            info = []
            for name in ('small_font', 'medium_font', 'large_font', 'tiny_font'):
                f = getattr(self, name, None)
                if f is None:
                    continue
                try:
                    gh = f.get_height()
                except Exception:
                    gh = 'ERR'
                try:
                    surf = f.render('Hg', True, (255,255,255))
                    sh = surf.get_height()
                except Exception:
                    sh = 'ERR'
                info.append(f"{name}:{_detect_backend(f)} get_height={gh} surf_h={sh}")
            print("Font diagnostics: ", ", ".join(info))
        except Exception:
            pass

        # Theme creator state (modal)
        self.theme_creator_open = False
        self.theme_creator_name = ""
        self.theme_creator_button_colors = {}
        self.theme_creator_selected_button = None
        self.theme_creator_selected_state = "normal"
        self.theme_creator_sliders = None

    def _player_safe_call(self, method_name: str, *args, **kwargs):
        """Safely call player methods, handling None player"""
        if self.player is None:
            return None
        method = getattr(self.player, method_name, None)
        if method and callable(method):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                print(f"Error calling player.{method_name}: {e}")
                return None
        return None

    def setup_buttons(self) -> None:
        """Setup UI buttons"""
        # Media control buttons are now square
        media_button_size = 50  # Square buttons

        controls_y = self.header_height + 10
        spacing = 10
        x = self.margin

        # Playback controls (left only) - now square
        # Older layout created three media control buttons here. We now
        # prefer placing the pause control inside the keypad image itself
        # (the empty top-row slot) and hide the top media controls by
        # default. Keep objects around for backward compatibility, but
        # hide/don't draw the top controls.
        self.show_top_media_controls = False

        self.play_button = Button(
            x,
            controls_y,
            media_button_size,
            media_button_size,
            "Play",
            None,
            theme=self.current_theme,
            icon_type="play",
        )
        x += media_button_size + spacing
        self.pause_button = Button(
            x,
            controls_y,
            media_button_size,
            media_button_size,
            ">|",
            None,
            theme=self.current_theme,
            icon_type=None,
        )
        x += media_button_size + spacing
        self.stop_button = Button(
            x,
            controls_y,
            media_button_size,
            media_button_size,
            "Stop",
            None,
            theme=self.current_theme,
            icon_type="stop",
        )

        # Export and Config + Album nav (right side anchored) - config and exit buttons (square)
        right_spacing = spacing
        right_x = self.width - self.margin
        # Place from right to left
        # Place exit button flush against the right margin, and move the
        # config (gear) left of it so both fit on the top controls bar.
        # Use an icon-type button for exit so themes can provide an exit icon
        self.exit_button = Button(
            right_x - media_button_size,
            controls_y,
            media_button_size,
            media_button_size,
            "Exit",
            Colors.RED,
            theme=self.current_theme,
            icon_type="exit",
        )

        self.config_button = Button(
            right_x - media_button_size - media_button_size - right_spacing,
            controls_y,
            media_button_size,
            media_button_size,
            "Config",
            Colors.YELLOW,
            theme=self.current_theme,
            is_gear_icon=True,
        )

        # Side navigation buttons for main screen album browsing (beside keypad)
        # These will be positioned dynamically in draw_number_pad_centered()
        # Make them taller than wide and scale based on screen mode
        nav_width = 60
        nav_height = 80
        self.left_nav_button = Button(
            0,
            0,
            nav_width,
            nav_height,
            "<",
            Colors.BLUE,
            theme=self.current_theme,
            icon_type="left",
        )
        self.right_nav_button = Button(
            0,
            0,
            nav_width,
            nav_height,
            ">",
            Colors.BLUE,
            theme=self.current_theme,
            icon_type="right",
        )
        # Credit button (will be positioned dynamically under right-column album cards)
        # Use requested visual size 65x85 so the credit artwork matches pad/nav sizing.
        self.credit_button = Button(
            0, 0, 65, 85, "Add Credit", theme=self.current_theme, icon_type="credits"
        )
        # Number pad (bottom right) — initialized inline below

        # Audio controls
        self.setup_audio_controls()

        # Config screen buttons
        self.setup_config_buttons()

        # Exit confirmation modal buttons (created once so tests can interact)
        self.exit_confirm_yes = Button(0, 0, 120, 40, "Yes", Colors.RED, theme=self.current_theme)
        self.exit_confirm_no = Button(0, 0, 120, 40, "No", Colors.GREEN, theme=self.current_theme)
        self.exit_confirm_open = False
        """Setup clickable number pad for 4-digit selection"""
        # Base origin for number pad; we'll re-center during draw
        pad_x = self.width - 360
        pad_y = self.height - 220
        button_w = 60
        button_h = 30
        spacing = 10

        self.number_pad_buttons: List[NumberPadButton] = []

        # Create 0-9 buttons in calculator layout
        # Row 1: 7 8 9
        for i, digit in enumerate(["7", "8", "9"]):
            x = pad_x + i * (button_w + spacing)
            y = pad_y
            btn = NumberPadButton(
                x, y, button_w, button_h, digit, theme=self.current_theme
            )
            self.number_pad_buttons.append(btn)

        # Row 2: 4 5 6
        for i, digit in enumerate(["4", "5", "6"]):
            x = pad_x + i * (button_w + spacing)
            y = pad_y + (button_h + spacing)
            btn = NumberPadButton(
                x, y, button_w, button_h, digit, theme=self.current_theme
            )
            self.number_pad_buttons.append(btn)

        # Row 3: 1 2 3
        for i, digit in enumerate(["1", "2", "3"]):
            x = pad_x + i * (button_w + spacing)
            y = pad_y + 2 * (button_h + spacing)
            btn = NumberPadButton(
                x, y, button_w, button_h, digit, theme=self.current_theme
            )
            self.number_pad_buttons.append(btn)

        # Row 4: 0 < (backspace)
        btn_0 = NumberPadButton(
            pad_x,
            pad_y + 3 * (button_h + spacing),
            button_w,
            button_h,
            "0",
            theme=self.current_theme,
        )
        self.number_pad_buttons.append(btn_0)

        btn_backspace = NumberPadButton(
            pad_x + (button_w + spacing),
            pad_y + 3 * (button_h + spacing),
            button_w,
            button_h,
            "<",
            theme=self.current_theme,
        )
        self.number_pad_buttons.append(btn_backspace)

        # Row 5: CLR ENT (clear and enter)
        btn_clr = NumberPadButton(
            pad_x,
            pad_y + 4 * (button_h + spacing),
            int(button_w * 1.5 + spacing),
            button_h,
            "CLR",
            theme=self.current_theme,
        )
        self.number_pad_buttons.append(btn_clr)

        btn_ent = NumberPadButton(
            pad_x + int(button_w * 1.5 + spacing * 2),
            pad_y + 4 * (button_h + spacing),
            int(button_w * 1.5),
            button_h,
            "ENT",
            theme=self.current_theme,
        )
        self.number_pad_buttons.append(btn_ent)
        # Store original pad origin and per-button base rects for re-centering AFTER all buttons added
        self.number_pad_origin = (pad_x, pad_y)
        self.number_pad_bases = [(b.rect.x, b.rect.y) for b in self.number_pad_buttons]

    def setup_audio_controls(self) -> None:
        """Setup audio control sliders and equalizer"""
        # Volume slider (horizontal, will be repositioned in draw_main_screen)
        self.volume_slider = Slider(
            x=self.margin,
            y=self.header_height + 20,
            width=320,
            height=30,
            min_val=0.0,
            max_val=100.0,
            initial_val=self.config.get("volume", 0.7) * 100,
            label="",  # Hide label on main screen (slider only)
            theme=self.current_theme,
        )

        # Equalizer vertical sliders (5 bands)
        self.eq_sliders: List[VerticalSlider] = []
        eq_start_x = 50
        eq_start_y = 500
        eq_slider_height = 150
        eq_spacing = 50

        for i in range(5):
            x = eq_start_x + i * eq_spacing
            slider = VerticalSlider(
                x=x,
                y=eq_start_y,
                width=30,
                height=eq_slider_height,
                min_val=-12.0,
                max_val=12.0,
                initial_val=0.0,
                label="",  # Remove band number labels
                theme=self.current_theme,
            )
            self.eq_sliders.append(slider)

        # Load equalizer values from config if present
        eq_vals = self.config.get("equalizer_values")
        if isinstance(eq_vals, list) and len(eq_vals) == 5:
            for i, v in enumerate(eq_vals):
                try:
                    self.eq_sliders[i].set_value(float(v))
                except Exception:
                    pass

        # Equalizer screen buttons
        self.eq_back_button = Button(
            self.width - 140, 30, 110, 36, "Back", Colors.RED, theme=self.current_theme
        )
        self.eq_save_button = Button(
            self.width - 260,
            30,
            110,
            36,
            "Save",
            Colors.GREEN,
            theme=self.current_theme,
        )
        self.eq_preset_buttons = []
        preset_names = list(self.equalizer.get_presets().keys())
        # Preset buttons lowered to avoid slider value text overlap
        for i, name in enumerate(preset_names):
            btn = Button(
                80 + i * 140, 520, 130, 40, name, Colors.BLUE, theme=self.current_theme
            )
            self.eq_preset_buttons.append((name, btn))

    def setup_config_buttons(self) -> None:
        """Setup configuration screen buttons"""
        button_width = 120
        button_height = 40

        config_y = 300
        center_x = self.width // 2

        # Config screen buttons
        self.config_rescan_button = Button(
            center_x - 260,
            config_y,
            button_width,
            button_height,
            "Rescan",
            Colors.GREEN,
            theme=self.current_theme,
        )
        self.config_reset_button = Button(
            center_x - 120,
            config_y,
            button_width,
            button_height,
            "Reset",
            Colors.YELLOW,
            theme=self.current_theme,
        )
        self.config_close_button = Button(
            center_x + 20,
            config_y,
            button_width,
            button_height,
            "Close",
            Colors.RED,
            theme=self.current_theme,
        )
        self.config_extract_art_button = Button(
            center_x + 160,
            config_y,
            button_width,
            button_height,
            "Extract Art",
            (128, 0, 128),
            theme=self.current_theme,
        )  # Purple color
        # Music library chooser button (opens a system folder dialog)
        # Lowered 40px to avoid clipping into the text above (moved down 20px total)
        self.config_choose_music_button = Button(
            center_x + 300,
            config_y + 40,
            button_width + 80,
            button_height,
            "Choose Library",
            (40, 120, 200),
            theme=self.current_theme,
        )
        # Audio effects access button
        effects_y = config_y + 60
        self.config_equalizer_button = Button(
            center_x - 120,
            effects_y,
            button_width,
            button_height,
            "Equalizer",
            Colors.BLUE,
            theme=self.current_theme,
        )
        self.config_fullscreen_button = Button(
            center_x + 20,
            effects_y,
            button_width,
            button_height,
            "Fullscreen",
            Colors.GRAY,
            theme=self.current_theme,
        )

        # Toggle button for compact track lists (states: ON/OFF visual)
        self.config_compact_button = Button(
            center_x - 260, config_y + 40 + 4 * 35, button_width + 40, 34, "Compact Track List", Colors.BLUE, theme=self.current_theme
        )

        # Density slider for track lists (0.5 .. 1.0)
        density_x = center_x - 260
        density_y = config_y + 40 + 4 * 35 + 48
        self.config_density_slider = Slider(
            density_x, density_y, button_width + 180, 36, min_val=0.5, max_val=1.0,
            initial_val=float(self.config.get("track_list_density", 0.8)), label="Density", theme=self.current_theme
        )

        # Auto-scroll speed slider for album cards (1.0 .. 5.0 seconds)
        auto_scroll_x = center_x - 260
        auto_scroll_y = density_y + 50
        self.config_auto_scroll_speed_slider = Slider(
            auto_scroll_x, auto_scroll_y, button_width + 180, 36, min_val=1.0, max_val=5.0,
            initial_val=float(self.config.get("album_auto_scroll_speed", 2.0)), label="Auto-Scroll Speed", theme=self.current_theme
        )

        # Theme selection buttons
        self.theme_buttons: List[tuple] = []
        self.setup_theme_buttons()

    def setup_theme_buttons(self) -> None:
        """Setup theme selection buttons"""
        self.theme_buttons = []
        themes = list(self.theme_manager.themes.keys())

        # Create buttons for each theme - positioned horizontally at bottom
        button_width = 100
        button_height = 30
        spacing = 15

        # Center the theme buttons horizontally
        total_width = len(themes) * button_width + (len(themes) - 1) * spacing
        start_x = (self.width - total_width) // 2
        start_y = self.height - 120  # Near bottom of screen

        for i, theme_name in enumerate(sorted(themes)):
            x = start_x + i * (button_width + spacing)
            # Highlight current theme
            is_selected = theme_name == self.config.get("theme", "dark")
            color = Colors.GREEN if is_selected else Colors.GRAY
            btn = Button(
                x,
                start_y,
                button_width,
                button_height,
                theme_name.capitalize(),
                color,
                theme=self.current_theme,
            )
            self.theme_buttons.append((theme_name, btn))

        # Add a 'New Theme' button centered below the theme buttons so users
        # can create a new theme from the config screen.
        new_x = (self.width - 120) // 2
        new_y = start_y + button_height + 12
        self.new_theme_button = Button(
            new_x, new_y, 120, 30, "New Theme", Colors.BLUE, theme=self.current_theme
        )

    def handle_number_input(self, event: pygame.event.EventType) -> None:
        """
        Handle number key input for 4-digit song selection (AATT)
        A = Album (2 digits)
        T = Track (2 digits)

        Args:
            event: pygame key event
        """
        # Convert key event to digit
        key_map = {
            pygame.K_0: "0",
            pygame.K_1: "1",
            pygame.K_2: "2",
            pygame.K_3: "3",
            pygame.K_4: "4",
            pygame.K_5: "5",
            pygame.K_6: "6",
            pygame.K_7: "7",
            pygame.K_8: "8",
            pygame.K_9: "9",
            # also accept numeric keypad keys
            pygame.K_KP0: "0",
            pygame.K_KP1: "1",
            pygame.K_KP2: "2",
            pygame.K_KP3: "3",
            pygame.K_KP4: "4",
            pygame.K_KP5: "5",
            pygame.K_KP6: "6",
            pygame.K_KP7: "7",
            pygame.K_KP8: "8",
            pygame.K_KP9: "9",
        }

        if event.key in key_map:
            digit = key_map[event.key]
            self.selection_buffer += digit
            self.selection_mode = True

            # Auto-execute when 4 digits are entered
            if len(self.selection_buffer) == 4:
                self.execute_selection()

    def execute_selection(self) -> None:
        """Execute 4-digit song selection"""
        if len(self.selection_buffer) != 4:
            print(
                f"Invalid selection: {self.selection_buffer if self.selection_buffer else 'empty'} (need 4 digits)"
            )
            self.selection_buffer = ""
            self.selection_mode = False
            return

        try:
            album_id = int(self.selection_buffer[:2])
            track_num = int(self.selection_buffer[2:4])

            # Validate album ID (1-50)
            if album_id < 1 or album_id > 50:
                print(f"Invalid album ID: {album_id:02d} (must be 01-50)")
                self.selection_buffer = ""
                self.selection_mode = False
                return

            # Get the album
            album = self.library.get_album(album_id)
            if not album:
                print(f"Album {album_id:02d} not found")
                self.selection_buffer = ""
                self.selection_mode = False
                return

            # Validate track number (1-99)
            if track_num < 1 or track_num > 99:
                print(f"Invalid track number: {track_num:02d} (must be 01-99)")
                self.selection_buffer = ""
                self.selection_mode = False
                return

            # Track index is 0-based
            track_index = track_num - 1

            if track_index >= len(album.tracks):
                print(f"Album {album_id:02d} only has {len(album.tracks)} tracks")
                self.selection_buffer = ""
                self.selection_mode = False
                return

            # Play the selected track
            print(f"Selection: Album {album_id:02d}, Track {track_num:02d}")
            self._player_safe_call("play", album_id=album_id, track_index=track_index)
            # Clear the typing buffer so the user can enter a new selection
            self.selection_buffer = ""
            self.selection_mode = False

        except ValueError:
            print(f"Invalid selection format: {self.selection_buffer}")
            self.selection_buffer = ""
            self.selection_mode = False

    def handle_events(self) -> None:
        """Handle pygame events"""
        events = pygame.event.get()
        if not events:  # Early exit if no events
            return

        for event in events:
            # handle events normally
            if event.type == pygame.QUIT:
                self.running = False
                return  # Early exit on quit
            elif event.type == pygame.VIDEORESIZE:
                if not self.fullscreen:  # Only handle resize if not in fullscreen
                    # Update internal dimensions and recreate screen surface
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.RESIZABLE
                    )
                    # Optionally clamp minimum size for layout integrity
                    if self.width < 800 or self.height < 600:
                        self.width = max(800, self.width)
                        self.height = max(600, self.height)
                        self.screen = pygame.display.set_mode(
                            (self.width, self.height), pygame.RESIZABLE
                        )

                # Invalidate cached background on resize
                self._cached_background = None
                self._needs_full_redraw = True
                # Invalidate cached background on resize
                self._cached_background = None
                self._needs_full_redraw = True
                # Navigation button positions are now handled in draw_number_pad_centered()

            elif event.type == pygame.MOUSEMOTION:
                # If an exit confirmation modal is open, handle its clicks first
                if getattr(self, "exit_confirm_open", False):
                    # Only update hover states on motion; clicks are handled in MOUSEBUTTONDOWN
                    # Only update hover states on motion; clicks are handled in MOUSEBUTTONDOWN
                    try:
                        self.exit_confirm_yes.update(event.pos)
                        self.exit_confirm_no.update(event.pos)
                    except Exception:
                        pass
                    continue

                # If an exit confirmation modal is open, handle its clicks first
                if getattr(self, "exit_confirm_open", False):
                    if self.exit_confirm_yes.is_clicked(getattr(event, 'pos', None)):
                        self.running = False
                        self.exit_confirm_open = False
                        continue
                    elif self.exit_confirm_no.is_clicked(getattr(event, 'pos', None)):
                        self.exit_confirm_open = False
                        continue

                # If exit modal open, handle yes/no first
                if getattr(self, "exit_confirm_open", False):
                    if self.exit_confirm_yes.is_clicked(event.pos):
                        self.running = False
                        self.exit_confirm_open = False
                        continue
                    elif self.exit_confirm_no.is_clicked(event.pos):
                        self.exit_confirm_open = False
                        continue

                # If exit confirmation modal is open, handle yes/no first
                if getattr(self, "exit_confirm_open", False):
                    if self.exit_confirm_yes.is_clicked(event.pos):
                        self.running = False
                        self.exit_confirm_open = False
                        continue
                    elif self.exit_confirm_no.is_clicked(event.pos):
                        self.exit_confirm_open = False
                        continue

                if self.config_screen_open:
                    # If the in-app music-directory modal is open, handle modal clicks first
                    if self.config_music_editing:
                        # Update hover state only (actual actions happen on click)
                        rects = self._get_music_modal_rects()
                        hover = None
                        if rects["browse"].collidepoint(event.pos):
                            hover = "browse"
                        elif rects["preview"].collidepoint(event.pos):
                            hover = "preview"
                        elif rects["apply"].collidepoint(event.pos):
                            hover = "apply"
                        elif rects["cancel"].collidepoint(event.pos):
                            hover = "cancel"
                        self.config_music_hover = hover
                        # If the user hovers away from buttons, close browser hover
                        if hover != "browse" and self.config_browser_open:
                            # do not close browser on hover changes, only on explicit actions
                            pass
                        # If the browser is open, allow clicks inside the preview area
                        if self.config_browser_open:
                            pa = rects["preview_area"]
                            if pa.collidepoint(event.pos):
                                # compute index relative to visible entries
                                x, y = event.pos
                                header_h = self.small_font.get_height() + 8
                                row_h = max(self.small_font.get_height(), 18)
                                rel_y = y - (pa.y + 8 + header_h)
                                if rel_y >= 0:
                                    idx = self.config_browser_scroll + (rel_y // row_h)
                                    if 0 <= idx < len(self.config_browser_entries):
                                        self.config_browser_selected = int(idx)
                                        # Update text input to selected path so apply will work
                                        ent = self.config_browser_entries[
                                            self.config_browser_selected
                                        ]
                                        full = os.path.join(
                                            self.config_browser_path, ent["name"]
                                        )
                                        self.config_music_input = full
                                        # Double-click detection (more robust than relying on event.clicks)
                                        now = pygame.time.get_ticks()
                                        last_idx = self._browser_last_click_idx
                                        last_time = self._browser_last_click_time
                                        self._browser_last_click_idx = int(
                                            self.config_browser_selected
                                        )
                                        self._browser_last_click_time = now
                                        # If same index clicked within threshold -> open directory
                                        if (
                                            last_idx == self.config_browser_selected
                                            and (now - last_time)
                                            <= self._double_click_threshold_ms
                                        ):
                                            if ent["is_dir"]:
                                                self._open_browser(full)
                                # ignore other click areas
                                continue

                        # If browser is open, allow clicks inside the large preview area as selection/open actions
                        if self.config_browser_open:
                            pa2 = rects["preview_area"]
                            if pa2.collidepoint(event.pos):
                                x, y = event.pos
                                header_h = self.small_font.get_height()
                                row_h = max(self.small_font.get_height(), 18)
                                rel_y = y - (pa2.y + header_h + 8)
                                if rel_y >= 0:
                                    idx = self.config_browser_scroll + (rel_y // row_h)
                                    if 0 <= idx < len(self.config_browser_entries):
                                        self.config_browser_selected = int(idx)
                                        ent = self.config_browser_entries[
                                            self.config_browser_selected
                                        ]
                                        full = os.path.join(
                                            self.config_browser_path, ent["name"]
                                        )
                                        self.config_music_input = full
                                        # double-click detection
                                        now = pygame.time.get_ticks()
                                        last_idx = self._browser_last_click_idx
                                        last_time = self._browser_last_click_time
                                        self._browser_last_click_idx = int(
                                            self.config_browser_selected
                                        )
                                        self._browser_last_click_time = now
                                        if (
                                            last_idx == self.config_browser_selected
                                            and (now - last_time)
                                            <= self._double_click_threshold_ms
                                        ):
                                            if ent["is_dir"]:
                                                self._open_browser(full)
                                continue

                        # If the browser is open, handle clicks inside the preview area (selection/open)
                        if self.config_browser_open:
                            pa2 = rects["preview_area"]
                            if pa2.collidepoint(event.pos):
                                x, y = event.pos
                                header_h = self.small_font.get_height()
                                row_h = max(self.small_font.get_height(), 18)
                                rel_y = y - (pa2.y + header_h + 8)
                                if rel_y >= 0:
                                    idx = self.config_browser_scroll + (rel_y // row_h)
                                    if 0 <= idx < len(self.config_browser_entries):
                                        self.config_browser_selected = int(idx)
                                        ent = self.config_browser_entries[
                                            self.config_browser_selected
                                        ]
                                        full = os.path.join(
                                            self.config_browser_path, ent["name"]
                                        )
                                        self.config_music_input = full
                                        # double-click detection
                                        now = pygame.time.get_ticks()
                                        last_idx = self._browser_last_click_idx
                                        last_time = self._browser_last_click_time
                                        self._browser_last_click_idx = int(
                                            self.config_browser_selected
                                        )
                                        self._browser_last_click_time = now
                                        if (
                                            last_idx == self.config_browser_selected
                                            and (now - last_time)
                                            <= self._double_click_threshold_ms
                                        ):
                                            if ent["is_dir"]:
                                                self._open_browser(full)
                                continue

                        # do not process other config clicks while modal open
                        continue
                    self.config_rescan_button.update(event.pos)
                    self.config_reset_button.update(event.pos)
                    self.config_close_button.update(event.pos)
                    self.config_extract_art_button.update(event.pos)
                    self.config_compact_button.update(event.pos)
                    # Update density slider hover/drag state
                    try:
                        mouse_pressed = pygame.mouse.get_pressed()[0]
                        self.config_density_slider.update(event.pos, mouse_pressed)
                        self.config_auto_scroll_speed_slider.update(event.pos, mouse_pressed)
                    except Exception:
                        # In tests, pygame mouse may not be available - ignore
                        pass
                    self.config_equalizer_button.update(event.pos)
                    self.config_fullscreen_button.update(event.pos)
                    self.config_choose_music_button.update(event.pos)

                    for theme_name, btn in self.theme_buttons:
                        btn.update(event.pos)
                    # Update the 'New Theme' button if present
                    if hasattr(self, "new_theme_button"):
                        self.new_theme_button.update(event.pos)
                    # Update theme creator sliders if present (hover/drag state)
                    if getattr(self, "theme_creator_open", False) and self.theme_creator_sliders:
                        try:
                            mouse_pressed = pygame.mouse.get_pressed()[0]
                            for s in self.theme_creator_sliders:
                                s.update(event.pos, mouse_pressed)
                        except Exception:
                            pass
                # If theme creator modal is open globally (any screen), handle
                # slider hover/drag updates here and consume the motion event.
                if getattr(self, "theme_creator_open", False) and self.theme_creator_sliders:
                    try:
                        mouse_pressed = pygame.mouse.get_pressed()[0]
                        for s in self.theme_creator_sliders:
                            s.update(event.pos, mouse_pressed)
                    except Exception:
                        pass
                    continue

                elif self.screen_mode == "equalizer":
                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    for slider in self.eq_sliders:
                        slider.update(event.pos, mouse_pressed)
                    self.eq_back_button.update(event.pos)
                    self.eq_save_button.update(event.pos)
                    for _, btn in self.eq_preset_buttons:
                        btn.update(event.pos)
                elif self.screen_mode == "fader":
                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    self.fader_target_slider.update(event.pos, mouse_pressed)
                    self.fader_speed_slider.update(event.pos, mouse_pressed)
                    self.fader_back_button.update(event.pos)
                    self.fader_save_button.update(event.pos)
                    self.fade_in_button.update(event.pos)
                    self.fade_out_button.update(event.pos)
                    self.fade_set_button.update(event.pos)
                else:
                    self.play_button.update(event.pos)
                    self.pause_button.update(event.pos)
                    self.stop_button.update(event.pos)
                    self.config_button.update(event.pos)
                    self.exit_button.update(event.pos)
                    self.left_nav_button.update(event.pos)
                    self.right_nav_button.update(event.pos)
                    # Credit button (main screen)
                    if hasattr(self, "credit_button"):
                        self.credit_button.update(event.pos)
                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    self.volume_slider.update(event.pos, mouse_pressed)
                    if self.show_equalizer:
                        for slider in self.eq_sliders:
                            slider.update(event.pos, mouse_pressed)
                    for btn in self.number_pad_buttons:
                        btn.update(event.pos)

                # Handle album card hover for auto-scroll pause
                if not self.config_screen_open and self.album_card_auto_scroll_enabled:
                    mouse_pos = event.pos
                    albums = self.player.library.get_albums() if self.player and self.player.library else []
                    if albums:
                        # Calculate card positions (same logic as in draw_main_screen)
                        controls_margin_top = self.header_height + 20
                        button_height = 50
                        media_button_size = 50
                        spacing = 12
                        buttons_y = controls_margin_top + 20
                        content_top = buttons_y + button_height + 25
                        content_height = self.height - content_top - self.bottom_area_height - 20
                        if content_height < 200:
                            content_height = 200
                        row1_y = content_top + 10
                        row2_y = row1_y + content_height // 2 + 35
                        card_h = (content_height // 2) + 15

                        total_content_width = self.width - 40
                        col1_width = int(total_content_width * 0.32)
                        col2_width = int(total_content_width * 0.36)
                        col3_width = int(total_content_width * 0.32)
                        col1_x = 20
                        col2_x = col1_x + col1_width + 10
                        col3_x = col2_x + col2_width + 10

                        # Get current album indices
                        left_album_1 = self.browse_position
                        left_album_2 = self.browse_position + 1
                        right_album_1 = self.browse_position + 2
                        right_album_2 = self.browse_position + 3

            elif event.type == pygame.MOUSEBUTTONUP:
                # Also treat mouse up events for the exit confirmation modal (helps some environments)
                if getattr(self, "exit_confirm_open", False):
                    pass
                    if self.exit_confirm_yes.is_clicked(getattr(event, 'pos', None)):
                        self.running = False
                        self.exit_confirm_open = False
                        continue
                    elif self.exit_confirm_no.is_clicked(getattr(event, 'pos', None)):
                        self.exit_confirm_open = False
                        continue

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If browser open and using older SDL, button 4/5 indicate wheel scroll
                if (
                    self.config_music_editing
                    and self.config_browser_open
                    and hasattr(event, "button")
                    and event.button in (4, 5)
                ):
                    rects_local = self._get_music_modal_rects()
                    pa = rects_local["preview_area"]
                    # Only scroll when mouse is inside preview area
                    if pa.collidepoint(pygame.mouse.get_pos()):
                        if event.button == 4:
                            self.config_browser_scroll = max(
                                0, self.config_browser_scroll - 1
                            )
                        else:
                            max_scroll = max(
                                0,
                                len(self.config_browser_entries)
                                - self._browser_visible_count(),
                            )
                            self.config_browser_scroll = min(
                                max_scroll, self.config_browser_scroll + 1
                            )
                        continue
                # If theme creator modal is open, it should globally capture
                # mouse clicks regardless of other UI state so clicks cannot
                # pass through to background controls.
                if getattr(self, "theme_creator_open", False):
                    # Delegate to modal click handler which will update state
                    # and return as appropriate. This prevents clicks behind
                    # the modal from taking effect.
                    self._handle_theme_creator_click(event.pos)
                    continue

                if self.config_screen_open:
                    # Config screen button clicks
                    if self.config_rescan_button.is_clicked(event.pos):
                        self.handle_rescan()
                    elif self.config_reset_button.is_clicked(event.pos):
                        self.handle_reset_config()
                    elif self.config_close_button.is_clicked(event.pos):
                        self.config_screen_open = False
                        self.clear_caches()  # Clear caches when closing config
                    elif self.config_extract_art_button.is_clicked(event.pos):
                        self.handle_extract_art()
                    elif self.config_equalizer_button.is_clicked(event.pos):
                        self.screen_mode = "equalizer"
                        self.config_screen_open = False
                        self.clear_caches()  # Clear caches when opening equalizer
                    elif self.config_fullscreen_button.is_clicked(event.pos):
                        self.toggle_fullscreen()
                        self.setup_config_buttons()  # Refresh button positions
                    elif self.config_choose_music_button.is_clicked(event.pos):
                        # Open in-app modal editor for choosing/previewing the music directory
                        self.config_music_editing = True
                        self.config_music_hover = None
                        cur = self.config.get("music_dir")
                        if not cur:
                            if (
                                sys.platform.startswith("linux")
                                or sys.platform == "darwin"
                            ):
                                cur = os.path.expanduser(
                                    os.path.join("~", "Music", "JukeBox")
                                )
                            else:
                                cur = os.path.join(
                                    os.path.dirname(__file__), "..", "music"
                                )
                        self.config_music_input = cur
                        self.config_music_preview = None
                        # don't process other clicks
                        continue

                    # Toggle compact track list
                    if self.config_compact_button.is_clicked(event.pos):
                        try:
                                    current = bool(self.config.get("compact_track_list", True))
                                    self.config.set("compact_track_list", not current)
                                    self.config.save()
                                    self.config_message = f"Compact Track List: {'ON' if not current else 'OFF'}"
                                    self.config_message_timer = 180
                                    # Force a full redraw / clear caches so layout updates apply immediately
                                    try:
                                        self.clear_caches()
                                    except Exception:
                                        pass
                        except Exception:
                            pass

                    # Persist density slider value on any click inside the configuration screen
                    try:
                        if hasattr(self, "config_density_slider"):
                            val = float(self.config_density_slider.get_value())
                            val = max(0.5, min(1.0, val))
                            self.config.set("track_list_density", val)
                            self.config.save()
                            self.config_message = f"Track list density: {val:.2f}"
                            self.config_message_timer = 140
                            try:
                                self.clear_caches()
                            except Exception:
                                pass
                    except Exception:
                        pass

                    # Handle clicks on config setting labels to toggle them
                    mouse_x, mouse_y = event.pos
                    # Calculate layout positions (same as in draw_config_screen)
                    left_x = 50
                    col_gap = 40
                    col_width = (self.width - left_x * 2 - col_gap * 2) // 3
                    settings_y = 100
                    config_y = settings_y + 40
                    line_height = 36
                    # Define config items (same as in draw_config_screen)
                    config_items = [
                        ("Auto Play Next Track", self.config.get("auto_play_next")),
                        ("Shuffle Enabled", self.config.get("shuffle_enabled")),
                        ("Show Album Art", self.config.get("show_album_art")),
                        ("Keyboard Shortcuts", self.config.get("keyboard_shortcut_enabled")),
                        ("Album Auto-Scroll", self.config.get("album_auto_scroll", True)),
                        ("Use New Keypad Layout", self.config.get("use_new_keypad_layout", False)),
                        ("Fullscreen Mode", self.fullscreen),
                    ]
                    if left_x <= mouse_x <= left_x + col_width:
                        for i, (label, current_value) in enumerate(config_items):
                            item_y = config_y + i * line_height
                            if item_y <= mouse_y <= item_y + line_height:
                                if label == "Auto Play Next Track":
                                    new_val = not bool(current_value)
                                    self.config.set("auto_play_next", new_val)
                                    self.config.save()
                                    self.config_message = f"Auto play next: {'ON' if new_val else 'OFF'}"
                                    self.config_message_timer = 140
                                elif label == "Shuffle Enabled":
                                    new_val = not bool(current_value)
                                    self.config.set("shuffle_enabled", new_val)
                                    self.config.save()
                                    self.config_message = f"Shuffle: {'ON' if new_val else 'OFF'}"
                                    self.config_message_timer = 140
                                elif label == "Show Album Art":
                                    new_val = not bool(current_value)
                                    self.config.set("show_album_art", new_val)
                                    self.config.save()
                                    self.config_message = f"Album art: {'ON' if new_val else 'OFF'}"
                                    self.config_message_timer = 140
                                elif label == "Keyboard Shortcuts":
                                    new_val = not bool(current_value)
                                    self.config.set("keyboard_shortcut_enabled", new_val)
                                    self.config.save()
                                    self.config_message = f"Keyboard shortcuts: {'ON' if new_val else 'OFF'}"
                                    self.config_message_timer = 140
                                elif label == "Album Auto-Scroll":
                                    new_val = not bool(current_value)
                                    self.config.set("album_auto_scroll", new_val)
                                    self.config.save()
                                    self.album_card_auto_scroll_enabled = new_val  # Update runtime value
                                    self.config_message = f"Album auto-scroll: {'ON' if new_val else 'OFF'}"
                                    self.config_message_timer = 140
                                elif label == "Use New Keypad Layout":
                                    new_val = not bool(current_value)
                                    self.config.set("use_new_keypad_layout", new_val)
                                    self.config.save()
                                    self.use_new_keypad_layout = new_val
                                    self.config_message = f"Use new keypad layout: {'ON' if new_val else 'OFF'}"
                                    self.config_message_timer = 140
                                elif label == "Fullscreen Mode":
                                    self.toggle_fullscreen()
                                    self.setup_config_buttons()  # Refresh button positions
                                break

                    # Persist auto-scroll speed slider value on any click inside the configuration screen
                    try:
                        if hasattr(self, "config_auto_scroll_speed_slider"):
                            val = float(self.config_auto_scroll_speed_slider.get_value())
                            val = max(1.0, min(5.0, val))
                            self.config.set("album_auto_scroll_speed", val)
                            self.config.save()
                            self.album_card_auto_scroll_speed = val  # Update runtime value
                            self.config_message = f"Auto-scroll speed: {val:.1f}s"
                            self.config_message_timer = 140
                    except Exception:
                        pass

                    # Theme creator modal: if open, handle clicks inside and ignore other config clicks
                    if getattr(self, "theme_creator_open", False):
                        self._handle_theme_creator_click(event.pos)
                        continue

                    # If modal is active, handle clicks on modal buttons
                    if self.config_music_editing:
                        rects = self._get_music_modal_rects()
                        if rects["browse"].collidepoint(event.pos):
                            # Open the pure-pygame browser (modal preview area becomes folder browser)
                            self.config_browser_open = True
                            start_path = os.path.expanduser(
                                self.config_music_input
                                or os.path.expanduser(
                                    os.path.join("~", "Music", "JukeBox")
                                )
                            )
                            self._open_browser(start_path)
                        elif rects["preview"].collidepoint(event.pos):
                            path = os.path.expanduser(self.config_music_input)
                            self.config_music_preview = self._compute_music_preview(
                                path
                            )
                        elif rects["apply"].collidepoint(event.pos):
                            path = os.path.expanduser(self.config_music_input)
                            try:
                                new_lib = AlbumLibrary(path)
                                new_lib.scan_library()
                                self.library = new_lib
                                if self.player:
                                    try:
                                        self.player.library = new_lib
                                    except Exception:
                                        pass
                                self.config.set("music_dir", path)
                                self.config.save()
                                self.config_message = f"Music directory set to: {path}"
                                self.config_message_timer = 200
                                self.config_music_editing = False
                                self.config_music_preview = None
                                self.clear_caches()
                            except Exception as e:
                                self.config_message = f"Failed to set music dir: {e}"
                                self.config_message_timer = 200
                        elif rects["cancel"].collidepoint(event.pos):
                            self.config_music_editing = False
                            self.config_music_preview = None
                            self.config_browser_open = False
                            self.config_browser_entries = []
                            self.config_browser_selected = 0
                        # do not process other config clicks while modal open
                        continue

                    else:
                        # Check theme button clicks
                            self.handle_theme_selection(event.pos)
                elif self.screen_mode == "equalizer":
                    # Equalizer screen interactions
                    if self.eq_back_button.is_clicked(event.pos):
                        # Save before leaving
                        self.config.set(
                            "equalizer_values", [s.get_value() for s in self.eq_sliders]
                        )
                        self.config.save()
                        # Apply equalizer changes
                        self.update_audio_controls()
                        self.screen_mode = "main"
                    elif self.eq_save_button.is_clicked(event.pos):
                        self.config.set(
                            "equalizer_values", [s.get_value() for s in self.eq_sliders]
                        )
                        self.config.save()
                        # Apply equalizer changes
                        self.update_audio_controls()
                    else:
                        # Preset buttons
                        for name, btn in self.eq_preset_buttons:
                            if btn.is_clicked(event.pos):
                                preset_func = self.equalizer.get_presets().get(name)
                                if preset_func:
                                    preset_func()
                                    # Update sliders to equalizer model
                                    for i, gain in enumerate(
                                        self.equalizer.get_all_bands()
                                    ):
                                        self.eq_sliders[i].set_value(gain)
                                    # Update volume to apply equalizer changes
                                    self.update_audio_controls()
                                break
                elif self.screen_mode == "fader":
                    if self.fader_back_button.is_clicked(event.pos):
                        # Save current fader settings
                        self.config.set(
                            "fader_volume", self.audio_fader.get_volume() * 100
                        )
                        self.config.set(
                            "fade_speed", self.audio_fader.fade_speed * 1000
                        )
                        self.config.save()
                        self.screen_mode = "main"
                    elif self.fader_save_button.is_clicked(event.pos):
                        self.config.set(
                            "fader_volume", self.audio_fader.get_volume() * 100
                        )
                        self.config.set(
                            "fade_speed", self.audio_fader.fade_speed * 1000
                        )
                        self.config.save()
                    elif self.fade_in_button.is_clicked(event.pos):
                        speed = max(0.01, self.fader_speed_slider.get_value() / 1000.0)
                        self.audio_fader.fade_to_max(speed)
                    elif self.fade_out_button.is_clicked(event.pos):
                        speed = max(0.01, self.fader_speed_slider.get_value() / 1000.0)
                        self.audio_fader.fade_to_mute(speed)
                    elif self.fade_set_button.is_clicked(event.pos):
                        target = self.fader_target_slider.get_value() / 100.0
                        speed = max(0.01, self.fader_speed_slider.get_value() / 1000.0)
                        self.audio_fader.set_target(target, speed)
                    else:
                        pass
                else:
                    # Main screen button clicks
                    if self.show_top_media_controls and self.play_button.is_clicked(event.pos):
                        self._player_safe_call("play")
                    elif self.pause_button.is_clicked(event.pos):
                        if self.player and self.player.is_paused:
                            self._player_safe_call("resume")
                        elif self.player:
                            self._player_safe_call("pause")
                    elif self.show_top_media_controls and self.stop_button.is_clicked(event.pos):
                        self._player_safe_call("stop")
                    elif self.config_button.is_clicked(event.pos):
                        self.config_screen_open = True
                        self.config_message = ""
                        self.clear_caches()  # Clear caches when opening config
                    elif self.exit_button.is_clicked(event.pos):
                        # Open an exit confirmation dialog/modal
                        self.exit_confirm_open = True
                    elif self.left_nav_button.is_clicked(event.pos):
                        albums = self.player.library.get_albums()
                        if albums:
                            # Move left by 4 albums, but don't go before album 01
                            self.browse_position = max(0, self.browse_position - 4)
                    elif self.right_nav_button.is_clicked(event.pos):
                        albums = self.player.library.get_albums()
                        if albums:
                            # Move right by 4 albums, but don't go past album 49
                            self.browse_position = min(48, self.browse_position + 4)
                    elif hasattr(self, "credit_button") and self.credit_button.is_clicked(
                        event.pos
                    ):
                            # Add a single credit when the button is pressed
                            if self.player:
                                try:
                                    self.player.add_credit(1)
                                    self.config_message = f"Added 1 credit (Total: {self.player.get_credits()})"
                                    self.config_message_timer = 180  # 3 seconds at 60fps
                                except Exception:
                                    pass
                            else:
                                # No player available (headless tests) - ignore
                                pass
                    else:
                        # Check number pad buttons
                        self.handle_number_pad_click(event.pos)

            elif event.type == pygame.MOUSEWHEEL:
                # Scroll browser when wheel used
                if self.config_music_editing and self.config_browser_open:
                    rects_local = self._get_music_modal_rects()
                    pa = rects_local["preview_area"]
                    # Only scroll when mouse inside preview area
                    if pa.collidepoint(pygame.mouse.get_pos()):
                        # event.y: positive up, negative down
                        delta = -int(event.y)
                        max_scroll = max(
                            0,
                            len(self.config_browser_entries)
                            - self._browser_visible_count(),
                        )
                        self.config_browser_scroll = max(
                            0, min(max_scroll, self.config_browser_scroll + delta)
                        )
                        continue

                # Handle album card scrolling
                mouse_pos = pygame.mouse.get_pos()
                albums = self.player.library.get_albums() if self.player and self.player.library else []
                if albums:
                    # Calculate card positions (same logic as in draw_main_screen)
                    controls_margin_top = self.header_height + 20
                    button_height = 50
                    media_button_size = 50
                    spacing = 12
                    buttons_y = controls_margin_top + 20
                    content_top = buttons_y + button_height + 25
                    content_height = self.height - content_top - self.bottom_area_height - 20
                    if content_height < 200:
                        content_height = 200
                    row1_y = content_top + 10
                    row2_y = row1_y + content_height // 2 + 35
                    card_h = (content_height // 2) + 15

                    total_content_width = self.width - 40
                    col1_width = int(total_content_width * 0.32)
                    col2_width = int(total_content_width * 0.36)
                    col3_width = int(total_content_width * 0.32)
                    col1_x = 20
                    col2_x = col1_x + col1_width + 10
                    col3_x = col2_x + col2_width + 10

                    # Get current album indices
                    left_album_1 = self.browse_position
                    left_album_2 = self.browse_position + 1
                    right_album_1 = self.browse_position + 2
                    right_album_2 = self.browse_position + 3

                    # Check each album card for mouse hover and scroll
                    album_cards = [
                        (left_album_1, col1_x, row1_y, col1_width - 10, card_h),
                        (left_album_2, col1_x, row2_y, col1_width - 10, card_h),
                        (right_album_1, col3_x, row1_y, col3_width - 10, card_h),
                        (right_album_2, col3_x, row2_y, col3_width - 10, card_h),
                    ]

                    for album_idx, card_x, card_y, card_w, card_h in album_cards:
                        if album_idx >= 0 and album_idx < len(albums):
                            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
                            if card_rect.collidepoint(mouse_pos):
                                album = albums[album_idx]
                                current_offset = self.album_card_scroll_offsets.get(album.album_id, 0)

                                # Calculate how many tracks fit in the card
                                compact = bool(self.config.get("compact_track_list", True))
                                density = float(self.config.get("track_list_density", 0.8))
                                density = max(0.5, min(1.0, density))
                                if self.fullscreen:
                                    base_line = 16 if compact else 18
                                else:
                                    base_line = 10 if compact else 12
                                track_line_height = max(6, int(base_line * density))

                                # Estimate available space for tracks (rough calculation)
                                text_area_height = card_h - 80  # Rough estimate for title/artist area
                                max_tracks_visible = max(1, text_area_height // track_line_height)

                                # Scroll up/down
                                delta = -int(event.y)  # event.y is positive up, negative down
                                new_offset = max(0, min(len(album.tracks) - max_tracks_visible, current_offset + delta))

                                if new_offset != current_offset:
                                    self.album_card_scroll_offsets[album.album_id] = new_offset
                                    self._needs_full_redraw = True
                                break

            elif event.type == pygame.KEYDOWN:
                # If exit confirm modal is open, handle keyboard shortcuts first
                if getattr(self, "exit_confirm_open", False):
                    # Enter (or keypad Enter) -> confirm exit
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.running = False
                        self.exit_confirm_open = False
                        return
                    # Escape -> cancel
                    elif event.key == pygame.K_ESCAPE:
                        self.exit_confirm_open = False
                        # consume this event
                        continue
                # If theme creator modal is open, capture keyboard input for
                # the modal (name entry, cancel/create) and stop further
                # handling so keys don't fall through to global shortcuts.
                if getattr(self, "theme_creator_open", False):
                    # Escape -> cancel
                    if event.key == pygame.K_ESCAPE:
                        self.theme_creator_open = False
                        self.theme_creator_name = ""
                        self.theme_creator_button_colors = {}
                        self.theme_creator_selected_button = None
                        self.theme_creator_sliders = None
                        continue

                    # Enter -> try to create theme
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        name = self.theme_creator_name.strip()
                        if not name:
                            self.config_message = "Theme name required"
                            self.config_message_timer = 160
                        else:
                            safe_name = name.strip().lower().replace(" ", "_")
                            ok = False
                            try:
                                # persist any slider values first
                                if self.theme_creator_selected_button and self.theme_creator_sliders:
                                    r_s, g_s, b_s = self.theme_creator_sliders
                                    btn = self.theme_creator_selected_button
                                    entry = self.theme_creator_button_colors.get(btn)
                                    if not isinstance(entry, dict):
                                        entry = {} if entry is None else {"normal": entry}
                                    entry[self.theme_creator_selected_state] = (
                                        int(r_s.get_value()), int(g_s.get_value()), int(b_s.get_value())
                                    )
                                    self.theme_creator_button_colors[btn] = entry

                                ok = self.theme_manager.create_theme(
                                    safe_name, button_colors=self.theme_creator_button_colors
                                )
                            except Exception:
                                ok = False

                            if ok:
                                self.config_message = f"Theme '{safe_name}' created"
                                self.config_message_timer = 200
                                self.theme_creator_open = False
                                self.theme_creator_name = ""
                                self.theme_creator_button_colors = {}
                                self.theme_creator_selected_button = None
                                self.theme_creator_sliders = None
                                self.setup_theme_buttons()
                            else:
                                self.config_message = "Failed to create theme (exists?)"
                                self.config_message_timer = 200
                        continue

                    # Backspace -> remove last char (only acts on input area)
                    if event.key == pygame.K_BACKSPACE:
                        if getattr(self, 'theme_creator_input_active', False):
                            self.theme_creator_name = self.theme_creator_name[:-1]
                        continue

                    # Other printable characters — only append when input has focus
                    if getattr(self, 'theme_creator_input_active', False):
                        try:
                            ch = event.unicode
                            if ch and len(ch) == 1 and (32 <= ord(ch) <= 126):
                                self.theme_creator_name += ch
                        except Exception:
                            pass
                    continue

                # If in music dir modal, capture typing and modal key actions
                if self.config_music_editing:
                    if event.key == pygame.K_ESCAPE:
                        self.config_music_editing = False
                        self.config_music_preview = None
                    elif event.key == pygame.K_RETURN:
                        # Apply selection
                        path = os.path.expanduser(self.config_music_input)
                        try:
                            new_lib = AlbumLibrary(path)
                            new_lib.scan_library()
                            self.library = new_lib
                            if self.player:
                                try:
                                    self.player.library = new_lib
                                except Exception:
                                    pass
                            self.config.set("music_dir", path)
                            self.config.save()
                            self.config_message = f"Music directory set to: {path}"
                            self.config_message_timer = 200
                            self.config_music_editing = False
                            self.config_music_preview = None
                            self.clear_caches()
                        except Exception as e:
                            self.config_message = f"Failed to set music dir: {e}"
                            self.config_message_timer = 200
                    elif event.key == pygame.K_BACKSPACE:
                        self.config_music_input = self.config_music_input[:-1]
                    else:
                        # Accept printable characters
                        try:
                            ch = event.unicode
                            if ch and len(ch) == 1 and (32 <= ord(ch) <= 126):
                                self.config_music_input += ch
                        except Exception:
                            pass
                    # If the in-modal pure-pygame browser is open handle navigation keys
                    if self.config_browser_open:
                        if event.key == pygame.K_UP:
                            self.config_browser_selected = max(
                                0, self.config_browser_selected - 1
                            )
                            if (
                                self.config_browser_selected
                                < self.config_browser_scroll
                            ):
                                self.config_browser_scroll = (
                                    self.config_browser_selected
                                )
                        elif event.key == pygame.K_DOWN:
                            self.config_browser_selected = min(
                                len(self.config_browser_entries) - 1,
                                self.config_browser_selected + 1,
                            )
                            h = self._browser_visible_count()
                            if (
                                self.config_browser_selected
                                >= self.config_browser_scroll + h
                            ):
                                self.config_browser_scroll = max(
                                    0, self.config_browser_selected - h + 1
                                )
                        elif (
                            event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN
                        ):
                            # Enter directory or select
                            if (
                                0
                                <= self.config_browser_selected
                                < len(self.config_browser_entries)
                            ):
                                ent = self.config_browser_entries[
                                    self.config_browser_selected
                                ]
                                if ent["is_dir"]:
                                    newpath = os.path.join(
                                        self.config_browser_path, ent["name"]
                                    )
                                    self._open_browser(newpath)
                                else:
                                    # for files do nothing, require apply
                                    pass
                        elif event.key == pygame.K_LEFT:
                            parent = os.path.dirname(self.config_browser_path)
                            if (
                                parent
                                and os.path.isdir(parent)
                                and parent != self.config_browser_path
                            ):
                                self._open_browser(parent)
                    # Don't process global shortcuts while editing
                    continue

                # Close config screen with Escape
                if event.key == pygame.K_ESCAPE:
                    if self.config_screen_open:
                        self.config_screen_open = False
                    else:
                        self.selection_buffer = ""
                        self.selection_mode = False

                # Backspace -> pop last digit from selection buffer (if not editing)
                elif event.key == pygame.K_BACKSPACE:
                    if not self.config_screen_open:
                        self.selection_buffer = self.selection_buffer[:-1]
                        self.selection_mode = len(self.selection_buffer) > 0

                # Number keys for 4-digit song selection
                elif event.key in [
                    pygame.K_0,
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5,
                    pygame.K_6,
                    pygame.K_7,
                    pygame.K_8,
                    pygame.K_9,
                    # include keypad numbers as well
                    pygame.K_KP0,
                    pygame.K_KP1,
                    pygame.K_KP2,
                    pygame.K_KP3,
                    pygame.K_KP4,
                    pygame.K_KP5,
                    pygame.K_KP6,
                    pygame.K_KP7,
                    pygame.K_KP8,
                    pygame.K_KP9,
                ]:
                    if not self.config_screen_open:
                        self.handle_number_input(event)

                # Enter to execute selection (also accept keypad Enter)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # Check for Alt+Enter for fullscreen toggle
                    if (
                        pygame.key.get_pressed()[pygame.K_LALT]
                        or pygame.key.get_pressed()[pygame.K_RALT]
                    ):
                        self.toggle_fullscreen()
                    elif not self.config_screen_open:
                        self.execute_selection()

                # Other keyboard shortcuts
                elif event.key == pygame.K_SPACE:
                    if not self.config_screen_open:
                        if self.player.is_playing and not self.player.is_paused:
                            self.player.pause()
                        else:
                            self.player.play()
                elif event.key == pygame.K_RIGHT:
                    if not self.config_screen_open:
                        self.player.next_track()
                elif event.key == pygame.K_LEFT:
                    if not self.config_screen_open:
                        self.player.previous_track()
                elif event.key == pygame.K_UP:
                    if not self.config_screen_open:
                        # Increase volume and update slider
                        new_volume = min(1.0, self.player.volume + 0.1)
                        self.player.set_volume(new_volume)
                        self.volume_slider.value = (
                            new_volume * 100
                        )  # Convert to 0-100 range
                elif event.key == pygame.K_DOWN:
                    if not self.config_screen_open:
                        # Decrease volume and update slider
                        new_volume = max(0.0, self.player.volume - 0.1)
                        self.player.set_volume(new_volume)
                        self.volume_slider.value = (
                            new_volume * 100
                        )  # Convert to 0-100 range
                elif event.key == pygame.K_n:
                    if not self.config_screen_open:
                        self.player.next_album()
                elif event.key == pygame.K_p:
                    if not self.config_screen_open:
                        self.player.previous_album()
                elif event.key == pygame.K_c:
                    self.config_screen_open = not self.config_screen_open
                    self.clear_caches()  # Clear caches when toggling config

    def handle_number_pad_click(self, pos: Tuple[int, int]) -> None:
        """Handle number pad button clicks"""
        for btn in self.number_pad_buttons:
            if btn.is_clicked(pos):
                if btn.digit == "CLR":
                    self.selection_buffer = ""
                    self.selection_mode = False
                elif btn.digit == "ENT":
                    self.execute_selection()
                elif btn.digit == "<":
                    # Backspace
                    self.selection_buffer = self.selection_buffer[:-1]
                    self.selection_mode = len(self.selection_buffer) > 0
                else:
                    # Number digit
                    self.selection_buffer += btn.digit
                    self.selection_mode = True

                    # Auto-execute when 4 digits are entered
                    if len(self.selection_buffer) == 4:
                        self.execute_selection()
                break

    def handle_rescan(self) -> None:
        """Rescan album directories"""
        self.config_message = "Rescanning albums..."
        self.config_message_timer = 60
        self.library.scan_library()
        self.config_message = (
            f"Rescan complete! Found {len(self.library.get_albums())} albums"
        )
        self.config_message_timer = 180
        print("Album library rescanned")

    def handle_reset_config(self) -> None:
        """Reset configuration to defaults"""
        self.config.reset_to_defaults()
        self.config_message = "Configuration reset to defaults"
        self.config_message_timer = 180
        print("Configuration reset to defaults")

    def handle_extract_art(self) -> None:
        """Handle extract album art button click"""
        self.config_message = "Extracting album art..."
        self.config_message_timer = 300  # Long timer for this operation

        # Run the extraction
        stats = self.library.extract_all_cover_art()

        # Clear the album art cache so newly extracted art will be loaded
        self.album_art_cache.clear()

        # Update the message with results
        extracted = stats["extracted"]
        existing = stats["existing"]
        failed = stats["failed"]
        self.config_message = (
            f"Art: {extracted} extracted, {existing} existing, {failed} failed"
        )
        self.config_message_timer = 240  # Display results for 4 seconds

    def handle_theme_selection(self, pos: Tuple[int, int]) -> None:
        """Handle theme button clicks"""
        # Check the 'New Theme' button first
        if hasattr(self, "new_theme_button") and self.new_theme_button.is_clicked(pos):
            # Open the theme creator modal
            self.theme_creator_open = True
            self.theme_creator_name = ""
            self.theme_creator_button_colors = {}
            self.theme_creator_selected_button = None
            self.theme_creator_sliders = None
            # Focus the name input by default so typing immediately works
            self.theme_creator_input_active = True
            return

        # Check clicks on the visible theme selection buttons (main/config screen)
        for theme_name, btn in self.theme_buttons:
            if btn.is_clicked(pos):
                # Switch to the selected theme
                self.theme_manager.set_current_theme(theme_name)
                self.config.set("theme", theme_name)
                self.config.save()  # Save the configuration to persist the theme choice
                self.current_theme = self.theme_manager.get_current_theme()

                # Update button colors to reflect selection
                self.setup_theme_buttons()

                # Update all buttons with new theme
                try:
                    self.left_nav_button.theme = self.current_theme
                    self.right_nav_button.theme = self.current_theme
                    self.play_button.theme = self.current_theme
                    self.pause_button.theme = self.current_theme
                    self.stop_button.theme = self.current_theme
                    self.config_button.theme = self.current_theme

                    # Update config screen buttons
                    self.config_rescan_button.theme = self.current_theme
                    self.config_reset_button.theme = self.current_theme
                    self.config_close_button.theme = self.current_theme
                    self.config_extract_art_button.theme = self.current_theme
                    self.config_equalizer_button.theme = self.current_theme
                    self.config_fullscreen_button.theme = self.current_theme

                    # Update equalizer buttons
                    self.eq_back_button.theme = self.current_theme
                    self.eq_save_button.theme = self.current_theme
                    for _, eq_btn in self.eq_preset_buttons:
                        eq_btn.theme = self.current_theme

                    # Update number pad buttons
                    for pad_btn in self.number_pad_buttons:
                        pad_btn.theme = self.current_theme

                    # Update theme selection buttons
                    for _, theme_btn in self.theme_buttons:
                        theme_btn.theme = self.current_theme
                except Exception:
                    # Some attributes may not exist in unit-test initialization
                    # (UI may be partially constructed), ignore those errors.
                    pass

                # Show confirmation message
                self.config_message = f"Theme changed to {theme_name.capitalize()}"
                self.config_message_timer = 180
                print(f"Theme switched to: {theme_name}")

                # Clear caches when theme changes for optimal performance
                self.clear_caches()
                break

    def _handle_theme_creator_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse clicks inside the theme creator modal."""
        rects = self._get_theme_creator_rects()

        # If clicking the theme name input area, just focus it and don't
        # let the click fall-through to other UI areas.
        if rects["input"].collidepoint(pos):
            # keep modal open and allow typing
            self.theme_creator_input_active = True
            return
        else:
            self.theme_creator_input_active = False

        # Cancel
        if rects["cancel"].collidepoint(pos):
            self.theme_creator_open = False
            self.theme_creator_name = ""
            self.theme_creator_button_colors = {}
            self.theme_creator_selected_button = None
            self.theme_creator_sliders = None
            return

        # Save / Create
        if rects["save"].collidepoint(pos):
            name = self.theme_creator_name.strip()
            if not name:
                self.config_message = "Theme name required"
                self.config_message_timer = 180
                return

            # Persist any currently selected slider values before saving
            if self.theme_creator_selected_button and self.theme_creator_sliders:
                r_s, g_s, b_s = self.theme_creator_sliders
                btn = self.theme_creator_selected_button
                entry = self.theme_creator_button_colors.get(btn)
                if not isinstance(entry, dict):
                    entry = {} if entry is None else {"normal": entry}
                entry[self.theme_creator_selected_state] = (
                    int(r_s.get_value()), int(g_s.get_value()), int(b_s.get_value())
                )
                self.theme_creator_button_colors[btn] = entry

            safe_name = name.strip().lower().replace(" ", "_")
            ok = self.theme_manager.create_theme(
                safe_name, button_colors=self.theme_creator_button_colors
            )
            if ok:
                self.config_message = f"Theme '{safe_name}' created"
                self.config_message_timer = 200
                self.theme_creator_open = False
                self.theme_creator_name = ""
                self.theme_creator_button_colors = {}
                self.theme_creator_selected_button = None
                self.theme_creator_sliders = None
                self.setup_theme_buttons()
            else:
                self.config_message = "Failed to create theme (exists?)"
                self.config_message_timer = 200
            return

        # Check clicks on available themable buttons grid
        # Also check clicks on the state selector (normal/hover/pressed) if a button is selected
        pick = rects["picker"]
        state_x = pick.x + 8
        state_y = pick.y + 36
        states = ["normal", "hover", "pressed"]
        ss_w = 64
        # Only allow state switching if a button is currently selected
        if self.theme_creator_selected_button:
            for si, st in enumerate(states):
                sx = state_x + si * (ss_w + 8)
                srect = pygame.Rect(sx, state_y, ss_w, 24)
                if srect.collidepoint(pos):
                    # Save current slider values into previous state
                    if self.theme_creator_selected_button and self.theme_creator_sliders:
                        r_s, g_s, b_s = self.theme_creator_sliders
                        btn_prev = self.theme_creator_selected_button
                        entry = self.theme_creator_button_colors.get(btn_prev)
                        if not isinstance(entry, dict):
                            entry = {} if entry is None else {"normal": entry}
                        entry[self.theme_creator_selected_state] = (
                            int(r_s.get_value()), int(g_s.get_value()), int(b_s.get_value())
                        )
                        self.theme_creator_button_colors[btn_prev] = entry

                    # Switch to new state
                    self.theme_creator_selected_state = st

                    # Load existing value for the new state (if any)
                    entry = self.theme_creator_button_colors.get(self.theme_creator_selected_button)
                    existing = None
                    if isinstance(entry, dict):
                        existing = entry.get(self.theme_creator_selected_state)
                    elif isinstance(entry, (tuple, list)) and self.theme_creator_selected_state == "normal":
                        existing = entry
                    if existing is None:
                        existing = (128, 128, 128)

                    # Create sliders for the selected state
                    base_x = rects["picker"].x + 12
                    base_y = rects["picker"].y + 48
                    width = rects["picker"].width - 24
                    r_s = Slider(base_x, base_y, width, 16, min_val=0, max_val=255, initial_val=existing[0], label="R", theme=self.current_theme)
                    g_s = Slider(base_x, base_y + 36, width, 16, min_val=0, max_val=255, initial_val=existing[1], label="G", theme=self.current_theme)
                    b_s = Slider(base_x, base_y + 72, width, 16, min_val=0, max_val=255, initial_val=existing[2], label="B", theme=self.current_theme)
                    self.theme_creator_sliders = (r_s, g_s, b_s)
                    return
        ba = rects["buttons_area"]
        padding = 8
        cols = 3
        btn_w = (ba.width - (cols + 1) * padding) // cols
        btn_h = 40
        x0 = ba.x + padding
        y0 = ba.y + padding

        for idx, (_label_text, key) in enumerate(THEMABLE_TEXT_BUTTONS):
            col = idx % cols
            row = idx // cols
            rx = x0 + col * (btn_w + padding)
            ry = y0 + row * (btn_h + padding)
            rect = pygame.Rect(rx, ry, btn_w, btn_h)
            if rect.collidepoint(pos):
                # If a previous button was selected, save its slider values
                if self.theme_creator_selected_button and self.theme_creator_sliders:
                    r_s, g_s, b_s = self.theme_creator_sliders
                    btn_prev = self.theme_creator_selected_button
                    entry = self.theme_creator_button_colors.get(btn_prev)
                    if not isinstance(entry, dict):
                        entry = {} if entry is None else {"normal": entry}
                    entry[self.theme_creator_selected_state] = (
                        int(r_s.get_value()), int(g_s.get_value()), int(b_s.get_value())
                    )
                    self.theme_creator_button_colors[btn_prev] = entry

                # Start editing this key
                # select the new key and initialize sliders with the value for the current selected state
                self.theme_creator_selected_button = key
                existing_entry = self.theme_creator_button_colors.get(key)
                existing = None
                if isinstance(existing_entry, dict):
                    existing = existing_entry.get(self.theme_creator_selected_state)
                elif isinstance(existing_entry, (tuple, list)):
                    # legacy single value treated as 'normal'
                    existing = existing_entry if self.theme_creator_selected_state == "normal" else None
                if existing is None:
                    existing = (128, 128, 128)
                # Build sliders for this key
                base_x = rects["picker"].x + 12
                base_y = rects["picker"].y + 48
                width = rects["picker"].width - 24
                r_s = Slider(base_x, base_y, width, 16, min_val=0, max_val=255, initial_val=existing[0], label="R", theme=self.current_theme)
                g_s = Slider(base_x, base_y + 36, width, 16, min_val=0, max_val=255, initial_val=existing[1], label="G", theme=self.current_theme)
                b_s = Slider(base_x, base_y + 72, width, 16, min_val=0, max_val=255, initial_val=existing[2], label="B", theme=self.current_theme)
                self.theme_creator_sliders = (r_s, g_s, b_s)
                return

        # Click outside interesting area -> ignore
        # NOTE: do not return here — we still need to check the theme
        # selection buttons below. Previously a stray return caused theme
        # buttons to never be processed which prevented changing themes.
        # Theme selection handled in handle_theme_selection() for clicks on
        # the theme buttons (main/config screen). The creator modal does not
        # need to process the theme selection buttons here.

    def update_audio_controls(self) -> None:
        """Update audio controls and apply effects"""
        # Update volume from slider
        slider_volume = self.volume_slider.get_value() / 100.0

        # Update equalizer bands first
        for i, slider in enumerate(self.eq_sliders):
            gain = slider.get_value()
            self.equalizer.set_band(i, gain)

        # Set volume after equalizer update (so EQ adjustments are applied)
        self._player_safe_call("set_volume", slider_volume)

    def get_cached_text(
        self, text: str, font: pygame.font.Font, color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """Get cached text surface or create new one"""
        cache_key = (text, id(font), color)
        if cache_key in self._text_cache:
            return self._text_cache[cache_key]

        # Create new text surface
        surface = font.render(text, True, color)

        # Add to cache if not full
        if self._text_cache_size < self._max_cache_size:
            self._text_cache[cache_key] = surface
            self._text_cache_size += 1

        return surface

    def get_cached_background(self) -> pygame.Surface:
        """Get cached background or create new one"""
        current_size = (self.width, self.height)
        if self._cached_background is None or self._last_bg_size != current_size:
            background = self.current_theme.get_background(self.width, self.height)
            if background:
                if background.get_size() == current_size:
                    self._cached_background = background
                else:
                    self._cached_background = pygame.transform.scale(
                        background, current_size
                    )
            else:
                self._cached_background = pygame.Surface(current_size)
                self._cached_background.fill(Colors.DARK_GRAY)
            self._last_bg_size = current_size
        return self._cached_background

    def clear_caches(self) -> None:
        """Clear caches when needed (theme changes, etc.)"""
        self._cached_background = None
        self._text_cache.clear()
        self._text_cache_size = 0
        self._needs_full_redraw = True

    def choose_music_directory(self) -> None:
        """Open a folder selection dialog (if available) and update the music library.

        Tries to use tkinter.filedialog.askdirectory for a native dialog; falls back
        to a simple console prompt if tkinter is unavailable or fails.
        """
        # Determine an initial directory for the dialog
        initial = self.config.get("music_dir")
        if not initial:
            if sys.platform.startswith("linux") or sys.platform == "darwin":
                initial = os.path.expanduser(os.path.join("~", "Music", "JukeBox"))
            else:
                initial = os.path.join(os.path.dirname(__file__), "..", "music")

        selected = None
        # Try to use tkinter for a GUI folder chooser
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            selected = filedialog.askdirectory(
                title="Select JukeBox Music Directory", initialdir=initial
            )
            root.destroy()
        except Exception:
            # Fallback to console input
            print("Tkinter folder dialog not available. Enter path to music directory:")
            selected = input("> ").strip()

        if not selected:
            self.config_message = "No directory selected"
            self.config_message_timer = 120
            return

        selected = os.path.expanduser(selected)

        # Create new library and re-wire UI/player to use it
        new_lib = AlbumLibrary(selected)
        new_lib.scan_library()

        self.library = new_lib
        if self.player is not None:
            try:
                self.player.library = new_lib
            except Exception:
                # Safe fallback if player doesn't accept direct assignment
                pass

        # Persist selection to config
        self.config.set("music_dir", selected)
        self.config.save()

        # Give user visual feedback and refresh caches
        self.config_message = f"Music directory set to: {selected}"
        self.config_message_timer = 240
        self.clear_caches()

    def _compute_music_preview(self, path: str) -> dict:
        """Return a short preview summary of the selected directory.

        Returns a dict containing: total_files, audio_files, sample_files (list), total_size_bytes
        """
        result = {
            "total_files": 0,
            "audio_files": 0,
            "sample_files": [],
            "total_size_bytes": 0,
        }
        try:
            if not os.path.exists(path):
                return result

            supported = getattr(AlbumLibrary, "MAX_ALBUMS", None)  # not used here
            audio_exts = (".mp3", ".wav", ".ogg", ".flac")
            total = 0
            audio_count = 0
            samples = []
            total_size = 0
            # Walk top-level files and immediate subdirectories (non-recursive for preview)
            # Collect sample files for display
            for entry in sorted(os.listdir(path)):
                p = os.path.join(path, entry)
                if os.path.isfile(p):
                    total += 1
                    sz = os.path.getsize(p)
                    total_size += sz
                    if entry.lower().endswith(audio_exts):
                        audio_count += 1
                        if len(samples) < 10:
                            samples.append(entry)
                elif os.path.isdir(p):
                    # Optionally list files inside first few subdirs
                    try:
                        for f in sorted(os.listdir(p))[:3]:
                            total += 1
                            fp = os.path.join(p, f)
                            if os.path.isfile(fp):
                                sz = os.path.getsize(fp)
                                total_size += sz
                                if f.lower().endswith(audio_exts):
                                    audio_count += 1
                                    if len(samples) < 10:
                                        samples.append(os.path.join(entry, f))
                    except Exception:
                        pass

                # Theme creator modal keyboard handling
                if getattr(self, "theme_creator_open", False):
                    if event.key == pygame.K_ESCAPE:
                        # Cancel theme creation
                        self.theme_creator_open = False
                        self.theme_creator_name = ""
                        self.theme_creator_button_colors = {}
                        self.theme_creator_selected_button = None
                        self.theme_creator_sliders = None
                        continue
                    elif event.key == pygame.K_RETURN:
                        # Attempt to create theme
                        name = self.theme_creator_name.strip()
                        if not name:
                            self.config_message = "Theme name required"
                            self.config_message_timer = 160
                        else:
                            # Sanitise name to safe directory name
                            safe_name = name.strip().lower().replace(" ", "_")
                            ok = False
                            try:
                                ok = self.theme_manager.create_theme(
                                    safe_name, button_colors=self.theme_creator_button_colors
                                )
                            except Exception:
                                ok = False

                            if ok:
                                self.config_message = f"Theme '{safe_name}' created"
                                self.config_message_timer = 200
                                self.theme_creator_open = False
                                self.theme_creator_name = ""
                                self.theme_creator_button_colors = {}
                                self.theme_creator_selected_button = None
                                self.theme_creator_sliders = None
                                # Refresh theme buttons
                                self.setup_theme_buttons()
                            else:
                                self.config_message = "Failed to create theme (exists?)"
                                self.config_message_timer = 200
                        continue
                    elif event.key == pygame.K_BACKSPACE:
                        self.theme_creator_name = self.theme_creator_name[:-1]
                    else:
                        try:
                            ch = event.unicode
                            if ch and len(ch) == 1 and (32 <= ord(ch) <= 126):
                                self.theme_creator_name += ch
                        except Exception:
                            pass

            result["total_files"] = total
            result["audio_files"] = audio_count
            result["sample_files"] = samples
            result["total_size_bytes"] = total_size
        except Exception:
            pass

        return result

    def _get_music_modal_rects(self) -> dict:
        """Return rects for the music modal's elements (input field, buttons, preview area)."""
        w = min(900, int(self.width * 0.8))
        h = min(480, int(self.height * 0.6))
        x = (self.width - w) // 2
        y = (self.height - h) // 2
        # Input field at top
        input_rect = pygame.Rect(x + 20, y + 40, w - 40, 32)
        # Buttons row below input
        btn_w = 140
        btn_h = 36
        spacing = 12
        btn_y = y + 88
        btn_x = x + 20
        browse_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        preview_rect = pygame.Rect(btn_x + (btn_w + spacing), btn_y, btn_w, btn_h)
        apply_rect = pygame.Rect(btn_x + 2 * (btn_w + spacing), btn_y, btn_w, btn_h)
        cancel_rect = pygame.Rect(btn_x + 3 * (btn_w + spacing), btn_y, btn_w, btn_h)

        preview_area = pygame.Rect(
            x + 20, btn_y + btn_h + 20, w - 40, h - (btn_y - y) - btn_h - 40
        )

        return {
            "bg": pygame.Rect(x, y, w, h),
            "input": input_rect,
            "browse": browse_rect,
            "preview": preview_rect,
            "apply": apply_rect,
            "cancel": cancel_rect,
            "preview_area": preview_area,
        }

    def _get_theme_creator_rects(self) -> dict:
        """Return rects for the theme creator modal (name input, button list, color picker, actions)."""
        w = min(800, int(self.width * 0.75))
        h = min(600, int(self.height * 0.8))  # Increased height for better color picker layout
        x = (self.width - w) // 2
        y = (self.height - h) // 2

        input_rect = pygame.Rect(x + 20, y + 40, w - 40, 36)

        # Color picker area on the right (increased height)
        picker_width = 280
        picker_height = 280  # Increased from 200 to prevent control overlap
        picker_rect = pygame.Rect(x + w - picker_width, y + 96, picker_width - 40, picker_height)

        # Buttons area: grid below input — stay to the left of picker so they
        # never overlap. Reserve spacing for the picker area.
        buttons_area = pygame.Rect(x + 20, y + 96, w - 40 - picker_width, picker_height)

        # Save / Cancel action buttons
        btn_w = 140
        btn_h = 36
        save_rect = pygame.Rect(x + 20, y + h - 72, btn_w, btn_h)
        cancel_rect = pygame.Rect(x + 20 + btn_w + 12, y + h - 72, btn_w, btn_h)

        return {
            "bg": pygame.Rect(x, y, w, h),
            "input": input_rect,
            "buttons_area": buttons_area,
            "picker": picker_rect,
            "save": save_rect,
            "cancel": cancel_rect,
        }

    def draw_theme_creator_dialog(self) -> None:
        """Render the theme creation modal when open."""
        rects = self._get_theme_creator_rects()
        # Dim background to indicate modal state and prevent visual click-through
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        bg = rects["bg"]

        # Modal background
        modal_surf = pygame.Surface((bg.width, bg.height), pygame.SRCALPHA)
        modal_surf.fill((10, 10, 10, 220))
        self.screen.blit(modal_surf, (bg.x, bg.y))

        # Title
        title = self.medium_font.render("Create New Theme", True, self.accent_color())
        title_rect = title.get_rect(center=(bg.centerx, bg.y + 20))
        self.screen.blit(title, title_rect)

        # Name input label and field
        label = self.small_font.render("Theme name:", True, self.text_secondary_color())
        self.screen.blit(label, (rects["input"].x, rects["input"].y - 20))

        # Input box
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, rects["input"])
        pygame.draw.rect(self.screen, Colors.WHITE, rects["input"], 2)
        name_display = self.small_font.render(self.theme_creator_name or "<enter name>", True, self.text_color())
        name_pos = (rects["input"].x + 8, rects["input"].y + 6)
        self.screen.blit(name_display, name_pos)

        # Draw caret when input active (blinking)
        if getattr(self, 'theme_creator_input_active', False):
            try:
                blink_on = (pygame.time.get_ticks() // 500) % 2 == 0
                if blink_on:
                    caret_x = name_pos[0] + name_display.get_width() + 3
                    caret_y0 = rects["input"].y + 8
                    caret_y1 = rects["input"].y + rects["input"].height - 8
                    pygame.draw.line(self.screen, Colors.YELLOW, (caret_x, caret_y0), (caret_x, caret_y1), 2)
            except Exception:
                pass

        # Draw buttons grid (left area) showing available buttons you can theme
        ba = rects["buttons_area"]
        padding = 8
        cols = 3
        btn_w = (ba.width - (cols + 1) * padding) // cols
        btn_h = 40
        x0 = ba.x + padding
        y0 = ba.y + padding

        for idx, (label_text, key) in enumerate(THEMABLE_TEXT_BUTTONS):
            col = idx % cols
            row = idx // cols
            rx = x0 + col * (btn_w + padding)
            ry = y0 + row * (btn_h + padding)
            rect = pygame.Rect(rx, ry, btn_w, btn_h)

            # Fill background and border
            pygame.draw.rect(self.screen, Colors.GRAY, rect)
            pygame.draw.rect(self.screen, Colors.WHITE, rect, 2)

            # Color preview box on left
            preview_rect = pygame.Rect(rx + 8, ry + 8, 24, 24)
            color_val = self.theme_creator_button_colors.get(key)
            # color_val may be a tuple/list (legacy single value) or a dict
            # mapping states -> rgb tuples. Choose a usable rgb tuple for the
            # preview (prefer 'normal' state if present).
            chosen = None
            try:
                if isinstance(color_val, dict):
                    chosen = color_val.get("normal") or next(iter(color_val.values()))
                elif isinstance(color_val, (tuple, list)):
                    chosen = color_val
            except Exception:
                chosen = None

            if chosen and isinstance(chosen, (tuple, list)) and len(chosen) >= 3:
                c = (int(chosen[0]), int(chosen[1]), int(chosen[2]))
                pygame.draw.rect(self.screen, c, preview_rect)
            else:
                # fallback display color
                pygame.draw.rect(self.screen, (160, 160, 160), preview_rect)

            # Label text
            lab = self.small_font.render(label_text, True, self.text_color())
            self.screen.blit(lab, (rx + 40, ry + (btn_h - lab.get_height()) // 2))

            # If selected, draw highlight
            if self.theme_creator_selected_button == key:
                pygame.draw.rect(self.screen, Colors.YELLOW, rect, 3)

        # Color picker area (right side)
        pick = rects["picker"]
        pygame.draw.rect(self.screen, (24, 24, 24), pick)
        pygame.draw.rect(self.screen, Colors.WHITE, pick, 2)
        pick_label = self.small_font.render("Color Picker", True, self.text_secondary_color())
        self.screen.blit(pick_label, (pick.x + 8, pick.y + 8))

        # State selector (normal / hover / pressed)
        state_x = pick.x + 8
        state_y = pick.y + 36
        states = ["normal", "hover", "pressed"]
        ss_w = 64
        for si, st in enumerate(states):
            sx = state_x + si * (ss_w + 8)
            srect = pygame.Rect(sx, state_y, ss_w, 24)
            # Highlight selected state
            if self.theme_creator_selected_state == st:
                pygame.draw.rect(self.screen, Colors.YELLOW, srect)
            else:
                pygame.draw.rect(self.screen, Colors.GRAY, srect)
            pygame.draw.rect(self.screen, Colors.WHITE, srect, 2)
            lbl = self.small_font.render(st.capitalize(), True, self.text_color() if self.theme_creator_selected_state == st else self.text_secondary_color())
            self.screen.blit(lbl, (srect.x + 8, srect.y + 4))

        # If a button selected, show RGB sliders and preview
        if self.theme_creator_selected_button:
            if self.theme_creator_sliders is None:
                # no sliders configured - show hint
                hint = self.small_font.render("Click a button to set its color", True, self.text_color())
                self.screen.blit(hint, (pick.x + 8, pick.y + 36))
            else:
                r_s, g_s, b_s = self.theme_creator_sliders
                # Draw sliders (they render themselves with current fonts)
                # Position sliders inside picker with better spacing
                slider_start_y = pick.y + 95  # Start below state selector with more padding to avoid overlap
                slider_spacing = 50  # Increased spacing for 25px padding around each slider
                
                r_s.x = pick.x + 12
                r_s.y = slider_start_y
                r_s.width = pick.width - 24
                r_s.height = 16
                r_s.draw(self.screen, self.small_font)

                g_s.x = pick.x + 12
                g_s.y = slider_start_y + slider_spacing
                g_s.width = pick.width - 24
                g_s.height = 16
                g_s.draw(self.screen, self.small_font)

                b_s.x = pick.x + 12
                b_s.y = slider_start_y + 2 * slider_spacing
                b_s.width = pick.width - 24
                b_s.height = 16
                b_s.draw(self.screen, self.small_font)

                # RGB preview box (positioned to fit properly within the picker bounds)
                preview_y = pick.y + 200  # Fixed position for better fit
                preview_height = 60  # Fixed height for consistent display
                preview = pygame.Rect(pick.x + 12, preview_y, pick.width - 24, preview_height)
                col = (int(r_s.get_value()), int(g_s.get_value()), int(b_s.get_value()))
                pygame.draw.rect(self.screen, col, preview)
                pygame.draw.rect(self.screen, Colors.WHITE, preview, 2)

        # Draw action buttons
        pygame.draw.rect(self.screen, Colors.GREEN, rects["save"]) 
        pygame.draw.rect(self.screen, Colors.WHITE, rects["save"], 2)
        s = self.small_font.render("Create Theme", True, self.text_color())
        self.screen.blit(s, (rects["save"].x + 12, rects["save"].y + 8))

        pygame.draw.rect(self.screen, Colors.RED, rects["cancel"]) 
        pygame.draw.rect(self.screen, Colors.WHITE, rects["cancel"], 2)
        s2 = self.small_font.render("Cancel", True, self.text_color())
        self.screen.blit(s2, (rects["cancel"].x + 12, rects["cancel"].y + 8))

    def _open_browser(self, path: str) -> None:
        """Open a directory in the in-modal pure-pygame browser.

        This loads entries using src.fs_utils.list_directory and resets selection/scroll.
        """
        try:
            info = list_directory(path)
            self.config_browser_path = info.get("path")
            self.config_browser_entries = info.get("entries", [])
            # reset selection/scroll
            self.config_browser_selected = 0
            self.config_browser_scroll = 0
            # Also update the input path field so the user can apply the selection
            self.config_music_input = self.config_browser_path
        except Exception:
            # On error, leave browser state unchanged
            pass

    def _browser_visible_count(self) -> int:
        """Return how many rows of entries fit inside the preview area.

        Used to compute scrolling behavior.
        """
        rects = self._get_music_modal_rects()
        header_h = self.small_font.get_height() + 8
        row_h = max(self.small_font.get_height(), 18)
        avail = rects["preview_area"].height - header_h - 24  # leave room for hints
        if avail <= 0:
            return 0
        return max(1, avail // row_h)

    def _ellipsize_text(self, text: str, font: pygame.font.Font, max_width: int) -> str:
        """Return a text shortened with ellipsis to fit inside max_width using the provided font."""
        if font.size(text)[0] <= max_width:
            return text
        # Need room for '...'
        ell = "..."
        # Trim characters until fits
        left = 0
        right = len(text)
        # Binary search for best fit
        while left < right:
            mid = (left + right) // 2
            candidate = text[:mid].rstrip() + ell
            if font.size(candidate)[0] <= max_width:
                left = mid + 1
            else:
                right = mid

        candidate = text[: max(0, left - 1)].rstrip() + ell
        return candidate

    def _draw_music_dir_modal(self) -> None:
        """Draw the in-app music directory selection / preview modal."""
        rects = self._get_music_modal_rects()
        # Dark overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Modal background
        bg = pygame.Surface((rects["bg"].width, rects["bg"].height))
        bg.fill((40, 40, 40))
        pygame.draw.rect(bg, Colors.WHITE, bg.get_rect(), 2)
        self.screen.blit(bg, (rects["bg"].x, rects["bg"].y))

        # Title
        title = self.medium_font.render(
            "Select Music Library (in-app)", True, Colors.WHITE
        )
        self.screen.blit(title, (rects["bg"].x + 20, rects["bg"].y + 8))

        # Input label and box
        label = self.small_font.render("Path:", True, Colors.LIGHT_GRAY)
        self.screen.blit(label, (rects["input"].x, rects["input"].y - 18))
        pygame.draw.rect(self.screen, Colors.BLACK, rects["input"])
        pygame.draw.rect(self.screen, Colors.WHITE, rects["input"], 2)
        # Render the current input text (truncate if too long)
        display_text = self.config_music_input
        # Trim to fit
        max_chars = 120
        if len(display_text) > max_chars:
            display_text = "..." + display_text[-max_chars:]
        txt_surf = self.small_font.render(display_text, True, Colors.WHITE)
        self.screen.blit(txt_surf, (rects["input"].x + 6, rects["input"].y + 6))

        # Draw buttons (highlight hovered button)
        hover = getattr(self, "config_music_hover", None)
        for name, r in [
            ("Browse", rects["browse"]),
            ("Preview", rects["preview"]),
            ("Apply", rects["apply"]),
            ("Cancel", rects["cancel"]),
        ]:
            btn_key = name.lower()
            color = Colors.YELLOW if hover == btn_key else Colors.GRAY
            pygame.draw.rect(self.screen, color, r)
            pygame.draw.rect(self.screen, Colors.WHITE, r, 2)
            t = self.small_font.render(
                name, True, Colors.BLACK if hover == btn_key else Colors.WHITE
            )
            tpos = t.get_rect(center=r.center)
            self.screen.blit(t, tpos)

        # Draw preview area (if present)
        pygame.draw.rect(self.screen, (18, 18, 18), rects["preview_area"])
        pygame.draw.rect(self.screen, Colors.WHITE, rects["preview_area"], 1)
        pa_x = rects["preview_area"].x + 8
        pa_y = rects["preview_area"].y + 8

        if self.config_browser_open:
            # Render the folder browser view inside the preview area
            browser = {
                "path": self.config_browser_path,
                "entries": self.config_browser_entries,
            }
            header = self.small_font.render(f"{browser['path']}", True, Colors.YELLOW)
            self.screen.blit(header, (pa_x, pa_y))

            # Compute visible rows inside preview area
            row_y = pa_y + header.get_height() + 8
            row_height = max(self.small_font.get_height(), 18)
            visible = self._browser_visible_count()
            start = self.config_browser_scroll
            end = min(len(browser["entries"]), start + visible)

            # Draw each visible entry
            for idx in range(start, end):
                ent = browser["entries"][idx]
                sel = idx == self.config_browser_selected
                bg_rect = pygame.Rect(
                    pa_x,
                    row_y + (idx - start) * row_height,
                    rects["preview_area"].width - 12,
                    row_height,
                )
                # Alternate row stripe for readability
                if not sel and ((idx - start) % 2) == 0:
                    pygame.draw.rect(self.screen, (28, 28, 28), bg_rect)
                if sel:
                    pygame.draw.rect(self.screen, (64, 64, 96), bg_rect)

                # icon
                icon_x = pa_x + 4
                icon_y = bg_rect.y + 2
                if ent["is_dir"]:
                    pygame.draw.polygon(
                        self.screen,
                        Colors.LIGHT_GRAY,
                        [
                            (icon_x, icon_y + 8),
                            (icon_x + 10, icon_y + 4),
                            (icon_x + 10, icon_y + 12),
                        ],
                    )
                else:
                    pygame.draw.rect(
                        self.screen, Colors.LIGHT_GRAY, (icon_x, icon_y + 3, 10, 10)
                    )

                # name and meta
                name_x = icon_x + 16
                meta = f"{ent['size']} bytes"
                meta_s = self.tiny_font.render(meta, True, Colors.LIGHT_GRAY)
                # Compute max width for name text so it doesn't overlap meta
                max_name_w = (
                    rects["preview_area"].width
                    - 12
                    - (name_x - rects["preview_area"].x)
                    - meta_s.get_width()
                    - 16
                )
                name_text = self._ellipsize_text(
                    ent["name"], self.small_font, max_name_w
                )
                name_s = self.small_font.render(
                    name_text, True, self.text_color() if not sel else self.accent_color()
                )
                self.screen.blit(name_s, (name_x, bg_rect.y + 1))
                # size/time right-justified
                meta_pos = (
                    rects["preview_area"].right - 8 - meta_s.get_width(),
                    bg_rect.y + 1,
                )
                self.screen.blit(meta_s, meta_pos)

            # Scrollbar if needed
            total = len(browser["entries"])
            if total > visible and visible > 0:
                bar_h = rects["preview_area"].height - 12 - header.get_height() - 8
                sb_h = max(20, int((visible / total) * bar_h))
                sb_range = bar_h - sb_h
                if sb_range > 0:
                    sb_pos = int(
                        (self.config_browser_scroll / max(1, total - visible))
                        * sb_range
                    )
                else:
                    sb_pos = 0
                sb_x = rects["preview_area"].right - 8
                sb_y = row_y + sb_pos
                pygame.draw.rect(self.screen, Colors.GRAY, (sb_x, row_y, 8, bar_h))
                pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (sb_x, sb_y, 8, sb_h))

            # Instruction hint
            hint = self.tiny_font.render(
                "Use ↑↓ keys to navigate, → or double-click to open, Enter to apply selected path",
                True,
                Colors.LIGHT_GRAY,
            )
            self.screen.blit(hint, (pa_x, rects["preview_area"].bottom - 18))

        elif self.config_music_preview is None:
            hint = self.small_font.render(
                "Preview will show a small summary of files and sample audio files in the selected folder.",
                True,
                Colors.LIGHT_GRAY,
            )
            self.screen.blit(hint, (pa_x, pa_y))
        else:
            res = self.config_music_preview
            lines = [
                f"Total files (top-level & first few subfolders): {res.get('total_files',0)}",
                f"Audio files found (top-level & previews): {res.get('audio_files',0)}",
                f"Total size: {res.get('total_size_bytes',0)} bytes",
            ]
            for i, ln in enumerate(lines):
                s = self.small_font.render(ln, True, Colors.LIGHT_GRAY)
                self.screen.blit(s, (pa_x, pa_y + i * 20))
            # Sample files list
            sample_y = pa_y + len(lines) * 20 + 8
            header = self.small_font.render("Sample files:", True, Colors.YELLOW)
            self.screen.blit(header, (pa_x, sample_y))
            for i, fn in enumerate(res.get("sample_files", [])[:10]):
                s = self.small_font.render(f"  - {fn}", True, Colors.LIGHT_GRAY)
                self.screen.blit(s, (pa_x + 8, sample_y + 18 + i * 18))

    def draw(self) -> None:
        """Draw the UI"""
        if self.config_screen_open:
            self.draw_config_screen()
        elif self.screen_mode == "equalizer":
            self.draw_equalizer_screen()
        else:
            self.draw_main_screen()

        # Optional on-screen font diagnostic overlay (disabled by default).
        # Turn on by setting config key 'debug_font_overlay' to True or
        # set environment variable JBOX_DEBUG_FONT=1 for quick local testing.
        try:
            dbg = bool(self.config.get("debug_font_overlay", False)) or os.getenv("JBOX_DEBUG_FONT")
        except Exception:
            dbg = bool(os.getenv("JBOX_DEBUG_FONT"))

        if dbg:
            try:
                self._draw_font_debug_overlay()
            except Exception:
                pass

    def _draw_font_debug_overlay(self) -> None:
        """Draw a small overlay showing font backends, measured heights and
        sample bounding boxes so clipping issues are visible on-screen.
        This overlay is intentionally minimal and only enabled for debugging.
        """
        overlay_x = 12
        overlay_y = 12
        pad = 6
        bg_w = 420
        # Background box
        bl = pygame.Rect(overlay_x, overlay_y, bg_w, 12 + (len(("small_font","medium_font","large_font","tiny_font")) * 36))
        s = pygame.Surface((bl.width, bl.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (bl.x, bl.y))

        info_y = overlay_y + 8
        # Header
        head = self.small_font.render("Font diagnostics (overlay)", True, Colors.YELLOW)
        self.screen.blit(head, (overlay_x + pad, info_y))
        info_y += head.get_height() + 6

        fonts = ["small_font", "medium_font", "large_font", "tiny_font"]
        for name in fonts:
            f = getattr(self, name, None)
            if f is None:
                continue
            try:
                fh = f.get_height()
            except Exception:
                fh = "ERR"
            try:
                sample = f.render("Hgqyp", True, Colors.WHITE)
                sh = sample.get_height()
            except Exception:
                sample = None
                sh = "ERR"

            label = f"{name}: backend={getattr(f, '__class__').__name__} get_h={fh} surf_h={sh}"
            row = self.tiny_font.render(label, True, Colors.LIGHT_GRAY)
            self.screen.blit(row, (overlay_x + pad, info_y))

            # draw sample box on the right
            sx = overlay_x + bg_w - 140
            try:
                box = pygame.Rect(sx, info_y, 120, int(fh) if isinstance(fh, int) else 18)
            except Exception:
                box = pygame.Rect(sx, info_y, 120, 18)
            pygame.draw.rect(self.screen, Colors.GRAY, box)
            pygame.draw.rect(self.screen, Colors.WHITE, box, 1)

            if sample is not None:
                # center sample inside box
                spos = sample.get_rect(center=box.center)
                self.screen.blit(sample, spos)
                # outline sample bounds in red so clipping is obvious
                srect = pygame.Rect(spos.x, spos.y, sample.get_width(), sample.get_height())
                pygame.draw.rect(self.screen, (255, 64, 64), srect, 1)

            info_y += row.get_height() + 8

    def draw_equalizer_screen(self) -> None:
        """Draw the full-screen equalizer adjustment UI with centered layout"""
        # Use cached background for performance (like main screen)
        background = self.get_cached_background()
        self.screen.blit(background, (0, 0))

        # Calculate centered equalizer layout
        band_names = ["60 Hz", "250 Hz", "1 kHz", "4 kHz", "16 kHz"]
        spacing = 150
        slider_height = 300
        slider_width = 30

        # Calculate total width needed for sliders
        total_slider_width = (len(band_names) - 1) * spacing + slider_width

        # Calculate equalizer box dimensions
        eq_box_padding = 40
        eq_box_width = total_slider_width + (eq_box_padding * 2)
        eq_box_height = (
            520  # Reduced height to minimize dead space below preset buttons
        )

        # Center the equalizer box on screen
        eq_box_x = (self.width - eq_box_width) // 2
        eq_box_y = (self.height - eq_box_height) // 2

        # Draw semi-transparent black background box
        eq_background = pygame.Surface((eq_box_width, eq_box_height))
        eq_background.set_alpha(int(255 * 0.75))  # 75% opacity
        eq_background.fill((0, 0, 0))  # Black
        self.screen.blit(eq_background, (eq_box_x, eq_box_y))

        # Calculate centered positions within the box
        start_x = eq_box_x + eq_box_padding
        title_y = eq_box_y + 20
        instructions_y = title_y + 35
        slider_top = instructions_y + 50
        preset_y = slider_top + slider_height + 60

        # Title centered in the box
        title = self.large_font.render("Equalizer", True, self.text_color())
        title_rect = title.get_rect(center=(eq_box_x + eq_box_width // 2, title_y))
        self.screen.blit(title, title_rect)

        # Instructions centered in the box
        instructions = self.small_font.render(
            "Adjust gains, apply preset, then Save or Back", True, Colors.LIGHT_GRAY
        )
        instructions_rect = instructions.get_rect(
            center=(eq_box_x + eq_box_width // 2, instructions_y)
        )
        self.screen.blit(instructions, instructions_rect)

        # Draw each vertical slider with label & value
        for i, (slider, name) in enumerate(zip(self.eq_sliders, band_names)):
            slider.x = start_x + i * spacing
            slider.y = slider_top
            slider.height = slider_height
            slider.draw(
                self.screen,
                self.small_font,
                track_color=Colors.GRAY,
                knob_color=Colors.BLUE,
                fill_color=Colors.BLUE,
            )

            # Frequency label (keep these - 60 Hz, 250 Hz, etc.)
            label = self.small_font.render(name, True, Colors.WHITE)
            label_rect = label.get_rect(
                center=(slider.x + slider.width // 2, slider_top - 25)
            )
            self.screen.blit(label, label_rect)

            # Value
            gain = slider.get_value()
            val_color = (
                Colors.GREEN
                if gain > 0
                else (Colors.RED if gain < 0 else Colors.YELLOW)
            )
            val_text = self.small_font.render(f"{gain:.1f} dB", True, val_color)
            val_rect = val_text.get_rect(
                center=(slider.x + slider.width // 2, slider_top + slider_height + 15)
            )
            self.screen.blit(val_text, val_rect)

        # Update and draw preset buttons - center them in the box
        preset_start_x = (
            eq_box_x + (eq_box_width - (len(self.eq_preset_buttons) * 140 - 10)) // 2
        )
        for i, (name, btn) in enumerate(self.eq_preset_buttons):
            btn.rect.x = preset_start_x + i * 140
            btn.rect.y = preset_y
            btn.draw(self.screen, self.small_font)

        # Save / Back buttons (keep in top-right corner outside the box)
        self.eq_save_button.rect.x = self.width - 260
        self.eq_back_button.rect.x = self.width - 140
        self.eq_save_button.rect.y = 30
        self.eq_back_button.rect.y = 30
        self.eq_save_button.draw(self.screen, self.small_font)
        self.eq_back_button.draw(self.screen, self.small_font)

    def draw_main_screen(self) -> None:
        """Draw the main playbook screen with 3-column 2-row layout"""
        # Always use cached background for consistent rendering
        background = self.get_cached_background()
        self.screen.blit(background, (0, 0))

        # Track changes for potential future optimizations
        current_volume = self.player.get_volume()
        current_track = (
            self.player.get_current_track_info()
            if self.player.is_music_playing()
            else None
        )
        self._last_volume = current_volume
        self._last_track_info = current_track

        # Draw title at top header area with overlay
        text_y = self.header_height // 2 + 2
        self.draw_top_text_overlay(text_y)
        title = self.get_cached_text("JukeBox", self.large_font, self.text_color())
        title_rect = title.get_rect(center=(self.width // 2, text_y))
        self.screen.blit(title, title_rect)

        # Auto-scroll update will happen later in the frame (after we
        # compute album card rects) so we can correctly compute visible
        # tracks per-card. We set a transient attribute here which will
        # be populated later in the frame before the update call.
        # (placeholder; actual update happens once card rectangles are known)
        pass

        # Top controls layout (volume slider left, playback buttons centered, config button right)
        controls_margin_top = (
            self.header_height + 20
        )  # Increased margin to avoid title bar overlap
        button_height = 50  # Match square button size
        media_button_size = 50  # Square buttons
        spacing = 12
        # Volume slider positioning
        volume_label = self.small_font.render("Volume", True, self.text_color())
        self.screen.blit(volume_label, (self.margin, controls_margin_top + 2))

        self.volume_slider.x = self.margin
        self.volume_slider.y = controls_margin_top + 25  # Adjusted for increased margin
        self.volume_slider.width = 220
        self.volume_slider.height = 20
        # Draw a semi-transparent black box behind the volume slider to
        # improve contrast (50% opacity). This sits behind the slider and
        # does not affect interaction with the slider itself.
        try:
            # Include the volume label above the slider in the overlay so the
            # label and slider are visible against busy backgrounds.
            label_h = self.small_font.get_height()
            vol_overlay_w = self.volume_slider.width + 20
            # Top padding: include previous 6px + label height + 6px spacing
            top_extra = label_h + 12
            # Extend downward by 10px to give the slider more breathing room
            vol_overlay_h = self.volume_slider.height + 12 + top_extra + 10
            vol_overlay_surf = pygame.Surface((vol_overlay_w, vol_overlay_h), pygame.SRCALPHA)
            vol_overlay_surf.fill((0, 0, 0, int(255 * 0.5)))
            vol_overlay_x = self.volume_slider.x - 8
            vol_overlay_y = self.volume_slider.y - top_extra
            self.screen.blit(vol_overlay_surf, (vol_overlay_x, vol_overlay_y))
        except Exception:
            pass

        self.volume_slider.draw(
            self.screen,
            self.small_font,
            track_color=Colors.GRAY,
            knob_color=Colors.GREEN,
            fill_color=Colors.GREEN,
        )
        # Playback buttons centering
        col_width = (self.width - self.margin * 4) // 3
        col2_x = self.margin * 2 + col_width
        center_x = col2_x + (col_width // 2)
        buttons_y = controls_margin_top + 20  # Adjusted for increased margin
        # Use actual button widths to prevent overlap
        bw_play = self.play_button.rect.width
        bw_pause = self.pause_button.rect.width
        bw_stop = self.stop_button.rect.width
        total_w = bw_play + bw_pause + bw_stop + spacing * 2
        start_x = center_x - total_w // 2
        self.play_button.rect.x = start_x
        self.play_button.rect.y = buttons_y
        self.pause_button.rect.x = self.play_button.rect.x + bw_play + spacing
        self.pause_button.rect.y = buttons_y
        self.stop_button.rect.x = self.pause_button.rect.x + bw_pause + spacing
        self.stop_button.rect.y = buttons_y
        if self.show_top_media_controls:
            self.play_button.draw(self.screen, self.small_font)
            self.pause_button.draw(self.screen, self.small_font)
            self.stop_button.draw(self.screen, self.small_font)
        # Exit and Config buttons at top-right (exit flush to margin, config to left)
        self.exit_button.rect.x = self.width - self.margin - media_button_size
        self.exit_button.rect.y = controls_margin_top + 15
        self.exit_button.draw(self.screen, self.small_font)

        # Place config button to the left of exit button
        self.config_button.rect.x = self.exit_button.rect.x - media_button_size - spacing
        self.config_button.rect.y = controls_margin_top + 15
        self.config_button.draw(self.screen, self.small_font)

        # Determine start of album content area below controls
        content_top = buttons_y + button_height + 25

        # Get albums for display
        albums = self.library.get_albums()

        # Handle empty library
        if len(albums) == 0:
            # Draw empty library message
            empty_msg = self.medium_font.render("No albums found", True, self.accent_color())
            empty_msg_rect = empty_msg.get_rect(
                center=(self.width // 2, self.height // 2 - 60)
            )
            self.screen.blit(empty_msg, empty_msg_rect)

            hint_msg = self.small_font.render(
                "Add music files to the 'music' directory and use Config > Rescan",
                True,
                Colors.LIGHT_GRAY,
            )
            hint_msg_rect = hint_msg.get_rect(
                center=(self.width // 2, self.height // 2)
            )
            self.screen.blit(hint_msg, hint_msg_rect)

            # Top controls already drawn above; avoid duplicate buttons

            # Draw side navigation buttons
            self.left_nav_button.draw(self.screen, self.small_font)
            self.right_nav_button.draw(self.screen, self.small_font)

            # Draw instructions at very bottom with overlay
            text_y = self.height - 20  # 20 pixels from bottom
            self.draw_bottom_text_overlay(text_y)
            instructions = self.small_font.render(
                "C: Config | Space: Play/Pause | ↑↓: Volume", True, Colors.WHITE
            )
            self.screen.blit(instructions, (20, text_y))

            # If exit confirmation is open, draw the modal on top before flipping
            if getattr(self, "exit_confirm_open", False):
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.screen.blit(overlay, (0, 0))

                modal_w = 520
                modal_h = 180
                modal_x = (self.width - modal_w) // 2
                modal_y = (self.height - modal_h) // 2
                modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
                pygame.draw.rect(self.screen, Colors.WHITE, modal_rect)
                pygame.draw.rect(self.screen, Colors.GRAY, modal_rect, 3)

                msg = self.medium_font.render("Confirm Exit", True, self.text_color())
                self.screen.blit(msg, (modal_x + 20, modal_y + 18))
                body = self.small_font.render(
                    "Are you sure you want to exit the program?", True, Colors.DARK_GRAY
                )
                self.screen.blit(body, (modal_x + 20, modal_y + 60))

                self.exit_confirm_yes.rect.x = modal_x + modal_w - 260
                self.exit_confirm_yes.rect.y = modal_y + modal_h - 64
                self.exit_confirm_no.rect.x = modal_x + modal_w - 130
                self.exit_confirm_no.rect.y = modal_y + modal_h - 64
                self.exit_confirm_yes.draw(self.screen, self.small_font)
                self.exit_confirm_no.draw(self.screen, self.small_font)

            pygame.display.flip()
            return  # Exit early for empty library

        # Content area (between top controls and bottom area)
        content_height = self.height - content_top - self.bottom_area_height - 20
        if content_height < 200:
            content_height = 200

        # 3-column layout with proper justification
        total_content_width = self.width - self.margin * 4
        col1_width = int(total_content_width * 0.32)  # Left album cards: 32%
        col2_width = int(total_content_width * 0.36)  # Now playing (wider): 36%
        col3_width = int(total_content_width * 0.32)  # Right album cards: 32%

        # Left-justify left column
        col1_x = self.margin
        # Right-justify right column - align with rightmost edge of options button
        col3_x = self.width - self.margin - col3_width + 12
        # Center the now playing box between the actual left and right columns
        left_edge = col1_x + col1_width
        right_edge = col3_x
        available_space = right_edge - left_edge

        # Center the now playing box between the actual left and right columns
        # (restore the previous behavior which centers the center column
        # between the left/right album columns)
        col2_x = left_edge + (available_space - col2_width) // 2

        # Two rows within content area. Move the Now Playing row down by
        # 25px from the previous placement while keeping the selection
        # overlay visually fixed via selection_anchor_shift.
        row1_y = content_top + 10 - 15 + 25
        row2_y = row1_y + content_height // 2 + 35

        current_album_idx = None
        for i, alb in enumerate(albums):
            if alb.album_id == self.player.current_album_id:
                current_album_idx = i
                break

        if current_album_idx is None:
            current_album_idx = 0

        # Determine which albums to show in left and right columns
        # Left column: albums 1,2 | Right column: albums 3,4 (as requested)
        # Browse position shows 4 albums: position, position+1, position+2, position+3
        left_album_1 = self.browse_position  # Top left: album 1
        left_album_2 = self.browse_position + 1  # Bottom left: album 2
        right_album_1 = self.browse_position + 2  # Top right: album 3
        right_album_2 = self.browse_position + 3  # Bottom right: album 4

        # Calculate card height for hover detection
        card_h = (content_height // 2) + 15  # Half height plus extra space

        # Update hover states for album cards every frame
        mouse_pos = pygame.mouse.get_pos()
        album_cards = [
            (left_album_1, col1_x, row1_y, col1_width - 10, card_h),
            (left_album_2, col1_x, row2_y, col1_width - 10, card_h),
            (right_album_1, col3_x, row1_y, col3_width - 10, card_h),
            (right_album_2, col3_x, row2_y, col3_width - 10, card_h),
        ]
        for album_idx, card_x, card_y, card_w, card_h in album_cards:
            if album_idx >= 0 and album_idx < len(albums):
                card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
                album = albums[album_idx]
                is_hovering = card_rect.collidepoint(mouse_pos)
                self.album_card_hover_pause[album.album_id] = is_hovering

        # Provide the album card rects to the auto-scroll updater which
        # will compute visible-row counts using the exact same layout
        # rules as drawing. This ensures we don't mis-estimate visible
        # rows and accidentally skip the final tracks.
        album_card_rects = {}
        for album_idx, card_x, card_y, card_w, card_h in album_cards:
            if album_idx >= 0 and album_idx < len(albums):
                album_card_rects[album_idx] = pygame.Rect(card_x, card_y, card_w, card_h)

        # Attach transient rects for the update function, call update, then
        # remove the temporary attribute.
        self._album_card_rects_for_update = album_card_rects
        try:
            self._update_album_card_auto_scroll()
        finally:
            try:
                delattr(self, '_album_card_rects_for_update')
            except Exception:
                pass

        # LEFT COLUMN - Two albums (each taking half height)
        if len(albums) > 0:
            # Only draw if indices are valid
            if left_album_1 >= 0 and left_album_1 < len(albums):
                track_offset_1 = self.album_card_scroll_offsets.get(albums[left_album_1].album_id, 0)
                self.draw_album_card(
                    albums[left_album_1], col1_x, row1_y, col1_width - 10, card_h, track_offset_1
                )
            if left_album_2 >= 0 and left_album_2 < len(albums):
                track_offset_2 = self.album_card_scroll_offsets.get(albums[left_album_2].album_id, 0)
                self.draw_album_card(
                    albums[left_album_2], col1_x, row2_y, col1_width - 10, card_h, track_offset_2
                )

        # CENTER COLUMN - Always show Now Playing, never browsed albums (smaller now)
        current_album_obj = self.player.get_current_album()

        # Make now playing window taller in windowed mode to push down keypad
        now_playing_height_factor = (
            0.85 if self.fullscreen else 0.95
        )  # Taller in windowed mode
        now_playing_height = int(content_height * now_playing_height_factor) - 10

        if current_album_obj and self.player.is_music_playing():
            self.draw_current_album_display(
                current_album_obj, col2_x, row1_y, col2_width - 10, now_playing_height
            )
        else:
            # Show empty Now Playing box when nothing is playing
            self.draw_empty_now_playing(
                col2_x, row1_y, col2_width - 10, now_playing_height
            )

        # RIGHT COLUMN - Two albums (each taking half height)
        if len(albums) > 0:
            # Only draw if indices are valid
            if right_album_1 >= 0 and right_album_1 < len(albums):
                track_offset_3 = self.album_card_scroll_offsets.get(albums[right_album_1].album_id, 0)
                self.draw_album_card(
                    albums[right_album_1], col3_x, row1_y, col3_width - 10, card_h, track_offset_3
                )
            if right_album_2 >= 0 and right_album_2 < len(albums):
                track_offset_4 = self.album_card_scroll_offsets.get(albums[right_album_2].album_id, 0)
                self.draw_album_card(
                    albums[right_album_2], col3_x, row2_y, col3_width - 10, card_h, track_offset_4
                )

        # Credit UI placed under the two right column album cards
        try:
            # Compute a centered position within the right column
            credit_w = min(self.credit_button.rect.width, col3_width - 40)
            credit_x = col3_x + (col3_width - credit_w) // 2
            # Lower the credit button slightly to give breathing room
            credit_y = row2_y + card_h + 27  # moved down by 15px
            # Draw a semi-transparent black box behind the credit button and
            # the credits counter for visual separation.
            try:
                overlay_w = credit_w + 100  # Increased to accommodate text to the right
                overlay_h = self.credit_button.rect.height + 12
                overlay_surf = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
                overlay_surf.fill((0, 0, 0, int(255 * 0.5)))
                overlay_x = credit_x - 8
                overlay_y = credit_y - 6
                self.screen.blit(overlay_surf, (overlay_x, overlay_y))
            except Exception:
                pass

            self.credit_button.rect.x = credit_x
            self.credit_button.rect.y = credit_y
            self.credit_button.rect.width = credit_w
            self.credit_button.draw(self.screen, self.small_font)

            # Draw current credit count to the right of the button
            credits = 0
            if self.player:
                try:
                    credits = self.player.get_credits()
                except Exception:
                    credits = 0
            # Render credits count using the dedicated larger credits font
            credit_txt = self.credits_font.render(f"Credits: {credits}", True, self.accent_color())
            txt_rect = credit_txt.get_rect(midleft=(credit_x + credit_w + 10, credit_y + self.credit_button.rect.height // 2))
            self.screen.blit(credit_txt, txt_rect)
        except Exception:
            # UI drawing should never crash tests; ignore if player or layout not available
            pass

        # Draw side navigation buttons
        self.left_nav_button.draw(self.screen, self.small_font)
        self.right_nav_button.draw(self.screen, self.small_font)

        # Top controls already drawn; skip duplicate playback button drawing

        # Draw number pad in center bottom
        self.draw_number_pad_centered()

        # Draw audio controls above number pad
        self.draw_audio_controls()

        # Draw instructions at very bottom with overlay
        text_y = self.height - 20  # 20 pixels from bottom
        self.draw_bottom_text_overlay(text_y)
        instructions = self.small_font.render(
            "4-digit: Album(2) + Track(2) | C: Config | Space: Play/Pause | Alt+Enter: Fullscreen | ↑↓: Volume",
            True,
            Colors.WHITE,
        )
        self.screen.blit(instructions, (20, text_y))

        # Draw queue counter in lower right corner
        queue_count = len(self.player.queue)
        if queue_count > 0:
            queue_text = f"Queue: {queue_count} song{'s' if queue_count != 1 else ''}"
            queue_surface = self.small_font.render(queue_text, True, self.text_color())
            queue_rect = queue_surface.get_rect()
            queue_x = self.width - queue_rect.width - 20
            queue_y = text_y  # Use same y position as instructions
            self.screen.blit(queue_surface, (queue_x, queue_y))

        # If exit confirmation is open, draw modal on top of the screen (draw before final flip)
        if self.exit_confirm_open:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            modal_w = 520
            modal_h = 180
            modal_x = (self.width - modal_w) // 2
            modal_y = (self.height - modal_h) // 2
            modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
            pygame.draw.rect(self.screen, Colors.WHITE, modal_rect)
            pygame.draw.rect(self.screen, Colors.GRAY, modal_rect, 3)

            # Message
            msg = self.medium_font.render("Confirm Exit", True, self.text_color())
            self.screen.blit(msg, (modal_x + 20, modal_y + 18))
            body = self.small_font.render(
                "Are you sure you want to exit the program?", True, Colors.DARK_GRAY
            )
            self.screen.blit(body, (modal_x + 20, modal_y + 60))

            # Position Yes/No buttons
            self.exit_confirm_yes.rect.x = modal_x + modal_w - 260
            self.exit_confirm_yes.rect.y = modal_y + modal_h - 64
            self.exit_confirm_no.rect.x = modal_x + modal_w - 130
            self.exit_confirm_no.rect.y = modal_y + modal_h - 64
            self.exit_confirm_yes.draw(self.screen, self.small_font)
            self.exit_confirm_no.draw(self.screen, self.small_font)

        # Final flip once per frame
        pygame.display.flip()

    def _update_album_card_auto_scroll(self) -> None:
        """Update auto-scrolling for album cards that have more tracks than can be displayed"""
        if not self.album_card_auto_scroll_enabled:
            return

        # Check if we have a valid player and library
        if not self.player or not hasattr(self.player, 'library') or not self.player.library:
            return

        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        # debug: show whether we have rects and configured speed
        # No debug output here (normal runtime)
        albums = self.player.library.get_albums() if self.player and self.player.library else []

        if not albums:
            return

        # Calculate how many tracks fit in a card (same logic as in draw_album_card)
        compact = bool(self.config.get("compact_track_list", True))
        density = float(self.config.get("track_list_density", 0.8))
        density = max(0.5, min(1.0, density))
        if self.fullscreen:
            base_line = 16 if compact else 18
        else:
            base_line = 10 if compact else 12
        track_line_height = max(6, int(base_line * density))

        # Use 8 as the minimum number of tracks to trigger auto-scroll
        scroll_trigger_threshold = 8

        # _update_album_card_auto_scroll can be called with a mapping of
        # album indices to card rectangles (so we can compute visible rows
        # precisely per-card). If none are provided, fall back to a rough
        # estimate based on overall layout.
        # album_card_rects should be a dict: {album_idx: pygame.Rect}
        passed_rects = getattr(self, '_album_card_rects_for_update', None)

        # Get current album indices
        left_album_1 = self.browse_position
        left_album_2 = self.browse_position + 1
        right_album_1 = self.browse_position + 2
        right_album_2 = self.browse_position + 3

        current_album_indices = [left_album_1, left_album_2, right_album_1, right_album_2]

        for album_idx in current_album_indices:
            if album_idx >= 0 and album_idx < len(albums):
                album = albums[album_idx]
                album_id = album.album_id

                # Only auto-scroll if album has more than the configured
                # minimal trigger (8+ tracks). We compute max_tracks_visible
                # per-card when we have card rects available so scrolling
                # can't skip final rows due to mismatched estimates.
                if len(album.tracks) <= scroll_trigger_threshold:
                    continue

                # Compute visible rows for this album card. Use the passed
                # rects mapping if available; otherwise fall back to the
                # rough layout guess computed earlier.
                if passed_rects and album_idx in passed_rects:
                    rect = passed_rects[album_idx]
                    max_tracks_visible = self._compute_visible_tracks_for_card(album, rect.x, rect.y, rect.width, rect.height, track_line_height)
                else:
                    # fall back to previous rough estimate
                    max_tracks_visible = max(1, ( (self.height - (self.header_height + 20 + 50 + 25) - self.bottom_area_height - 20) // 2 + 15 - 80) // track_line_height)

                if len(album.tracks) <= max_tracks_visible:
                    # If there are more tracks than our configured trigger
                    # but they all fit (per-card), we still allow scrolling
                    # to reveal any rows that might be clipped (this is a
                    # safety measure), so do not continue here unless there
                    # are truly no extra rows to show.
                    # However if max_tracks_visible >= len(album.tracks) and
                    # the computed visible tracks equals the total tracks,
                    # there's nothing to scroll — continue.
                    if max_tracks_visible >= len(album.tracks):
                        continue

                # Skip if user is hovering over this album card
                if self.album_card_hover_pause.get(album_id, False):
                    continue

                # Ensure we persist per-album state so the timer counts across
                # frames instead of defaulting to "now" every time which blocks
                # the countdown (previous bug: get(..., current_time) effectively
                # reset the timer on every frame and prevented any scrolls).
                current_offset = self.album_card_scroll_offsets.get(album_id, 0)

                # Initialize timer if missing so the count starts now and will
                # advance once the configured speed elapses.
                if album_id not in self.album_card_auto_scroll_timers:
                    # Persist the initial value so it's not re-created each frame
                    self.album_card_auto_scroll_timers[album_id] = current_time
                last_scroll_time = self.album_card_auto_scroll_timers[album_id]

                # Initialize direction if necessary (1=down, -1=up)
                if album_id not in self.album_card_auto_scroll_directions:
                    self.album_card_auto_scroll_directions[album_id] = 1
                scroll_direction = self.album_card_auto_scroll_directions[album_id]

                # Check if it's time to scroll
                if current_time - last_scroll_time >= self.album_card_auto_scroll_speed:
                    # Calculate new offset
                    new_offset = current_offset + scroll_direction

                    # Reverse direction at boundaries
                    # Bound the offset so the final page shows the last
                    # `max_tracks_visible` tracks (avoid skipping the final
                    # rows when visible area differs from our threshold).
                    max_offset = max(0, len(album.tracks) - max_tracks_visible)
                    if new_offset >= max_offset:
                        new_offset = max_offset
                        scroll_direction = -1  # Start scrolling up
                    elif new_offset <= 0:
                        new_offset = 0
                        scroll_direction = 1  # Start scrolling down

                    # Update scroll state
                    self.album_card_scroll_offsets[album_id] = max(0, new_offset)
                    self.album_card_auto_scroll_timers[album_id] = current_time
                    self.album_card_auto_scroll_directions[album_id] = scroll_direction
                    self._needs_full_redraw = True
                    # Debug output to allow quick verification during manual
                    # checks; this will be removed/cleaned up if requested.
                    # no debug prints in production mode
                    # Small debug print to verify scrolling happens during test runs
                    # debug print removed after verification

    def draw_album_card(self, album, x: int, y: int, width: int, height: int, track_offset: int = 0) -> None:
        """Draw a card displaying album information with square art on right and text on left"""
        card_height = height
        card_rect = pygame.Rect(x, y, width, card_height)

        # Draw card background
        pygame.draw.rect(self.screen, Colors.WHITE, card_rect)
        pygame.draw.rect(self.screen, Colors.GRAY, card_rect, 2)

        # Card padding
        padding = 8
        content_x = x + padding
        content_y = y + padding
        content_width = width - padding * 2
        content_height = card_height - padding * 2

        # Calculate square album art size (right side) - larger size
        art_size = min(
            content_height - 10, content_width // 2.2
        )  # About half width, square aspect
        art_x = x + width - padding - art_size
        art_y = content_y
        art_rect = pygame.Rect(art_x, art_y, art_size, art_size)

        # Text area (left side, excluding larger art area)
        text_width = content_width - art_size - padding - 5
        text_x = content_x
        text_y = content_y

        # Draw album art (square, right-justified)
        art_img = self.get_album_art(album)
        if art_img:
            # Scale to square maintaining aspect ratio
            scaled = pygame.transform.smoothscale(art_img, (art_size, art_size))
            self.screen.blit(scaled, art_rect)
            # Overlay album id tag with white border
            album_num_text = self.large_font.render(f"{album.album_id:02d}", True, Colors.BLACK)
            text_rect = album_num_text.get_rect()
            # Create white border background
            border_padding = 4
            border_rect = pygame.Rect(
                art_rect.x + 3 - border_padding,
                art_rect.y + 3 - border_padding,
                text_rect.width + border_padding * 2,
                text_rect.height + border_padding * 2,
            )
            pygame.draw.rect(self.screen, Colors.WHITE, border_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, border_rect, 2)
            self.screen.blit(album_num_text, (art_rect.x + 3, art_rect.y + 3))
        else:
            pygame.draw.rect(self.screen, Colors.GRAY, art_rect)
            album_num_text = self.large_font.render(f"{album.album_id:02d}", True, Colors.BLACK)
            # Position album number overlay consistently in the top-left of
            # the album-art area. If the album is a placeholder (invalid)
            # we still keep the small number box in the art area, but the
            # textual content (artist/title) will be moved to the left side
            # of the card.
            album_num_x = art_rect.x + 3
            album_num_y = art_rect.y + 3

            # For textual content we use text_x/text_y; default to the
            # art area origin but placeholders will render text on the
            # left content column.
            text_x = album_num_x
            text_y = album_num_y
            if not getattr(album, "is_valid", True):
                text_x = content_x
                text_y = content_y

            # Add white border around the number box and then blit the
            # album number at the album-art origin (not the textual origin)
            border_padding = 4  # Match the padding used for album art overlay
            border_rect = pygame.Rect(
                album_num_x - border_padding,
                album_num_y - border_padding,
                album_num_text.get_width() + border_padding * 2,
                album_num_text.get_height() + border_padding * 2,
            )
            pygame.draw.rect(self.screen, Colors.WHITE, border_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, border_rect, 2)
            self.screen.blit(album_num_text, (album_num_x, album_num_y))

        # Text content (left side) - we'll use measured font heights for
        # vertical spacing instead of fixed numeric line heights. This
        # prevents overlap/clipping when rendered surfaces are taller
        # than the previous fixed values.
        current_y = text_y

        # Album ID and artist - use larger font in fullscreen with text wrapping
        artist_font = self.large_font if self.fullscreen else self.medium_font
        artist_text = album.artist

        # Wrap artist name if over 16 characters, only at word boundaries
        if len(artist_text) > 16:
            # Find the best place to wrap at or before 16 characters
            wrap_point = 16
            # Look for the last space at or before position 16
            last_space = artist_text.rfind(" ", 0, wrap_point + 1)
            if last_space > 0:
                artist_line1 = artist_text[:last_space]
                artist_line2 = artist_text[
                    last_space + 1 : last_space + 17
                ]  # Up to 16 more chars after the space
            else:
                # No space found, fall back to character-based wrapping
                artist_line1 = artist_text[:16]
                artist_line2 = artist_text[16:32]
        else:
            artist_line1 = artist_text
            artist_line2 = ""

        # Draw first line of artist
        artist_text1 = artist_font.render(artist_line1, True, self.artist_text_color())
        artist_rect = artist_text1.get_rect()
        artist_bg_rect = pygame.Rect(
            text_x - 2, current_y - 2, artist_rect.width + 4, artist_rect.height + 4
        )
        # Create transparent surface for padding
        padding_surface = pygame.Surface(
            (artist_rect.width + 4, artist_rect.height + 4), pygame.SRCALPHA
        )
        padding_surface.fill((0, 0, 0, 0))  # Fully transparent
        self.screen.blit(padding_surface, (text_x - 2, current_y - 2))
        self.screen.blit(artist_text1, (text_x, current_y))
        current_y += artist_rect.height

        # Draw second line of artist if needed
        if artist_line2:
            current_y += 2  # Add 2px spacing between artist lines
            artist_text2 = artist_font.render(artist_line2, True, self.artist_text_color())
            artist_rect2 = artist_text2.get_rect()
            self.screen.blit(artist_text2, (text_x, current_y))
            current_y += artist_rect2.height

        spacing_after_artist = 6 if self.fullscreen else 4
        current_y += (
            spacing_after_artist + 4
        )  # Add extra space after artist name + 4px between artist and album

        # Album title - use larger font in fullscreen with text wrapping (only wrap if not fullscreen)
        album_font = self.medium_font if self.fullscreen else self.small_medium_font
        album_title = album.title

        # Handle album title display based on mode
        if self.fullscreen:
            # In fullscreen, cut off at first space after 28 characters
            if len(album_title) > 28:
                # Find the first space at or after position 28
                first_space = album_title.find(" ", 28)
                if first_space > 0:
                    album_line1 = album_title[:first_space]
                else:
                    # No space found, just truncate at 28
                    album_line1 = album_title[:28]
            else:
                album_line1 = album_title
            album_line2 = ""
        else:
            # In windowed mode, wrap at 14 characters
            if len(album_title) > 14:
                album_line1 = album_title[:14]
                album_line2 = album_title[14:28]  # Max 14 more chars for second line
            else:
                album_line1 = album_title
                album_line2 = ""

        # Draw first line of album title
        album_text1 = album_font.render(album_line1, True, self.album_text_color())
        album_rect1 = album_text1.get_rect()
        self.screen.blit(album_text1, (text_x, current_y))
        current_y += album_rect1.height

        # Draw second line of album title if needed
        if album_line2:
            album_text2 = album_font.render(album_line2, True, self.album_text_color())
            album_rect2 = album_text2.get_rect()
            self.screen.blit(album_text2, (text_x, current_y))
            current_y += album_rect2.height

        spacing_after_album = 4 if self.fullscreen else 2
        current_y += spacing_after_album

        # Track count - use larger font in fullscreen
        count_font = self.small_medium_font if self.fullscreen else self.tiny_font
        track_count_text = count_font.render(
            f"{len(album.tracks)} tracks", True, Colors.BLUE
        )
        self.screen.blit(track_count_text, (text_x, current_y))
        spacing_after_count = 5 if self.fullscreen else 3
        current_y += track_count_text.get_height() + spacing_after_count

        # Show all tracks that fit - line-height depends on fullscreen and compact setting
        compact = bool(self.config.get("compact_track_list", True))
        # Read density multiplier from config (0.5 to 1.0 where smaller => denser)
        density = float(self.config.get("track_list_density", 0.8))
        density = max(0.5, min(1.0, density))
        # Base line heights (px) depending on mode and compact flag, then scale by density
        if self.fullscreen:
            base_line = 16 if compact else 18
        else:
            base_line = 10 if compact else 12
        track_line_height = max(6, int(base_line * density))
        max_tracks = min(
            len(album.tracks),
            (content_height - (current_y - text_y) - 10) // track_line_height,
        )
        # Local debug flag for per-card bounding visualization (respects same
        # debug flag as the overlay). This visual aid helps reproduce
        # clipping in-situ on the album cards themselves.
        try:
            dbg_card = bool(self.config.get("debug_font_overlay", False)) or os.getenv("JBOX_DEBUG_FONT")
        except Exception:
            dbg_card = bool(os.getenv("JBOX_DEBUG_FONT"))

        for i, track in enumerate(album.tracks[track_offset:track_offset + max_tracks]):
            # Render the track text first so we can accurately measure the
            # real surface height. Previously the code tested against a
            # pre-computed numeric line height and then blitted a potentially
            # taller surface which could overflow the card and get clipped.
            # Measure and require the full height to fit before drawing.
            # Truncate track title to fit width for the rendered surface.
                # Truncate track title to fit. Allow slightly more characters
                # by assuming roughly 6px per character.
                max_chars = max(15, int(text_width // 6))  # Ensure integer
                title = track["title"][:max_chars]
                if len(track["title"]) > max_chars:
                    title += "..."
                # Derive an appropriate font size based on density and compact state
                try:
                    if self.fullscreen:
                        base_font_size = 12 if compact else max(12, self.small_font.get_height())
                    else:
                        base_font_size = 9 if compact else max(10, self.tiny_font.get_height())
                    font_size = max(8, int(base_font_size * density))

                    # Prefer the bundled font file for on-the-fly track fonts
                    # when pygame.font.Font is available. Fall back to SysFont
                    # for environments that don't support loading from file.
                    if getattr(self, 'bundled_font_path', None) and os.path.exists(self.bundled_font_path):
                        track_font = pygame.font.Font(self.bundled_font_path, font_size)
                    else:
                        track_font = pygame.font.SysFont("Arial", font_size)
                except Exception:
                    # Fall back to pre-created fonts on any error
                    if self.fullscreen:
                        track_font = self.track_list_font_fullscreen if compact else self.small_font
                    else:
                        track_font = self.track_list_font if compact else self.tiny_font
                track_text = track_font.render(f"{i+1+track_offset:2d}. {title}", True, self.track_text_color())

                track_h = track_text.get_height()
                # Add a small runtime safety padding to the slot height so
                # that rounding or compositor behavior (eg Wayland) which
                # might drop the final pixel row does not visually clip
                # glyph descenders. A 1-2px pad is inexpensive and prevents
                # intermittent single-row clipping seen on some systems.
                safety_pad = 2
                needed = max(track_line_height, track_h) + safety_pad

                # Compute a conservative inner bottom bound for where
                # textual content may be drawn. The card border is drawn
                # using a thickness of 2px which occupies space inside the
                # rect — ensure our fitting check accounts for that to avoid
                # drawing under the border where glyphs could be clipped.
                border_thickness = 2
                # Add an additional final pad to the inner bottom bound.
                # This small guard helps prevent compositor/rounding issues
                # (eg Wayland fractional pixel rounding) from trimming the
                # final rows of glyphs when displayed on-screen. Raised
                # from 2px to 4px as a conservative fix for Wayland edge cases.
                final_pad = 4
                allowed_bottom = y + card_height - padding - border_thickness - final_pad

                # Ensure the full rendered surface fits inside the card
                # area before blitting. If it won't fit, stop rendering
                # further tracks so we never create a partly visible line.
                if current_y + needed > allowed_bottom:
                    if dbg_card:
                        try:
                            print(
                                f"[FONTDBG] album={getattr(album,'album_id',None)} i={i} current_y={current_y} needed={needed} allowed_bottom={allowed_bottom} -> SKIP (final_pad={final_pad})"
                            )
                        except Exception:
                            pass
                    break

                # Draw the track text and optional debug bounding box
                self.screen.blit(track_text, (text_x + 5, current_y))
                if dbg_card:
                    try:
                        # Outline the actual rendered surface in red and
                        # the expected 'slot' in yellow so any mismatch is
                        # immediately obvious in screenshots.
                        surf_rect = pygame.Rect(text_x + 5, current_y, track_text.get_width(), track_h)
                        slot_rect = pygame.Rect(text_x + 5, current_y, int(text_width), needed)
                        pygame.draw.rect(self.screen, (255, 64, 64), surf_rect, 1)
                        pygame.draw.rect(self.screen, (255, 200, 64), slot_rect, 1)
                    except Exception:
                        pass
                # When debugging print the bounds used for the slot so we can
                # capture and correlate with screenshots/logs in Wayland.
                if dbg_card:
                    try:
                        print(
                            f"[FONTDBG] album={getattr(album,'album_id',None)} i={i} blit_y={current_y} track_h={track_h} slot_h={needed} (incl pad={safety_pad}) allowed_bottom={allowed_bottom}"
                        )
                    except Exception:
                        pass

                # If debug overlay is on, optionally export each track render
                # surface into a png so the developer/user can inspect the
                # exact pixels produced by the font backend before composition
                # (helps rule out renderer vs compositor issues).
                if dbg_card:
                    try:
                        # Write files into the repo top-level jbox_debug/ folder
                        import pathlib

                        out_dir = pathlib.Path(os.path.dirname(__file__)).parent / "jbox_debug"
                        out_dir.mkdir(parents=True, exist_ok=True)
                        fname = out_dir / f"album_{getattr(album,'album_id', 'unk')}_track_{i}.png"
                        # Save surfaces when track_text is a pygame Surface
                        if hasattr(track_text, "get_width"):
                            try:
                                # Some environments / build options do not support
                                # saving SRCALPHA surfaces directly. Convert to an
                                # opaque RGB surface before saving to ensure the
                                # operation succeeds universally.
                                to_save = track_text
                                try:
                                    flags = getattr(track_text, 'get_flags', None)
                                    has_alpha = False
                                    if flags is not None:
                                        has_alpha = bool(track_text.get_flags() & pygame.SRCALPHA)
                                    if has_alpha:
                                        w, h = track_text.get_size()
                                        conv = pygame.Surface((w, h))
                                        # Use white background for exported debugging images
                                        conv.fill((255, 255, 255))
                                        conv.blit(track_text, (0, 0))
                                        to_save = conv

                                except Exception:
                                    to_save = track_text

                                try:
                                    # Try a PIL-backed save which works even when
                                    # pygame.build lacks full image write support.
                                    from PIL import Image

                                    raw = pygame.image.tostring(to_save, "RGBA")
                                    im = Image.frombytes("RGBA", to_save.get_size(), raw)
                                    # Convert to RGB (writeable) to avoid extended
                                    # format issues and keep compatibility.
                                    im = im.convert("RGB")
                                    im.save(str(fname))
                                    print(f"[FONTDBG] saved surface (PIL) to: {fname}")
                                except Exception:
                                    # Fall back to pygame.save if PIL unavailable
                                    pygame.image.save(to_save, str(fname))
                                    print(f"[FONTDBG] saved surface (pygame) to: {fname}")
                            except Exception as e:
                                print(f"[FONTDBG] failed to save surface {fname}: {e}")
                    except Exception:
                        pass

                # Advance by whichever is larger: our computed line height
                # (based on density) or the actual rendered text height.
                current_y += needed

        # Add scroll indicators if there are more tracks above or below
        # Trigger indicators for albums with more than our configured
        # auto-scroll trigger (8+) so users see the arrows when albums are
        # considered for auto-scroll.
        if len(album.tracks) > 8:
            indicator_font = self.tiny_font
            indicator_color = self.accent_color()

            # Up arrow if there are tracks above current view
            if track_offset > 0:
                up_text = indicator_font.render("▲", True, indicator_color)
                up_y = current_y + 8
                if up_y + up_text.get_height() <= allowed_bottom:
                    up_rect = up_text.get_rect(center=(text_x + text_width // 2, up_y))
                    self.screen.blit(up_text, up_rect)
                    current_y += up_text.get_height() + 4

            # Down arrow if there are tracks below current view
            if track_offset + max_tracks < len(album.tracks):
                down_text = indicator_font.render("▼", True, indicator_color)
                down_y = current_y + 8
                if down_y + down_text.get_height() <= allowed_bottom:
                    down_rect = down_text.get_rect(center=(text_x + text_width // 2, down_y))
                    self.screen.blit(down_text, down_rect)

        # If debug overlay is enabled, capture the full card rectangle from
        # the screen and write it to jbox_debug/ so we can verify whether
        # the card as finally composed on the display still contains the
        # complete text rows (helps determine if clipping happens during
        # final blit/composition or earlier in the renderer).
        if dbg_card:
            try:
                import pathlib

                out_dir = pathlib.Path(os.path.dirname(__file__)).parent / "jbox_debug"
                out_dir.mkdir(parents=True, exist_ok=True)
                fname = out_dir / f"album_{getattr(album,'album_id','unk')}_card.png"
                # Extract the drawn card area from the main screen and save
                # as an image for later inspection.
                # Use a copy of the subsurface to avoid issues with live
                # surface references.
                try:
                    card_surf = self.screen.subsurface(card_rect).copy()
                except Exception:
                    card_surf = pygame.Surface((card_rect.width, card_rect.height))
                    card_surf.blit(self.screen, (0, 0), card_rect)

                try:
                    from PIL import Image

                    raw = pygame.image.tostring(card_surf, "RGBA")
                    im = Image.frombytes("RGBA", card_surf.get_size(), raw)
                    im = im.convert("RGB")
                    im.save(str(fname))
                    print(f"[FONTDBG] saved card surface (PIL) to: {fname}")
                except Exception:
                    pygame.image.save(card_surf, str(fname))
                    print(f"[FONTDBG] saved card surface (pygame) to: {fname}")
            except Exception:
                pass

    def draw_empty_now_playing(self, x: int, y: int, width: int, height: int) -> None:
        """Draw empty 'Now Playing' box when nothing is playing"""
        display_height = max(200, height)
        display_rect = pygame.Rect(x, y, width, display_height)

        # Draw display background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, display_rect)
        pygame.draw.rect(self.screen, Colors.YELLOW, display_rect, 3)

        # Draw the 4-digit selection display above the Now Playing box.
        # Use the dedicated selection font (72pt) in red with a bounding box.
        # Show the currently playing selection if available, otherwise show
        # the typed buffer (or dashes).
        if getattr(self, 'last_track_info', None):
            at = self.last_track_info
            try:
                album_id = int(at.get('album_id', 0))
                track_idx = int(at.get('track_index', 0))
                display_sel = f"{album_id:02d}{track_idx+1:02d}"
            except Exception:
                display_sel = self.selection_buffer[:4].ljust(4, "-") if self.selection_mode else "----"
        else:
            display_sel = self.selection_buffer[:4].ljust(4, "-") if self.selection_mode else "----"
        try:
            sel_font = getattr(self, 'selection_digits_font', self.medium_font)
            sel_color = Colors.RED
            sel_text = sel_font.render(display_sel, True, sel_color)
            offset = int(sel_text.get_height() / 2) + 12
            # Center the selection display horizontally with the main window
            # (aligns with top controls like volume/config/exit)
            # If a custom center is set, use that to allow independent
            # placement of the selection overlay; otherwise center relative
            # to the Now Playing box as before.
            if getattr(self, 'selection_center_override', None):
                cx, cy = self.selection_center_override
                sel_rect = sel_text.get_rect(center=(int(cx), int(cy)))
            else:
                # Allow keeping the selection visually fixed when the
                # Now Playing box moves by applying the anchor shift.
                shift = getattr(self, 'selection_anchor_shift', 0)
                sel_rect = sel_text.get_rect(center=(x + width // 2, y - offset - shift))
            # Draw bounding box behind the digits for clarity
            pad_x = 12
            pad_y = 8
            bg = pygame.Rect(sel_rect.x - pad_x, sel_rect.y - pad_y, sel_rect.width + pad_x * 2, sel_rect.height + pad_y * 2)
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, bg)
            # Use a red border for the selection box so it stands out from the white
            # album frames and matches the requested style
            pygame.draw.rect(self.screen, Colors.RED, bg, 2)
            self.screen.blit(sel_text, sel_rect)
            try:
                self.last_selection_draw_rect = sel_rect
                self.last_selection_bg_rect = bg
                self.last_selection_display_string = display_sel
            except Exception:
                pass
        except Exception:
            pass

        # Legacy small selection display removed — we now only show the large
        # selection digits above the Now Playing box so there is no duplicate
        # overlapping box that previously caused visual clutter.

        # Draw "Now Playing" header
        padding = 15
        content_x = x + padding
        content_y = y + padding

        label_text = self.medium_font.render("Now Playing", True, self.accent_color())
        self.screen.blit(label_text, (content_x, content_y))

        # Draw centered "Choose an album and song." message
        center_y = y + display_height // 2
        no_music_text = self.medium_font.render(
            "Choose an album and song.", True, Colors.LIGHT_GRAY
        )
        text_rect = no_music_text.get_rect(center=(x + width // 2, center_y))
        self.screen.blit(no_music_text, text_rect)

    def draw_current_album_display(
        self, album, x: int, y: int, width: int, height: int
    ) -> None:
        """Draw persistent 'Now Playing' box with only current track details.
        Does not clear when playback stops; only updates upon new playing track."""
        display_height = max(200, height)
        display_rect = pygame.Rect(x, y, width, display_height)

        # Draw display background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, display_rect)
        pygame.draw.rect(self.screen, Colors.YELLOW, display_rect, 3)

        # Draw the 4-digit selection display above the Now Playing box so
        # selection digits are centered just above the box.
        # Show the currently playing selection if available, otherwise show
        # the typed buffer (or dashes).
        if getattr(self, 'last_track_info', None):
            at = self.last_track_info
            try:
                album_id = int(at.get('album_id', 0))
                track_idx = int(at.get('track_index', 0))
                display_sel = f"{album_id:02d}{track_idx+1:02d}"
            except Exception:
                display_sel = self.selection_buffer[:4].ljust(4, "-") if self.selection_mode else "----"
        else:
            display_sel = self.selection_buffer[:4].ljust(4, "-") if self.selection_mode else "----"
        try:
            sel_font = getattr(self, 'selection_digits_font', self.medium_font)
            sel_color = Colors.RED
            sel_text = sel_font.render(display_sel, True, sel_color)
            offset = int(sel_text.get_height() / 2) + 12
            # Center the selection display horizontally with the main window
            if getattr(self, 'selection_center_override', None):
                cx, cy = self.selection_center_override
                sel_rect = sel_text.get_rect(center=(int(cx), int(cy)))
            else:
                shift = getattr(self, 'selection_anchor_shift', 0)
                sel_rect = sel_text.get_rect(center=(x + width // 2, y - offset - shift))
            pad_x = 12
            pad_y = 8
            bg = pygame.Rect(sel_rect.x - pad_x, sel_rect.y - pad_y, sel_rect.width + pad_x * 2, sel_rect.height + pad_y * 2)
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, bg)
            pygame.draw.rect(self.screen, Colors.RED, bg, 2)
            self.screen.blit(sel_text, sel_rect)
            try:
                self.last_selection_draw_rect = sel_rect
                self.last_selection_bg_rect = bg
                self.last_selection_display_string = display_sel
            except Exception:
                pass
        except Exception:
            pass

        # Padding
        padding = 15
        content_x = x + padding
        content_y = y + padding
        content_width = width - padding * 2

        # Large square album art (top center) - scale to fill available space
        max_art_width = content_width
        max_art_height = display_height - padding * 3 - 120  # Leave room for text below
        art_size = min(max_art_width, max_art_height)
        art_x = content_x + (content_width - art_size) // 2  # Center horizontally
        art_rect = pygame.Rect(art_x, content_y, art_size, art_size)
        art_img = self.get_album_art(album)
        if art_img:
            scaled = pygame.transform.smoothscale(art_img, (art_size, art_size))
            self.screen.blit(scaled, art_rect)
        else:
            pygame.draw.rect(self.screen, Colors.GRAY, art_rect)
            album_num_text = self.large_font.render(f"{album.album_id:02d}", True, Colors.BLACK)
            album_num_rect = album_num_text.get_rect(center=art_rect.center)
            # Add white border around the number
            border_padding = 6
            border_rect = pygame.Rect(
                album_num_rect.x - border_padding,
                album_num_rect.y - border_padding,
                album_num_rect.width + border_padding * 2,
                album_num_rect.height + border_padding * 2,
            )
            pygame.draw.rect(self.screen, Colors.WHITE, border_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, border_rect, 2)
            self.screen.blit(album_num_text, album_num_rect)

        # Update persistent info if a track is actively playing from this album
        track = self.player.get_current_track()
        current_album = self.player.get_current_album()
        if (
            track
            and current_album
            and self.player.is_playing
            and current_album.album_id == album.album_id
        ):
            self.last_track_info = {
                "album_id": current_album.album_id,
                "track_index": self.player.current_track_index,
                "title": track["title"],
                "duration": track["duration_formatted"],
            }

        # Text area (below album art)
        text_x = content_x
        text_y = content_y + art_size + padding

        label_text = self.medium_font.render("Now Playing", True, self.accent_color())
        label_rect = label_text.get_rect(center=(x + width // 2, text_y))
        self.screen.blit(label_text, label_rect)

        if self.last_track_info:
            # Song title (large, centered at top)
            title_text = self.large_font.render(
                self.last_track_info["title"], True, Colors.WHITE
            )
            title_rect = title_text.get_rect(center=(x + width // 2, text_y + 35))
            self.screen.blit(title_text, title_rect)

            # No longer display the album/track numeric selection here —
            # the 4-digit selection buffer is shown above the box as requested.
        else:
            placeholder = self.medium_font.render("--", True, self.text_secondary_color())
            placeholder_rect = placeholder.get_rect(
                center=(x + width // 2, text_y + 35)
            )
            self.screen.blit(placeholder, placeholder_rect)

    def draw_number_pad_centered(self) -> None:
        """Draw number pad centered at bottom without overlapping audio controls"""
        # Scale keypad based on screen mode to maintain proportions
        if self.fullscreen:
            # Full size for fullscreen
            scale_factor = 1.0
        else:
            # Scale down for windowed mode to maintain same proportional size
            scale_factor = 0.75  # 75% of fullscreen size

        # Compute scaled dimensions
        base_button_w = 60  # Base button width
        base_button_h = 40  # Base button height
        base_spacing = 8  # Base spacing

        pad_button_w = int(base_button_w * scale_factor)
        pad_button_h = int(base_button_h * scale_factor)
        spacing = int(base_spacing * scale_factor)

        total_width = pad_button_w * 3 + spacing * 2
        # Main keypad area: 7 columns for the visual keypad image, plus
        # 2 columns reserved for the left/right nav buttons (integrated)
        main_cols = 7
        nav_cols = 2
        total_grid_cols = main_cols + nav_cols
        pad_main_w = pad_button_w * main_cols + spacing * (main_cols - 1)
        total_width_new = pad_main_w
        pad_x = self.width // 2 - total_width // 2

        # Position keypad lower in windowed mode to account for taller now playing area
        if self.fullscreen:
            pad_y = self.height - self.bottom_area_height - int(35 * scale_factor)
        else:
            # Move keypad significantly lower in windowed mode
            pad_y = self.height - self.bottom_area_height + int(20 * scale_factor)

        # If using the new keypad layout, position it below the Now Playing
        # card in the center column (between left/right album cards). To do
        # this we reproduce the same layout math used by draw_main_screen so
        # the pad sits under the Now Playing area.
        if self.use_new_keypad_layout:
            try:
                controls_margin_top = self.header_height + 20
                button_height = 50
                buttons_y = controls_margin_top + 20
                content_top = buttons_y + button_height + 25
                content_height = self.height - content_top - self.bottom_area_height - 20
                if content_height < 200:
                    content_height = 200

                total_content_width = self.width - self.margin * 4
                col1_width = int(total_content_width * 0.32)
                col2_width = int(total_content_width * 0.36)
                col3_width = int(total_content_width * 0.32)

                col1_x = self.margin
                col3_x = self.width - self.margin - col3_width + 12
                left_edge = col1_x + col1_width
                right_edge = col3_x
                available_space = right_edge - left_edge
                col2_x = left_edge + (available_space - col2_width) // 2

                # Two rows: the now playing card sits at row1
                row1_y = content_top + 10
                now_playing_height_factor = 0.85 if self.fullscreen else 0.95
                now_playing_height = int(content_height * now_playing_height_factor) - 10

                # Ensure the keypad sits inside the center column and does not
                # overflow into the left/right album cards. Compute the desired
                # width for the image-driven pad and scale down if it would
                # exceed the available center column width.
                # Nav button sizes (w x h: 65x85 scaled) are considered
                # part of the overall pad width so the full pad will be
                # centered; use keypad spacing for internal gaps.
                nav_button_w = int(65 * scale_factor)
                nav_button_h = int(85 * scale_factor)
                nav_spacing_inside = spacing
                inner_gap = spacing

                # If nav buttons are wider than the pad buttons, expand the
                # pad_button_w so each grid column is wide enough to contain
                # the nav buttons. This keeps consistent column alignment
                # so spacing between columns remains uniform.
                if nav_button_w > pad_button_w:
                    pad_button_w = nav_button_w

                main_cols = 7
                nav_cols = 2
                total_grid_cols = main_cols + nav_cols

                # pad_total_w = width occupied by full grid (main + nav)
                pad_total_w = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
                desired_pad_w = pad_total_w
                max_pad_w = max(0, col2_width - 20)  # small gutter inside column
                if desired_pad_w > max_pad_w and desired_pad_w > 0:
                    # Compute scale factor and adjust button/spacing sizes
                    scale = max_pad_w / float(desired_pad_w)
                    if scale < 1.0:
                        pad_button_w = max(20, int(pad_button_w * scale))
                        pad_button_h = max(14, int(pad_button_h * scale))
                        spacing = max(2, int(spacing * scale))
                        # Scale nav keys proportionally as well
                        nav_button_w = max(10, int(nav_button_w * scale))
                        nav_button_h = max(10, int(nav_button_h * scale))
                        pad_total_w = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
                        total_width_new = pad_button_w * main_cols + spacing * (main_cols - 1)

                # Center the (possibly rescaled) pad (including nav keys) inside column 2
                pad_total_w = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
                pad_x = col2_x + max(0, (col2_width - pad_total_w) // 2)
                # Lower the keypad so it doesn't overlap the Now Playing card
                # by an extra amount requested by the user (approx 75px scaled)
                extra_lower = int(75 * scale_factor)
                pad_y = row1_y + now_playing_height + int(8 * scale_factor) + extra_lower
            except Exception:
                # Any layout failure should keep the fallback pad_y
                pass

        # Compute nav sizes early so bounding box can include nav keys
        if self.use_new_keypad_layout:
            # Use the keypad's spacing for internal gaps so nav keys sit
            # visually consistent with the other keys. DO NOT reassign
            # nav button sizes here — they are computed earlier and may
            # have been scaled to match pad columns.
            nav_spacing_inside = spacing
            inner_gap = spacing
        else:
            nav_button_w = int(60 * scale_factor)
            nav_button_h = int(80 * scale_factor)
            nav_distance = int(40 * scale_factor)

        # Draw semi-transparent black border around keypad (15% opacity)
        border_padding = int(12 * scale_factor)
        # Expand the keypad border so it fully encloses the bottom row
        # (CLR and ENT) — swap 4 rows -> 5 rows and one additional spacing
        if self.use_new_keypad_layout:
            # Expand the border to include the two nav keys which now live to
            # the right of the key area (they're part of the pad). The layout
            # uses an inner_gap between keys and nav keys, and a small spacing
            # between the two nav keys.
            border_w = total_width_new + inner_gap + (nav_button_w * 2) + nav_spacing_inside
            border_h = pad_button_h * 2 + spacing + int(60 * scale_factor)
        else:
            border_w = total_width
            border_h = pad_button_h * 5 + spacing * 4 + int(60 * scale_factor)

        # Align keypad border vertically with album cards when using the
        # new image-driven layout so the pad appears flush with the album
        # column bottom. Fall back to previous placement on error.
        if self.use_new_keypad_layout:
            try:
                # Recompute the same layout geometry used in draw_main_screen
                # and align the border bottom to the bottom of the album cards
                controls_margin_top = self.header_height + 20
                button_height = 50
                buttons_y = controls_margin_top + 20
                content_top = buttons_y + button_height + 25
                content_height = self.height - content_top - self.bottom_area_height - 20
                if content_height < 200:
                    content_height = 200

                row1_y = content_top + 10
                row2_y = row1_y + content_height // 2 + 35
                card_h = (content_height // 2) + 15

                bottom_target = row2_y + card_h
                top = bottom_target - border_h
                border_rect = pygame.Rect(
                    pad_x - border_padding,
                    top,
                    border_w + border_padding * 2,
                    border_h,
                )
            except Exception:
                border_rect = pygame.Rect(
                    pad_x - border_padding,
                    pad_y - border_padding - int(40 * scale_factor),
                    border_w + border_padding * 2,
                    border_h,
                )
        else:
            border_rect = pygame.Rect(
                pad_x - border_padding,
                pad_y - border_padding - int(40 * scale_factor),
                border_w + border_padding * 2,
                border_h,
            )
        # Create semi-transparent surface
        border_surface = pygame.Surface(
            (border_rect.width, border_rect.height), pygame.SRCALPHA
        )
        border_surface.fill((0, 0, 0, int(255 * 0.5)))  # Black at 50% opacity
        # Record for tests/QA so callers can assert border geometry
        try:
            self.last_pad_border_rect = border_rect.copy()
        except Exception:
            self.last_pad_border_rect = border_rect

        self.screen.blit(border_surface, border_rect.topleft)

        # Ensure the pad image (two rows) is vertically centered inside the
        # border rect so keys are not too low and won't stick out of the
        # bounding box. Compute the visual pad height (two rows + spacing)
        # and center it within the border's inner area (excluding padding).
        try:
            if self.use_new_keypad_layout:
                pad_image_h = pad_button_h * 2 + spacing
                inner_v_space = border_rect.height - (border_padding * 2)
                # If there's extra vertical space inside the border, center the pad image
                if inner_v_space > pad_image_h:
                    pad_y = border_rect.y + border_padding + max(0, (inner_v_space - pad_image_h) // 2)
        except Exception:
            # keep computed pad_y if centering fails
            pass

        # Scale navigation button positions and sizes.
        # For image-driven keypad layout we place these inside the box and
        # make them look like regular buttons (not media-icon-only).
        if self.use_new_keypad_layout:
            # spacing between the two nav keys = keypad spacing
            # NOTE: do not overwrite nav_button_w/nav_button_h here; they may
            # have been scaled above to keep the pad columns consistent.
            nav_spacing_inside = spacing
        else:
            nav_button_w = int(60 * scale_factor)
            nav_button_h = int(80 * scale_factor)
            nav_distance = int(40 * scale_factor)

        # Update navigation button sizes
        self.left_nav_button.rect.width = nav_button_w
        self.left_nav_button.rect.height = nav_button_h
        self.right_nav_button.rect.width = nav_button_w
        self.right_nav_button.rect.height = nav_button_h

        # Position navigation buttons together on the right side of the keypad
        # and vertically align them with the keypad's visual center so they
        # sit in line with the key rows.
        pad_visual_h = (pad_button_h * (2 if self.use_new_keypad_layout else 5)) + (spacing if self.use_new_keypad_layout else spacing * 4)
        button_y = pad_y + max(0, (pad_visual_h - nav_button_h) // 2)
        if self.use_new_keypad_layout:
            # Compute column origins for all columns (main + nav) so nav
            # button positions can be derived consistently. We compute this
            # here because pad_x may have been adjusted above when centering
            # the full pad inside the center column.
            cols = [pad_x + c * (pad_button_w + spacing) for c in range(total_grid_cols)]
            # Put both nav buttons inside the keypad bounding box on the
            # right side so they are presented with the rest of the keys.
            # Place them aligned with the grid columns so spacing matches the keypad spacing.
            left_button_x = cols[main_cols]
            right_button_x = cols[main_cols + 1]
            # Convert to text-rendered buttons (not icon-only)
            self.left_nav_button.icon_type = None
            self.right_nav_button.icon_type = None
            # Ensure button labels are arrows (text) so they render as normal buttons
            self.left_nav_button.text = "◄"
            self.right_nav_button.text = "►"
        else:
            # Legacy behaviour: place buttons on either side of keypad
            left_button_x = pad_x - nav_distance - nav_button_w
            right_button_x = pad_x + total_width + nav_distance

        self.left_nav_button.rect.x = left_button_x
        self.left_nav_button.rect.y = button_y
        self.right_nav_button.rect.x = right_button_x
        self.right_nav_button.rect.y = button_y

        # Draw navigation buttons
        font_to_use = self.medium_font if self.fullscreen else self.small_font
        # When using new keypad layout the nav buttons are placed inside the
        # pad and should render like normal keys. If legacy mode, they are
        # still drawn on the sides as before.
        self.left_nav_button.draw(self.screen, font_to_use)
        self.right_nav_button.draw(self.screen, font_to_use)

        # The pad label was intentionally removed to keep the UI clean and
        # avoid cluttering the center column above the keypad.

        # Choose appropriate font for buttons based on scale
        button_font = self.medium_font if self.fullscreen else self.small_font

        # Update button sizes and positions - draw all buttons properly
        # Draw according to the active keypad layout mode
        if self.use_new_keypad_layout:
            # New image-driven layout
            # Try to draw the keypad background image if present (scaled to our area)
            try:
                img_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'keypad_new.png')
                img_path = os.path.normpath(img_path)
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path)
                    img_surf = pygame.transform.smoothscale(img, (total_width_new, pad_button_h * 2 + spacing))
                    self.screen.blit(img_surf, (pad_x, pad_y))
            except Exception:
                pass

            # Map digit labels to button objects so we can place them according to the image design
            btn_by_digit = {b.digit: b for b in self.number_pad_buttons}

            # Column origin positions for 7 columns in the image area
            cols = [pad_x + c * (pad_button_w + spacing) for c in range(7)]

            # Row 0: 1 2 3 4 5 (col 0..4), (empty) , ENT (col 6)
            # The 'None' slot intentionally leaves the underlying image visible
            # which can accidentally show unrelated artwork (eg. the media
            # pause icon). To prevent unexpected media-art showing through we
            # draw a placeholder button background in any None slot so the
            # area is covered by the UI and behaves consistently.
            row0 = ["1", "2", "3", "4", "5", None, "ENT"]
            # Clear any previously recorded placeholders for tests or debugging
            self.keypad_image_placeholders = []

            for i, label in enumerate(row0):
                if not label:
                    # Use the existing pause_button instance as the interactive
                    # control in this None slot so the pause control is relocated
                    # into the keypad image area (replacing the top pause button).
                    self.pause_button.rect.width = pad_button_w
                    self.pause_button.rect.height = pad_button_h
                    self.pause_button.rect.x = cols[i]
                    self.pause_button.rect.y = pad_y
                    # Draw the pause icon (the Button class will render the
                    # themed pause image if available, otherwise draw the icon)
                    self.pause_button.draw(self.screen, self.small_font if not self.fullscreen else self.medium_font)
                    # Keep reference to this rect for tests
                    self.keypad_image_placeholders = [self.pause_button.rect]
                    continue
                btn = btn_by_digit.get(label)
                if not btn:
                    continue
                btn.rect.width = pad_button_w
                btn.rect.height = pad_button_h
                btn.rect.x = cols[i]
                btn.rect.y = pad_y
                btn.draw(self.screen, self.medium_font if label == "ENT" else button_font)

            # Row 1: 6 7 8 9 0 < CLR
            row1 = ["6", "7", "8", "9", "0", "<", "CLR"]
            for i, label in enumerate(row1):
                btn = btn_by_digit.get(label)
                if not btn:
                    continue
                btn.rect.width = pad_button_w
                btn.rect.height = pad_button_h
                btn.rect.x = cols[i]
                btn.rect.y = pad_y + (pad_button_h + spacing)
                btn.draw(self.screen, button_font)

        else:
            # First 9 buttons (1-9) in 3x3 grid (legacy calculator layout)
            for row in range(3):
                for col in range(3):
                    idx = row * 3 + col
                    if idx < len(self.number_pad_buttons):
                        btn = self.number_pad_buttons[idx]
                        btn.rect.width = pad_button_w
                        btn.rect.height = pad_button_h
                        btn.rect.x = pad_x + col * (pad_button_w + spacing)
                        btn.rect.y = pad_y + row * (pad_button_h + spacing)
                        btn.draw(self.screen, button_font)

        # Draw button 0 (index 9) - left position in row 4
        if not self.use_new_keypad_layout:
            if len(self.number_pad_buttons) > 9:
                btn_0 = self.number_pad_buttons[9]
                btn_0.rect.width = pad_button_w
                btn_0.rect.height = pad_button_h
                btn_0.rect.x = pad_x
                btn_0.rect.y = pad_y + 3 * (pad_button_h + spacing)
                btn_0.draw(self.screen, button_font)

        # Draw backspace button (index 10) - middle position in row 4
        if not self.use_new_keypad_layout:
            if len(self.number_pad_buttons) > 10:
                btn_back = self.number_pad_buttons[10]
                btn_back.rect.width = pad_button_w
                btn_back.rect.height = pad_button_h
                btn_back.rect.x = pad_x + (pad_button_w + spacing)
                btn_back.rect.y = pad_y + 3 * (pad_button_h + spacing)
                btn_back.draw(self.screen, button_font)

        # Draw CLR button (index 11) - left side of row 5
        if not self.use_new_keypad_layout:
            if len(self.number_pad_buttons) > 11:
                btn_clr = self.number_pad_buttons[11]
                btn_clr.rect.width = int(pad_button_w * 1.6)  # Adjusted for wider buttons
                btn_clr.rect.height = pad_button_h
                btn_clr.rect.x = pad_x
                btn_clr.rect.y = pad_y + 4 * (pad_button_h + spacing)
                btn_clr.draw(self.screen, button_font)

        # Draw ENT button (index 12) - right side of row 5
        if not self.use_new_keypad_layout:
            if len(self.number_pad_buttons) > 12:
                btn_ent = self.number_pad_buttons[12]
                btn_ent.rect.width = int(pad_button_w * 1.6)  # Adjusted for wider buttons
                btn_ent.rect.height = pad_button_h
                btn_ent.rect.x = pad_x + int(pad_button_w * 1.6) + spacing
                btn_ent.rect.y = pad_y + 4 * (pad_button_h + spacing)
                btn_ent.draw(self.screen, button_font)
                btn_ent.rect.width = int(pad_button_w * 1.6)  # Adjusted for wider buttons
                btn_ent.rect.height = pad_button_h
            btn_ent.rect.x = pad_x + int(pad_button_w * 1.6) + spacing
            btn_ent.rect.y = pad_y + 4 * (pad_button_h + spacing)
            btn_ent.draw(self.screen, self.medium_font)

        # Selection display is shown above the Now Playing card (moved there)

    def draw_audio_controls(self) -> None:
        """Draw audio control elements in bottom-left area"""
        y_base = self.height - self.bottom_area_height + 20
        # Volume slider moved to top-left; no rendering here anymore
        # Fader controls moved to dedicated fader screen; no display here

        # Draw equalizer if visible
        # (EQ preview removed from main screen; access via Config)

    def draw_theme_selector(self) -> None:
        """Draw theme preview and selection interface"""
        # Position themes at bottom center
        theme_section_y = self.height - 180
        # In windowed mode make room: move the theme title and buttons down so they
        # don't overlap other UI elements (e.g., when windowed, bump down ~50px).
        if not self.fullscreen:
            theme_section_y += 50

        # Draw section title
        theme_title = self.medium_font.render("Theme Selection", True, self.accent_color())
        theme_title_rect = theme_title.get_rect(
            center=(self.width // 2, theme_section_y - 30)
        )
        self.screen.blit(theme_title, theme_title_rect)

        # Position theme buttons centered under the title and draw them
        btn_count = len(self.theme_buttons)
        if btn_count:
            spacing = 15
            # Use the actual widths of the buttons (assume uniform width) for total width calc
            btn_width = self.theme_buttons[0][1].rect.width
            total_width = btn_count * btn_width + (btn_count - 1) * spacing
            start_x = (self.width - total_width) // 2
            btn_y = theme_section_y

            for i, (theme_name, btn) in enumerate(self.theme_buttons):
                btn.rect.x = start_x + i * (btn_width + spacing)
                btn.rect.y = btn_y
                btn.draw(self.screen, self.small_font)

        # Draw the 'New Theme' button below the theme buttons
        if hasattr(self, "new_theme_button"):
            self.new_theme_button.rect.x = (self.width - self.new_theme_button.rect.width) // 2
            self.new_theme_button.rect.y = btn_y + 48
            self.new_theme_button.draw(self.screen, self.small_font)

        # Draw theme preview if hovering
        for theme_name, btn in self.theme_buttons:
            if btn.is_hovered:
                # Position preview differently for fullscreen vs windowed:
                # - windowed: keep previous behavior (above buttons)
                # - fullscreen: place preview above the 'Theme Selection' title
                px, py = self._get_theme_preview_pos(theme_section_y)
                self.draw_theme_preview(theme_name, px, py)
                break

    def _get_theme_preview_pos(self, theme_section_y: int) -> tuple:
        """Return (x,y) the position for the theme preview box.

        When fullscreen, we place the preview above the title area, otherwise
        above the theme buttons area (previous behavior).
        """
        preview_width = 200
        # default windowed placement above buttons (previous behavior)
        default_x = self.width // 2 - preview_width // 2
        # move preview up by an additional 20px (total -40) to give it more breathing room
        # NOTE: windowed mode gets an extra -20px nudge to lift the preview further
        # so it doesn't collide with other UI elements when the window is not fullscreen
        default_y = theme_section_y - 130 - 60

        if self.fullscreen:
            # place above the title which sits at theme_section_y - 30
            title_y = theme_section_y - 30
            # Move preview above the title with a small gap
            # Move fullscreen preview up by an additional 20px too
            py = title_y - 10 - 120 - 40  # 120 is preview height
            px = self.width // 2 - preview_width // 2
            return px, py

        return default_x, default_y

    def draw_theme_preview(self, theme_name: str, x: int, y: int) -> None:
        """Draw a preview of the selected theme"""
        theme = self.theme_manager.themes.get(theme_name)
        if not theme:
            return

        # Preview box dimensions
        preview_width = 200
        preview_height = 120

        # Draw preview background
        preview_rect = pygame.Rect(x, y, preview_width, preview_height)
        pygame.draw.rect(self.screen, Colors.GRAY, preview_rect)
        pygame.draw.rect(self.screen, Colors.WHITE, preview_rect, 2)

        # Draw theme background preview (scaled down)
        bg = theme.get_background()
        if bg:
            scaled_bg = pygame.transform.scale(bg, (preview_width - 4, 60))
            self.screen.blit(scaled_bg, (x + 2, y + 2))
        else:
            pygame.draw.rect(
                self.screen,
                Colors.DARK_GRAY,
                pygame.Rect(x + 2, y + 2, preview_width - 4, 60),
            )

        # Draw sample button preview
        btn_preview_x = x + 20
        btn_preview_y = y + 70
        btn_preview_width = 60
        btn_preview_height = 35

        btn_color = theme.get_color("button", Colors.GRAY)
        pygame.draw.rect(
            self.screen,
            btn_color,
            pygame.Rect(
                btn_preview_x, btn_preview_y, btn_preview_width, btn_preview_height
            ),
        )
        pygame.draw.rect(
            self.screen,
            Colors.WHITE,
            pygame.Rect(
                btn_preview_x, btn_preview_y, btn_preview_width, btn_preview_height
            ),
            1,
        )

        # Draw sample slider preview
        slider_x = x + 90
        slider_y = y + 80
        track_color = theme.get_color("slider_track", Colors.GRAY)
        pygame.draw.rect(
            self.screen, track_color, pygame.Rect(slider_x, slider_y, 90, 4)
        )
        knob_color = theme.get_color("slider_knob", Colors.LIGHT_GRAY)
        pygame.draw.circle(self.screen, knob_color, (slider_x + 45, slider_y + 2), 6)

        # Draw theme name
        name_text = self.small_font.render(theme_name.capitalize(), True, self.text_color())
        self.screen.blit(name_text, (x + 20, y + preview_height + 5))

    def draw_bottom_text_overlay(self, text_y_position, text_height=25):
        """Draw a semi-transparent black overlay across the bottom for better text contrast"""
        overlay_surface = pygame.Surface((self.width, text_height))
        overlay_surface.set_alpha(int(255 * 0.85))  # 85% opacity
        overlay_surface.fill(Colors.BLACK)
        # Position overlay to cover the text area
        overlay_y = text_y_position - 5  # Slightly above the text
        self.screen.blit(overlay_surface, (0, overlay_y))

    def draw_top_text_overlay(self, text_y_position, text_height=50):
        """Draw a semi-transparent black overlay across the top for better text contrast"""
        overlay_surface = pygame.Surface((self.width, text_height))
        overlay_surface.set_alpha(int(255 * 0.85))  # 85% opacity
        overlay_surface.fill(Colors.BLACK)
        # Position overlay to cover the text area from the top
        overlay_y = 0  # Start from the very top of the screen
        self.screen.blit(overlay_surface, (0, overlay_y))

    def get_album_art(self, album):
        """Return cached album art surface or attempt to load one"""
        if album.album_id in self.album_art_cache:
            return self.album_art_cache[album.album_id]
        candidates = [
            "cover.jpg",
            "cover.png",
            "folder.jpg",
            "folder.png",
            "album.jpg",
            "album.png",
            "art.jpg",
            "art.png",
        ]
        art_surface = None
        try:
            # Prefer robust loader which can use Pillow if pygame doesn't
            try:
                from src.image_utils import load_image_surface
            except Exception:
                load_image_surface = None

            for name in candidates:
                path = os.path.join(album.directory, name)
                if os.path.isfile(path):
                    if load_image_surface is not None:
                        art_surface = load_image_surface(path)
                    else:
                        art_surface = pygame.image.load(path)

                    # Convert to alpha if available
                    try:
                        art_surface = art_surface.convert_alpha()
                    except Exception:
                        pass
                    break
        except Exception as e:
            print(f"Album art load failed for album {album.album_id:02d}: {e}")
        self.album_art_cache[album.album_id] = art_surface
        return art_surface

    def compute_album_text_origin(self, album, x: int, y: int, width: int, height: int):
        """Compute the (text_x, text_y) origin positions for album text in draw_album_card.

        This duplicates the positioning logic used by draw_album_card and is useful
        for unit-testing layout behavior without requiring surface inspection.
        """
        padding = 8
        content_x = x + padding
        content_y = y + padding
        content_width = width - padding * 2
        content_height = height - padding * 2

        art_size = min(content_height - 10, content_width // 2.2)
        art_x = x + width - padding - art_size
        art_y = content_y
        # Determine if there is album art present
        art_img = self.get_album_art(album)

        if art_img:
            # with art, text starts at the left content area
            text_x = content_x
            text_y = content_y
        else:
            # no art: default to art area top-left for the numeric overlay,
            # but textual content will be either here or the left column
            # for placeholders.
            text_x = int(art_x + 3)
            text_y = int(art_y + 3)
            if not getattr(album, "is_valid", True):
                text_x = content_x
                text_y = content_y

        return text_x, text_y, int(art_x)

    def compute_album_number_origin(self, album, x: int, y: int, width: int, height: int):
        """Compute the (x,y) position of the album-number overlay for testing.

        The album-number should always be placed in the top-left of the album
        art area (even for placeholder albums), so this helper returns that
        origin for assertions in unit tests.
        """
        padding = 8
        content_width = width - padding * 2
        content_height = height - padding * 2

        art_size = min(content_height - 10, content_width // 2.2)
        art_x = x + width - padding - art_size
        art_y = y + padding

        # album number overlay sits at a fixed offset inside the art rect
        return int(art_x + 3), int(art_y + 3)

    def compute_volume_overlay_origin(self):
        """Return the computed overlay rectangle (x, y, w, h) used for the
        semi-transparent background behind the main volume slider.

        This reads the current volume_slider attributes and returns the
        coordinates used when drawing the overlay. Useful for unit tests.
        """
        try:
            label_h = self.small_font.get_height()
            top_extra = label_h + 12
            x = int(self.volume_slider.x - 8)
            y = int(self.volume_slider.y - top_extra)
            w = int(self.volume_slider.width + 20)
            # Overlay is extended down 10px to leave extra padding beneath the slider
            h = int(self.volume_slider.height + 12 + top_extra + 10)
            return x, y, w, h
        except Exception:
            # If slider isn't initialized, return a sensible empty rectangle
            return 0, 0, 0, 0

    def _compute_visible_tracks_for_card(self, album, x: int, y: int, width: int, height: int, track_line_height: int) -> int:
        """Estimate how many tracks will actually fit in the card area using
        the same layout rules as draw_album_card. This mirrors the drawing
        logic so auto-scroll uses consistent visible-row counts when deciding
        boundaries and offsets.
        """
        try:
            padding = 8
            content_x = x + padding
            content_y = y + padding
            content_width = width - padding * 2
            content_height = height - padding * 2

            # Determine textual origin (matches draw_album_card)
            text_x, text_y, _ = self.compute_album_text_origin(album, x, y, width, height)
            current_y = text_y

            # Artist font and wrapping rules
            compact = bool(self.config.get("compact_track_list", True))
            artist_font = self.large_font if self.fullscreen else self.medium_font
            artist_text = album.artist
            if len(artist_text) > 16:
                wrap_point = 16
                last_space = artist_text.rfind(" ", 0, wrap_point + 1)
                if last_space > 0:
                    artist_line1 = artist_text[:last_space]
                    artist_line2 = artist_text[last_space + 1 : last_space + 17]
                else:
                    artist_line1 = artist_text[:16]
                    artist_line2 = artist_text[16:32]
            else:
                artist_line1 = artist_text
                artist_line2 = ""

            try:
                artist_text1 = artist_font.render(artist_line1, True, self.artist_text_color())
                current_y += artist_text1.get_height()
                if artist_line2:
                    current_y += 2
                    artist_text2 = artist_font.render(artist_line2, True, self.artist_text_color())
                    current_y += artist_text2.get_height()
            except Exception:
                # fall back to approximate values
                current_y += artist_font.get_height() * (1 + (1 if artist_line2 else 0))

            spacing_after_artist = 6 if self.fullscreen else 4
            current_y += spacing_after_artist + 4

            # Album title
            album_font = self.medium_font if self.fullscreen else self.small_medium_font
            album_title = album.title
            album_line1 = album_title
            album_line2 = ""
            if not self.fullscreen and len(album_title) > 14:
                album_line1 = album_title[:14]
                album_line2 = album_title[14:28]
            elif self.fullscreen and len(album_title) > 28:
                first_space = album_title.find(" ", 28)
                if first_space > 0:
                    album_line1 = album_title[:first_space]

            try:
                album_text1 = album_font.render(album_line1, True, self.album_text_color())
                current_y += album_text1.get_height()
                if album_line2:
                    album_text2 = album_font.render(album_line2, True, self.album_text_color())
                    current_y += album_text2.get_height()
            except Exception:
                current_y += album_font.get_height() * (1 + (1 if album_line2 else 0))

            spacing_after_album = 4 if self.fullscreen else 2
            current_y += spacing_after_album

            # Track count line
            count_font = self.small_medium_font if self.fullscreen else self.tiny_font
            try:
                track_count_text = count_font.render(f"{len(album.tracks)} tracks", True, Colors.BLUE)
                current_y += track_count_text.get_height()
            except Exception:
                current_y += count_font.get_height()

            spacing_after_count = 5 if self.fullscreen else 3
            current_y += spacing_after_count

            # allowed_bottom same as draw_album_card
            border_thickness = 2
            final_pad = 4
            allowed_bottom = y + height - padding - border_thickness - final_pad

            # Conservative guard for top/bottom bounds
            available = allowed_bottom - current_y - 10
            if available <= 0:
                return 0

            # Iterate through each track and compute the rendered height
            # using the same logic as draw_album_card to avoid mismatches.
            visible = 0
            safety_pad = 2

            # Compute text width (left column width minus artwork)
            art_size = min(content_height - 10, int(content_width // 2.2))
            text_width = content_width - art_size - padding - 5

            # density and compact state should match draw_album_card
            density = float(self.config.get("track_list_density", 0.8))
            density = max(0.5, min(1.0, density))
            compact = bool(self.config.get("compact_track_list", True))

            # Pre-compute base font sizes similar to draw_album_card
            if self.fullscreen:
                base_font_size = 12 if compact else max(12, self.small_font.get_height())
            else:
                base_font_size = 9 if compact else max(10, self.tiny_font.get_height())

            for i, track in enumerate(album.tracks):
                # Derive title and truncation rules to match draw_album_card
                max_chars = max(15, int(text_width // 6))
                title = track.get('title', '')[:max_chars]
                if len(track.get('title', '')) > max_chars:
                    title += "..."

                # Select an appropriate font matching draw_album_card
                font_size = max(8, int(base_font_size * density))
                try:
                    if getattr(self, 'bundled_font_path', None) and os.path.exists(self.bundled_font_path):
                        track_font = pygame.font.Font(self.bundled_font_path, font_size)
                    else:
                        track_font = pygame.font.SysFont('Arial', font_size)
                except Exception:
                    # fall back to pre-created attributes
                    if self.fullscreen:
                        track_font = self.track_list_font_fullscreen if compact else self.small_font
                    else:
                        track_font = self.track_list_font if compact else self.tiny_font

                track_text = track_font.render(f"{i+1}: {title}", True, self.track_text_color())
                track_h = track_text.get_height()
                needed = max(track_line_height, track_h) + safety_pad

                if current_y + needed > allowed_bottom:
                    break
                visible += 1
                current_y += needed

            return max(1, visible)
        except Exception:
            return 1

    def draw_config_screen(self) -> None:
        """Draw the configuration screen with improved organization"""
        self.screen.fill(Colors.DARK_GRAY)

        # Update message timer
        if self.config_message_timer > 0:
            self.config_message_timer -= 1

        # Draw title
        title = self.large_font.render("Configuration", True, self.text_color())
        title_rect = title.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title, title_rect)

        # Three column layout for configuration screen (left/settings, middle/library, right/audio/visual)
        left_x = 50
        settings_y = 100
        col_gap = 40
        col_width = (self.width - left_x * 2 - col_gap * 2) // 3
        mid_x = left_x + col_width + col_gap
        right_x = mid_x + col_width + col_gap

        # Settings section (left column)
        settings_header = self.medium_font.render("Settings", True, self.accent_color())
        self.screen.blit(settings_header, (left_x, settings_y))

        config_y = settings_y + 40
        line_height = 36

        config_items = [
            ("Auto Play Next Track", self.config.get("auto_play_next")),
            ("Shuffle Enabled", self.config.get("shuffle_enabled")),
            ("Show Album Art", self.config.get("show_album_art")),
            ("Keyboard Shortcuts", self.config.get("keyboard_shortcut_enabled")),
            ("Album Auto-Scroll", self.config.get("album_auto_scroll", True)),
            ("Use New Keypad Layout", self.config.get("use_new_keypad_layout", False)),
            ("Fullscreen Mode", self.fullscreen),
        ]

        for i, (label, value) in enumerate(config_items):
            y = config_y + i * line_height
            label_text = self.small_font.render(f"{label}:", True, self.text_color())
            self.screen.blit(label_text, (left_x + 10, y))

            value_str = "ON" if value else "OFF"
            value_color = Colors.GREEN if value else Colors.RED
            value_text = self.small_font.render(value_str, True, value_color)
            self.screen.blit(value_text, (left_x + col_width - 20, y))

        # Compact setting and density control
        try:
            compact_state = bool(self.config.get("compact_track_list", True))
            compact_button_x = left_x + 10
            compact_button_y = config_y + len(config_items) * line_height + 8
            self.config_compact_button.rect.x = compact_button_x
            self.config_compact_button.rect.y = compact_button_y
            # ensure button width fits within column
            self.config_compact_button.rect.width = min(self.config_compact_button.rect.width, col_width - 20)
            self.config_compact_button.draw(self.screen, self.small_font)

            state_txt = "ON" if compact_state else "OFF"
            state_color = Colors.GREEN if compact_state else Colors.RED
            state_surf = self.small_font.render(state_txt, True, state_color)
            self.screen.blit(state_surf, (compact_button_x + self.config_compact_button.rect.width + 8, compact_button_y + 8))

            # Density slider below compact toggle
            if hasattr(self, "config_density_slider"):
                den_x = compact_button_x
                # Lower density slider slightly for better spacing
                den_y = compact_button_y + self.config_compact_button.rect.height + 14 + 30
                self.config_density_slider.x = den_x
                self.config_density_slider.y = den_y
                # cap slider width to column width
                self.config_density_slider.width = min(self.config_density_slider.width, col_width - 40)
                # Previously a semi-transparent box was drawn behind the density
                # slider. That overlay has been removed to avoid visual clutter
                # while keeping the slider itself intact.
                self.config_density_slider.draw(self.screen, self.small_font)
                dval = float(self.config.get("track_list_density", 0.8))
                txt = self.small_font.render(f"{dval:.2f}", True, Colors.LIGHT_GRAY)
                self.screen.blit(txt, (den_x + self.config_density_slider.width + 10, den_y + 8))

            # Auto-scroll speed slider below density slider
            if hasattr(self, "config_auto_scroll_speed_slider"):
                asc_x = compact_button_x
                asc_y = den_y + 50
                self.config_auto_scroll_speed_slider.x = asc_x
                self.config_auto_scroll_speed_slider.y = asc_y
                self.config_auto_scroll_speed_slider.width = min(self.config_auto_scroll_speed_slider.width, col_width - 40)
                self.config_auto_scroll_speed_slider.draw(self.screen, self.small_font)
                asc_val = float(self.config.get("album_auto_scroll_speed", 2.0))
                asc_txt = self.small_font.render(f"{asc_val:.1f}s", True, Colors.LIGHT_GRAY)
                self.screen.blit(asc_txt, (asc_x + self.config_auto_scroll_speed_slider.width + 10, asc_y + 8))
        except Exception:
            pass

        # Library information section (middle column)
        info_x = mid_x
        # Raise the Library header to the same top alignment as Settings
        info_y = settings_y
        info_header = self.medium_font.render("Library Info", True, Colors.YELLOW)
        self.screen.blit(info_header, (info_x, info_y))

        stats = self.library.get_library_stats()
        info_lines = [
            f"Albums: {stats['total_albums']}/{stats['max_albums']}",
            f"Total Tracks: {stats['total_tracks']}",
            f"Total Duration: {stats['total_duration_formatted']}",
            f"Current Theme: {self.config.get('theme')}",
        ]

        for i, info in enumerate(info_lines):
            y = info_y + 40 + i * 25
            info_text = self.small_font.render(info, True, Colors.LIGHT_GRAY)
            self.screen.blit(info_text, (info_x + 10, y))

        # Show configured music directory (or default)
        music_dir = self.config.get("music_dir")
        if not music_dir:
            if sys.platform.startswith("linux") or sys.platform == "darwin":
                music_dir = os.path.expanduser(os.path.join("~", "Music", "JukeBox"))
            else:
                music_dir = os.path.join(os.path.dirname(__file__), "..", "music")

        y = info_y + 40 + len(info_lines) * 25
        md_text = self.small_font.render(
            f"Music folder: {music_dir}", True, Colors.LIGHT_GRAY
        )
        self.screen.blit(md_text, (info_x + 10, y))

        # Right Column - Actions (audio / visual kept on the right)
        # right_x was computed earlier as right_x variable (col position)

        # Audio effects section (kept to the right column)
        # Align vertically with the top Settings header so controls are parallel
        # with the left-hand settings area and avoid overlap.
        effects_y = settings_y
        effects_header = self.medium_font.render("Audio Effects", True, Colors.YELLOW)
        self.screen.blit(effects_header, (right_x, effects_y))

        self.config_equalizer_button.rect.x = right_x + 10
        # move equalizer button 10px higher
        self.config_equalizer_button.rect.y = effects_y + 30
        self.config_equalizer_button.draw(self.screen, self.small_font)

        # Visual effects section (below audio effects, still aligned with right column)
        # move visual effects a bit lower to provide separation from audio effects
        visual_effects_y = effects_y + 85
        visual_effects_header = self.medium_font.render(
            "Visual Effects", True, Colors.YELLOW
        )
        self.screen.blit(visual_effects_header, (right_x, visual_effects_y))

        # Fullscreen button in Visual Effects section
        self.config_fullscreen_button.rect.x = right_x + 20
        # move fullscreen button 10px higher
        self.config_fullscreen_button.rect.y = visual_effects_y + 30
        self.config_fullscreen_button.draw(self.screen, self.small_font)

        # Draw choose music directory button (middle column)
        md_button_x = info_x + 10
        # Nudge the choose-library button a few pixels further down so it is
        # visually separated from the music-folder text above.
        md_button_y = y + 28
        self.config_choose_music_button.rect.x = md_button_x
        self.config_choose_music_button.rect.y = md_button_y
        # Make sure button width fits inside column
        self.config_choose_music_button.rect.width = min(self.config_choose_music_button.rect.width, col_width - 20)
        self.config_choose_music_button.draw(self.screen, self.small_font)

        # Consolidated Library Actions: place action buttons in two columns under the Music folder area
        actions_header = self.medium_font.render("Library Actions", True, Colors.YELLOW)
        # Move the library actions header down ~25px to avoid clipping (further nudge)
        # This ensures the heading and subsequent action rows are comfortably below the button
        actions_header_y = md_button_y + 55
        self.screen.blit(actions_header, (md_button_x, actions_header_y))

        # Two-column layout
        # Start rows slightly below the header
        action_row_y = actions_header_y + 24 + 20
        col_spacing = self.config_rescan_button.rect.width + 12
        col1_x = md_button_x
        col2_x = md_button_x + col_spacing

        # First row: Rescan | Extract Art
        self.config_rescan_button.rect.x = col1_x
        self.config_rescan_button.rect.y = action_row_y
        self.config_rescan_button.draw(self.screen, self.small_font)

        self.config_extract_art_button.rect.x = col2_x
        self.config_extract_art_button.rect.y = action_row_y
        self.config_extract_art_button.draw(self.screen, self.small_font)

        # Second row: Reset (left column)
        self.config_reset_button.rect.x = col1_x
        self.config_reset_button.rect.y = action_row_y + 46
        self.config_reset_button.draw(self.screen, self.small_font)

        # Theme selection section (bottom center) - draw first so modal overlays it
        self.draw_theme_selector()

        # If theme creator modal is open draw it on top of everything
        if getattr(self, "theme_creator_open", False):
            try:
                self.draw_theme_creator_dialog()
            except Exception:
                # Drawing should not crash the whole UI - ignore drawing errors in tests
                pass

        # If the user is editing the music directory (in-app modal), draw it on top
        if self.config_music_editing:
            self._draw_music_dir_modal()

        # Close button (top right)
        self.config_close_button.rect.x = self.width - 140
        self.config_close_button.rect.y = 20
        self.config_close_button.draw(self.screen, self.small_font)

        # Draw messages
        if self.config_message and self.config_message_timer > 0:
            msg_color = (
                Colors.GREEN
                if "success" in self.config_message.lower()
                or "complete" in self.config_message.lower()
                else Colors.YELLOW
            )
            message_text = self.medium_font.render(self.config_message, True, msg_color)
            message_rect = message_text.get_rect(
                center=(self.width // 2, self.height - 60)
            )
            self.screen.blit(message_text, message_rect)

        # Draw instructions
        instructions = self.small_font.render(
            "ESC or Close button to exit | Alt+Enter: Toggle Fullscreen",
            True,
            Colors.GRAY,
        )
        instructions_rect = instructions.get_rect(
            center=(self.width // 2, self.height - 30)
        )
        self.screen.blit(instructions, instructions_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Main UI loop"""
        frame_count = 0
        while self.running:
            self.handle_events()

            # Only update audio controls every few frames for performance
            if frame_count % 3 == 0:
                self.update_audio_controls()

            # Update music state and handle queue progression
            self.player.update_music_state()
            self.draw()

            # Use standard display flip for consistent rendering
            pygame.display.flip()

            self.clock.tick(self.fps)
            frame_count += 1

        # Persist window size on exit
        self.config.set("window_width", self.width)
        self.config.set("window_height", self.height)
        self.config.set("fullscreen", self.fullscreen)

    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual fullscreen dimensions
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
        else:
            # Switch to windowed mode
            windowed_width = self.config.get("window_width", 1200)
            windowed_height = self.config.get("window_height", 800)
            self.width = windowed_width
            self.height = windowed_height
            self.screen = pygame.display.set_mode(
                (self.width, self.height), pygame.RESIZABLE
            )

        # Save fullscreen state
        self.config.set("fullscreen", self.fullscreen)
        print(f"Switched to {'fullscreen' if self.fullscreen else 'windowed'} mode")
