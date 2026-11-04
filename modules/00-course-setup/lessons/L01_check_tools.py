"""L01 · Are the tools installed?

Chapter section 2. Run from the repo root:
    python3 modules/00-course-setup/lessons/L01_check_tools.py

Checks the Python version and that the command-line tools the course uses are on PATH.
"""

from __future__ import annotations

import shutil
import sys

from _common import load_checks, report


def main() -> int:
    cfg = load_checks()["tools"]
    print("\nTools")
    required_py = tuple(int(part) for part in cfg["python_min"].split("."))
    ok = report(
        sys.version_info >= required_py,
        f"python >= {cfg['python_min']}",
        f"found {sys.version.split()[0]}",
    )
    for tool in cfg["required"]:
        path = shutil.which(tool)
        ok &= report(path is not None, tool, path or "not found: see chapter section 2")
    for tool in cfg["optional"]:
        path = shutil.which(tool)
        report(path is not None, f"{tool} (optional)", path or "not found (fine in Colab)")
    print("\n  All required tools found." if ok else "\n  Install the missing tools, then re-run.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
