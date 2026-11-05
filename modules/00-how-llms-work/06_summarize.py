"""Module 0 · Section 6: DocuMind's first feature, summarize a document.

Run:   uv run modules/00-how-llms-work/06_summarize.py
Or from the command line, the same code:
       uv run python -m documind summarize data/receipts/RCPT-3002-handy-hardware.txt

What the app adds on top of the bare call from Section 1:
- documind/documents.py  checks the file first (type, size), before any money is spent
- documind/prompts/*.md  the prompt text lives in files, not in Python
- documind/summarize.py  the feature: fill the prompts, make the call, return the result
- documind/llm.py        makes the call and reports model, tokens, cost and time

Look for: a short factual summary per document, and one stats line per call.
"""

from documind.config import DATA_DIR, get_settings
from documind.summarize import summarize_document

DOCUMENTS = [
    DATA_DIR / "invoices" / "INV-1001-acme-supplies.txt",
    DATA_DIR / "receipts" / "RCPT-3001-bean-there-cafe.txt",
]

get_settings()
for path in DOCUMENTS:
    summary = summarize_document(path)
    print(f"── {summary.document_name} ──\n{summary.text}\n{summary.reply.stats()}\n")
