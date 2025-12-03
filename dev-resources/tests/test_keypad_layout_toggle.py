import os
import pygame
from src.ui import UI


def _compute_pad_origin(ui):
    # replicate draw_number_pad_centered scaling logic for pad_x/pad_y
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


def test_keypad_toggle_changes_positions():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init(); pygame.font.init()
    try:
        # Create UI with default config (new layout disabled)
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
        # Draw old layout
        ui.use_new_keypad_layout = False
        ui.draw_number_pad_centered()
        # Old layout places index 0 at pad_x
        assert ui.number_pad_buttons[0].rect.x == pad_x

        # Now enable new layout and draw
        ui.use_new_keypad_layout = True
        ui.draw_number_pad_centered()

        # For new layout compute the expected pad_x inside the center column
        if ui.fullscreen:
            scale_factor = 1.0
        else:
            scale_factor = 0.75
        base_button_w = 60
        base_spacing = 8
        pad_button_w = int(base_button_w * scale_factor)
        spacing = int(base_spacing * scale_factor)
        # main keypad area width (7 columns) for image
        total_width_new = pad_button_w * 7 + spacing * 6

        # replicate column math from draw_main_screen
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

        # Before centering, account for nav button width which can expand
        # the pad button width in the UI to keep columns aligned.
        nav_button_w = int(65 * scale_factor)
        if nav_button_w > pad_button_w:
            pad_button_w = nav_button_w

        # If pad doesn't fit, we would have scaled down in draw_number_pad_centered
        max_pad_w = max(0, col2_width - 20)
        # Here the UI calculates desired_pad_w across all grid columns (main+nav)
        total_grid_cols = 9
        desired_pad_w = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
        if desired_pad_w > max_pad_w and desired_pad_w > 0:
            scale2 = max_pad_w / float(desired_pad_w)
            if scale2 < 1.0:
                pad_button_w = max(20, int(pad_button_w * scale2))
                spacing = max(2, int(spacing * scale2))
                desired_pad_w = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)

        # Center using total grid columns (7 main + 2 nav)
        total_grid_cols = 9
        pad_total = desired_pad_w
        pad_x_new = col2_x + (col2_width - pad_total) // 2

        # For new layout, index 6 (digit 1) should occupy the top-left slot at pad_x_new
        assert ui.number_pad_buttons[6].rect.x == pad_x_new
    finally:
        pygame.quit()
