"""Module 2 · Section 6: switch vendor by configuration only.

Run:   uv run modules/02-litellm-gateway/06_switch_vendor_by_config.py

The payoff. We run the unchanged DocuMind command line twice:
1. as configured: "fast" means Anthropic
2. with one environment variable, DOCUMIND_GATEWAY__SHORTCUTS__FAST=fast-openai

You could make the same change permanent by editing one line of settings.yaml. Either way,
no Python changes.

Look for: the model name in the last line of each run.
"""

import os
import subprocess
import sys

from documind.config import DATA_DIR

DOCUMENT = DATA_DIR / "receipts" / "RCPT-3002-handy-hardware.txt"
COMMAND = [sys.executable, "-m", "documind", "summarize", str(DOCUMENT)]

for label, override in (
    ("as configured", {}),
    ("fast → OpenAI", {"DOCUMIND_GATEWAY__SHORTCUTS__FAST": "fast-openai"}),
):
    print(f"── {label} ──" + (f"  {override}" if override else ""))
    run = subprocess.run(COMMAND, env={**os.environ, **override}, capture_output=True, text=True)
    lines = (run.stdout or run.stderr).strip().splitlines()
    print("  " + (lines[-1] if lines else "(no output)") + "\n")
