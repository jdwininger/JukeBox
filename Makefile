# Makefile for JukeBox
# Usage:
#   make run    - runs the application using ./run.sh (preferred)
#   make package-macos - creates an unsigned .dmg containing JukeBox.app (macOS only)

.PHONY: run package-macos

run:
	./run.sh

package-macos:
	./scripts/package-macos.sh

package-appimage:
	./scripts/build-appimage.sh
