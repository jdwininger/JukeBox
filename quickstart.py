#!/usr/bin/env python3
"""
JukeBox Quick Start - Enhanced Music Player with Equalizer
Demonstrates the complete JukeBox application with all features
"""

import os
import sys

from src.album_library import AlbumLibrary
from src.config import Config


def display_banner():
    """Display JukeBox banner"""
    print(f"\n{'='*70}")
    print("🎵 JukeBox - Enhanced Music Player with Professional Equalizer 🎵")
    print(f"{'='*70}")
    print("Features:")
    print("  ✓ Real-time 5-band equalizer with numpy/scipy processing")
    print("  ✓ Beautiful themed UI with semi-transparent overlays")
    print("  ✓ Album library management (supports 50 albums)")
    print("  ✓ Professional media controls and volume slider")
    print("  ✓ Multiple themes (dark, light, custom)")
    print("  ✓ PNG-optimized backgrounds for smooth performance")
    print("  ✓ Self-contained macOS app distribution")
    print("  ✓ Virtual environment management")
    print(f"{'='*70}\n")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    try:
        import numpy

        print("  ✓ numpy - for real-time audio processing")
    except ImportError:
        print("  ✗ numpy - REQUIRED for equalizer functionality")
        return False

    try:
        import scipy

        print("  ✓ scipy - for frequency band filtering")
    except ImportError:
        print("  ✗ scipy - REQUIRED for equalizer functionality")
        return False

    try:
        import pygame

        print("  ✓ pygame - for audio playback and UI")
    except ImportError:
        print("  ✗ pygame - REQUIRED for music playback")
        return False

    try:
        import mutagen

        print("  ✓ mutagen - for metadata extraction")
    except ImportError:
        print("  ✗ mutagen - REQUIRED for music file parsing")
        return False

    try:
        import reportlab
        import svglib

        print("  ✓ svglib/reportlab - for theme system")
    except ImportError:
        print("  ✗ svglib/reportlab - REQUIRED for theme backgrounds")
        return False

    print("  ✓ All dependencies satisfied!\n")
    return True


def setup_library():
    """Setup and scan the music library"""
    # Default music library location: on macOS and Linux use ~/Music/JukeBox
    # to follow common user expectations; fall back to a project-local
    # `music/` folder on other platforms or when a different layout is desired.
    program_dir = os.path.dirname(__file__)
    if sys.platform.startswith("linux") or sys.platform == "darwin":
        # Check for user-configured music_dir in config (if quickstart is being used
        # outside of the full UI the user can still benefit from previously saved
        # settings). If the setting exists use it, otherwise use the platform default.
        cfg = Config()
        cfg_music_dir = cfg.get("music_dir")
        if cfg_music_dir:
            music_dir = os.path.expanduser(cfg_music_dir)
        else:
            # Prefer an existing Music/Jukebox-like folder when available
            home_music = os.path.expanduser(os.path.join("~", "Music"))
            variants = ["JukeBox", "Jukebox", "jukebox", "Juke Box", "Juke-Box"]
            found = None
            for v in variants:
                cand = os.path.join(home_music, v)
                if os.path.exists(cand):
                    found = cand
                    break

            if found:
                music_dir = found
            else:
                music_dir = os.path.expanduser(os.path.join("~", "Music", "JukeBox"))
    else:
        music_dir = os.path.join(program_dir, "music")

    print(f"Setting up music library...")
    print(f"Library directory: {music_dir}")

    if not os.path.exists(music_dir):
        print(f"  Creating music directory...")
        os.makedirs(music_dir, exist_ok=True)

        # Create sample album directories
        for i in range(1, 3):
            album_dir = os.path.join(music_dir, f"{i:02d}")
            os.makedirs(album_dir, exist_ok=True)

        print(f"  ✓ Created sample album directories (01, 02)")
        print(f"  📁 Add your music files to: {music_dir}/01/, {music_dir}/02/, etc.")

    library = AlbumLibrary(music_dir)
    print(f"  📀 Scanning for albums...")
    library.scan_library()

    return library


