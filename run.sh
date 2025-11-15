#!/usr/bin/env bash
# run.sh - Launch JukeBox from project root
# Usage: ./run.sh
set -euo pipefail

# Resolve project root (directory containing this script)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Set PYTHONPATH to project root for module imports
export PYTHONPATH="$ROOT_DIR"

# Set environment variables for better GUI experience
export SDL_VIDEO_WINDOW_POS="centered"
export PYGAME_HIDE_SUPPORT_PROMPT=1

VENV_DIR="$ROOT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
VENV_ACTIVATE="$VENV_DIR/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
  echo "Activating virtual environment: $VENV_DIR"
  # shellcheck disable=SC1091
  . "$VENV_ACTIVATE"
  echo "Starting JukeBox using venv python..."
  exec python -c "from src.main import main; main()"
elif [ -x "$VENV_PY" ]; then
  echo "Using venv python at: $VENV_PY"
  exec "$VENV_PY" -c "from src.main import main; main()"
else
  echo "No virtual environment found at $VENV_DIR"
  echo "Attempting to run with system python3 (ensure dependencies installed)..."
  exec python3 -c "from src.main import main; main()"
fi
