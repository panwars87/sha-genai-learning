"""Module 0 · Break it. Predict what happens before you read each result.

Run:   uv run modules/00-how-llms-work/99_break_it.py

1. Feed it a PDF.                    → refused by a cheap check, before any money is spent
2. Feed it a 60,000-character file.  → same: guardrails sit in front of the model
3. Use a wrong API key.              → a clear AuthenticationError from the vendor
4. Ask about something not in the prompt (yesterday's invoices).
                                      → the model only knows its training data plus what you send

Write down which result surprised you.
"""

import tempfile
from pathlib import Path

import litellm

from documind.config import get_settings
from documind.documents import DocumentError
from documind.llm import chat
from documind.summarize import summarize_document

settings = get_settings()
scratch = Path(tempfile.mkdtemp())

print("── 1. A PDF ──")
(scratch / "scan.pdf").write_bytes(b"%PDF-1.7 not really")
try:
    summarize_document(scratch / "scan.pdf")
except DocumentError as error:
    print(f"  ✗ {error}")

print("\n── 2. A huge file ──")
(scratch / "huge.txt").write_text("Line item: paper $1.00\n" * 3000)
try:
    summarize_document(scratch / "huge.txt")
except DocumentError as error:
    print(f"  ✗ {error}")

print("\n── 3. A wrong API key ──")
try:
    litellm.completion(
        model="anthropic/claude-haiku-5-5",
        api_key="not-a-real-key",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=20,
    )
except litellm.AuthenticationError as error:
    print(f"  ✗ {type(error).__name__}: {str(error)[:120]}")

print("\n── 4. Something it was never told ──")
reply = chat([{"role": "user", "content": "Which invoices did Northwind receive yesterday?"}])
print(f"  {reply.text.strip()[:400]}")
print("  Retrieval (Module 7) is how we give it our documents to read.")
