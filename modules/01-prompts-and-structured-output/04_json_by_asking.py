"""Module 1 · Section 4: asking for JSON is not the same as getting it.

Explain like I'm 10: "please write neatly" doesn't make handwriting neat. A form with boxes does.

Run:   uv run modules/01-prompts-and-structured-output/04_json_by_asking.py

Part 1 asks politely for JSON and tries to use the answer, the way a program would.
Part 2 shows four answers models really give (no API call), and what each one does to a program.

Look for: json.loads() checks only that text is JSON. Pydantic checks that it is the RIGHT JSON:
the fields exist and have the right types. You need both, or better: Section 5.
"""

import json

from pydantic import BaseModel, ValidationError

from documind.config import DATA_DIR, get_settings
from documind.llm import chat


class Total(BaseModel):
    vendor: str
    total: float


PROMPT = "Return the vendor and total of this invoice as JSON with keys vendor and total.\n\n"
DOCUMENT = (DATA_DIR / "invoices" / "INV-1001-acme-supplies.txt").read_text()
TYPICAL_ANSWERS = {
    "clean": '{"vendor": "Acme Office Supplies Ltd", "total": 1101.60}',
    "in a code fence": '```json\n{"vendor": "Acme", "total": 1101.60}\n```',
    "chatty": 'Sure! Here it is: {"vendor": "Acme", "total": 1101.60}',
    "number as text": '{"vendor": "Acme", "total": "$1,101.60"}',
}


def try_to_use(text: str) -> str:
    """What a program experiences when it tries to use this answer."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return f"✗ not JSON ({error.msg})"
    try:
        return f"✓ usable: {Total.model_validate(data)!r}"
    except ValidationError as error:
        return f"✗ JSON, but wrong shape: {error.errors()[0]['msg']}"


get_settings()
print("── 1. Ask politely ──")
reply = chat([{"role": "user", "content": PROMPT + DOCUMENT}])
print(f"  model said: {reply.text.strip()[:200]!r}")
print(f"  program   : {try_to_use(reply.text.strip())}")

print("\n── 2. Answers models really give ──")
for label, text in TYPICAL_ANSWERS.items():
    print(f"  {label:<16} {try_to_use(text)}")
