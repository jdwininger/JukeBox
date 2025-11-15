"""
UI Module - Handles the graphical user interface
"""
import pygame
import os
from src.player import MusicPlayer
from src.album_library import AlbumLibrary
from src.config import Config
from src.audio_effects import Equalizer
from src.widgets import Slider, VerticalSlider
from typing import Tuple, List


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
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int] = Colors.GRAY, theme=None, is_gear_icon: bool = False, icon_type: str = None):
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
                config_img = self.theme.get_media_button_image('config')
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
                button_img = self.theme.get_button_image('hover' if self.is_hovered else 'normal')
                if button_img and not (self.is_gear_icon or self.icon_type):
                    # Only use theme background for regular text buttons
                    scaled_img = pygame.transform.scale(button_img, (self.rect.width, self.rect.height))
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
                config_img = self.theme.get_media_button_image('config')
                if config_img:
                    # Scale image to button size
                    scaled_img = pygame.transform.scale(config_img, (self.rect.width, self.rect.height))
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
                    scaled_img = pygame.transform.scale(media_img, (self.rect.width, self.rect.height))
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
        
        if self.icon_type == 'play':
            # Draw play triangle (pointing right)
            triangle_points = [
                (center_x - icon_size//2, center_y - icon_size//2),
                (center_x - icon_size//2, center_y + icon_size//2),
                (center_x + icon_size//2, center_y)
            ]
            pygame.draw.polygon(surface, color, triangle_points)
            
        elif self.icon_type == 'pause':
            # Draw pause (two vertical bars)
            bar_width = icon_size // 4
            bar_height = icon_size
            left_bar = pygame.Rect(center_x - icon_size//3, center_y - bar_height//2, bar_width, bar_height)
            right_bar = pygame.Rect(center_x + icon_size//6, center_y - bar_height//2, bar_width, bar_height)
            pygame.draw.rect(surface, color, left_bar)
            pygame.draw.rect(surface, color, right_bar)
            
        elif self.icon_type == 'stop':
            # Draw stop (square)
            stop_rect = pygame.Rect(center_x - icon_size//2, center_y - icon_size//2, icon_size, icon_size)
            pygame.draw.rect(surface, color, stop_rect)
    
    def update(self, pos: Tuple[int, int]) -> None:
        """Update button hover state"""
        self.is_hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button is clicked"""
        return self.rect.collidepoint(pos)
    
    def apply_brightness_filter(self, image: pygame.Surface, brightness: float) -> pygame.Surface:
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
        if digit == 'CLR':
            self.color = Colors.RED
            self.hover_color = (255, 100, 100)
        elif digit == 'ENT':
            self.color = Colors.GREEN
            self.hover_color = (100, 255, 100)
        elif digit == '<':
            self.color = Colors.BLUE
            self.hover_color = (100, 150, 255)


class UI:
    """Main UI class for the JukeBox application"""
    
    def __init__(self, player: MusicPlayer, library: AlbumLibrary, config: Config, theme_manager):
        """
        Initialize the UI
        
        Args:
            player: MusicPlayer instance
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
        self.width = int(self.config.get('window_width', 1280))
        self.height = int(self.config.get('window_height', 800))
        self.fullscreen = self.config.get('fullscreen', False)
        
        # Set display mode based on fullscreen setting
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual fullscreen dimensions
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
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
        self.large_font = pygame.font.SysFont('Arial', 36)
        self.medium_font = pygame.font.SysFont('Arial', 20)
        self.small_medium_font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.tiny_font = pygame.font.SysFont('Arial', 10)
        
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
        
        # Audio effects
        self.equalizer = Equalizer()

        
        # UI state for effects
        self.show_equalizer = False
        # Persistent now playing track info; retains last track details between stops
        self.last_track_info = None
        
        # Album view offset for side navigation
        self.browse_position = 0  # Absolute position when browsing, starts showing albums 1-4

        # Screen mode: 'main', 'equalizer', 'config'
        self.screen_mode = 'main'
        # Album art cache
        self.album_art_cache = {}
        
        # Create buttons
        self.setup_buttons()
    
    def setup_buttons(self) -> None:
        """Setup UI buttons"""
        # Media control buttons are now square
        media_button_size = 50  # Square buttons
        
        controls_y = self.header_height + 10
        spacing = 10
        x = self.margin
        
        # Playback controls (left only) - now square
        self.play_button = Button(x, controls_y, media_button_size, media_button_size, "Play", Colors.GREEN, theme=self.current_theme, icon_type='play')
        x += media_button_size + spacing
        self.pause_button = Button(x, controls_y, media_button_size, media_button_size, "Pause", Colors.BLUE, theme=self.current_theme, icon_type='pause')
        x += media_button_size + spacing
        self.stop_button = Button(x, controls_y, media_button_size, media_button_size, "Stop", Colors.RED, theme=self.current_theme, icon_type='stop')
        
        # Export and Config + Album nav (right side anchored) - config button also square
        right_spacing = spacing
        right_x = self.width - self.margin
        # Place from right to left
        self.config_button = Button(right_x - media_button_size, controls_y, media_button_size, media_button_size, "Config", Colors.YELLOW, theme=self.current_theme, is_gear_icon=True)
        
        # Side navigation buttons for main screen album browsing (beside keypad)
        # These will be positioned dynamically in draw_number_pad_centered()
        # Make them taller than wide and scale based on screen mode
        nav_width = int(60 * (1.0 if self.fullscreen else 0.75))
        nav_height = int(80 * (1.0 if self.fullscreen else 0.75))
        self.left_nav_button = Button(0, 0, nav_width, nav_height, "<", Colors.BLUE, theme=self.current_theme, icon_type='left')
        self.right_nav_button = Button(0, 0, nav_width, nav_height, ">", Colors.BLUE, theme=self.current_theme, icon_type='right')
        # Number pad (bottom right) — initialized inline below
        
        # Audio controls
        self.setup_audio_controls()
        
        # Config screen buttons
        self.setup_config_buttons()
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
        for i, digit in enumerate(['7', '8', '9']):
            x = pad_x + i * (button_w + spacing)
            y = pad_y
            btn = NumberPadButton(x, y, button_w, button_h, digit, theme=self.current_theme)
            self.number_pad_buttons.append(btn)
        
        # Row 2: 4 5 6
        for i, digit in enumerate(['4', '5', '6']):
            x = pad_x + i * (button_w + spacing)
            y = pad_y + (button_h + spacing)
            btn = NumberPadButton(x, y, button_w, button_h, digit, theme=self.current_theme)
            self.number_pad_buttons.append(btn)
        
        # Row 3: 1 2 3
        for i, digit in enumerate(['1', '2', '3']):
            x = pad_x + i * (button_w + spacing)
            y = pad_y + 2 * (button_h + spacing)
            btn = NumberPadButton(x, y, button_w, button_h, digit, theme=self.current_theme)
            self.number_pad_buttons.append(btn)
        
        # Row 4: 0 < (backspace)
        btn_0 = NumberPadButton(pad_x, pad_y + 3 * (button_h + spacing), button_w, button_h, '0', theme=self.current_theme)
        self.number_pad_buttons.append(btn_0)
        
        btn_backspace = NumberPadButton(pad_x + (button_w + spacing), pad_y + 3 * (button_h + spacing), button_w, button_h, '<', theme=self.current_theme)
        self.number_pad_buttons.append(btn_backspace)
        
        # Row 5: CLR ENT (clear and enter)
        btn_clr = NumberPadButton(pad_x, pad_y + 4 * (button_h + spacing), int(button_w * 1.5 + spacing), button_h, 'CLR', theme=self.current_theme)
        self.number_pad_buttons.append(btn_clr)
        
        btn_ent = NumberPadButton(pad_x + int(button_w * 1.5 + spacing * 2), pad_y + 4 * (button_h + spacing), int(button_w * 1.5), button_h, 'ENT', theme=self.current_theme)
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
            initial_val=self.config.get('volume', 0.7) * 100,
                label="",  # Hide label on main screen (slider only)
            theme=self.current_theme
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
                x=x, y=eq_start_y, width=30, height=eq_slider_height,
                min_val=-12.0, max_val=12.0, initial_val=0.0,
                label=f"Band {i+1}",
                theme=self.current_theme
            )
            self.eq_sliders.append(slider)

        # Load equalizer values from config if present
        eq_vals = self.config.get('equalizer_values')
        if isinstance(eq_vals, list) and len(eq_vals) == 5:
            for i, v in enumerate(eq_vals):
                try:
                    self.eq_sliders[i].set_value(float(v))
                except Exception:
                    pass

        # Equalizer screen buttons
        self.eq_back_button = Button(self.width - 140, 30, 110, 36, "Back", Colors.RED, theme=self.current_theme)
        self.eq_save_button = Button(self.width - 260, 30, 110, 36, "Save", Colors.GREEN, theme=self.current_theme)
        self.eq_preset_buttons = []
        preset_names = list(self.equalizer.get_presets().keys())
        # Preset buttons lowered to avoid slider value text overlap
        for i, name in enumerate(preset_names):
            btn = Button(80 + i * 140, 520, 130, 40, name, Colors.BLUE, theme=self.current_theme)
            self.eq_preset_buttons.append((name, btn))


    
    def setup_config_buttons(self) -> None:
        """Setup configuration screen buttons"""
        button_width = 120
        button_height = 40
        
        config_y = 300
        center_x = self.width // 2
        
        # Config screen buttons
        self.config_rescan_button = Button(center_x - 260, config_y, button_width, button_height, "Rescan", Colors.GREEN, theme=self.current_theme)
        self.config_reset_button = Button(center_x - 120, config_y, button_width, button_height, "Reset", Colors.YELLOW, theme=self.current_theme)
        self.config_close_button = Button(center_x + 20, config_y, button_width, button_height, "Close", Colors.RED, theme=self.current_theme)
        self.config_extract_art_button = Button(center_x + 160, config_y, button_width, button_height, "Extract Art", (128, 0, 128), theme=self.current_theme)  # Purple color
        # Audio effects access button
        effects_y = config_y + 60
        self.config_equalizer_button = Button(center_x - 120, effects_y, button_width, button_height, "Equalizer", Colors.BLUE, theme=self.current_theme)
        self.config_fullscreen_button = Button(center_x + 20, effects_y, button_width, button_height, "Fullscreen", Colors.GRAY, theme=self.current_theme)
        
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
            is_selected = theme_name == self.config.get('theme', 'dark')
            color = Colors.GREEN if is_selected else Colors.GRAY
            btn = Button(x, start_y, button_width, button_height, theme_name.capitalize(), color, theme=self.current_theme)
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
            pygame.K_0: '0', pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3',
            pygame.K_4: '4', pygame.K_5: '5', pygame.K_6: '6', pygame.K_7: '7',
            pygame.K_8: '8', pygame.K_9: '9'
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
            print(f"Invalid selection: {self.selection_buffer if self.selection_buffer else 'empty'} (need 4 digits)")
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
            self.player.play(album_id=album_id, track_index=track_index)
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
            if event.type == pygame.QUIT:
                self.running = False
                return  # Early exit on quit
            elif event.type == pygame.VIDEORESIZE:
                if not self.fullscreen:  # Only handle resize if not in fullscreen
                    # Update internal dimensions and recreate screen surface
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    # Optionally clamp minimum size for layout integrity
                    if self.width < 800 or self.height < 600:
                        self.width = max(800, self.width)
                        self.height = max(600, self.height)
                        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                
                # Invalidate cached background on resize
                self._cached_background = None
                self._needs_full_redraw = True
                # Invalidate cached background on resize
                self._cached_background = None
                self._needs_full_redraw = True
                # Navigation button positions are now handled in draw_number_pad_centered()
            
            elif event.type == pygame.MOUSEMOTION:
                if self.config_screen_open:
                    self.config_rescan_button.update(event.pos)
                    self.config_reset_button.update(event.pos)
                    self.config_close_button.update(event.pos)
                    self.config_extract_art_button.update(event.pos)
                    self.config_equalizer_button.update(event.pos)
                    self.config_fullscreen_button.update(event.pos)

                    for theme_name, btn in self.theme_buttons:
                        btn.update(event.pos)
                elif self.screen_mode == 'equalizer':
                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    for slider in self.eq_sliders:
                        slider.update(event.pos, mouse_pressed)
                    self.eq_back_button.update(event.pos)
                    self.eq_save_button.update(event.pos)
                    for _, btn in self.eq_preset_buttons:
                        btn.update(event.pos)
                elif self.screen_mode == 'fader':
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
                    self.left_nav_button.update(event.pos)
                    self.right_nav_button.update(event.pos)
                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    self.volume_slider.update(event.pos, mouse_pressed)
                    if self.show_equalizer:
                        for slider in self.eq_sliders:
                            slider.update(event.pos, mouse_pressed)
                    for btn in self.number_pad_buttons:
                        btn.update(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                        self.screen_mode = 'equalizer'
                        self.config_screen_open = False
                        self.clear_caches()  # Clear caches when opening equalizer
                    elif self.config_fullscreen_button.is_clicked(event.pos):
                        self.toggle_fullscreen()
                        self.setup_config_buttons()  # Refresh button positions

                    else:
                        # Check theme button clicks
                        self.handle_theme_selection(event.pos)
                elif self.screen_mode == 'equalizer':
                    # Equalizer screen interactions
                    if self.eq_back_button.is_clicked(event.pos):
                        # Save before leaving
                        self.config.set('equalizer_values', [s.get_value() for s in self.eq_sliders])
                        self.config.save()
                        self.screen_mode = 'main'
                    elif self.eq_save_button.is_clicked(event.pos):
                        self.config.set('equalizer_values', [s.get_value() for s in self.eq_sliders])
                        self.config.save()
                    else:
                        # Preset buttons
                        for name, btn in self.eq_preset_buttons:
                            if btn.is_clicked(event.pos):
                                preset_func = self.equalizer.get_presets().get(name)
                                if preset_func:
                                    preset_func()
                                    # Update sliders to equalizer model
                                    for i, gain in enumerate(self.equalizer.get_all_bands()):
                                        self.eq_sliders[i].set_value(gain)
                                break
                elif self.screen_mode == 'fader':
                    if self.fader_back_button.is_clicked(event.pos):
                        # Save current fader settings
                        self.config.set('fader_volume', self.audio_fader.get_volume() * 100)
                        self.config.set('fade_speed', self.audio_fader.fade_speed * 1000)
                        self.config.save()
                        self.screen_mode = 'main'
                    elif self.fader_save_button.is_clicked(event.pos):
                        self.config.set('fader_volume', self.audio_fader.get_volume() * 100)
                        self.config.set('fade_speed', self.audio_fader.fade_speed * 1000)
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
                        self.player.play()
                    elif self.pause_button.is_clicked(event.pos):
                        if self.player.is_paused:
                            self.player.resume()
                        else:
                            self.player.pause()
                    elif self.stop_button.is_clicked(event.pos):
                        self.player.stop()
                    elif self.config_button.is_clicked(event.pos):
                        self.config_screen_open = True
                        self.config_message = ""
                        self.clear_caches()  # Clear caches when opening config
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
                    else:
                        # Check number pad buttons
                        self.handle_number_pad_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                # Close config screen with Escape
                if event.key == pygame.K_ESCAPE:
                    if self.config_screen_open:
                        self.config_screen_open = False
                    else:
                        self.selection_buffer = ""
                        self.selection_mode = False
                
                # Number keys for 4-digit song selection
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    if not self.config_screen_open:
                        self.handle_number_input(event)
                
                # Enter to execute selection
                elif event.key == pygame.K_RETURN:
                    # Check for Alt+Enter for fullscreen toggle
                    if pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]:
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
                        self.volume_slider.value = new_volume * 100  # Convert to 0-100 range
                elif event.key == pygame.K_DOWN:
                    if not self.config_screen_open:
                        # Decrease volume and update slider
                        new_volume = max(0.0, self.player.volume - 0.1)
                        self.player.set_volume(new_volume)
                        self.volume_slider.value = new_volume * 100  # Convert to 0-100 range
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
                if btn.digit == 'CLR':
                    self.selection_buffer = ""
                    self.selection_mode = False
                elif btn.digit == 'ENT':
                    self.execute_selection()
                elif btn.digit == '<':
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
        self.config_message = f"Rescan complete! Found {len(self.library.get_albums())} albums"
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
        extracted = stats['extracted']
        existing = stats['existing'] 
        failed = stats['failed']
        self.config_message = f"Art: {extracted} extracted, {existing} existing, {failed} failed"
        self.config_message_timer = 240  # Display results for 4 seconds
    
    def handle_theme_selection(self, pos: Tuple[int, int]) -> None:
        """Handle theme button clicks"""
        for theme_name, btn in self.theme_buttons:
            if btn.is_clicked(pos):
                # Switch to the selected theme
                self.theme_manager.set_current_theme(theme_name)
                self.config.set('theme', theme_name)
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
        self.player.set_volume(slider_volume)
        
        # Update equalizer bands
        for i, slider in enumerate(self.eq_sliders):
            gain = slider.get_value()
            self.equalizer.set_band(i, gain)
    
    def get_cached_text(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int]) -> pygame.Surface:
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
                    self._cached_background = pygame.transform.scale(background, current_size)
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
    
    def draw(self) -> None:
        """Draw the UI"""
        if self.config_screen_open:
            self.draw_config_screen()
        elif self.screen_mode == 'equalizer':
            self.draw_equalizer_screen()
        else:
            self.draw_main_screen()

    def draw_equalizer_screen(self) -> None:
        """Draw the full-screen equalizer adjustment UI"""
        # Background - request specific size for SVG optimization
        background = self.current_theme.get_background(self.width, self.height)
        if background:
            # If we got a pre-scaled SVG, use it directly, otherwise scale
            if background.get_size() == (self.width, self.height):
                self.screen.blit(background, (0, 0))
            else:
                scaled_bg = pygame.transform.scale(background, (self.width, self.height))
                self.screen.blit(scaled_bg, (0, 0))
        else:
            self.screen.fill(Colors.DARK_GRAY)

        # Title (leave left margin clear of buttons)
        title = self.large_font.render("Equalizer", True, Colors.WHITE)
        self.screen.blit(title, (40, 32))

        # Instructions
        instructions = self.small_font.render("Adjust gains, apply preset, then Save or Back", True, Colors.LIGHT_GRAY)
        self.screen.blit(instructions, (40, 78))

        # Slider area
        band_names = ["60 Hz", "250 Hz", "1 kHz", "4 kHz", "16 kHz"]
        start_x = 120
        spacing = 150
        slider_top = 140
        slider_height = 300

        # Draw each vertical slider with label & value
        for i, (slider, name) in enumerate(zip(self.eq_sliders, band_names)):
            slider.x = start_x + i * spacing
            slider.y = slider_top
            slider.height = slider_height
            slider.draw(self.screen, self.small_font, track_color=Colors.GRAY, knob_color=Colors.BLUE, fill_color=Colors.BLUE)

            # Label
            label = self.small_font.render(name, True, Colors.WHITE)
            label_rect = label.get_rect(center=(slider.x + slider.width // 2, slider_top - 25))
            self.screen.blit(label, label_rect)

            # Value
            gain = slider.get_value()
            val_color = Colors.GREEN if gain > 0 else (Colors.RED if gain < 0 else Colors.YELLOW)
            val_text = self.small_font.render(f"{gain:.1f} dB", True, val_color)
            val_rect = val_text.get_rect(center=(slider.x + slider.width // 2, slider_top + slider_height + 15))
            self.screen.blit(val_text, val_rect)

        # Preset buttons
        for _, btn in self.eq_preset_buttons:
            btn.draw(self.screen, self.small_font)

        # Save / Back buttons
        # Save / Back buttons (ensure they stay top-right even if window resized)
        self.eq_save_button.rect.x = self.width - 260
        self.eq_back_button.rect.x = self.width - 140
        self.eq_save_button.rect.y = 30
        self.eq_back_button.rect.y = 30
        self.eq_save_button.draw(self.screen, self.small_font)
        self.eq_back_button.draw(self.screen, self.small_font)

        pygame.display.flip()

    def draw_main_screen(self) -> None:
        """Draw the main playbook screen with 3-column 2-row layout"""
        # Always use cached background for consistent rendering
        background = self.get_cached_background()
        self.screen.blit(background, (0, 0))
        
        # Track changes for potential future optimizations
        current_volume = self.player.get_volume()
        current_track = self.player.get_current_track_info() if self.player.is_music_playing() else None
        self._last_volume = current_volume
        self._last_track_info = current_track
        
        # Draw title at top header area
        title = self.get_cached_text("JukeBox - Album Library", self.large_font, Colors.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, self.header_height // 2 + 2))
        self.screen.blit(title, title_rect)

        # Top controls layout (volume slider left, playback buttons centered, config button right)
        controls_margin_top = self.header_height + 5
        button_height = 50  # Match square button size
        media_button_size = 50  # Square buttons
        spacing = 12
        # Volume slider positioning
        volume_label = self.small_font.render("Volume", True, Colors.WHITE)
        self.screen.blit(volume_label, (self.margin, controls_margin_top + 2))
        
        self.volume_slider.x = self.margin
        self.volume_slider.y = controls_margin_top + 20  # leave room for its label
        self.volume_slider.width = 220
        self.volume_slider.height = 20
        self.volume_slider.draw(self.screen, self.small_font,
                                track_color=Colors.GRAY,
                                knob_color=Colors.GREEN,
                                fill_color=Colors.GREEN)
        # Playback buttons centering
        col_width = (self.width - self.margin * 4) // 3
        col2_x = self.margin * 2 + col_width
        center_x = col2_x + (col_width // 2)
        buttons_y = controls_margin_top + 15
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
        # Config button at top-right
        self.config_button.rect.x = self.width - self.margin - media_button_size
        self.config_button.rect.y = controls_margin_top + 10
        self.config_button.draw(self.screen, self.small_font)

        # Determine start of album content area below controls
        content_top = buttons_y + button_height + 25
        
        # Get albums for display
        albums = self.library.get_albums()
        
        # Handle empty library
        if len(albums) == 0:
            # Draw empty library message
            empty_msg = self.medium_font.render("No albums found", True, Colors.YELLOW)
            empty_msg_rect = empty_msg.get_rect(center=(self.width // 2, self.height // 2 - 60))
            self.screen.blit(empty_msg, empty_msg_rect)
            
            hint_msg = self.small_font.render(
                "Add music files to the 'music' directory and use Config > Rescan",
                True, Colors.LIGHT_GRAY
            )
            hint_msg_rect = hint_msg.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(hint_msg, hint_msg_rect)
            
            # Top controls already drawn above; avoid duplicate buttons
            
            # Draw side navigation buttons
            self.left_nav_button.draw(self.screen, self.small_font)
            self.right_nav_button.draw(self.screen, self.small_font)
            
            # Draw instructions at very bottom
            instructions = self.small_font.render(
                "C: Config | Space: Play/Pause | ↑↓: Volume",
                True, Colors.GRAY
            )
            self.screen.blit(instructions, (20, self.height - 25))
            
            pygame.display.flip()
            return
        
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
        left_album_1 = self.browse_position       # Top left: album 1
        left_album_2 = self.browse_position + 1   # Bottom left: album 2
        right_album_1 = self.browse_position + 2  # Top right: album 3
        right_album_2 = self.browse_position + 3  # Bottom right: album 4
        
        # LEFT COLUMN - Two albums (each taking half height)
        if len(albums) > 0:
            card_h = (content_height // 2) + 15  # Half height plus extra space
            # Only draw if indices are valid
            if left_album_1 >= 0 and left_album_1 < len(albums):
                self.draw_album_card(albums[left_album_1], col1_x, row1_y, col1_width - 10, card_h)
            if left_album_2 >= 0 and left_album_2 < len(albums):
                self.draw_album_card(albums[left_album_2], col1_x, row2_y, col1_width - 10, card_h)
        
        # CENTER COLUMN - Always show Now Playing, never browsed albums (smaller now)
        current_album_obj = self.player.get_current_album()
        
        # Make now playing window taller in windowed mode to push down keypad
        now_playing_height_factor = 0.85 if self.fullscreen else 0.95  # Taller in windowed mode
        now_playing_height = int(content_height * now_playing_height_factor) - 10
        
        if current_album_obj and self.player.is_music_playing():
            self.draw_current_album_display(current_album_obj, col2_x, row1_y, col2_width - 10, now_playing_height)
        else:
            # Show empty Now Playing box when nothing is playing
            self.draw_empty_now_playing(col2_x, row1_y, col2_width - 10, now_playing_height)
        
        # RIGHT COLUMN - Two albums (each taking half height)
        if len(albums) > 0:
            card_h = (content_height // 2) + 15  # Half height plus extra space
            # Only draw if indices are valid
            if right_album_1 >= 0 and right_album_1 < len(albums):
                self.draw_album_card(albums[right_album_1], col3_x, row1_y, col3_width - 10, card_h)
            if right_album_2 >= 0 and right_album_2 < len(albums):
                self.draw_album_card(albums[right_album_2], col3_x, row2_y, col3_width - 10, card_h)
        
        # Draw side navigation buttons
        self.left_nav_button.draw(self.screen, self.small_font)
        self.right_nav_button.draw(self.screen, self.small_font)
        
        # Top controls already drawn; skip duplicate playback button drawing
        
        # Draw number pad in center bottom
        self.draw_number_pad_centered()
        
        # Draw audio controls above number pad
        self.draw_audio_controls()
        
        # Draw instructions at very bottom
        instructions = self.small_font.render(
            "4-digit: Album(2) + Track(2) | C: Config | Space: Play/Pause | Alt+Enter: Fullscreen | ↑↓: Volume",
            True, Colors.GRAY
        )
        self.screen.blit(instructions, (20, self.height - 25))
        
        # Draw queue counter in lower right corner
        queue_count = len(self.player.queue)
        if queue_count > 0:
            queue_text = f"Queue: {queue_count} song{'s' if queue_count != 1 else ''}"
            queue_surface = self.small_font.render(queue_text, True, Colors.WHITE)
            queue_rect = queue_surface.get_rect()
            queue_x = self.width - queue_rect.width - 20
            queue_y = self.height - 25
            self.screen.blit(queue_surface, (queue_x, queue_y))
        
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
        art_size = min(content_height - 10, content_width // 2.2)  # About half width, square aspect
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
            border_rect = pygame.Rect(art_rect.x + 3 - border_padding, art_rect.y + 3 - border_padding, 
                                    text_rect.width + border_padding * 2, text_rect.height + border_padding * 2)
            pygame.draw.rect(self.screen, Colors.WHITE, border_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, border_rect, 2)
            self.screen.blit(album_num_text, (art_rect.x + 3, art_rect.y + 3))
        else:
            pygame.draw.rect(self.screen, Colors.GRAY, art_rect)
            album_num_text = self.large_font.render(f"{album.album_id:02d}", True, Colors.BLACK)
            # Position consistently with album art overlay (top-left corner)
            text_x = art_rect.x + 3
            text_y = art_rect.y + 3
            # Add white border around the number
            border_padding = 4  # Match the padding used for album art overlay
            border_rect = pygame.Rect(text_x - border_padding, text_y - border_padding,
                                    album_num_text.get_width() + border_padding * 2, 
                                    album_num_text.get_height() + border_padding * 2)
            pygame.draw.rect(self.screen, Colors.WHITE, border_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, border_rect, 2)
            self.screen.blit(album_num_text, (text_x, text_y))
        
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
            last_space = artist_text.rfind(' ', 0, wrap_point + 1)
            if last_space > 0:
                artist_line1 = artist_text[:last_space]
                artist_line2 = artist_text[last_space + 1:last_space + 17]  # Up to 16 more chars after the space
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
        artist_bg_rect = pygame.Rect(text_x - 2, current_y - 2, artist_rect.width + 4, artist_rect.height + 4)
        # Create transparent surface for padding
        padding_surface = pygame.Surface((artist_rect.width + 4, artist_rect.height + 4), pygame.SRCALPHA)
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
        current_y += spacing_after_artist + 4  # Add extra space after artist name + 4px between artist and album
        
        # Album title - use larger font in fullscreen with text wrapping (only wrap if not fullscreen)
        album_font = self.medium_font if self.fullscreen else self.small_medium_font
        album_title = album.title
        
        # Handle album title display based on mode
        if self.fullscreen:
            # In fullscreen, cut off at first space after 28 characters
            if len(album_title) > 28:
                # Find the first space at or after position 28
                first_space = album_title.find(' ', 28)
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
        track_count_text = count_font.render(f"{len(album.tracks)} tracks", True, Colors.BLUE)
        self.screen.blit(track_count_text, (text_x, current_y))
        spacing_after_count = 5 if self.fullscreen else 3
        current_y += line_height + spacing_after_count
        
        # Show all tracks that fit - adjust track line height for fullscreen
        track_line_height = 18 if self.fullscreen else 12
        max_tracks = min(len(album.tracks), (content_height - (current_y - text_y) - 10) // track_line_height)
        for i, track in enumerate(album.tracks[:max_tracks]):
            if current_y + track_line_height < y + card_height - padding:
                # Truncate track title to fit
                max_chars = max(15, int(text_width // 7))  # Ensure integer
                title = track['title'][:max_chars]
                if len(track['title']) > max_chars:
                    title += "..."
                # Use larger font for track listing in fullscreen
                track_font = self.small_font if self.fullscreen else self.tiny_font
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
        no_music_text = self.medium_font.render("Choose an album and song.", True, Colors.LIGHT_GRAY)
        text_rect = no_music_text.get_rect(center=(x + width // 2, center_y))
        self.screen.blit(no_music_text, text_rect)

    def draw_current_album_display(self, album, x: int, y: int, width: int, height: int) -> None:
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
            album_num_text = self.large_font.render(f"{album.album_id:02d}", True, Colors.BLACK)
            album_num_rect = album_num_text.get_rect(center=art_rect.center)
            # Add white border around the number
            border_padding = 6
            border_rect = pygame.Rect(album_num_rect.x - border_padding, album_num_rect.y - border_padding,
                                    album_num_rect.width + border_padding * 2, album_num_rect.height + border_padding * 2)
            pygame.draw.rect(self.screen, Colors.WHITE, border_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, border_rect, 2)
            self.screen.blit(album_num_text, album_num_rect)

        # Update persistent info if a track is actively playing from this album
        track = self.player.get_current_track()
        current_album = self.player.get_current_album()
        if track and current_album and self.player.is_playing and current_album.album_id == album.album_id:
            self.last_track_info = {
                'album_id': current_album.album_id,
                'track_index': self.player.current_track_index,
                'title': track['title'],
                'duration': track['duration_formatted']
            }

        # Text area (below album art)
        text_x = content_x
        text_y = content_y + art_size + padding
        
        label_text = self.medium_font.render("Now Playing", True, Colors.YELLOW)
        label_rect = label_text.get_rect(center=(x + width // 2, text_y))
        self.screen.blit(label_text, label_rect)
        
        if self.last_track_info:
            # Song title (large, centered at top)
            title_text = self.large_font.render(self.last_track_info['title'], True, Colors.WHITE)
            title_rect = title_text.get_rect(center=(x + width // 2, text_y + 35))
            self.screen.blit(title_text, title_rect)
            
            # Selection info (centered, below title) - medium font, smaller than title
            selection_text = self.medium_font.render(
                f"Selection {self.last_track_info['album_id']:02d} {self.last_track_info['track_index'] + 1:02d}",
                True, Colors.LIGHT_GRAY
            )
            selection_rect = selection_text.get_rect(center=(x + width // 2, text_y + 85))
            self.screen.blit(selection_text, selection_rect)
        else:
            placeholder = self.medium_font.render("--", True, Colors.LIGHT_GRAY)
            placeholder_rect = placeholder.get_rect(center=(x + width // 2, text_y + 35))
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
        base_spacing = 8   # Base spacing
        
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
            pad_button_h * 4 + spacing * 3 + int(60 * scale_factor)
        )
        # Create semi-transparent surface
        border_surface = pygame.Surface((border_rect.width, border_rect.height), pygame.SRCALPHA)
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
        label_rect = pad_label.get_rect(center=(self.width // 2, pad_y - int(25 * scale_factor)))
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
            selection_text = self.medium_font.render(selection_display, True, selection_color)
            selection_rect = selection_text.get_rect(center=(self.width // 2, pad_y - 40))  # Adjusted position
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
        
        # Draw section title
        theme_title = self.medium_font.render("Theme Selection", True, Colors.YELLOW)
        theme_title_rect = theme_title.get_rect(center=(self.width // 2, theme_section_y - 30))
        self.screen.blit(theme_title, theme_title_rect)
        
        # Draw theme buttons
        for theme_name, btn in self.theme_buttons:
            btn.draw(self.screen, self.small_font)
        
        # Draw theme preview if hovering
        for theme_name, btn in self.theme_buttons:
            if btn.is_hovered:
                # Position preview above theme buttons
                self.draw_theme_preview(theme_name, self.width // 2 - 100, theme_section_y - 130)
                break
    
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
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, 
                            pygame.Rect(x + 2, y + 2, preview_width - 4, 60))
        
        # Draw sample button preview
        btn_preview_x = x + 20
        btn_preview_y = y + 70
        btn_preview_width = 60
        btn_preview_height = 35
        
        btn_color = theme.get_color('button', Colors.GRAY)
        pygame.draw.rect(self.screen, btn_color, 
                        pygame.Rect(btn_preview_x, btn_preview_y, btn_preview_width, btn_preview_height))
        pygame.draw.rect(self.screen, Colors.WHITE, 
                        pygame.Rect(btn_preview_x, btn_preview_y, btn_preview_width, btn_preview_height), 1)
        
        # Draw sample slider preview
        slider_x = x + 90
        slider_y = y + 80
        track_color = theme.get_color('slider_track', Colors.GRAY)
        pygame.draw.rect(self.screen, track_color, pygame.Rect(slider_x, slider_y, 90, 4))
        knob_color = theme.get_color('slider_knob', Colors.LIGHT_GRAY)
        pygame.draw.circle(self.screen, knob_color, (slider_x + 45, slider_y + 2), 6)
        
        # Draw theme name
        name_text = self.small_font.render(theme_name.capitalize(), True, Colors.WHITE)
        self.screen.blit(name_text, (x + 20, y + preview_height + 5))

    def get_album_art(self, album):
        """Return cached album art surface or attempt to load one"""
        if album.album_id in self.album_art_cache:
            return self.album_art_cache[album.album_id]
        candidates = ['cover.jpg','cover.png','folder.jpg','folder.png','album.jpg','album.png','art.jpg','art.png']
        art_surface = None
        try:
            for name in candidates:
                path = os.path.join(album.directory, name)
                if os.path.isfile(path):
                    art_surface = pygame.image.load(path).convert_alpha()
                    break
        except Exception as e:
            print(f"Album art load failed for album {album.album_id:02d}: {e}")
        self.album_art_cache[album.album_id] = art_surface
        return art_surface

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
        
        # Left Column - Settings
        left_x = 50
        settings_y = 100
        
        # Settings section header
        settings_header = self.medium_font.render("Settings", True, Colors.YELLOW)
        self.screen.blit(settings_header, (left_x, settings_y))
        
        # Configuration toggles
        config_y = settings_y + 40
        line_height = 35
        
        config_items = [
            ("Auto Play Next Track", self.config.get('auto_play_next')),
            ("Shuffle Enabled", self.config.get('shuffle_enabled')),
            ("Show Album Art", self.config.get('show_album_art')),
            ("Keyboard Shortcuts", self.config.get('keyboard_shortcut_enabled')),
            ("Fullscreen Mode", self.fullscreen),
        ]
        
        for i, (label, value) in enumerate(config_items):
            y = config_y + i * line_height
            label_text = self.small_font.render(f"{label}:", True, Colors.WHITE)
            self.screen.blit(label_text, (left_x + 20, y))
            
            value_str = "ON" if value else "OFF"
            value_color = Colors.GREEN if value else Colors.RED
            value_text = self.small_font.render(value_str, True, value_color)
            self.screen.blit(value_text, (left_x + 280, y))
        
        # Library information section
        info_y = config_y + len(config_items) * line_height + 30
        info_header = self.medium_font.render("Library Info", True, Colors.YELLOW)
        self.screen.blit(info_header, (left_x, info_y))
        
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
            self.screen.blit(info_text, (left_x + 20, y))
        
        # Right Column - Actions
        right_x = self.width // 2 + 50
        
        # Library actions section
        actions_header = self.medium_font.render("Library Actions", True, Colors.YELLOW)
        self.screen.blit(actions_header, (right_x, settings_y))
        
        # Reposition library action buttons vertically
        action_y = settings_y + 50
        self.config_rescan_button.rect.x = right_x + 20
        self.config_rescan_button.rect.y = action_y
        self.config_rescan_button.draw(self.screen, self.small_font)
        
        self.config_extract_art_button.rect.x = right_x + 20
        self.config_extract_art_button.rect.y = action_y + 50
        self.config_extract_art_button.draw(self.screen, self.small_font)
        
        self.config_reset_button.rect.x = right_x + 20
        self.config_reset_button.rect.y = action_y + 100
        self.config_reset_button.draw(self.screen, self.small_font)
        
        # Audio effects section
        effects_y = action_y + 170
        effects_header = self.medium_font.render("Audio Effects", True, Colors.YELLOW)
        self.screen.blit(effects_header, (right_x, effects_y))
        
        self.config_equalizer_button.rect.x = right_x + 20
        self.config_equalizer_button.rect.y = effects_y + 40
        self.config_equalizer_button.draw(self.screen, self.small_font)
        
        # Visual effects section
        visual_effects_y = effects_y + 100
        visual_effects_header = self.medium_font.render("Visual Effects", True, Colors.YELLOW)
        self.screen.blit(visual_effects_header, (right_x, visual_effects_y))
        
        # Fullscreen button in Visual Effects section
        self.config_fullscreen_button.rect.x = right_x + 20
        self.config_fullscreen_button.rect.y = visual_effects_y + 40
        self.config_fullscreen_button.draw(self.screen, self.small_font)
        
        # Theme selection section (bottom center)
        self.draw_theme_selector()
        
        # Close button (top right)
        self.config_close_button.rect.x = self.width - 140
        self.config_close_button.rect.y = 20
        self.config_close_button.draw(self.screen, self.small_font)
        
        # Draw messages
        if self.config_message and self.config_message_timer > 0:
            msg_color = Colors.GREEN if "success" in self.config_message.lower() or "complete" in self.config_message.lower() else Colors.YELLOW
            message_text = self.medium_font.render(self.config_message, True, msg_color)
            message_rect = message_text.get_rect(center=(self.width // 2, self.height - 60))
            self.screen.blit(message_text, message_rect)
        
        # Draw instructions
        instructions = self.small_font.render(
            "ESC or Close button to exit | Alt+Enter: Toggle Fullscreen",
            True, Colors.GRAY
        )
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height - 30))
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
        self.config.set('window_width', self.width)
        self.config.set('window_height', self.height)
        self.config.set('fullscreen', self.fullscreen)
    
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
            windowed_width = self.config.get('window_width', 1200)
            windowed_height = self.config.get('window_height', 800)
            self.width = windowed_width
            self.height = windowed_height
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        # Save fullscreen state
        self.config.set('fullscreen', self.fullscreen)
        print(f"Switched to {'fullscreen' if self.fullscreen else 'windowed'} mode")