def display_library_info(library):
    """Display library statistics and album information"""
    stats = library.get_library_stats()
    albums = library.get_albums()

    print(f"\n{'='*70}")
    print(f"📊 Library Statistics")
    print(f"{'='*70}")
    print(f"Albums Found: {stats['total_albums']}/{stats['max_albums']}")
    print(f"Total Tracks: {stats['total_tracks']}")
    print(f"Total Duration: {stats['total_duration_formatted']}")
    print(f"Library Size: {len(albums)} albums")

    if albums:
        print(f"\n{'='*70}")
        print(f"🎵 Albums in Library")
        print(f"{'='*70}")
        for album in albums[:5]:  # Show first 5 albums
            print(f"\n[Album {album.album_id:02d}] {album.artist} - {album.title}")
            print(f"  📀 {len(album.tracks)} tracks")
            for i, track in enumerate(album.tracks[:3], 1):
                print(f"    {i}. {track['title']} ({track['duration_formatted']})")
            if len(album.tracks) > 3:
                print(f"    ... and {len(album.tracks) - 3} more tracks")

        if len(albums) > 5:
            print(f"\n... and {len(albums) - 5} more albums")
    else:
        print(f"\n⚠️  No albums found!")
        print(f"   📁 Add music files to numbered folders in: {library.library_path}")
        print(f"   💡 Example: music/01/song1.mp3, music/02/album2_song1.mp3")

    print(f"{'='*70}")


def display_equalizer_info():
    """Display equalizer feature information"""
    print(f"\n{'='*70}")
    print(f"🎛️  Professional Equalizer Features")
    print(f"{'='*70}")

    # Import the Equalizer lazily so quickstart can run in bootstrap mode
    from src.audio_effects import Equalizer

    equalizer = Equalizer()
    presets = equalizer.get_presets()

    print(f"5-Band Frequency Control:")
    print(f"  🎵 60 Hz    - Sub-bass and kick drums")
    print(f"  🎵 250 Hz   - Bass and low midrange")
    print(f"  🎵 1 kHz    - Midrange vocals and instruments")
    print(f"  🎵 4 kHz    - Presence and vocal clarity")
    print(f"  🎵 16 kHz   - High frequencies and air")

    print(f"\nAvailable Presets:")
    for i, preset_name in enumerate(presets.keys(), 1):
        preset_values = presets[preset_name]
        print(f"  {i}. {preset_name}: {preset_values}")

    print(f"\nReal-time Processing:")
    print(f"  ✓ numpy-based frequency analysis")
    print(f"  ✓ scipy signal processing filters")
    print(f"  ✓ Live audio effects during playback")
    print(f"  ✓ Persistent settings saved to config")
    print(f"{'='*70}")


