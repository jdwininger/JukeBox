# Makefile for JukeBox
# Usage:
#   make run    - runs the application using ./run.sh (preferred)
#   make package-macos - creates an unsigned .dmg containing JukeBox.app (macOS only)

.PHONY: run icon package-macos package-appimage

run:
	./run.sh

icon:
	python3 scripts/generate-icon.py

package-macos:
	./scripts/package-macos.sh

package-appimage:
	./scripts/build-appimage.sh
