import os
import pygame
from src.ui import UI


def test_selection_display_above_now_playing():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init(); pygame.font.init()
    try:
        player_stub = type('P', (), {'library': None, 'current_album_id': 1, 'get_current_track': lambda self: None, 'get_current_album': lambda self: None})()

        class Cfg:
            def get(self, key, default=None):
                return default

        class LibStub:
            def get_albums(self):
                return []

        class TM:
            themes = {}

            class Th:
                def get_color(self, key, default=None, *a, **k):
                    # Test theme should return the supplied default when asked
                    return default

                def get_media_button_image(self, *a, **k):
                    return None

                def get_button_image(self, *a, **k):
                    return None

                def get_background(self, w, h):
                    # Return a simple opaque surface so draw_main_screen can blit
                    s = pygame.Surface((max(1, w), max(1, h)))
                    s.fill((0, 0, 0))
                    return s

            def get_current_theme(self):
                return TM.Th()

        ui = UI(player=player_stub, library=LibStub(), config=Cfg(), theme_manager=TM())

        ui.selection_buffer = "1234"
        ui.selection_mode = True

        # Create a tiny album stub and configure the player so draw_main_screen
        # will render the Now Playing box and our selection overlay. This lets
        # us validate the center alignment relative to top controls.
        class AlbumStub:
            def __init__(self):
                self.album_id = 1
                self.title = 'T'
                self.artist = 'A'
                self.tracks = []

        album = AlbumStub()

        # Make library return our album so draw_main_screen uses it. Also
        # make the player return this album as the current album and claim
        # music is playing so draw_current_album_display is called.
        class PlayerStub:
            def __init__(self, album):
                self.library = None
                self.current_album_id = album.album_id
                self._album = album
                # Simulate a simple queue and credits available on a real player
                self.queue = []

            def get_current_track(self):
                return None

            def get_current_track_info(self):
                return None

            def get_volume(self):
                return 0.0

            def get_current_album(self):
                return self._album

            def is_music_playing(self):
                return True

            def get_credits(self):
                return 0

        # Replace UI player with our configured stub and give the library one album
        ui.player = PlayerStub(album)
        class LibOne:
            def get_albums(self):
                return [album]

        ui.library = LibOne()

        # Render the entire main screen (which will position top controls)
        ui.draw_main_screen()

        # The selection rect should have been recorded and its center y should be above the card y
        assert hasattr(ui, 'last_selection_draw_rect')
        sel_rect = ui.last_selection_draw_rect
        # Selection should now be centered between the left volume control
        # end and the left edge of the exit button (midpoint of the top control
        # region). That is what draw_main_screen computes for the center column.
        # Recompute the center column layout the same way draw_main_screen
        total_content_width = ui.width - ui.margin * 4
        col1_width = int(total_content_width * 0.32)
        col2_width = int(total_content_width * 0.36)
        col3_width = int(total_content_width * 0.32)
        left_edge = ui.margin + col1_width
        right_edge = ui.width - ui.margin - col3_width + 12

        # draw_current_album_display receives width=col2_width-10, so compute
        # using the original center-between-columns placement of col2_x
        col2_x = left_edge + (right_edge - left_edge - col2_width) // 2
        expected_center = col2_x + ((col2_width - 10) // 2)
        assert sel_rect.centerx == expected_center
        # Compute the expected Now Playing y used by draw_main_screen so we
        # can assert the selection sits above the card top
        controls_margin_top = ui.header_height + 20
        button_height = 50
        buttons_y = controls_margin_top + 20
        content_top = buttons_y + button_height + 25
        # The Now Playing row has been moved down 25px compared to the
        # (previous) raised position, so the top is content_top + 10 - 15 + 25
        row1_y = content_top + 10 - 15 + 25
        assert sel_rect.centery < row1_y

        # The bounding box behind the digits should also have been recorded
        assert hasattr(ui, 'last_selection_bg_rect')
        bg_rect = ui.last_selection_bg_rect
        # bounding box must be larger than the text rect and sit above the card
        assert bg_rect.width >= sel_rect.width
        assert bg_rect.top < row1_y

        # Now test independent positioning: set a custom center and ensure
        # the selection overlay is drawn there (independent of the Now
        # Playing card). Use a point near the left of the screen.
        ui.selection_center_override = (120, 40)
        # Force a redraw of main screen
        ui.draw_main_screen()
        assert hasattr(ui, 'last_selection_draw_rect')
        sel_rect2 = ui.last_selection_draw_rect
        assert sel_rect2.centerx == 120
        assert sel_rect2.centery == 40

        # When a playing selection is available but the user is actively
        # typing a new selection (selection_mode True), the typed buffer
        # should be displayed instead of the current-playing selection.
        ui.last_track_info = {"album_id": 2, "track_index": 1, "title": "X", "duration_formatted": "0:00"}
        ui.draw_main_screen()
        # selection_mode is still True so typed buffer should take precedence
        assert getattr(ui, 'last_selection_display_string', None) == "1234"
        # And the display should indicate it was typed input (visual cue)
        assert getattr(ui, 'last_selection_is_typed', None) is True

        # Once typing stops (selection_mode False) the display should show
        # the current playing selection again.
        ui.selection_mode = False
        ui.draw_main_screen()
        assert getattr(ui, 'last_selection_display_string', None) == "0202"
        # After typing stops this should be the playing selection (not typed)
        assert getattr(ui, 'last_selection_is_typed', None) is False

    finally:
        pygame.quit()
