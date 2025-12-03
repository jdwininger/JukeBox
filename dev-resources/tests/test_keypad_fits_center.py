import os
import pygame
from src.ui import UI


def test_keypad_fits_inside_center_column():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init(); pygame.font.init()
    try:
        player_stub = type('P', (), {'library': None, 'current_album_id': 1})()

        class Cfg:
            def get(self, key, default=None):
                return default

        class LibStub:
            def get_albums(self):
                return []

        class TM:
            themes = {}

            class Th:
                def get_color(self, *a, **k):
                    return None

                def get_media_button_image(self, *a, **k):
                    return None

                def get_button_image(self, *a, **k):
                    return None

            def get_current_theme(self):
                return TM.Th()

        ui = UI(player=player_stub, library=LibStub(), config=Cfg(), theme_manager=TM())

        ui.use_new_keypad_layout = True
        # Call draw_main_screen to ensure layout math is prepared (draws pads)
        # Replicate minimal content situation by forcing draw_main_screen to run
        # with no albums by hooking library.get_albums -> [] (already stubbed)
        ui.draw_number_pad_centered()

        # Recompute center column geometry using same logic as UI
        controls_margin_top = ui.header_height + 20
        button_height = 50
        buttons_y = controls_margin_top + 20
        content_top = buttons_y + button_height + 25
        content_height = ui.height - content_top - ui.bottom_area_height - 20
        if content_height < 200:
            content_height = 200

        total_content_width = ui.width - ui.margin * 4
        col1_width = int(total_content_width * 0.32)
        col2_width = int(total_content_width * 0.36)
        col3_width = int(total_content_width * 0.32)

        col1_x = ui.margin
        col3_x = ui.width - ui.margin - col3_width + 12
        left_edge = col1_x + col1_width
        right_edge = col3_x
        available_space = right_edge - left_edge
        col2_x = left_edge + (available_space - col2_width) // 2

        # Determine the pad rect currently used by the UI.
        # When using the image-driven layout we assigned pause_button to the empty slot
        pad_w = ui.pause_button.rect.width if getattr(ui, 'pause_button', None) else 0
        pad_x = ui.pause_button.rect.x if getattr(ui, 'pause_button', None) else 0

        # The pad should be fully inside the center column
        assert pad_x >= col2_x - 1
        assert pad_x + pad_w <= col2_x + col2_width + 1

    finally:
        pygame.quit()
