#!/usr/bin/env bash
# Create a minimal release tarball containing only the files needed to run the program
# Produces JukeBox-<version>.tar.gz where <version> comes from git describe --tags (if available)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR="$ROOT_DIR/build/release"
mkdir -p "$OUTDIR"

VERSION="$(git -C "$ROOT_DIR" describe --tags --dirty --always 2>/dev/null || true)"
if [ -z "$VERSION" ]; then
  VERSION="unversioned-$(date +%Y%m%d%H%M%S)"
fi

NAME="JukeBox-${VERSION}"
TMPDIR="$(mktemp -d -t ${NAME}.XXXX)"

echo "Creating release tar in $OUTDIR for version: $VERSION"

# Files and directories required at runtime
INCLUDE=(
  src
  assets
  themes
  README.md
  LICENSE
  requirements.txt
  run.sh
  quickstart.py
  setup.py
  MAIN_SCREEN_LAYOUT.md
)

# Helper: copy if exists
copy_if_exists() {
  local p="$1"
  if [ -e "$ROOT_DIR/$p" ]; then
    mkdir -p "$(dirname "$TMPDIR/$p")"
    cp -a "$ROOT_DIR/$p" "$TMPDIR/$p"
  fi
}

echo "Copying runtime files to temporary dir: $TMPDIR"
for p in "${INCLUDE[@]}"; do
  copy_if_exists "$p"
done

# Ensure we don't include tests, .git, or other development cruft by accident
rm -rf "$TMPDIR/.git" || true
rm -rf "$TMPDIR/tests" || true
rm -rf "$TMPDIR/test_*" || true
rm -rf "$TMPDIR/.pytest_cache" || true
rm -rf "$TMPDIR/__pycache__" || true

# Create a small bootstrap helper that makes a virtualenv and installs requirements
cat > "$TMPDIR/setup_and_run.sh" <<'BASH'
#!/usr/bin/env bash
# setup_and_run.sh - initial helper for release tar users
# Creates a Python virtualenv in ./venv, installs requirements and runs JukeBox.
set -euo pipefail

if [ ! -f requirements.txt ]; then
  echo "No requirements.txt found — please install dependencies manually or use system python." >&2
fi

if [ ! -d venv ]; then
  python3 -m venv venv
fi

venv_bin="venv/bin/python"
if [ ! -x "$venv_bin" ]; then
  echo "Virtualenv python not found or not executable. Please ensure Python 3 is available." >&2
  exit 2
fi

echo "Upgrading pip and installing requirements..."
"$venv_bin" -m pip install --upgrade pip setuptools wheel >/dev/null
if [ -f requirements.txt ]; then
  "$venv_bin" -m pip install -r requirements.txt
fi

echo "Launching JukeBox via run.sh"
chmod +x run.sh || true
./run.sh
BASH

chmod +x "$TMPDIR/setup_and_run.sh"

# Remove any remaining unwanted files under src (developer-only files like fixtures marked 'tests')
find "$TMPDIR/src" -name "test_*.py" -type f -delete 2>/dev/null || true

pushd "$TMPDIR" >/dev/null
TARPATH="$OUTDIR/${NAME}.tar.gz"
echo "Creating compressed tarball: $TARPATH"
tar --exclude='*.pyc' -czf "$TARPATH" .
popd >/dev/null

echo "Release tar created: $TARPATH"
echo "Contents (top-level):"
tar -tzf "$TARPATH" | sed -n '1,40p'

echo "Cleaning temporary workspace"
rm -rf "$TMPDIR"

exit 0
