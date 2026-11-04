"""Shared bits for the Module 00 checks. Standard library only: nothing to install yet."""

from __future__ import annotations

import tomllib
from pathlib import Path

LESSONS_DIR = Path(__file__).resolve().parent
REPO_ROOT = LESSONS_DIR.parents[2]


def load_checks() -> dict:
    """Load checks.toml."""
    return tomllib.loads((LESSONS_DIR / "checks.toml").read_text(encoding="utf-8"))


def report(ok: bool, label: str, detail: str = "") -> bool:
    """Print one check result and return whether it passed."""
    mark = "✓" if ok else "✗"
    print(f"  {mark} {label:<28} {detail}")
    return ok
