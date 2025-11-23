"""
JukeBox - A music player application using pygame and SDL2
"""
import pygame
import sys
import os
from src.player import MusicPlayer
from src.album_library import AlbumLibrary
from src.config import Config
from src.theme import ThemeManager
from src.ui import UI


def main():
    """Main entry point for the JukeBox application"""
    import argparse

    parser = argparse.ArgumentParser(prog='JukeBox', add_help=False)
    parser.add_argument('--diagnose', action='store_true', help='Run system diagnostics and exit')
    parser.add_argument('--fix', action='store_true', help='Run diagnostics and interactively attempt suggested fixes')
    parser.add_argument('--autofix', action='store_true', help='Run diagnostics and automatically attempt suggested fixes (no prompts)')
    parser.add_argument('--autofix-yes', dest='autofix_yes', action='store_true', help='Skip confirmation when using --autofix')
    parser.add_argument('--preview-fix', dest='preview_fix', action='store_true', help='Run diagnostics and only show commands that would be executed (preview only)')
    args, _ = parser.parse_known_args()

    if args.diagnose or args.fix or args.autofix:
        try:
            from src.diagnostics import run_diagnostics, print_diagnostics
        except Exception as e:
            print('Diagnostics unavailable:', e)
            sys.exit(2)

        res = run_diagnostics()
        print_diagnostics(res)

        if args.fix or args.autofix or args.preview_fix:
            auto = bool(args.autofix)
            try:
                from src.diagnostics import interactive_fix_pick
            except Exception as e:
                print('Fixer helper unavailable:', e)
                sys.exit(2)

            if args.preview_fix:
                try:
                    from src.diagnostics import preview_fix_commands
                except Exception as e:
                    print('Preview helper unavailable:', e)
                    sys.exit(2)

                preview = preview_fix_commands(res)
                print('\nPreview commands (no actions performed):')
                for area, cmds in preview.items():
                    print(f"\n{area}:")
                    for c in cmds:
                        print(f"  {c}")
                results = {}
            else:
                if args.autofix:
                    try:
                        from src.diagnostics import preview_fix_commands, perform_fix
                    except Exception as e:
                        print('Fixer helper unavailable:', e)
                        sys.exit(2)

                    to_run = preview_fix_commands(res)
                    if not to_run:
                        print('No suggested commands to run.')
                        results = {}
                    else:
                        print('\nCommands that would be executed:')
                        for area, cmds in to_run.items():
                            print(f"\n{area}:")
                            for c in cmds:
                                print(f"  {c}")

                        do_it = False
                        if args.autofix_yes:
                            do_it = True
                        else:
                            print('\nProceed to run the commands above? (y/N):')
                            answer = input('> ').strip().lower()
                            if answer in ('y', 'yes'):
                                do_it = True

                        run_results = {}
                        if do_it:
                            for area, cmds in to_run.items():
                                area_results = []
                                for cmd in cmds:
                                    print(f"Running: {cmd}")
                                    rc, out, err = perform_fix(cmd, capture_output=True)
                                    area_results.append({'command': cmd, 'rc': rc, 'stdout': out, 'stderr': err})
                                run_results[area] = area_results
                        results = run_results
                else:
                    results = interactive_fix_pick(res, auto_accept=auto)
            print('\nFixer results:')
            for area, runs in results.items():
                for entry in runs:
                    status = 'OK' if entry['rc'] == 0 else f'ERR({entry["rc"]})'
                    print(f"  {area}: {status} - {entry['command']}")

        sys.exit(0)

    # Initialize pygame
    pygame.init()
    try:
        # Prefer a non-destructive availability check from audio_utils
        from src.audio_utils import is_mixer_available

        if not is_mixer_available():
            raise ModuleNotFoundError("pygame.mixer not available")

        pygame.mixer.init()
    except ModuleNotFoundError as exc:
        # Give a clear error message for users running on Linux without SDL_mixer
        print("\n❌ pygame.mixer is not available. This usually means system audio libraries (SDL_mixer / libsndfile) were missing when pygame was installed.")
        print("👉 On Debian/Ubuntu: sudo apt-get install -y libsdl2-dev libsdl2-mixer-dev libsndfile1-dev")
        print("👉 On Fedora/RPM:     sudo dnf install -y SDL2-devel SDL2_mixer SDL2_mixer-devel libsndfile-devel")
        print(f"Then reinstall pygame inside your virtualenv: {sys.executable} -m pip install --upgrade --force-reinstall pygame")
        raise
    
    # Load configuration
    config = Config()
    
    # Initialize theme system
    theme_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
    theme_manager = ThemeManager(theme_dir)
    theme_manager.discover_themes()
    theme_name = config.get('theme', 'dark')  # Default to 'dark' theme
    if not theme_manager.set_current_theme(theme_name):
        # Fallback to first available theme if configured theme not found
        available = theme_manager.get_available_themes()
        if available:
            theme_manager.set_current_theme(available[0])
        else:
            print("Warning: No themes available")
    
    # Setup library
    # User-configurable music directory (config 'music_dir') takes precedence.
    # If not set, default to ~/Music/JukeBox on macOS/Linux, or project-local
    # 'music' directory elsewhere.
    cfg_music_dir = config.get('music_dir')
    if cfg_music_dir:
        music_dir = os.path.expanduser(cfg_music_dir)
    else:
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            music_dir = os.path.expanduser(os.path.join('~', 'Music', 'JukeBox'))
        else:
            music_dir = os.path.join(os.path.dirname(__file__), '..', 'music')
    library = AlbumLibrary(music_dir)
    library.scan_library()
    
    # Create the UI first (which creates the equalizer)
    ui = UI(None, library, config, theme_manager)  # Pass None for player initially
    
    # Create the player with the equalizer from UI
    player = MusicPlayer(library, ui.equalizer)
    
    # Now set the player in the UI
    ui.player = player
    
    # Run the application
    ui.run()
    
    # Cleanup
    player.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
