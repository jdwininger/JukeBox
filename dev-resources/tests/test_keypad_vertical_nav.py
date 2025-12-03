import os
import pygame
from src.ui import UI


def test_keypad_lowered_and_navs_together():
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

        # Compute expected pad_y baseline by centering the visual pad area
        # vertically inside the pad border. We use the recorded last_pad_border_rect
        # so this test follows the exact layout used in draw_number_pad_centered.
        assert hasattr(ui, 'last_pad_border_rect')
        br = ui.last_pad_border_rect
        if ui.fullscreen:
            scale_factor = 1.0
        else:
            scale_factor = 0.75
        # height used when computing layout in draw_number_pad_centered
        button_height = 50

        border_padding = int(12 * scale_factor)
        inner_v_space = br.height - (border_padding * 2)

        # Compute actual pad image height using the number pad button positions
        all_btns = [b for b in ui.number_pad_buttons if hasattr(b, 'rect')]
        top_y = min(b.rect.y for b in all_btns)
        bottom_y = max(b.rect.bottom for b in all_btns)
        pad_image_h = bottom_y - top_y

        expected_pad_y = br.y + border_padding + max(0, (inner_v_space - pad_image_h) // 2)

        assert hasattr(ui, 'pause_button')
        assert ui.pause_button.rect.y == expected_pad_y

        # Nav buttons should be adjacent (small gap) and located right of pad
        assert ui.right_nav_button.rect.x > ui.left_nav_button.rect.x
        gap = ui.right_nav_button.rect.x - (ui.left_nav_button.rect.x + ui.left_nav_button.rect.width)
        assert gap >= 0 and gap < 40

        # Nav buttons are requested to be 65x85 (scaled) but the UI will
        # scale them down as part of the pad layout if the pad must shrink
        # to fit the center column. Compute expected nav sizing using the
        # same math as draw_number_pad_centered.
        expected_nav_w = int(65 * scale_factor)
        expected_nav_h = int(85 * scale_factor)
        # The UI may have expanded pad_button_w to match nav widths earlier
        base_button_w = 60
        base_spacing = 8
        pad_button_w = int(base_button_w * scale_factor)
        spacing = int(base_spacing * scale_factor)
        if expected_nav_w > pad_button_w:
            pad_button_w = expected_nav_w

        total_grid_cols = 9
        # compute available center column width so we can mirror the UI's
        # possible scale-down behavior
        total_content_width = ui.width - ui.margin * 4
        col2_width = int(total_content_width * 0.36)
        max_pad_w = max(0, col2_width - 20)
        desired_pad = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
        if desired_pad > max_pad_w and desired_pad > 0:
            scale2 = max_pad_w / float(desired_pad)
            if scale2 < 1.0:
                expected_nav_w = max(10, int(expected_nav_w * scale2))
                expected_nav_h = max(10, int(expected_nav_h * scale2))

        assert ui.left_nav_button.rect.width == expected_nav_w
        assert ui.left_nav_button.rect.height == expected_nav_h
        assert ui.right_nav_button.rect.width == expected_nav_w
        assert ui.right_nav_button.rect.height == expected_nav_h

        # Verify they sit inside pad bounding box
        # Recompute pad geometry used for centering
        base_button_w = 60
        base_spacing = 8
        pad_button_w = int(base_button_w * scale_factor)
        # if nav buttons are wider than the pad buttons the UI expands
        # pad_button_w to match nav width so columns align
        nav_button_w = int(65 * scale_factor)
        if nav_button_w > pad_button_w:
            pad_button_w = nav_button_w
        spacing = int(base_spacing * scale_factor)
        # main keypad area: 7 columns
        total_width_new = pad_button_w * 7 + spacing * 6
        controls_margin_top = ui.header_height + 20
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

        # Now check desired pad width across main + nav columns and scale
        total_grid_cols = 9
        desired_pad = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)
        if desired_pad > max_pad_w and desired_pad > 0:
            scale2 = max_pad_w / float(desired_pad)
            if scale2 < 1.0:
                pad_button_w = max(20, int(pad_button_w * scale2))
                spacing = max(2, int(spacing * scale2))
                desired_pad = pad_button_w * total_grid_cols + spacing * (total_grid_cols - 1)

        # center across 9 grid columns (7 main + 2 nav)
        total_grid_cols = 9
        pad_total = desired_pad
        pad_x_new = col2_x + (col2_width - pad_total) // 2

        # Both nav buttons must lie to the right of the main key area and
        # within the pad bounding box which has been widened to include nav keys.
        # left nav should be at column index main_cols (7)
        main_cols = 7
        assert ui.left_nav_button.rect.x == pad_x_new + main_cols * (pad_button_w + spacing)

        # Compute expected border width expansion used by UI: inner_gap + two nav widths + internal spacing
        nav_spacing_inside = spacing
        inner_gap = spacing
        expected_border_w = pad_total

        # right nav should be at next column after left nav
        assert ui.right_nav_button.rect.x == pad_x_new + (main_cols + 1) * (pad_button_w + spacing)
        assert ui.right_nav_button.rect.x + ui.right_nav_button.rect.width <= pad_x_new + expected_border_w

    finally:
        pygame.quit()
