#!/usr/bin/env bash
# build-appimage.sh - Build an AppImage for JukeBox (Linux/x86_64)
# Notes:
# - This script packages the repository files into an AppDir and runs appimagetool to produce an AppImage.
# - The resulting AppImage will include the application code but not system Python or binary dependencies.
#   The host must provide a compatible `python3` and required Python packages (or you must vendor them into the AppDir).
# - Tested on x86_64 Linux systems.

set -euo pipefail

# Root of the repository (needed early because we reference it below)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Basic arg parsing: support '--slim' to build a smaller AppImage (omit heavy optional packages like numpy/scipy)
SLIM=0
if [ "${1:-}" = "--slim" ]; then
  SLIM=1
  echo "Slim build enabled: skipping heavy optional packages (numpy/scipy/svglib/reportlab)"
fi
# Check if running on Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Error: AppImage builds can only be created on Linux systems."
    echo "AppImage is a Linux-specific packaging format."
    echo ""
    echo "For macOS distribution, use:"
    echo "  make standalone-macos"
    echo "  ./scripts/create-standalone-macos.sh"
    exit 1
fi

# Run a quick repo safety check to avoid packaging accidental large artifacts (e.g. squashfs-root, repo venv, AppImages)
if [ -x "$ROOT_DIR/scripts/check-for-bloat.sh" ]; then
  echo "Running repository safety check..."
  "$ROOT_DIR/scripts/check-for-bloat.sh"
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
APPDIR_NAME="JukeBox.AppDir"
APPDIR="$BUILD_DIR/$APPDIR_NAME"
OUT_NAME="JukeBox-x86_64.AppImage"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/jukebox"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/applications"

# Copy application files into AppDir share
# Exclude previously-extracted or build artifacts that can be large (squashfs-root, repo venv, caches, existing AppImages, etc.)
rsync -a \
  --exclude='.git' \
  --exclude='build' \
  --exclude='music' \
  --exclude='JukeBox.app' \
  --exclude='*.AppImage' \
  --exclude='squashfs-root' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='JukeBox.AppDir' \
  "$ROOT_DIR/" "$APPDIR/usr/share/jukebox/"

