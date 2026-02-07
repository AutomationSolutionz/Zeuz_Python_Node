"""Root conftest.py - ensures project root is on sys.path for Framework imports."""

import sys
from pathlib import Path

# Add project root to sys.path so 'Framework' package is importable
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
