"""Module 1 · Section 5: structured output: hand the model a schema.

Explain like I'm 10: give the model a form with labelled boxes. It can only write in the boxes,
and we check every box before we file the form.

Run:   uv run modules/01-prompts-and-structured-output/05_structured_output.py

documind/schemas.py defines Invoice as a Pydantic model. Passing it as response_format tells the
vendor to return JSON in exactly that shape (LiteLLM translates this for each vendor). Then we
validate the answer anyway: trust, but verify.

Look for:
- the schema the model receives: field names, types, and our descriptions as hints
- a typed Python object at the end: invoice.total is a float, invoice.invoice_date a date
"""

import json

from documind.config import DATA_DIR, get_settings
from documind.llm import chat
from documind.prompting import render_prompt
from documind.schemas import Invoice

DOCUMENT = DATA_DIR / "invoices" / "INV-2047-globex-cloud.txt"

settings = get_settings()

print("── 1. The form the model must fill (from documind/schemas.py) ──")
schema = Invoice.model_json_schema()
for name, spec in schema["properties"].items():
    kind = spec.get("type") or " | ".join(t.get("type", "object") for t in spec.get("anyOf", []))
    print(f"  {name:<13} {kind or 'list':<16} {spec.get('description', '')}")

print("\n── 2. Ask, with the schema attached ──")
messages = [
    {"role": "system", "content": render_prompt("extract_invoice_system", settings)},
    {
        "role": "user",
        "content": render_prompt(
            "document_user",
            settings,
            document_name=DOCUMENT.name,
            document_text=DOCUMENT.read_text(),
        ),
    },
]
reply = chat(messages, response_format=Invoice)
print(f"  {reply.stats()}")

print("\n── 3. Validate, then use it like any Python object ──")
invoice = Invoice.model_validate_json(reply.text)
print(json.dumps(invoice.model_dump(mode="json"), indent=2, ensure_ascii=False))
days = (invoice.due_date - invoice.invoice_date).days if invoice.due_date else None
print(
    f"\n  {invoice.vendor} wants {invoice.total:,.2f} {invoice.currency}, payable in {days} days."
)
