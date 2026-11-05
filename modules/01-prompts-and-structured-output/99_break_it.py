"""Module 1 · Break it. Predict what happens before you read each result.

Run:   uv run modules/01-prompts-and-structured-output/99_break_it.py

1. Too few output tokens for the JSON.  → the JSON is cut off and validation catches it
2. The wrong form: a receipt pushed through the Invoice schema.
                                        → watch it invent an invoice number
3. Not a document at all (a poem).      → the classifier says "other"; no extraction is attempted
4. An ambiguous date: "03/04/2026".     → March 4th or April 3rd? Without a rule, it guesses

Write down which result surprised you.
"""

import tempfile
from pathlib import Path

from pydantic import BaseModel, ValidationError

from documind.config import DATA_DIR, get_settings
from documind.extract import extract_document
from documind.llm import chat
from documind.schemas import Invoice

get_settings()
receipt = (DATA_DIR / "receipts" / "RCPT-3003-luigis-trattoria.txt").read_text()

print("── 1. JSON cut off by a tight output limit ──")
reply = chat(
    [{"role": "user", "content": f"Extract this invoice.\n{receipt}"}],
    response_format=Invoice,
    max_output_tokens=40,
)
print(f"  finish_reason={reply.finish_reason}, text={reply.text[:80]!r}")
try:
    Invoice.model_validate_json(reply.text)
    print("  (it fit this time; try 20)")
except ValidationError as error:
    print(f"  ✗ validation caught it: {error.errors()[0]['msg']}")

print("\n── 2. The wrong form for the document ──")
reply = chat(
    [{"role": "user", "content": f"Extract this invoice.\n{receipt}"}], response_format=Invoice
)
try:
    wrong = Invoice.model_validate_json(reply.text)
    print(
        f"  vendor={wrong.vendor!r} invoice_no={wrong.invoice_no!r}  ← there is no invoice number"
    )
except ValidationError as error:
    print(f"  ✗ {error.errors()[0]['msg']}")
print("  This is why DocuMind classifies first, then picks the schema.")

print("\n── 3. Not a document ──")
poem = Path(tempfile.mkdtemp()) / "poem.txt"
poem.write_text(
    "Roses are red, invoices are due,\nthe coffee was four-seventy-five, and so were you."
)
result = extract_document(poem)
print(f"  doc_type={result.doc_type!r}, fields={result.fields}, reason={result.reason!r}")


class JustTheDate(BaseModel):
    date: str


print("\n── 4. An ambiguous date ──")
reply = chat(
    [{"role": "user", "content": "Receipt dated 03/04/2026. Give the date as YYYY-MM-DD."}],
    response_format=JustTheDate,
)
print(f"  {JustTheDate.model_validate_json(reply.text).date}  (US reads March 4; UK reads 3 April)")
print("  Fix: tell the model the locale, or keep the raw string and decide in code.")
