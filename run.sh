#!/usr/bin/env bash
# run.sh - Launch JukeBox from project root
# Usage: ./run.sh
set -euo pipefail

# Resolve project root (directory containing this script)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
VENV_ACTIVATE="$VENV_DIR/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
  echo "Activating virtual environment: $VENV_DIR"
  # shellcheck disable=SC1091
  . "$VENV_ACTIVATE"
  echo "Starting JukeBox using venv python (module mode)..."
  exec python -m src.main
elif [ -x "$VENV_PY" ]; then
  echo "Using venv python at: $VENV_PY (module mode)"
  exec "$VENV_PY" -m src.main
else
  echo "No virtual environment found at $VENV_DIR"
  echo "Attempting to run with system python3 (module mode; ensure dependencies installed)..."
  exec python3 -m src.main
fi
