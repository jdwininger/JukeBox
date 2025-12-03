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
test_debug_dir = os.path.join(os.path.dirname(__file__), 'jbox_debug')
repo_debug_dir = os.path.join(ROOT, 'jbox_debug')
try:
    if os.path.exists(repo_debug_dir) and not os.path.exists(test_debug_dir):
        os.symlink(repo_debug_dir, test_debug_dir)
except Exception:
    # If symlink creation fails (Windows or permissions), make a directory
    # so the tests won't error, tests will still look for files there.
    if not os.path.exists(test_debug_dir):
        os.makedirs(test_debug_dir, exist_ok=True)
