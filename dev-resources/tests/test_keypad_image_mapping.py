import os
import pygame
from src.ui import UI


def _compute_pad_origin(ui):
    if ui.fullscreen:
        scale_factor = 1.0
    else:
        scale_factor = 0.75
    base_button_w = 60
    base_spacing = 8
    pad_button_w = int(base_button_w * scale_factor)
    spacing = int(base_spacing * scale_factor)
    total_width = pad_button_w * 3 + spacing * 2
    pad_x = ui.width // 2 - total_width // 2
    return pad_x, pad_button_w, spacing


def test_image_driven_mapping_positions():
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

        pad_x, pad_button_w, spacing = _compute_pad_origin(ui)

        ui.use_new_keypad_layout = True
        ui.draw_number_pad_centered()

        # '1' is the 7th button (index 6); compute expected pad_x for new layout
        if ui.fullscreen:
            scale_factor = 1.0
        else:
            scale_factor = 0.75
        base_button_w = 60
        base_spacing = 8
        pad_button_w = int(base_button_w * scale_factor)
        spacing = int(base_spacing * scale_factor)
        # main keypad image width (7 columns)
        total_width_new = pad_button_w * 7 + spacing * 6

        # compute center column geometry
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

        max_pad_w = max(0, col2_width - 20)
        if total_width_new > max_pad_w and total_width_new > 0:
            scale2 = max_pad_w / float(total_width_new)
            if scale2 < 1.0:
                pad_button_w = max(20, int(pad_button_w * scale2))
                spacing = max(2, int(spacing * scale2))
                total_width_new = pad_button_w * 8 + spacing * 7

        # When computing the expected pad geometry follow the same rules
        # in draw_number_pad_centered: nav buttons may be wider than the
        # base pad button and thus pad_button_w expands to contain them.
        nav_button_w = int(65 * scale_factor)
        if nav_button_w > pad_button_w:
            pad_button_w = nav_button_w

        total_grid_cols = 9
        desired_pad_w = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
        pad_total = desired_pad_w
        # Scale down if necessary (matching the UI's scaling rules)
        max_pad_w = max(0, col2_width - 20)
        if pad_total > max_pad_w and pad_total > 0:
            scale = max_pad_w / float(pad_total)
            if scale < 1.0:
                pad_button_w = max(20, int(pad_button_w * scale))
                spacing = max(2, int(spacing * scale))
                nav_button_w = max(10, int(nav_button_w * scale))
                pad_total = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)

        pad_x_new = col2_x + (col2_width - pad_total) // 2
        assert ui.number_pad_buttons[6].rect.x == pad_x_new

        # '5' is index 4 and should be at pad_x_new + 4*(pad_button_w+spacing)
        expected_5_x = pad_x_new + 4 * (pad_button_w + spacing)
        assert ui.number_pad_buttons[4].rect.x == expected_5_x

        # '0' (index 9) should also be at the same column as '5'
        assert ui.number_pad_buttons[9].rect.x == expected_5_x

        # The image-driven layout intentionally left one top-row slot empty
        # (between '5' and 'ENT') — this slot now acts as the Pause control.
        placeholder_x = pad_x_new + 5 * (pad_button_w + spacing)
        assert ui.pause_button.rect.x == placeholder_x

        # Top-media controls are hidden by default — verify the UI flag
        assert not ui.show_top_media_controls

    finally:
        pygame.quit()
