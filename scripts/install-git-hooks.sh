#!/usr/bin/env bash
set -euo pipefail

# install-git-hooks.sh - Convenience script to enable repository local git hooks
# This will set git config core.hooksPath to the .githooks directory in repo root.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_DIR="$ROOT_DIR/.githooks"


if [ ! -d "$HOOK_DIR" ]; then
  echo "Creating .githooks directory"
  mkdir -p "$HOOK_DIR"
fi

echo "Linking or copying pre-commit hook into .githooks (ensure it's executable)"
if [ -e "$HOOK_DIR/pre-commit" ]; then
  echo "Pre-commit hook already present in $HOOK_DIR. Ensuring it's executable."
  chmod +x "$HOOK_DIR/pre-commit" || true
else
  # Copy the template hook in place
  cp -a "$ROOT_DIR/.githooks/pre-commit" "$HOOK_DIR/pre-commit"
  chmod +x "$HOOK_DIR/pre-commit"
fi

echo "Configuring git to use $HOOK_DIR as hooksPath"
git config core.hooksPath "$HOOK_DIR"

echo "Git hooks installed. The pre-commit safety check will now run on commits."