def launch_application():
    """Launch the full JukeBox application"""
    print(f"\n🚀 Launching JukeBox Application...")
    print(f"   Use the configuration button to access the equalizer!")
    print(f"   Press ESC or close window to exit")
    print(f"{'='*70}\n")

    try:
        # Defer importing pygame until we're ready to launch so quickstart
        # can still create virtualenvs and install dependencies when they
        # are missing.
        import pygame
        # Initialize pygame
        pygame.init()

        # Check for mixer availability before trying to init - helps on systems
        # where pygame was installed without SDL_mixer / system audio libs.
        try:
            from src.audio_utils import is_mixer_available
        except Exception:
            is_mixer_available = None

        if is_mixer_available is None or not is_mixer_available():
            raise ModuleNotFoundError("mixer module not available")

        pygame.mixer.init()

        # Load configuration
        config = Config()

        # Initialize theme system
        from src.theme import ThemeManager
        from src.ui import UI
        from src.player import MusicPlayer

        theme_dir = os.path.join(os.path.dirname(__file__), "themes")
        theme_manager = ThemeManager(theme_dir)
        theme_manager.discover_themes()
        theme_name = config.get("theme", "dark")

        if not theme_manager.set_current_theme(theme_name):
            available = theme_manager.get_available_themes()
            if available:
                theme_manager.set_current_theme(available[0])
                print(f"   Using theme: {available[0]}")

        # Setup library
        music_dir = os.path.join(os.path.dirname(__file__), "music")
        library = AlbumLibrary(music_dir)
        library.scan_library()

        # Create UI and player
        ui = UI(None, library, config, theme_manager)
        player = MusicPlayer(library, ui.equalizer)
        ui.player = player

        # Run the application
        ui.run()

        # Cleanup
        player.cleanup()
        pygame.quit()

    except KeyboardInterrupt:
        print(f"\n👋 JukeBox closed by user")
    except Exception as e:
        # Provide clearer, actionable advice for common platform problems (e.g., missing mixer)
        print(f"\n❌ Error launching JukeBox: {e}")

        # Detect common case where pygame was built without audio/mixer support
        err_msg = str(e).lower()
        if (
            "mixer module not available" in err_msg
            or 'no module named "pygame.mixer"' in err_msg
        ):
            print(
                "\n🩺 Diagnostic: The pygame.mixer module was not found. This usually means SDL_mixer or system audio libraries were missing when pygame was installed."
            )
            print("\n🔧 Quick fixes (pick one for your distro):")
            print("\n  Debian/Ubuntu:")
            print(
                "    sudo apt-get update && sudo apt-get install -y libsdl2-dev libsdl2-mixer-dev libsndfile1-dev"
            )
            print("\n  Fedora/RPM:")
            print(
                "    sudo dnf install -y SDL2-devel SDL2_mixer SDL2_mixer-devel libsndfile-devel"
            )
            print(
                "\n  After installing system packages, reinstall pygame inside your virtualenv:"
            )
            print(
                f"    {sys.executable} -m pip install --upgrade --force-reinstall --no-cache-dir pygame"
            )
        else:
            print(f"   Try running: make run")


