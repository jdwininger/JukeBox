#!/usr/bin/env bash
set -euo pipefail

# check-for-bloat.sh - Safety check to prevent packaging large repo artifacts into AppImage
# This script is intended to be used in CI to fail early if the repository contains
# extracted AppImage contents, a repo venv, or other large artifacts that would bloat
# packaged images.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Running repo safety checks for large artifacts..."

FAIL=0

warn_and_fail() {
  echo "ERROR: $1" >&2
  FAIL=1
}

# Forbidden top-level items that should not be committed
forbidden=("squashfs-root" "JukeBox.AppDir" "JukeBox-x86_64.AppImage" "*.AppImage" "venv" "__pycache__" ".pytest_cache")

echo "Checking for forbidden top-level entries (will fail only if tracked in git)..."
for entry in "${forbidden[@]}"; do
  if [[ "$entry" == *"*"* ]]; then
    # wildcard pattern (like *.AppImage) - check tracked files ending with .AppImage
    if git ls-files | grep -qE '\.AppImage$'; then
      warn_and_fail "Repository contains tracked AppImage files which should NOT be committed. Please remove or add to .gitignore before continuing."
    fi
  else
    # check for tracked files exactly matching the top-level name (or nested)
    # we look for tracked paths that begin with the item (top-level or nested)
    if git ls-files | grep -qE "^${entry}(/|$)"; then
      warn_and_fail "Repository contains tracked '$entry' which should NOT be committed/present. Please remove or add to .gitignore before continuing."
    fi
  fi
done

# Also allow an env override to skip the repo safety check (local experimentation only)
if [ "${SKIP_REPO_SAFETY:-0}" = "1" ]; then
  echo "SKIP_REPO_SAFETY=1 set — skipping strict repo file checks (only use for local testing)."
  exit 0
fi

# Check for large files (threshold configurable via env, default 25MB). This catches any accidental big binary.
THRESHOLD_MB=${REPO_FILE_SIZE_THRESHOLD_MB:-25}
echo "Scanning for repository files > ${THRESHOLD_MB}MB (this may take a moment)..."
bigfiles=$(git ls-files -z | xargs -0 -I{} bash -lc 'if [ -f "{}" ]; then du -m "{}" | cut -f1 && echo " {}"; fi' 2>/dev/null | awk -v t=$THRESHOLD_MB '$1+0 > t {print $0}') || true
if [ -n "$bigfiles" ]; then
  echo "Found large tracked file(s) exceeding ${THRESHOLD_MB}MB threshold:" >&2
  echo "$bigfiles" >&2
  echo "Remove or LFS/ignore them before packaging — these will bloat AppImage builds." >&2
  FAIL=1
fi

if [ $FAIL -ne 0 ]; then
  echo "One or more repository safety checks failed. Aborting." >&2
  exit 1
fi

echo "Repo safety checks passed. No unexpected large artifacts found."
