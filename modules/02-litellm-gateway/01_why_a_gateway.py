"""Module 2 · Section 1: why a gateway. Where do model names live in this repo?

Explain like I'm 10: a universal TV remote. One remote works every brand of TV, and only the
remote knows the passwords. You press "fast" or "smart"; the remote picks the TV.

Run:   uv run modules/02-litellm-gateway/01_why_a_gateway.py

No model calls: this script searches the repo for vendor model IDs ("anthropic/…", "openai/…").

Look for:
- documind/settings.yaml holds them all: the gateway's alias table
- the app's feature code (summarize.py, extract.py) holds none: it asks for aliases
- a few lesson scripts hold raw IDs on purpose: the "before" picture from Module 0
Imagine 30 apps each with their own model IDs and keys. That is the problem a gateway solves.
"""

import re

from documind.config import PACKAGE_DIR, REPO_ROOT

VENDOR_ID = re.compile(r"\b(anthropic|openai|ollama_chat)/[\w.\-]+")

places = sorted(PACKAGE_DIR.glob("*.py")) + [PACKAGE_DIR / "settings.yaml"]
places += sorted((REPO_ROOT / "modules").glob("0[01]-*/*.py"))
print(f"{'file':<58} vendor model IDs")
for path in places:
    found = sorted({m.group(0) for m in VENDOR_ID.finditer(path.read_text())})
    print(f"{str(path.relative_to(REPO_ROOT)):<58} {len(found):>2}  {', '.join(found)[:60]}")
