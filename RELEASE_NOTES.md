RELEASE NOTES — Recent changes (packaging, tooling, CI, and docs)
=============================================================

This file summarizes the recent improvements made to the JukeBox repository so developers and release managers understand the new packaging flows, CI checks, and local tooling.

Highlights
---------
- Minimal release tar: new `scripts/create-release-tar.sh` (and `make release-tar`) produces a compact tar.gz containing the runtime source, assets, themes, and a small `setup_and_run.sh` helper that quickly bootstraps a venv and launches the app. This tar is included as a release artifact in GitHub releases.
- Standalone AppImage improvements: `scripts/build-appimage.sh` now creates an AppImage containing an embedded virtualenv (opt/venv), bundles native libraries, and supports `--slim` mode to aggressively trim optional heavy packages and reduce final size.
- Repo safety & pre-commit: Added `scripts/check-for-bloat.sh` and a pre-commit hook (via `.pre-commit-config.yaml` and `.githooks/pre-commit`) to prevent committing large artifacts such as extracted AppImages, repo venvs, and other files that bloat releases.
- CI & release automation: `.github/workflows/ci.yml` and `.github/workflows/release.yml` build AppImages (full+slim), run tests, generate checksums, `.zsync` metadata (when available), and upload release artifacts including the release tar. Optional GPG signing and AppImageHub listing helpers are supported through repository secrets.
- Quickstart bootstrapping: `quickstart.py` gained new flags:
  - `--bootstrap` — create a virtualenv (default `.venv`) and install `requirements.txt` into it
  - `--install-deps` — install dependencies into an existing venv
  - `--venv <path>` — choose a specific venv location
  - `--no-install` — create the venv but skip installing requirements (handy for offline prep)

Why it matters
--------------
- Releases are smaller and: either fully standalone AppImages or compact release tarballs with a small bootstrap helper, improving portability and user onboarding.
- CI will detect and fail on accidental large artifacts, keeping the repository clean and release artifacts deterministic.
- Developers can quickly bootstrap local environments using `quickstart.py` or the included `setup_and_run.sh` inside the release tarball.

Files & Tools introduced or changed
----------------------------------
- scripts/create-release-tar.sh
- scripts/build-appimage.sh (improved: embedded venv, --slim, native libs, strip/upx passes)
- scripts/check-for-bloat.sh
- scripts/publish-to-appimagehub.sh (optional helper to request AppImageHub listing)
- .pre-commit-config.yaml (repo safety, Black, isort, flake8)
- scripts/install-git-hooks.sh and .githooks/pre-commit (local hook installer)
- quickstart.py (added bootstrapping flags)
- Makefile (release-tar target + clean-release)
- .github/workflows/release.yml updated to include release tar and checksums

If you want a fully offline, prebuilt venv included in release tar (fully standalone), we can add an optional mode to build and include it — note this *increases* the tarball size substantially.

Theme & styling improvements
----------------------------------
- Added theme.conf per-button color overrides (new `[button_colors]` section) so theme authors can assign specific colors to text-labeled buttons (eg. `CLR`, `ENT`, `Credits`) without image assets. The system still prefers per-button images where provided and falls back to general theme colors.
