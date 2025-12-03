import os
import sys

# Ensure repository root (two levels up) is on the Python path so tests
# that import `src.*` continue to work after being moved under
# dev-resources/tests/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
