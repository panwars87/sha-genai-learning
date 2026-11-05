"""Module 0 · Setup check: is this Mac ready for the course?

Run:   uv run modules/00-how-llms-work/00_check_setup.py

Checks Python, uv and git, that your two API keys are in .env (it prints names, never values),
and lists the sample documents you will use all course.

Look for: ticks everywhere. Fix anything marked ✗ with the hint next to it, then run it again.
"""

import shutil
import sys

from dotenv import dotenv_values

from documind.config import DATA_DIR, ENV_FILE

KEY_NAMES = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")

print("── Tools ──")
ok = sys.version_info >= (3, 12)
print(f"{'✓' if ok else '✗'} Python {sys.version.split()[0]} (need 3.12+; uv installs it for you)")
for tool, hint in (("uv", "brew install uv"), ("git", "xcode-select --install")):
    found = shutil.which(tool)
    print(f"{'✓' if found else '✗'} {tool:<4} {found or 'missing → ' + hint}")

print("\n── API keys in .env (names only; values are never printed) ──")
if not ENV_FILE.is_file():
    print(f"✗ No .env file. Run:  cp .env.example .env   then paste in your keys ({ENV_FILE})")
values = dotenv_values(ENV_FILE) if ENV_FILE.is_file() else {}
for name in KEY_NAMES:
    has_value = bool((values.get(name) or "").strip())
    print(f"{'✓' if has_value else '✗'} {name:<18} {'set' if has_value else 'empty or missing'}")
print("  (A key can be set but wrong. 01_first_call.py proves it works.)")

print("\n── Sample documents (all made up) ──")
for folder in ("invoices", "receipts"):
    for path in sorted((DATA_DIR / folder).glob("*.txt")):
        text = path.read_text()
        print(f"  {folder[:-1]:<8} {path.name:<34} {len(text):>5} characters")
print(f"  golden answers: {len(list((DATA_DIR / 'golden').glob('*.json')))} (used from Module 1)")
