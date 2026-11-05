"""Module 1 · Section 6: how hallucination happens, and how a schema can cause it.

Explain like I'm 10: if a form has a box marked "required", people write *something* in it, even
when they don't know the answer.

Run:   uv run modules/01-prompts-and-structured-output/06_hallucination.py

INV-3310 has NO due date ("Due upon receipt") and NO purchase-order number. We ask for both:
- STRICT schema: both fields required, no way to say "not there". The model must invent.
- HONEST schema: both fields nullable, plus the rule "use null if it is not in the document".

Look for: plausible-looking made-up values from STRICT (a date 30 days out, "PO-…"), or an
answer that breaks the form because there was nothing true to put in it. HONEST should return
null. Hallucination is often the prompt's fault, not the model's.
"""

from datetime import date

from pydantic import BaseModel, Field, ValidationError

from documind.config import DATA_DIR, get_settings
from documind.llm import chat

DOCUMENT = (DATA_DIR / "invoices" / "INV-3310-initech-consulting.txt").read_text()


class Strict(BaseModel):
    due_date: date
    po_number: str


class Honest(BaseModel):
    due_date: date | None = Field(description="null if no calendar date is printed")
    po_number: str | None = Field(description="null if no PO number is printed")


ASK = "Extract the due date and the purchase order (PO) number from this invoice."
HONEST_RULE = " If a value is not printed in the document, use null. Never guess."

get_settings()
for label, schema, rule in (("STRICT", Strict, ""), ("HONEST", Honest, HONEST_RULE)):
    messages = [
        {"role": "system", "content": ASK + rule},
        {"role": "user", "content": f"<document>\n{DOCUMENT}\n</document>"},
    ]
    reply = chat(messages, response_format=schema)
    try:
        answer = repr(schema.model_validate_json(reply.text))
    except ValidationError as error:  # the model refused to fill a required box: good, but a crash
        answer = (
            f"✗ the answer broke the form: {error.errors()[0]['loc']} {error.errors()[0]['msg']}"
        )
    print(f"── {label} ──\n  {answer}\n  {reply.stats()}\n")
print("The truth: due_date=None (due upon receipt), po_number=None (not printed).")
