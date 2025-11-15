# Makefile for JukeBox
# Usage:
#   make run                    - runs the application using ./run.sh (preferred)
#   make package-macos          - creates an unsigned .dmg containing JukeBox.app (macOS only)
#   make standalone-macos       - creates a self-contained macOS app with embedded Python
#   make standalone-dmg         - creates a DMG of the self-contained app

.PHONY: run icon package-macos package-appimage standalone-macos standalone-dmg

run:
	./run.sh

icon:
	python3 scripts/generate-icon.py

package-macos:
	@if [ "$$(uname)" != "Darwin" ]; then \
		echo "Error: macOS app bundles can only be created on macOS systems."; \
		echo "This target requires macOS-specific tools and frameworks."; \
		echo ""; \
		echo "For Linux distribution, use:"; \
		echo "  make package-appimage"; \
		echo "  ./scripts/build-appimage.sh"; \
		exit 1; \
	fi
	./scripts/package-macos.sh

package-appimage:
	@if [ "$$(uname)" = "Darwin" ]; then \
		echo "Error: AppImage builds can only be created on Linux systems."; \
		echo "AppImage is a Linux-specific packaging format."; \
		echo ""; \
		echo "For macOS distribution, use:"; \
		echo "  make standalone-macos"; \
		echo "  ./scripts/create-standalone-macos.sh"; \
		exit 1; \
	fi
	./scripts/build-appimage.sh

standalone-macos:
	@if [ "$$(uname)" != "Darwin" ]; then \
		echo "Error: macOS app bundles can only be created on macOS systems."; \
		echo "This target requires macOS-specific tools and frameworks."; \
		echo ""; \
		echo "For Linux distribution, use:"; \
		echo "  make package-appimage"; \
		echo "  ./scripts/build-appimage.sh"; \
		exit 1; \
	fi
	./scripts/create-standalone-macos.sh

standalone-dmg: standalone-macos
	./scripts/package-standalone-macos.sh
