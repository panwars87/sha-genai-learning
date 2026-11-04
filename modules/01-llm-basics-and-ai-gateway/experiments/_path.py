"""Lets experiments reuse the lesson helpers in ../lessons/_shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lessons"))