# Prepare an embedded virtualenv for a standalone AppImage
VENV_SRC="$BUILD_DIR/venv"
if [ -f "$ROOT_DIR/requirements.txt" ]; then
  echo "Creating virtualenv and installing requirements into $VENV_SRC..."
  rm -rf "$VENV_SRC"
  # create venv with --copies so the interpreter is copied into the venv (not symlinked to /usr/bin)
  python3 -m venv --copies "$VENV_SRC"
  # Ensure the venv has a local python interpreter binary (not a symlink pointing outside the AppDir).
  # On some systems venv may create a symlink to /usr/bin/python3 — copy the real interpreter into the venv so the AppImage can run it.
  HOST_PY_BIN="$(readlink -f "$(command -v python3)" || true)"
  if [ -n "$HOST_PY_BIN" ] && [ -f "$HOST_PY_BIN" ]; then
    # copy the interpreter into venv/bin/python3 (overwrite any symlink)
    cp --preserve=mode "$HOST_PY_BIN" "$VENV_SRC/bin/python3" || true
    chmod +x "$VENV_SRC/bin/python3" || true
    # make sure python -> python3 exists inside venv
    if [ ! -e "$VENV_SRC/bin/python" ]; then
      ln -s python3 "$VENV_SRC/bin/python" || true
    fi
  fi
  # Use the venv's pip to install requirements. Upgrade pip and wheel first.
  "$VENV_SRC/bin/python" -m pip install --upgrade pip setuptools wheel >/dev/null
  # Optionally create a slim requirements list if requested
  if [ "$SLIM" -eq 1 ]; then
    TMP_REQ="$BUILD_DIR/requirements-slim.txt"
    # Exclude heavy packages commonly responsible for large size
    grep -Ev "^\s*(numpy|scipy|svglib|reportlab)" "$ROOT_DIR/requirements.txt" > "$TMP_REQ"
    "$VENV_SRC/bin/python" -m pip install -r "$TMP_REQ"
    # After install, proactively remove heavy packages in case pip pulled them (defensive)
    rm -rf "$VENV_SRC/lib64/python3.14/site-packages/numpy" || true
    rm -rf "$VENV_SRC/lib64/python3.14/site-packages/scipy" || true
    rm -rf "$VENV_SRC/lib64/python3.14/site-packages/svglib" || true
    rm -rf "$VENV_SRC/lib64/python3.14/site-packages/reportlab" || true
  else
    "$VENV_SRC/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt"
  fi
  # If pygame wheel was installed but lacks compiled mixer/image binaries, try building pygame from source
  # so that SDL_mixer / image features are compiled and available (requires dev headers on the build host).
  # Check for presence of mixer compiled module inside the installed pygame package.
  PY_PKG_DIR="$VENV_SRC/lib64/$(basename $(dirname "$VENV_SRC"))/site-packages"
  # Fallback detection path for common layout
  if [ -d "$VENV_SRC/lib64/python3.14/site-packages/pygame" ]; then
    PYG_DIR="$VENV_SRC/lib64/python3.14/site-packages/pygame"
  else
    PYG_DIR="$VENV_SRC/lib64/site-packages/pygame"
  fi
  if [ -d "$PYG_DIR" ]; then
    if ! ls "$PYG_DIR"/mixer*.so >/dev/null 2>&1; then
      echo "pygame mixer extension not found, attempting to build pygame from source to enable mixer/image support..."
      "$VENV_SRC/bin/python" -m pip uninstall -y pygame || true
      # attempt to build from source (this requires system dev packages like SDL2-devel, SDL2_mixer-devel, libsndfile-devel, libjpeg-turbo-devel, libpng-devel)
      if ! "$VENV_SRC/bin/python" -m pip install --no-binary :all: pygame; then
        echo "Warning: building pygame from source failed. Mixer/image support may be unavailable in the embedded environment. Continuing..."
      else
        echo "Rebuilt pygame from source."
      fi
      # If the rebuilt venv still lacks mixer compiled module, try to copy the system-installed pygame compiled extensions
      if ! ls "$PYG_DIR"/mixer*.so >/dev/null 2>&1; then
        echo "pygame mixer still missing in venv — attempting to copy compiled pygame extensions from host python installation (if available)"
        SYS_PYG_DIR="$(python3 -c 'import pygame, os; print(os.path.dirname(pygame.__file__))' 2>/dev/null || true)"
        # also check common system site-packages paths if python3 lookup failed
        if [ -z "$SYS_PYG_DIR" ]; then
          if [ -d "/usr/lib64/python3.14/site-packages/pygame" ]; then
            SYS_PYG_DIR="/usr/lib64/python3.14/site-packages/pygame"
          elif [ -d "/usr/lib/python3.14/site-packages/pygame" ]; then
            SYS_PYG_DIR="/usr/lib/python3.14/site-packages/pygame"
          elif [ -d "/usr/local/lib/python3.14/site-packages/pygame" ]; then
            SYS_PYG_DIR="/usr/local/lib/python3.14/site-packages/pygame"
          fi
        fi
        if [ -n "$SYS_PYG_DIR" ] && [ -d "$SYS_PYG_DIR" ]; then
          echo "  Found system pygame at $SYS_PYG_DIR — copying .so files into venv"
          mkdir -p "$PYG_DIR"
          cp -a "$SYS_PYG_DIR"/*.so "$PYG_DIR/" 2>/dev/null || true
        else
          # Try explicitly-known install locations (some distros place pygame in /usr/lib64 or /usr/lib)
          for candidate in "/usr/lib64/python3.14/site-packages/pygame" "/usr/lib/python3.14/site-packages/pygame" "/usr/local/lib/python3.14/site-packages/pygame"; do
            if [ -d "$candidate" ]; then
              echo "  Found system pygame at $candidate — copying .so files into venv"
              mkdir -p "$PYG_DIR"
              cp -a "$candidate"/*.so "$PYG_DIR/" 2>/dev/null || true
              SYS_PYG_DIR="$candidate"
              break
            fi
          done
          if [ -z "$SYS_PYG_DIR" ]; then
            echo "  No system-installed pygame found to copy from. Skipping (mixer likely unavailable)."
          fi
        fi
      fi
    fi
  fi
  echo "Virtualenv prepared. Bundling into AppDir..."
  mkdir -p "$APPDIR/opt"
  cp -a "$VENV_SRC" "$APPDIR/opt/venv"
else
  echo "No requirements.txt found; packaging without embedded venv. AppImage will rely on system python3."
fi

# Add a small launcher that uses the embedded python (if available) or falls back to system python3
cat > "$APPDIR/usr/bin/jukebox" <<'EOF'
#!/usr/bin/env bash
# Launcher inside AppImage - runs the packaged app with system python3
HERE="$(dirname "$(readlink -f "$0")")/.."
APPDIR_ROOT="$HERE/usr/share/jukebox"
export PYTHONUNBUFFERED=1
# Prefer the embedded venv python if it exists
EMBEDDED_PYTHON="$HERE/opt/venv/bin/python"
if [ -x "$EMBEDDED_PYTHON" ]; then
  # Ensure the package root is visible to the interpreter so imports like `from src.*` work
  export PYTHONPATH="$APPDIR_ROOT"
  exec "$EMBEDDED_PYTHON" -m src.main "$@"
else
  export PYTHONPATH="$APPDIR_ROOT"
  exec /usr/bin/env python3 -m src.main "$@"
fi
EOF
chmod +x "$APPDIR/usr/bin/jukebox"

# Add a desktop file
cat > "$APPDIR/usr/share/applications/jukebox.desktop" <<'EOF'
[Desktop Entry]
Name=JukeBox
Exec=jukebox
Icon=jukebox
Type=Application
# Use AudioVideo category as required by appimagetool checks so we don't get a warning
Categories=AudioVideo;Player;
EOF

# appimagetool expects a top-level desktop file and icon in the AppDir root
cp "$APPDIR/usr/share/applications/jukebox.desktop" "$APPDIR/jukebox.desktop"

# Provide a top-level AppRun so the AppImage runtime executes our app directly and uses the embedded venv
cat > "$APPDIR/AppRun" <<'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
# Make sure packaged app root is available
export PYTHONPATH="$HERE/usr/share/jukebox"
# Ensure native libs from AppDir/usr/lib and AppDir/usr/lib64 are preferred
export LD_LIBRARY_PATH="$HERE/usr/lib:$HERE/usr/lib64:$LD_LIBRARY_PATH"
EMBEDDED_PY="$HERE/opt/venv/bin/python"
if [ -x "$EMBEDDED_PY" ]; then
  exec "$EMBEDDED_PY" -m src.main "$@"
else
  exec /usr/bin/env python3 -m src.main "$@"
fi
EOF
chmod +x "$APPDIR/AppRun"

# Collect common native libraries (SDL2, SDL_mixer, libsndfile, png/jpeg, freetype, etc.) and copy them into AppDir so the AppImage can run without host packages
echo "Collecting native libraries to bundle into AppDir..."
mkdir -p "$APPDIR/usr/lib" "$APPDIR/usr/lib64"

copy_lib_from_ldconfig() {
  local name="$1"
  # Try to locate via ldconfig -p
  local entry
  entry=$(ldconfig -p 2>/dev/null | grep -m1 -E "${name}" || true)
  if [ -z "$entry" ]; then
    return 1
  fi
  # Extract the full path (format: libxxx.so (libc6,x86-64) => /usr/lib64/libxxx.so)
  local path
  path=$(printf "%s" "$entry" | awk -F'=> ' '{print $2}')
  if [ -z "$path" ]; then
    return 1
  fi
  if [ ! -e "$path" ]; then
    return 1
  fi
  local real
  real=$(readlink -f "$path")
  local base_real=$(basename "$real")
  local base_link=$(basename "$path")
  echo "  Found $name -> $path (real: $real)"
  # Copy the real file and also ensure a symlink with the original name exists
  cp -a "$real" "$APPDIR/usr/lib/$base_real" || cp -a "$real" "$APPDIR/usr/lib64/$base_real" || true
  ln -sf "$base_real" "$APPDIR/usr/lib/$base_link" 2>/dev/null || ln -sf "$base_real" "$APPDIR/usr/lib64/$base_link" 2>/dev/null || true
  return 0
}

# Candidate libraries to bundle (common runtime deps for SDL2, sound, image support)
libs=(libSDL2.so libSDL2-2.0.so.0 libSDL2_mixer.so libSDL2_mixer.so.1 libsndfile.so libsndfile.so.1 libvorbis.so libvorbisfile.so libogg.so libopenal.so libpng16.so.16 libpng16.so libpng.so.16 libjpeg.so.62 libjpeg.so libfreetype.so.6 libharfbuzz.so.0 libX11.so.6 libxcb.so.1 libXext.so.6 libSDL2_image.so libSDL2_ttf.so)

for l in "${libs[@]}"; do
  copy_lib_from_ldconfig "$l" || true
done

# Also try to copy libpython used by the venv (if present) to avoid mismatches
if [ -f "$VENV_SRC/bin/python3" ]; then
  if ldd "$VENV_SRC/bin/python3" 2>/dev/null | grep -q "libpython"; then
    for lib in $(ldd "$VENV_SRC/bin/python3" 2>/dev/null | awk '/libpython/ {print $1}'); do
      copy_lib_from_ldconfig "$lib" || true
    done
  fi
fi

echo "Native library bundling step complete."

# --- Trim and optimize AppDir to reduce final AppImage size ---
echo "Trimming AppDir and bundled virtualenv to reduce size..."

# Remove common unneeded files from the venv to shrink footprint
if [ -d "$APPDIR/opt/venv" ]; then
  # Remove pip cache (wheels) and setuptools/pip caches
  rm -rf "$APPDIR/opt/venv/.cache" || true

  # Remove tests, examples, docs and __pycache__ everywhere under site-packages
  find "$APPDIR/opt/venv" -type d \( -name 'tests' -o -name 'test' -o -name 'docs' -o -name 'examples' -o -name '__pycache__' \) -print -exec rm -rf {} + 2>/dev/null || true
  find "$APPDIR/opt/venv" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.pyi' \) -print -delete 2>/dev/null || true

  # Remove pip/shims and dist-info that are not required at runtime (leave metadata minimal)
  # Remove recursively - many packages embed .dist-info/.egg-info in different locations
  find "$APPDIR/opt/venv" -type d -name '*.dist-info' -print -exec rm -rf {} + 2>/dev/null || true
  find "$APPDIR/opt/venv" -type d -name '*.egg-info' -print -exec rm -rf {} + 2>/dev/null || true

  # Keep small metadata but remove large archives, wheels, and test data
  rm -rf "$APPDIR/opt/venv/lib64/python3.14/site-packages/__pycache__" || true
fi

# Strip ELF binaries inside AppDir to reduce size (if strip exists)
if command -v strip >/dev/null 2>&1; then
  echo "Stripping ELF binaries in AppDir/usr and venv..."
  find "$APPDIR/usr/lib" "$APPDIR/usr/lib64" "$APPDIR/opt/venv" -type f -exec file {} \; | grep -E ': ELF ' | awk -F: '{print $1}' | while read -r f; do
    strip --strip-unneeded "$f" >/dev/null 2>&1 || true
  done
fi

# Additional aggressive cleanup in slim mode
if [ "$SLIM" -eq 1 ]; then
  echo "Extra cleanup for slim build: removing optional large artifacts (tests/docs/optional extras)"
  # Remove numpy/scipy test data and examples if present
  rm -rf "$APPDIR/opt/venv/lib64/python3.14/site-packages/numpy" || true
  rm -rf "$APPDIR/opt/venv/lib64/python3.14/site-packages/scipy" || true
  rm -rf "$APPDIR/opt/venv/lib64/python3.14/site-packages/svglib" || true
  rm -rf "$APPDIR/opt/venv/lib64/python3.14/site-packages/reportlab" || true
  # Remove man pages, locale and large docs
  rm -rf "$APPDIR/usr/share/doc" "$APPDIR/usr/share/man" "$APPDIR/usr/share/locale" || true

  # Use upx to compress binaries if available (optional). Only attempt ratio-friendly files.
  if command -v upx >/dev/null 2>&1; then
    echo "Compressing ELF binaries with upx..."
    find "$APPDIR/usr/lib" "$APPDIR/usr/lib64" "$APPDIR/opt/venv" -type f -exec file {} \; | grep -E ': ELF ' | awk -F: '{print $1}' | while read -r f; do
      # upx can fail for some binaries — ignore failures
      upx -9 -q "$f" >/dev/null 2>&1 || true
    done
  fi
fi

# Additional aggressive removals (slim): remove dist-info, .pyi stubs, pip/setuptools/wheel runtime artifacts
if [ "$SLIM" -eq 1 ]; then
  echo "Aggressive slim trimming: removing dist-info, stub files, pip/setuptools/wheel from venv"
  # Support both lib and lib64 site-packages layout inside the venv
  VENV_SP_LIB="$APPDIR/opt/venv/lib/python3.14/site-packages"
  VENV_SP_LIB64="$APPDIR/opt/venv/lib64/python3.14/site-packages"
  VENV_SP=""
  if [ -d "$VENV_SP_LIB64" ]; then
    VENV_SP="$VENV_SP_LIB64"
  elif [ -d "$VENV_SP_LIB" ]; then
    VENV_SP="$VENV_SP_LIB"
  fi

  if [ -n "$VENV_SP" ]; then
    # Remove nested test/examples/docs/__pycache__ recursively (lots of packages include these)
    find "$VENV_SP" -type d \( -iname 'tests' -o -iname 'test' -o -iname 'examples' -o -iname 'docs' -o -iname '__pycache__' -o -iname 'benchmarks' \) -print -exec rm -rf {} + 2>/dev/null || true

    # Remove stub files and packaging artifacts across the tree
    find "$VENV_SP" -type f \( -iname '*.pyi' -o -iname '*.pth' \) -print -delete 2>/dev/null || true
    find "$VENV_SP" -type d -name '*.dist-info' -print -exec rm -rf {} + 2>/dev/null || true
    find "$VENV_SP" -type d -name '*.egg-info' -print -exec rm -rf {} + 2>/dev/null || true

    # Remove pip/setuptools/wheel-related packages (not required at runtime)
    rm -rf "$VENV_SP/pip" "$VENV_SP/pip-*" "$VENV_SP/setuptools" "$VENV_SP/setuptools-*" "$VENV_SP/wheel" "$VENV_SP/wheel-*" || true
  fi

  # Remove large caches or build dirs
  rm -rf "$APPDIR/opt/venv/build" "$APPDIR/opt/venv/src" "$APPDIR/opt/venv/share" || true
fi

echo "Trim/strip pass complete."

# Add icon (placeholder 256x256 PNG if not present in repo)
ICON_TARGET="$APPDIR/usr/share/icons/hicolor/256x256/apps/jukebox.png"
if [ -f "$ROOT_DIR/assets/icon.png" ]; then
  cp "$ROOT_DIR/assets/icon.png" "$ICON_TARGET"
  # also put a copy at the AppDir root (some tools expect top-level icon file)
  cp "$ROOT_DIR/assets/icon.png" "$APPDIR/jukebox.png"
else
  # Create a tiny placeholder PNG (1x1 transparent) and scale won't be ideal, but works.
  cat > "$ICON_TARGET" <<'PNG'
\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82
PNG
  # also write the tiny placeholder to top-level icon path
  cat > "$APPDIR/jukebox.png" <<'PNG'
\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82
PNG
fi

# Ensure appimagetool exists; try to download it if missing
APPIMAGETOOL="$(command -v appimagetool || true)"
if [ -z "$APPIMAGETOOL" ]; then
  echo "appimagetool not found in PATH. Attempting to download appimagetool (x86_64)..."
  TOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
  DL="$BUILD_DIR/appimagetool-x86_64.AppImage"
  mkdir -p "$BUILD_DIR"
  if command -v curl >/dev/null 2>&1; then
    curl -L -o "$DL" "$TOOL_URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$DL" "$TOOL_URL"
  else
    echo "Please install curl or wget to download appimagetool, or install appimagetool manually." >&2
    exit 1
  fi
  chmod +x "$DL"
  APPIMAGETOOL="$DL"
fi

# Build AppImage
echo "Building AppImage..."
# The -u/--updateinformation option expects an argument string. We don't need updateinfo here,
# so call appimagetool without -u to avoid "Missing argument for -u" errors.
"$APPIMAGETOOL" "$APPDIR" "$ROOT_DIR/$OUT_NAME" -n

# If we downloaded an appimagetool into $BUILD_DIR, remove it to avoid confusion next time
if [ -f "$BUILD_DIR/appimagetool-x86_64.AppImage" ]; then
  rm -f "$BUILD_DIR/appimagetool-x86_64.AppImage"
fi
echo "Created AppImage: $ROOT_DIR/$OUT_NAME"

if [ -d "$APPDIR/opt/venv" ]; then
  echo "AppImage build complete: $ROOT_DIR/$OUT_NAME"
  echo "Note: This AppImage contains an embedded Python virtualenv (opt/venv) with dependencies installed from requirements.txt — it should be standalone for Python packages."
else
  echo "AppImage build complete. Note: the AppImage uses system python3 and expects dependencies to be installed on the target host, or you must vendor them into the AppDir."
fi
