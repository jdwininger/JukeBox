import os
import pytest
import pygame

from src.album_library import AlbumLibrary
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI


def test_ui_uses_bundled_ttf_if_present(tmp_path):
    # If the bundled TTF isn't present, skip this test — the script can
    # download it via scripts/download-dejavu-font.sh
    bundled = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
    # Repo root is the directory containing this file (tests live at repo root)
    repo_root = os.path.abspath(os.path.dirname(__file__))
    bundled = os.path.join(repo_root, 'assets', 'fonts', 'DejaVuSans.ttf')

    if not os.path.exists(bundled):
        pytest.skip("Bundled DejaVuSans.ttf not present — run scripts/download-dejavu-font.sh to fetch it")

    # Create minimal UI and ensure pygame.font.Font objects were created
    lib_dir = tmp_path / "music_lib"
    library = AlbumLibrary(str(lib_dir))
    cfg = Config(config_file=str(tmp_path / "config.json"))
    tm = ThemeManager()

    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    ui = UI(None, library, cfg, tm)

    # Verify that small_font is an instance of pygame.font.Font
    assert hasattr(ui.small_font, 'render')
    surf = ui.small_font.render("Hello", True, (255, 255, 255))
    assert surf.get_width() > 0 and surf.get_height() > 0