def main():
    """Main entry point for JukeBox quickstart"""
    display_banner()

    import argparse

    parser = argparse.ArgumentParser(prog="quickstart", add_help=False)
    parser.add_argument(
        "--diagnose", action="store_true", help="Run system diagnostics and exit"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Run diagnostics and interactively attempt suggested fixes",
    )
    parser.add_argument(
        "--autofix",
        action="store_true",
        help="Run diagnostics and automatically attempt suggested fixes (no prompts)",
    )
    parser.add_argument(
        "--autofix-yes",
        dest="autofix_yes",
        action="store_true",
        help="Skip confirmation when using --autofix",
    )
    parser.add_argument(
        "--preview-fix",
        action="store_true",
        help="Run diagnostics and only show commands that would be executed (preview only)",
    )
    # Additional convenience options for bootstrapping an environment
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Create a virtualenv and install dependencies from requirements.txt",
    )
    parser.add_argument(
        "--venv",
        default=".venv",
        help="Path to virtualenv to create/use (default: .venv)",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install dependencies into the specified virtualenv (without creating a new one)",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="When bootstrapping, create the virtualenv but do NOT install Python packages",
    )
    args, _ = parser.parse_known_args()

    # (parser options already configured above)

    if args.bootstrap or args.install_deps:
        # Allow bootstrapping before trying to import modules that may be missing
        venv_path = os.path.abspath(args.venv)
        req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

        def create_venv(path):
            import subprocess

            if os.path.exists(path):
                print(f"Virtualenv already exists at {path}")
                return
            print(f"Creating virtualenv at {path}...")
            subprocess.check_call([sys.executable, "-m", "venv", path])
            print("Virtualenv created.")

        def pip_install(path, reqfile):
            import subprocess

            pybin = os.path.join(path, "bin", "python")
            if not os.path.exists(pybin):
                raise SystemExit(f"Python not found in virtualenv: {pybin}")
            print(f"Upgrading pip and installing requirements into {path}...")
            subprocess.check_call([pybin, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
            if os.path.exists(reqfile):
                subprocess.check_call([pybin, "-m", "pip", "install", "-r", reqfile])
            else:
                print(f"No requirements.txt at {reqfile} — nothing to install.")

        # Create venv first if requested
        if args.bootstrap:
            create_venv(venv_path)
            if args.no_install:
                print("Skipping installation of requirements (--no-install requested).")
            else:
                try:
                    pip_install(venv_path, req_path)
                except Exception as e:
                    print("Error installing requirements:", e)
                    print("You can retry using --install-deps or check your environment.")
            # If bootstrapping only, exit afterwards
            # (user can pass other flags later to launch app)
            if not (args.diagnose or args.fix or args.autofix):
                print("Bootstrap complete — exiting. Use the venv python to run the app: ./venv/bin/python -m src.main")
                return

        if args.install_deps:
            try:
                pip_install(venv_path, req_path)
            except Exception as e:
                print("Error installing requirements:", e)
                raise

    if args.diagnose or args.fix or args.autofix:
        # Run interactive diagnostics and exit
        try:
            from src.diagnostics import print_diagnostics, run_diagnostics
        except Exception as e:
            print("Diagnostics unavailable:", e)
            sys.exit(2)

        res = run_diagnostics()
        print_diagnostics(res)

        if args.fix or args.autofix or args.preview_fix:
            auto = bool(args.autofix)
            try:
                from src.diagnostics import interactive_fix_pick
            except Exception as e:
                print("Fixer helper unavailable:", e)
                sys.exit(2)

            # Preview-only mode (do not execute)
            if args.preview_fix:
                try:
                    from src.diagnostics import preview_fix_commands
                except Exception as e:
                    print("Preview helper unavailable:", e)
                    sys.exit(2)

                preview = preview_fix_commands(res)
                print("\nPreview commands (no actions performed):")
                for area, cmds in preview.items():
                    print(f"\n{area}:")
                    for c in cmds:
                        print(f"  {c}")
                results = {}
            else:
                # If automatic mode, ask for a final confirmation unless --autofix-yes
                if args.autofix:
                    try:
                        from src.diagnostics import (perform_fix,
                                                     preview_fix_commands)
                    except Exception as e:
                        print("Fixer helper unavailable:", e)
                        sys.exit(2)

                    to_run = preview_fix_commands(res)
                    if not to_run:
                        print("No suggested commands to run.")
                        results = {}
                    else:
                        print("\nCommands that would be executed:")
                        for area, cmds in to_run.items():
                            print(f"\n{area}:")
                            for c in cmds:
                                print(f"  {c}")

                        do_it = False
                        if args.autofix_yes:
                            do_it = True
                        else:
                            print("\nProceed to run the commands above? (y/N):")
                            answer = input("> ").strip().lower()
                            if answer in ("y", "yes"):
                                do_it = True

                        run_results = {}
                        if do_it:
                            for area, cmds in to_run.items():
                                area_results = []
                                for cmd in cmds:
                                    print(f"Running: {cmd}")
                                    rc, out, err = perform_fix(cmd, capture_output=True)
                                    area_results.append(
                                        {
                                            "command": cmd,
                                            "rc": rc,
                                            "stdout": out,
                                            "stderr": err,
                                        }
                                    )
                                run_results[area] = area_results
                        results = run_results
                else:
                    results = interactive_fix_pick(res, auto_accept=auto)
            print("\nFixer results:")
            for area, runs in results.items():
                for entry in runs:
                    status = "OK" if entry["rc"] == 0 else f'ERR({entry["rc"]})'
                    print(f"  {area}: {status} - {entry['command']}")
        sys.exit(0)

    # Check dependencies
    if not check_dependencies():
        print(f"❌ Missing dependencies. Run: pip install -r requirements.txt")
        sys.exit(1)

    # Setup library
    library = setup_library()

    # Display information
    display_library_info(library)
    display_equalizer_info()

    # Export library data
    print(f"\n📄 Exporting library data...")
    export_path = os.path.join(os.path.dirname(__file__), "library_export.csv")
    if library.export_to_csv(export_path):
        print(f"  ✓ Library data exported to: {export_path}")
    else:
        print(f"  ✗ Export failed")

    # Offer to launch full application
    print(f"\n{'='*70}")
    choice = input("🎵 Launch full JukeBox application? (y/N): ").lower().strip()
    if choice in ["y", "yes"]:
        launch_application()
    else:
        print(f"\n💡 To launch JukeBox manually, run:")
        print(f"   make run")
        print(f"   # or")
        print(f"   python3 src/main.py")
        print(f"\n👋 Quickstart complete!")


if __name__ == "__main__":
    main()
