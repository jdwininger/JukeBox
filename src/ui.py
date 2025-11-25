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


class Button:
    """Simple button class for UI controls"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        color: Tuple[int, int, int] = Colors.GRAY,
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
        self.color = color
        self.hover_color = tuple(min(c + 50, 255) for c in color)
        self.is_hovered = False
        self.theme = theme
        self.is_gear_icon = is_gear_icon
        self.icon_type = icon_type

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button on the surface"""
        # Check if this button will use a themed image
        has_themed_image = False

        if self.theme:
            if self.is_gear_icon:
                # Check if config button has themed image
                config_img = self.theme.get_media_button_image("config")
                has_themed_image = config_img is not None
            elif self.icon_type:
                # Check if media/navigation button has themed image
                media_img = self.theme.get_media_button_image(self.icon_type)
                has_themed_image = media_img is not None
            else:
                # Regular buttons (text-based) don't use themed images
                has_themed_image = False

        # Only draw background and border for text-based buttons (not themed image buttons)
        if not has_themed_image:
            if self.theme:
                # Use theme background if available for regular buttons
                button_img = self.theme.get_button_image(
                    "hover" if self.is_hovered else "normal"
                )
                if button_img and not (self.is_gear_icon or self.icon_type):
                    # Only use theme background for regular text buttons
                    scaled_img = pygame.transform.scale(
                        button_img, (self.rect.width, self.rect.height)
                    )
                    surface.blit(scaled_img, self.rect)
                else:
                    # Text-based button: draw background and border
                    color = self.hover_color if self.is_hovered else self.color
                    pygame.draw.rect(surface, color, self.rect)
                    pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)
            else:
                # No theme, use color and border
                color = self.hover_color if self.is_hovered else self.color
                pygame.draw.rect(surface, color, self.rect)
                pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)

        if self.is_gear_icon:
            # Try to use themed config button image first
            if self.theme:
                config_img = self.theme.get_media_button_image("config")
                if config_img:
                    # Scale image to button size
                    scaled_img = pygame.transform.scale(
                        config_img, (self.rect.width, self.rect.height)
                    )
                    # Apply brightness effect on hover
                    if self.is_hovered:
                        scaled_img = self.apply_brightness_filter(scaled_img, 1.3)
                    surface.blit(scaled_img, self.rect)
                else:
                    # Fall back to gear icon
                    self.draw_gear_icon(surface)
            else:
                # No theme, draw gear icon
                self.draw_gear_icon(surface)
        elif self.icon_type:
            # Try to use themed media/navigation button image first
            if self.theme:
                media_img = self.theme.get_media_button_image(self.icon_type)
                if media_img:
                    # Scale image to button size
                    scaled_img = pygame.transform.scale(
                        media_img, (self.rect.width, self.rect.height)
                    )
                    # Apply brightness effect on hover
                    if self.is_hovered:
                        scaled_img = self.apply_brightness_filter(scaled_img, 1.3)
                    surface.blit(scaled_img, self.rect)
                else:
                    # Fall back to drawn icon
                    self.draw_media_icon(surface)
            else:
                # No theme, draw media control icon
                self.draw_media_icon(surface)
        else:
            # Draw text as usual
            text_surface = font.render(self.text, True, Colors.WHITE)
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

        # Fonts
        self.large_font = pygame.font.SysFont("Arial", 36)
        self.medium_font = pygame.font.SysFont("Arial", 20)
        self.small_medium_font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.tiny_font = pygame.font.SysFont("Arial", 10)
        # Dedicated font for album track lists (slightly smaller than tiny_font)
        self.track_list_font = pygame.font.SysFont("Arial", 9)
        # Smaller fullscreen track font when compact mode enabled
        self.track_list_font_fullscreen = pygame.font.SysFont("Arial", 12)

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

        # Screen mode: 'main', 'equalizer', 'config'
        self.screen_mode = "main"
        # Album art cache
        self.album_art_cache = {}

        # Create buttons
        self.setup_buttons()

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
        self.play_button = Button(
            x,
            controls_y,
            media_button_size,
            media_button_size,
            "Play",
            Colors.GREEN,
            theme=self.current_theme,
            icon_type="play",
        )
        x += media_button_size + spacing
        self.pause_button = Button(
            x,
            controls_y,
            media_button_size,
            media_button_size,
            "Pause",
            Colors.BLUE,
            theme=self.current_theme,
            icon_type="pause",
        )
        x += media_button_size + spacing
        self.stop_button = Button(
            x,
            controls_y,
            media_button_size,
            media_button_size,
            "Stop",
            Colors.RED,
            theme=self.current_theme,
            icon_type="stop",
        )

        # Export and Config + Album nav (right side anchored) - config and exit buttons (square)
        right_spacing = spacing
        right_x = self.width - self.margin
        # Place from right to left
        # Place exit button flush against the right margin, and move the
        # config (gear) left of it so both fit on the top controls bar.
        self.exit_button = Button(
            right_x - media_button_size,
            controls_y,
            media_button_size,
            media_button_size,
            "Exit",
            Colors.RED,
            theme=self.current_theme,
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
        nav_width = int(60 * (1.0 if self.fullscreen else 0.75))
        nav_height = int(80 * (1.0 if self.fullscreen else 0.75))
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
        self.credit_button = Button(
            0, 0, 160, 36, "Add Credit", Colors.YELLOW, theme=self.current_theme
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
                    except Exception:
                        # In tests, pygame mouse may not be available - ignore
                        pass
                    self.config_equalizer_button.update(event.pos)
                    self.config_fullscreen_button.update(event.pos)
                    self.config_choose_music_button.update(event.pos)

                    for theme_name, btn in self.theme_buttons:
                        btn.update(event.pos)
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
                    if self.play_button.is_clicked(event.pos):
                        self._player_safe_call("play")
                    elif self.pause_button.is_clicked(event.pos):
                        if self.player and self.player.is_paused:
                            self._player_safe_call("resume")
                        elif self.player:
                            self._player_safe_call("pause")
                    elif self.stop_button.is_clicked(event.pos):
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
                ]:
                    if not self.config_screen_open:
                        self.handle_number_input(event)

                # Enter to execute selection
                elif event.key == pygame.K_RETURN:
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

                # Show confirmation message
                self.config_message = f"Theme changed to {theme_name.capitalize()}"
                self.config_message_timer = 180
                print(f"Theme switched to: {theme_name}")

                # Clear caches when theme changes for optimal performance
                self.clear_caches()
                break

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
                    name_text, True, Colors.WHITE if not sel else Colors.YELLOW
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
        title = self.large_font.render("Equalizer", True, Colors.WHITE)
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
        title = self.get_cached_text("JukeBox", self.large_font, Colors.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, text_y))
        self.screen.blit(title, title_rect)

        # Top controls layout (volume slider left, playback buttons centered, config button right)
        controls_margin_top = (
            self.header_height + 20
        )  # Increased margin to avoid title bar overlap
        button_height = 50  # Match square button size
        media_button_size = 50  # Square buttons
        spacing = 12
        # Volume slider positioning
        volume_label = self.small_font.render("Volume", True, Colors.WHITE)
        self.screen.blit(volume_label, (self.margin, controls_margin_top + 2))

        self.volume_slider.x = self.margin
        self.volume_slider.y = controls_margin_top + 25  # Adjusted for increased margin
        self.volume_slider.width = 220
        self.volume_slider.height = 20
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
            empty_msg = self.medium_font.render("No albums found", True, Colors.YELLOW)
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

                msg = self.medium_font.render("Confirm Exit", True, Colors.BLACK)
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
        col2_x = left_edge + (available_space - col2_width) // 2

        # Two rows within content area
        row1_y = content_top + 10
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

        # LEFT COLUMN - Two albums (each taking half height)
        if len(albums) > 0:
            card_h = (content_height // 2) + 15  # Half height plus extra space
            # Only draw if indices are valid
            if left_album_1 >= 0 and left_album_1 < len(albums):
                self.draw_album_card(
                    albums[left_album_1], col1_x, row1_y, col1_width - 10, card_h
                )
            if left_album_2 >= 0 and left_album_2 < len(albums):
                self.draw_album_card(
                    albums[left_album_2], col1_x, row2_y, col1_width - 10, card_h
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
            card_h = (content_height // 2) + 15  # Half height plus extra space
            # Only draw if indices are valid
            if right_album_1 >= 0 and right_album_1 < len(albums):
                self.draw_album_card(
                    albums[right_album_1], col3_x, row1_y, col3_width - 10, card_h
                )
            if right_album_2 >= 0 and right_album_2 < len(albums):
                self.draw_album_card(
                    albums[right_album_2], col3_x, row2_y, col3_width - 10, card_h
                )

        # Credit UI placed under the two right column album cards
        try:
            # Compute a centered position within the right column
            credit_w = min(self.credit_button.rect.width, col3_width - 40)
            credit_x = col3_x + (col3_width - credit_w) // 2
            # Lower the credit button slightly to give breathing room
            credit_y = row2_y + card_h + 27  # moved down by 15px
            self.credit_button.rect.x = credit_x
            self.credit_button.rect.y = credit_y
            self.credit_button.rect.width = credit_w
            self.credit_button.draw(self.screen, self.small_font)

            # Draw current credit count underneath the button
            credits = 0
            if self.player:
                try:
                    credits = self.player.get_credits()
                except Exception:
                    credits = 0
            credit_txt = self.small_font.render(f"Credits: {credits}", True, Colors.YELLOW)
            txt_rect = credit_txt.get_rect(center=(credit_x + credit_w // 2, credit_y + self.credit_button.rect.height + 12))
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
            queue_surface = self.small_font.render(queue_text, True, Colors.WHITE)
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
            msg = self.medium_font.render("Confirm Exit", True, Colors.BLACK)
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

    def draw_album_card(self, album, x: int, y: int, width: int, height: int) -> None:
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
            album_num_text = self.large_font.render(
                f"{album.album_id:02d}", True, Colors.BLACK
            )
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
            album_num_text = self.large_font.render(
                f"{album.album_id:02d}", True, Colors.BLACK
            )
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

        # Text content (left side) - adjust spacing for fullscreen
        line_height = 24 if self.fullscreen else 16
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
        artist_text1 = artist_font.render(artist_line1, True, Colors.BLACK)
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
        current_y += line_height

        # Draw second line of artist if needed
        if artist_line2:
            current_y += 2  # Add 2px spacing between artist lines
            artist_text2 = artist_font.render(artist_line2, True, Colors.BLACK)
            self.screen.blit(artist_text2, (text_x, current_y))
            current_y += line_height

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
        album_text1 = album_font.render(album_line1, True, Colors.DARK_GRAY)
        self.screen.blit(album_text1, (text_x, current_y))
        current_y += line_height

        # Draw second line of album title if needed
        if album_line2:
            album_text2 = album_font.render(album_line2, True, Colors.DARK_GRAY)
            self.screen.blit(album_text2, (text_x, current_y))
            current_y += line_height

        spacing_after_album = 4 if self.fullscreen else 2
        current_y += spacing_after_album

        # Track count - use larger font in fullscreen
        count_font = self.small_medium_font if self.fullscreen else self.tiny_font
        track_count_text = count_font.render(
            f"{len(album.tracks)} tracks", True, Colors.BLUE
        )
        self.screen.blit(track_count_text, (text_x, current_y))
        spacing_after_count = 5 if self.fullscreen else 3
        current_y += line_height + spacing_after_count

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
        for i, track in enumerate(album.tracks[:max_tracks]):
            if current_y + track_line_height < y + card_height - padding:
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
                    track_font = pygame.font.SysFont("Arial", font_size)
                except Exception:
                    # Fall back to pre-created fonts on any error
                    if self.fullscreen:
                        track_font = self.track_list_font_fullscreen if compact else self.small_font
                    else:
                        track_font = self.track_list_font if compact else self.tiny_font
                track_text = track_font.render(f"{i+1:2d}. {title}", True, Colors.GRAY)
                self.screen.blit(track_text, (text_x + 5, current_y))
                current_y += track_line_height

    def draw_empty_now_playing(self, x: int, y: int, width: int, height: int) -> None:
        """Draw empty 'Now Playing' box when nothing is playing"""
        display_height = max(200, height)
        display_rect = pygame.Rect(x, y, width, display_height)

        # Draw display background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, display_rect)
        pygame.draw.rect(self.screen, Colors.YELLOW, display_rect, 3)

        # Draw "Now Playing" header
        padding = 15
        content_x = x + padding
        content_y = y + padding

        label_text = self.medium_font.render("Now Playing", True, Colors.YELLOW)
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
            album_num_text = self.large_font.render(
                f"{album.album_id:02d}", True, Colors.BLACK
            )
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

        label_text = self.medium_font.render("Now Playing", True, Colors.YELLOW)
        label_rect = label_text.get_rect(center=(x + width // 2, text_y))
        self.screen.blit(label_text, label_rect)

        if self.last_track_info:
            # Song title (large, centered at top)
            title_text = self.large_font.render(
                self.last_track_info["title"], True, Colors.WHITE
            )
            title_rect = title_text.get_rect(center=(x + width // 2, text_y + 35))
            self.screen.blit(title_text, title_rect)

            # Selection info (centered, below title) - medium font, smaller than title
            selection_text = self.medium_font.render(
                f"Selection {self.last_track_info['album_id']:02d} {self.last_track_info['track_index'] + 1:02d}",
                True,
                Colors.LIGHT_GRAY,
            )
            selection_rect = selection_text.get_rect(
                center=(x + width // 2, text_y + 85)
            )
            self.screen.blit(selection_text, selection_rect)
        else:
            placeholder = self.medium_font.render("--", True, Colors.LIGHT_GRAY)
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
        pad_x = self.width // 2 - total_width // 2

        # Position keypad lower in windowed mode to account for taller now playing area
        if self.fullscreen:
            pad_y = self.height - self.bottom_area_height - int(35 * scale_factor)
        else:
            # Move keypad significantly lower in windowed mode
            pad_y = self.height - self.bottom_area_height + int(20 * scale_factor)

        # Draw semi-transparent black border around keypad (15% opacity)
        border_padding = int(12 * scale_factor)
        border_rect = pygame.Rect(
            pad_x - border_padding,
            pad_y - border_padding - int(40 * scale_factor),
            total_width + border_padding * 2,
            pad_button_h * 4 + spacing * 3 + int(60 * scale_factor),
        )
        # Create semi-transparent surface
        border_surface = pygame.Surface(
            (border_rect.width, border_rect.height), pygame.SRCALPHA
        )
        border_surface.fill((0, 0, 0, int(255 * 0.15)))  # Black at 15% opacity
        self.screen.blit(border_surface, border_rect.topleft)

        # Scale navigation button positions and sizes
        nav_button_w = int(60 * scale_factor)
        nav_button_h = int(80 * scale_factor)
        nav_distance = int(40 * scale_factor)

        # Update navigation button sizes
        self.left_nav_button.rect.width = nav_button_w
        self.left_nav_button.rect.height = nav_button_h
        self.right_nav_button.rect.width = nav_button_w
        self.right_nav_button.rect.height = nav_button_h

        # Position navigation buttons on either side of keypad - equidistant
        button_y = pad_y + int(30 * scale_factor)
        left_button_x = pad_x - nav_distance - nav_button_w
        right_button_x = pad_x + total_width + nav_distance

        self.left_nav_button.rect.x = left_button_x
        self.left_nav_button.rect.y = button_y
        self.right_nav_button.rect.x = right_button_x
        self.right_nav_button.rect.y = button_y

        # Draw navigation buttons
        font_to_use = self.medium_font if self.fullscreen else self.small_font
        self.left_nav_button.draw(self.screen, font_to_use)
        self.right_nav_button.draw(self.screen, font_to_use)

        # Draw label
        label_font = self.small_font
        pad_label = label_font.render("4-Digit Selection Pad:", True, Colors.WHITE)
        label_rect = pad_label.get_rect(
            center=(self.width // 2, pad_y - int(25 * scale_factor))
        )
        self.screen.blit(pad_label, label_rect)

        # Choose appropriate font for buttons based on scale
        button_font = self.medium_font if self.fullscreen else self.small_font

        # Update button sizes and positions - draw all buttons properly
        # First 9 buttons (1-9) in 3x3 grid
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
        if len(self.number_pad_buttons) > 9:
            btn_0 = self.number_pad_buttons[9]
            btn_0.rect.width = pad_button_w
            btn_0.rect.height = pad_button_h
            btn_0.rect.x = pad_x
            btn_0.rect.y = pad_y + 3 * (pad_button_h + spacing)
            btn_0.draw(self.screen, button_font)

        # Draw backspace button (index 10) - middle position in row 4
        if len(self.number_pad_buttons) > 10:
            btn_back = self.number_pad_buttons[10]
            btn_back.rect.width = pad_button_w
            btn_back.rect.height = pad_button_h
            btn_back.rect.x = pad_x + (pad_button_w + spacing)
            btn_back.rect.y = pad_y + 3 * (pad_button_h + spacing)
            btn_back.draw(self.screen, button_font)

        # Draw CLR button (index 11) - left side of row 5
        if len(self.number_pad_buttons) > 11:
            btn_clr = self.number_pad_buttons[11]
            btn_clr.rect.width = int(pad_button_w * 1.6)  # Adjusted for wider buttons
            btn_clr.rect.height = pad_button_h
            btn_clr.rect.x = pad_x
            btn_clr.rect.y = pad_y + 4 * (pad_button_h + spacing)
            btn_clr.draw(self.screen, button_font)

        # Draw ENT button (index 12) - right side of row 5
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

        # Draw selection display above pad
        if self.selection_mode:
            selection_display = f"Selection: {self.selection_buffer:<4}"
            selection_color = Colors.YELLOW
            selection_text = self.medium_font.render(
                selection_display, True, selection_color
            )
            selection_rect = selection_text.get_rect(
                center=(self.width // 2, pad_y - 40)
            )  # Adjusted position
            self.screen.blit(selection_text, selection_rect)

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
        theme_title = self.medium_font.render("Theme Selection", True, Colors.YELLOW)
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
        name_text = self.small_font.render(theme_name.capitalize(), True, Colors.WHITE)
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

    def draw_config_screen(self) -> None:
        """Draw the configuration screen with improved organization"""
        self.screen.fill(Colors.DARK_GRAY)

        # Update message timer
        if self.config_message_timer > 0:
            self.config_message_timer -= 1

        # Draw title
        title = self.large_font.render("Configuration", True, Colors.WHITE)
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
        settings_header = self.medium_font.render("Settings", True, Colors.YELLOW)
        self.screen.blit(settings_header, (left_x, settings_y))

        config_y = settings_y + 40
        line_height = 36

        config_items = [
            ("Auto Play Next Track", self.config.get("auto_play_next")),
            ("Shuffle Enabled", self.config.get("shuffle_enabled")),
            ("Show Album Art", self.config.get("show_album_art")),
            ("Keyboard Shortcuts", self.config.get("keyboard_shortcut_enabled")),
            ("Fullscreen Mode", self.fullscreen),
        ]

        for i, (label, value) in enumerate(config_items):
            y = config_y + i * line_height
            label_text = self.small_font.render(f"{label}:", True, Colors.WHITE)
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
                self.config_density_slider.draw(self.screen, self.small_font)
                dval = float(self.config.get("track_list_density", 0.8))
                txt = self.small_font.render(f"{dval:.2f}", True, Colors.LIGHT_GRAY)
                self.screen.blit(txt, (den_x + self.config_density_slider.width + 10, den_y + 8))
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
