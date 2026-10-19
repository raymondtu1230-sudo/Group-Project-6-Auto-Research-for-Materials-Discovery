"""Make the repository-owned M2 package importable in its focused test suite."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
