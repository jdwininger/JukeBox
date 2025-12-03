import os
import pygame
from src.ui import UI


def test_keypad_border_bottom_aligns_with_album_cards():
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
        ui.draw_number_pad_centered()

        # Recompute expected bottom line for album cards as draw_number_pad_centered does
        if ui.fullscreen:
            scale_factor = 1.0
        else:
            scale_factor = 0.75

        controls_margin_top = ui.header_height + 20
        button_height = 50
        buttons_y = controls_margin_top + 20
        content_top = buttons_y + button_height + 25
        content_height = ui.height - content_top - ui.bottom_area_height - 20
        if content_height < 200:
            content_height = 200

        row1_y = content_top + 10
        row2_y = row1_y + content_height // 2 + 35
        card_h = (content_height // 2) + 15

        expected_bottom = row2_y + card_h

        # Validate we saved border rect and its bottom matches expected album bottom
        assert hasattr(ui, 'last_pad_border_rect')
        assert ui.last_pad_border_rect.bottom == expected_bottom
    finally:
        pygame.quit()
