import os
import sys

# Ensure repository root (two levels up) is on the Python path so tests
# that import `src.*` continue to work after being moved under
# dev-resources/tests/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Create a test-local jbox_debug symlink pointing to the repo's jbox_debug so
# tests that expect debug images relative to the test file continue to work.
#
# If repo-root jbox_debug does not exist (we keep debug images untracked),
# create the directory at the repository root so test code writing to
# <repo>/jbox_debug/ continues to work. Then create a test-local symlink
# dev-resources/tests/jbox_debug -> <repo>/jbox_debug so tests looking in the
# test directory still find debug images.
test_debug_dir = os.path.join(os.path.dirname(__file__), 'jbox_debug')
repo_debug_dir = os.path.join(ROOT, 'jbox_debug')

# Ensure the (untracked) repo-level jbox_debug exists so tests can write into it.
try:
    if not os.path.exists(repo_debug_dir):
        os.makedirs(repo_debug_dir, exist_ok=True)
except Exception:
    # If we cannot create repo-level dir, fall through and ensure the test-local
    # directory exists so tests still have a place to write debug files.
    pass

# Create a test-local symlink to the repo-level debug dir when possible.
try:
    # If the test-local path already exists and is not a symlink, leave it.
    if not os.path.exists(test_debug_dir):
        os.symlink(repo_debug_dir, test_debug_dir)
except Exception:
    # If symlink creation fails (Windows or permissions), create the local
    # directory so tests won't error and will write to it instead.
    if not os.path.exists(test_debug_dir):
        os.makedirs(test_debug_dir, exist_ok=True)
