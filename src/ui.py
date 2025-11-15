"""
UI Module - Handles the graphical user interface
"""
import pygame
import os
from src.player import MusicPlayer
from src.album_library import AlbumLibrary
from src.config import Config
from src.audio_effects import Equalizer, AudioFader
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
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int] = Colors.GRAY, theme=None):
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
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 50, 255) for c in color)
        self.is_hovered = False
        self.theme = theme
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button on the surface"""
        if self.theme:
            # Use theme images if available
            button_img = self.theme.get_button_image('hover' if self.is_hovered else 'normal')
            if button_img:
                scaled_img = pygame.transform.scale(button_img, (self.rect.width, self.rect.height))
                surface.blit(scaled_img, self.rect)
            else:
                # Fallback to color if image not available
                color = self.hover_color if self.is_hovered else self.color
                pygame.draw.rect(surface, color, self.rect)
                pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)
        else:
            # No theme, use color
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)
        
        text_surface = font.render(self.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, pos: Tuple[int, int]) -> None:
        """Update button hover state"""
        self.is_hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button is clicked"""
        return self.rect.collidepoint(pos)


class NumberPadButton(Button):
    """Number pad button with digit value"""
    
    def __init__(self, x: int, y: int, width: int, height: int, digit: str):
        """
        Initialize a number pad button
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            digit: Digit value (0-9 or special like 'CLR', 'ENT')
        """
        super().__init__(x, y, width, height, digit, Colors.GRAY)
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
        
        # Window setup
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("JukeBox - Album Library")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        
        # Fonts
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 18)
        
        # 4-digit selection system (AATT: Album Album Track Track)
        self.selection_buffer = ""
        self.selection_mode = False
        
        # Configuration screen state
        self.config_screen_open = False
        self.config_message = ""
        self.config_message_timer = 0
        
        # Audio effects
        self.equalizer = Equalizer()
        self.audio_fader = AudioFader(config.get('volume', 0.7))
        
        # UI state for effects
        self.show_equalizer = False
        
        # Album view offset for side navigation
        self.album_view_offset = 0  # Offset from current album for display
        
        # Create buttons
        self.setup_buttons()
    
    def setup_buttons(self) -> None:
        """Setup UI buttons"""
        button_width = 90
        button_height = 40
        
        # Playback controls (top left)
        self.play_button = Button(20, 20, button_width, button_height, "Play", Colors.GREEN)
        self.pause_button = Button(120, 20, button_width, button_height, "Pause", Colors.BLUE)
        self.stop_button = Button(220, 20, button_width, button_height, "Stop", Colors.RED)
        
        # Track navigation (top center)
        self.prev_track_button = Button(380, 20, button_width, button_height, "Prev Track", Colors.GRAY)
        self.next_track_button = Button(480, 20, button_width, button_height, "Next Track", Colors.GRAY)
        
        # Album navigation (top right)
        self.prev_album_button = Button(self.width - 200, 20, button_width, button_height, "Prev Album", Colors.GRAY)
        self.next_album_button = Button(self.width - 100, 20, button_width, button_height, "Next Album", Colors.GRAY)
        
        # Export and Config buttons
        self.export_button = Button(640, 20, button_width + 40, button_height, "Export CSV", Colors.YELLOW)
        self.config_button = Button(self.width - 300, 20, button_width, button_height, "Config", Colors.YELLOW)
        
        # Side navigation buttons for main screen album browsing
        self.left_nav_button = Button(10, self.height // 2 - 30, 30, 60, "<", Colors.BLUE, theme=self.current_theme)
        self.right_nav_button = Button(self.width - 40, self.height // 2 - 30, 30, 60, ">", Colors.BLUE, theme=self.current_theme)
        # Number pad (bottom right)
        self.setup_number_pad()
        
        # Audio controls
        self.setup_audio_controls()
        
        # Config screen buttons
        self.setup_config_buttons()
        """Setup clickable number pad for 4-digit selection"""
        pad_x = self.width - 330
        pad_y = self.height - 240
        button_size = 50
        spacing = 5
        
        self.number_pad_buttons: List[NumberPadButton] = []
        
        # Create 0-9 buttons in calculator layout
        # Row 1: 7 8 9
        for i, digit in enumerate(['7', '8', '9']):
            x = pad_x + i * (button_size + spacing)
            y = pad_y
            btn = NumberPadButton(x, y, button_size, button_size, digit)
            self.number_pad_buttons.append(btn)
        
        # Row 2: 4 5 6
        for i, digit in enumerate(['4', '5', '6']):
            x = pad_x + i * (button_size + spacing)
            y = pad_y + (button_size + spacing)
            btn = NumberPadButton(x, y, button_size, button_size, digit)
            self.number_pad_buttons.append(btn)
        
        # Row 3: 1 2 3
        for i, digit in enumerate(['1', '2', '3']):
            x = pad_x + i * (button_size + spacing)
            y = pad_y + 2 * (button_size + spacing)
            btn = NumberPadButton(x, y, button_size, button_size, digit)
            self.number_pad_buttons.append(btn)
        
        # Row 4: 0 < (backspace)
        btn_0 = NumberPadButton(pad_x, pad_y + 3 * (button_size + spacing), button_size, button_size, '0')
        self.number_pad_buttons.append(btn_0)
        
        btn_backspace = NumberPadButton(pad_x + (button_size + spacing), pad_y + 3 * (button_size + spacing), button_size, button_size, '<')
        self.number_pad_buttons.append(btn_backspace)
        
        # Row 5: CLR ENT (clear and enter)
        btn_clr = NumberPadButton(pad_x, pad_y + 4 * (button_size + spacing), button_size * 1.5 + spacing, button_size, 'CLR')
        self.number_pad_buttons.append(btn_clr)
        
        btn_ent = NumberPadButton(pad_x + button_size * 1.5 + spacing * 2, pad_y + 4 * (button_size + spacing), button_size * 1.5, button_size, 'ENT')
        self.number_pad_buttons.append(btn_ent)
    
    def setup_audio_controls(self) -> None:
        """Setup audio control sliders and equalizer"""
        # Volume slider (horizontal)
        self.volume_slider = Slider(
            x=50, y=450, width=200, height=20,
            min_val=0.0, max_val=100.0,
            initial_val=self.config.get('volume', 0.7) * 100,
            label="Volume",
            theme=self.current_theme
        )
        
        # Audio fader button
        self.fader_button = Button(270, 445, 90, 30, "Fader", Colors.BLUE)
        
        # Equalizer button
        self.equalizer_button = Button(370, 445, 90, 30, "EQ", Colors.BLUE)
        
        # Equalizer vertical sliders (5 bands)
        self.eq_sliders: List[VerticalSlider] = []
        eq_start_x = 50
        eq_start_y = 500
        eq_slider_height = 120
        eq_spacing = 40
        
        for i in range(5):
            x = eq_start_x + i * eq_spacing
            slider = VerticalSlider(
                x=x, y=eq_start_y, width=20, height=eq_slider_height,
                min_val=-12.0, max_val=12.0, initial_val=0.0,
                label=f"Band {i+1}",
                theme=self.current_theme
            )
            self.eq_sliders.append(slider)
    
    def setup_config_buttons(self) -> None:
        """Setup configuration screen buttons"""
        button_width = 120
        button_height = 40
        
        config_y = 300
        center_x = self.width // 2
        
        # Config screen buttons
        self.config_rescan_button = Button(center_x - 260, config_y, button_width, button_height, "Rescan", Colors.GREEN)
        self.config_export_button = Button(center_x - 120, config_y, button_width, button_height, "Export CSV", Colors.BLUE)
        self.config_reset_button = Button(center_x + 20, config_y, button_width, button_height, "Reset", Colors.YELLOW)
        self.config_close_button = Button(center_x + 160, config_y, button_width, button_height, "Close", Colors.RED)
        
        # Theme selection buttons
        self.theme_buttons: List[tuple] = []
        self.setup_theme_buttons()
    
    def setup_theme_buttons(self) -> None:
        """Setup theme selection buttons"""
        self.theme_buttons = []
        themes = list(self.theme_manager.themes.keys())
        
        # Create buttons for each theme
        button_width = 100
        button_height = 30
        spacing = 15
        start_x = 50
        start_y = 500
        
        for i, theme_name in enumerate(sorted(themes)):
            x = start_x + i * (button_width + spacing)
            # Highlight current theme
            is_selected = theme_name == self.config.get('theme', 'dark')
            color = Colors.GREEN if is_selected else Colors.GRAY
            btn = Button(x, start_y, button_width, button_height, theme_name.capitalize(), color)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.config_screen_open:
                    self.config_rescan_button.update(event.pos)
                    self.config_export_button.update(event.pos)
                    self.config_reset_button.update(event.pos)
                    self.config_close_button.update(event.pos)
                    # Update theme button hovers
                    for theme_name, btn in self.theme_buttons:
                        btn.update(event.pos)
                else:
                    self.play_button.update(event.pos)
                    self.pause_button.update(event.pos)
                    self.stop_button.update(event.pos)
                    self.prev_track_button.update(event.pos)
                    self.next_track_button.update(event.pos)
                    self.prev_album_button.update(event.pos)
                    self.next_album_button.update(event.pos)
                    self.export_button.update(event.pos)
                    self.config_button.update(event.pos)
                    self.fader_button.update(event.pos)
                    self.equalizer_button.update(event.pos)
                    
                    # Update side navigation button hovers
                    self.left_nav_button.update(event.pos)
                    self.right_nav_button.update(event.pos)
                    
                    # Update slider hovers
                    mouse_pressed = pygame.mouse.get_pressed()[0]
                    self.volume_slider.update(event.pos, mouse_pressed)
                    
                    # Update equalizer sliders
                    for slider in self.eq_sliders:
                        slider.update(event.pos, mouse_pressed)
                    
                    # Update number pad button hovers
                    for btn in self.number_pad_buttons:
                        btn.update(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.config_screen_open:
                    # Config screen button clicks
                    if self.config_rescan_button.is_clicked(event.pos):
                        self.handle_rescan()
                    elif self.config_export_button.is_clicked(event.pos):
                        self.handle_config_export()
                    elif self.config_reset_button.is_clicked(event.pos):
                        self.handle_reset_config()
                    elif self.config_close_button.is_clicked(event.pos):
                        self.config_screen_open = False
                    else:
                        # Check theme button clicks
                        self.handle_theme_selection(event.pos)
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
                    elif self.prev_track_button.is_clicked(event.pos):
                        self.player.previous()
                    elif self.next_track_button.is_clicked(event.pos):
                        self.player.next()
                    elif self.prev_album_button.is_clicked(event.pos):
                        self.player.previous_album()
                    elif self.next_album_button.is_clicked(event.pos):
                        self.player.next_album()
                    elif self.export_button.is_clicked(event.pos):
                        export_path = os.path.join(os.path.dirname(__file__), '..', 'library_export.csv')
                        self.player.export_library(export_path)
                        self.config_message = "Library exported successfully!"
                        self.config_message_timer = 120
                    elif self.config_button.is_clicked(event.pos):
                        self.config_screen_open = True
                        self.config_message = ""
                    elif self.fader_button.is_clicked(event.pos):
                        self.audio_fader.fade_to_mute(0.1)
                    elif self.equalizer_button.is_clicked(event.pos):
                        self.show_equalizer = not self.show_equalizer
                    elif self.left_nav_button.is_clicked(event.pos):
                        self.album_view_offset -= 1
                    elif self.right_nav_button.is_clicked(event.pos):
                        self.album_view_offset += 1
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
                    if not self.config_screen_open:
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
                        self.player.next()
                elif event.key == pygame.K_LEFT:
                    if not self.config_screen_open:
                        self.player.previous()
                elif event.key == pygame.K_UP:
                    if not self.config_screen_open:
                        self.player.set_volume(self.player.volume + 0.1)
                elif event.key == pygame.K_DOWN:
                    if not self.config_screen_open:
                        self.player.set_volume(self.player.volume - 0.1)
                elif event.key == pygame.K_n:
                    if not self.config_screen_open:
                        self.player.next_album()
                elif event.key == pygame.K_p:
                    if not self.config_screen_open:
                        self.player.previous_album()
                elif event.key == pygame.K_e:
                    if not self.config_screen_open:
                        export_path = os.path.join(os.path.dirname(__file__), '..', 'library_export.csv')
                        self.player.export_library(export_path)
                        self.config_message = "Library exported successfully!"
                        self.config_message_timer = 120
                elif event.key == pygame.K_c:
                    self.config_screen_open = not self.config_screen_open
    
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
    
    def handle_config_export(self) -> None:
        """Export library from config screen"""
        export_path = os.path.join(os.path.dirname(__file__), '..', 'library_export.csv')
        if self.player.export_library(export_path):
            self.config_message = "CSV exported successfully!"
            self.config_message_timer = 180
        else:
            self.config_message = "CSV export failed!"
            self.config_message_timer = 180
    
    def handle_reset_config(self) -> None:
        """Reset configuration to defaults"""
        self.config.reset_to_defaults()
        self.config_message = "Configuration reset to defaults"
        self.config_message_timer = 180
        print("Configuration reset to defaults")
    
    def handle_theme_selection(self, pos: Tuple[int, int]) -> None:
        """Handle theme button clicks"""
        for theme_name, btn in self.theme_buttons:
            if btn.is_clicked(pos):
                # Switch to the selected theme
                self.theme_manager.set_current_theme(theme_name)
                self.config.set('theme', theme_name)
                self.current_theme = self.theme_manager.get_current_theme()
                
                # Update button colors to reflect selection
                self.setup_theme_buttons()
                
                # Update side navigation buttons with new theme
                self.left_nav_button.theme = self.current_theme
                self.right_nav_button.theme = self.current_theme
                
                # Show confirmation message
                self.config_message = f"Theme changed to {theme_name.capitalize()}"
                self.config_message_timer = 180
                print(f"Theme switched to: {theme_name}")
                break
    
    def update_audio_controls(self) -> None:
        """Update audio controls and apply effects"""
        # Update volume from slider
        slider_volume = self.volume_slider.get_value() / 100.0
        self.player.set_volume(slider_volume)
        
        # Update audio fader
        fader_volume = self.audio_fader.update()
        self.player.set_volume(fader_volume)
        
        # Update equalizer bands
        for i, slider in enumerate(self.eq_sliders):
            gain = slider.get_value()
            self.equalizer.set_band(i, gain)
    
    def draw(self) -> None:
        """Draw the UI"""
        if self.config_screen_open:
            self.draw_config_screen()
        else:
            self.draw_main_screen()
    
    def draw_main_screen(self) -> None:
        """Draw the main playback screen with 3-column 2-row layout"""
        # Use theme background if available
        background = self.current_theme.get_background()
        if background:
            # Scale background to fit screen
            scaled_bg = pygame.transform.scale(background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            self.screen.fill(Colors.DARK_GRAY)
        
        # Draw title at top
        title = self.large_font.render("JukeBox - Album Library", True, Colors.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 25))
        self.screen.blit(title, title_rect)
        
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
            
            # Draw buttons at top
            self.draw_main_buttons()
            
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
        
        # 3-column layout with margins
        col_width = (self.width - 60) // 3
        margin = 20
        col1_x = margin
        col2_x = margin + col_width + margin
        col3_x = margin + col_width * 2 + margin * 2
        
        # Row 1 and Row 2 positions (2-row layout)
        row1_y = 60
        row2_y = row1_y + 300
        
        current_album_idx = None
        for i, alb in enumerate(albums):
            if alb.album_id == self.player.current_album_id:
                current_album_idx = i
                break
        
        if current_album_idx is None:
            current_album_idx = 0
        
        # Apply view offset for side navigation
        display_album_idx = (current_album_idx + self.album_view_offset) % len(albums)
        
        # Get adjacent albums relative to display offset
        prev_album_idx = (display_album_idx - 1) % len(albums)
        next_album_idx = (display_album_idx + 1) % len(albums)
        prev_album_idx_2 = (display_album_idx - 2) % len(albums)
        next_album_idx_2 = (display_album_idx + 2) % len(albums)
        
        # LEFT COLUMN - Previous 2 albums
        if len(albums) > 0:
            self.draw_album_card(albums[prev_album_idx_2], col1_x, row1_y, col_width - 10)
            self.draw_album_card(albums[prev_album_idx], col1_x, row2_y, col_width - 10)
        
        # CENTER COLUMN - Current album with big display
        if display_album_idx < len(albums):
            self.draw_current_album_display(albums[display_album_idx], col2_x, row1_y, col_width - 10)
        
        # RIGHT COLUMN - Next 2 albums
        if len(albums) > 0:
            self.draw_album_card(albums[next_album_idx], col3_x, row1_y, col_width - 10)
            self.draw_album_card(albums[next_album_idx_2], col3_x, row2_y, col_width - 10)
        
        # Draw side navigation buttons
        self.left_nav_button.draw(self.screen, self.small_font)
        self.right_nav_button.draw(self.screen, self.small_font)
        
        # Draw buttons at top
        self.draw_main_buttons()
        
        # Draw number pad in center bottom
        self.draw_number_pad_centered()
        
        # Draw audio controls above number pad
        self.draw_audio_controls()
        
        # Draw instructions at very bottom
        instructions = self.small_font.render(
            "4-digit: Album(2) + Track(2) | C: Config | Space: Play/Pause | N/P: Album | ↑↓: Volume",
            True, Colors.GRAY
        )
        self.screen.blit(instructions, (20, self.height - 25))
        
        pygame.display.flip()
    
    def draw_album_card(self, album, x: int, y: int, width: int) -> None:
        """Draw a card displaying album information"""
        card_height = 280
        card_rect = pygame.Rect(x, y, width, card_height)
        
        # Draw card background (semi-transparent)
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, card_rect)
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, card_rect, 2)
        
        # Card padding
        padding = 10
        content_x = x + padding
        content_y = y + padding
        content_width = width - padding * 2
        
        # Album number and art area (top)
        art_height = 100
        art_rect = pygame.Rect(content_x, content_y, content_width, art_height)
        pygame.draw.rect(self.screen, Colors.GRAY, art_rect)
        
        # Album number in art area
        album_num_text = self.large_font.render(f"#{album.album_id:02d}", True, Colors.YELLOW)
        album_num_rect = album_num_text.get_rect(center=art_rect.center)
        self.screen.blit(album_num_text, album_num_rect)
        
        # Album artist (below art)
        artist_y = content_y + art_height + padding
        artist_text = self.small_font.render(f"Artist: {album.artist[:20]}", True, Colors.WHITE)
        self.screen.blit(artist_text, (content_x, artist_y))
        
        # Album name (truncated)
        album_name_y = artist_y + 25
        album_name_text = self.small_font.render(f"Album: {album.title[:18]}", True, Colors.LIGHT_GRAY)
        self.screen.blit(album_name_text, (content_x, album_name_y))
        
        # Track list header
        tracks_header_y = album_name_y + 25
        tracks_header = self.small_font.render("Tracks:", True, Colors.YELLOW)
        self.screen.blit(tracks_header, (content_x, tracks_header_y))
        
        # Show first 3 tracks
        track_y = tracks_header_y + 22
        for i, track in enumerate(album.tracks[:3]):
            if track_y + 20 < y + card_height:
                track_text = self.small_font.render(
                    f"  {i+1}. {track['title'][:16]}",
                    True, Colors.LIGHT_GRAY
                )
                self.screen.blit(track_text, (content_x, track_y))
                track_y += 18
    
    def draw_current_album_display(self, album, x: int, y: int, width: int) -> None:
        """Draw large display for currently playing album"""
        display_height = 580
        display_rect = pygame.Rect(x, y, width, display_height)
        
        # Draw display background
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, display_rect)
        pygame.draw.rect(self.screen, Colors.YELLOW, display_rect, 3)
        
        # Padding
        padding = 15
        content_x = x + padding
        content_y = y + padding
        content_width = width - padding * 2
        
        # Large album art area (top)
        art_height = 150
        art_rect = pygame.Rect(content_x, content_y, content_width, art_height)
        pygame.draw.rect(self.screen, Colors.GRAY, art_rect)
        
        # Album number in art area
        album_num_text = self.large_font.render(f"#{album.album_id:02d}", True, Colors.YELLOW)
        album_num_rect = album_num_text.get_rect(center=art_rect.center)
        self.screen.blit(album_num_text, album_num_rect)
        
        # Current track display (if playing from this album)
        track = self.player.get_current_track()
        current_album = self.player.get_current_album()
        
        display_y = content_y + art_height + padding
        
        # Album and artist info
        artist_text = self.medium_font.render(f"Artist: {album.artist}", True, Colors.WHITE)
        self.screen.blit(artist_text, (content_x, display_y))
        
        album_name_y = display_y + 35
        album_name_text = self.medium_font.render(f"Album: {album.title}", True, Colors.WHITE)
        self.screen.blit(album_name_text, (content_x, album_name_y))
        
        # Current track info (if from this album)
        if current_album and current_album.album_id == album.album_id and track:
            track_info_y = album_name_y + 40
            track_label = self.small_font.render("Now Playing:", True, Colors.YELLOW)
            self.screen.blit(track_label, (content_x, track_info_y))
            
            track_num_y = track_info_y + 25
            track_num_text = self.medium_font.render(
                f"Track #{self.player.current_track_index + 1:02d}: {track['title']}",
                True, Colors.LIGHT_GRAY
            )
            self.screen.blit(track_num_text, (content_x, track_num_y))
            
            duration_y = track_num_y + 35
            duration_text = self.small_font.render(f"Duration: {track['duration_formatted']}", True, Colors.GREEN)
            self.screen.blit(duration_text, (content_x, duration_y))
        
        # Track list header
        tracks_header_y = album_name_y + 80 if not (current_album and current_album.album_id == album.album_id) else album_name_y + 150
        tracks_header = self.medium_font.render("All Tracks:", True, Colors.YELLOW)
        self.screen.blit(tracks_header, (content_x, tracks_header_y))
        
        # All tracks list
        track_y = tracks_header_y + 30
        for i, track_info in enumerate(album.tracks):
            if track_y + 20 < y + display_height:
                current_indicator = "► " if (current_album and current_album.album_id == album.album_id and i == self.player.current_track_index) else "  "
                track_text = self.small_font.render(
                    f"{current_indicator}{i+1:02d}. {track_info['title'][:25]} ({track_info['duration_formatted']})",
                    True, Colors.LIGHT_GRAY if i != self.player.current_track_index else Colors.YELLOW
                )
                self.screen.blit(track_text, (content_x, track_y))
                track_y += 22
    
    def draw_main_buttons(self) -> None:
        """Draw playback buttons at the top"""
        button_y = self.height - 320
        
        self.play_button.draw(self.screen, self.small_font)
        self.pause_button.draw(self.screen, self.small_font)
        self.stop_button.draw(self.screen, self.small_font)
        self.prev_track_button.draw(self.screen, self.small_font)
        self.next_track_button.draw(self.screen, self.small_font)
        self.prev_album_button.draw(self.screen, self.small_font)
        self.next_album_button.draw(self.screen, self.small_font)
        self.export_button.draw(self.screen, self.small_font)
        self.config_button.draw(self.screen, self.small_font)
    
    def draw_number_pad_centered(self) -> None:
        """Draw number pad centered at bottom"""
        pad_x = self.width // 2 - 160
        pad_y = self.height - 260
        
        # Draw label
        pad_label = self.small_font.render("4-Digit Selection Pad:", True, Colors.WHITE)
        label_rect = pad_label.get_rect(center=(self.width // 2, pad_y - 25))
        self.screen.blit(pad_label, label_rect)
        
        # Draw number pad buttons
        for btn in self.number_pad_buttons:
            # Update button positions to be centered
            btn.rect.x = pad_x + (self.number_pad_buttons.index(btn) % 3) * 60 + ((self.number_pad_buttons.index(btn) // 3) % 2) * 30
            btn.rect.y = pad_y + (self.number_pad_buttons.index(btn) // 3) * 60
            btn.draw(self.screen, self.small_font)
        
        # Draw selection display above pad
        if self.selection_mode:
            selection_display = f"Selection: {self.selection_buffer:<4}"
            selection_color = Colors.YELLOW
            selection_text = self.medium_font.render(selection_display, True, selection_color)
            selection_rect = selection_text.get_rect(center=(self.width // 2, pad_y - 60))
            self.screen.blit(selection_text, selection_rect)
    
    def draw_audio_controls(self) -> None:
        """Draw audio control elements"""
        # Draw volume slider
        vol_label = self.small_font.render("Volume", True, Colors.WHITE)
        self.screen.blit(vol_label, (50, 425))
        self.volume_slider.draw(self.screen, self.small_font, track_color=Colors.GRAY,
                               knob_color=Colors.GREEN, fill_color=Colors.GREEN)
        
        # Draw fader and equalizer buttons
        self.fader_button.draw(self.screen, self.small_font)
        self.equalizer_button.draw(self.screen, self.small_font)
        
        # Draw fader status
        fader_status = self.small_font.render(
            f"Fader: {self.audio_fader.get_volume() * 100:.0f}%",
            True, Colors.YELLOW
        )
        self.screen.blit(fader_status, (270, 480))
        
        # Draw equalizer if visible
        if self.show_equalizer:
            eq_title = self.medium_font.render("5-Band Equalizer", True, Colors.WHITE)
            self.screen.blit(eq_title, (50, 480))
            
            # Draw frequency band labels
            band_names = ["60 Hz", "250 Hz", "1 kHz", "4 kHz", "16 kHz"]
            eq_start_x = 50
            eq_spacing = 40
            
            for i, (slider, name) in enumerate(zip(self.eq_sliders, band_names)):
                x = eq_start_x + i * eq_spacing
                
                # Draw slider
                slider.draw(self.screen, self.small_font, track_color=Colors.GRAY,
                           knob_color=Colors.BLUE, fill_color=Colors.BLUE)
                
                # Draw frequency label
                label = self.small_font.render(name, True, Colors.LIGHT_GRAY)
                self.screen.blit(label, (x - 15, self.height - 40))
                
                # Draw dB value
                db_val = slider.get_value()
                color = Colors.GREEN if db_val > 0 else (Colors.RED if db_val < 0 else Colors.WHITE)
                db_text = self.small_font.render(f"{db_val:.1f}dB", True, color)
                self.screen.blit(db_text, (x - 15, self.height - 20))
    
    def draw_theme_selector(self) -> None:
        """Draw theme preview and selection interface"""
        theme_section_y = 450
        
        # Draw section title
        theme_title = self.small_font.render("Select Theme:", True, Colors.WHITE)
        self.screen.blit(theme_title, (40, theme_section_y - 30))
        
        # Draw theme buttons
        for theme_name, btn in self.theme_buttons:
            btn.draw(self.screen, self.small_font)
        
        # Draw theme preview if hovering
        for theme_name, btn in self.theme_buttons:
            if btn.is_hovered:
                self.draw_theme_preview(theme_name, self.width - 250, 350)
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

    def draw_config_screen(self) -> None:
        """Draw the configuration screen"""
        self.screen.fill(Colors.DARK_GRAY)
        
        # Update message timer
        if self.config_message_timer > 0:
            self.config_message_timer -= 1
        
        # Draw title
        title = self.large_font.render("Configuration", True, Colors.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw configuration options
        config_y = 140
        line_height = 40
        
        config_items = [
            ("Auto Play Next Track", self.config.get('auto_play_next')),
            ("Shuffle Enabled", self.config.get('shuffle_enabled')),
            ("Show Album Art", self.config.get('show_album_art')),
            ("Keyboard Shortcuts Enabled", self.config.get('keyboard_shortcut_enabled')),
        ]
        
        for i, (label, value) in enumerate(config_items):
            y = config_y + i * line_height
            label_text = self.small_font.render(f"{label}:", True, Colors.WHITE)
            self.screen.blit(label_text, (40, y))
            
            value_str = "ON" if value else "OFF"
            value_color = Colors.GREEN if value else Colors.RED
            value_text = self.small_font.render(value_str, True, value_color)
            self.screen.blit(value_text, (self.width - 200, y))
        
        # Draw additional info
        library_info_y = config_y + len(config_items) * line_height + 20
        stats = self.library.get_library_stats()
        info_lines = [
            f"Albums: {stats['total_albums']}/{stats['max_albums']}",
            f"Total Tracks: {stats['total_tracks']}",
            f"Total Duration: {stats['total_duration_formatted']}",
            f"Theme: {self.config.get('theme')}",
            f"Export Format: {self.config.get('export_format')}",
        ]
        
        for i, info in enumerate(info_lines):
            y = library_info_y + i * 30
            info_text = self.small_font.render(info, True, Colors.LIGHT_GRAY)
            self.screen.blit(info_text, (40, y))
        
        # Draw theme selection section
        self.draw_theme_selector()
        
        # Draw buttons
        button_y = 300
        self.config_rescan_button.draw(self.screen, self.medium_font)
        self.config_export_button.draw(self.screen, self.medium_font)
        self.config_reset_button.draw(self.screen, self.medium_font)
        self.config_close_button.draw(self.screen, self.medium_font)
        
        # Draw messages
        if self.config_message and self.config_message_timer > 0:
            msg_color = Colors.GREEN if "success" in self.config_message.lower() or "complete" in self.config_message.lower() else Colors.YELLOW
            message_text = self.medium_font.render(self.config_message, True, msg_color)
            message_rect = message_text.get_rect(center=(self.width // 2, self.height - 80))
            self.screen.blit(message_text, message_rect)
        
        # Draw instructions
        instructions = self.small_font.render(
            "ESC or Close button to exit configuration",
            True, Colors.GRAY
        )
        self.screen.blit(instructions, (self.width // 2 - 200, self.height - 30))
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main UI loop"""
        while self.running:
            self.handle_events()
            self.update_audio_controls()
            self.draw()
            self.clock.tick(self.fps)
            
            # Auto-play next track if current one finished (only on main screen)
            if not self.config_screen_open and self.player.is_playing and not self.player.is_music_playing():
                self.player.next()
