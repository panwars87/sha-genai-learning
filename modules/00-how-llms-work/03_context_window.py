"""Module 0 · Section 3: the context window and the output limit.

Explain like I'm 10: the model has a desk. Everything it reads and writes in one go has to fit
on the desk. The desk is big, but it has edges.

Run:   uv run modules/00-how-llms-work/03_context_window.py

Two limits matter:
- the context window: the most tokens the model can READ in one request
- max output tokens: the most it may WRITE. You set it per call; thinking counts toward it.

Look for:
- the window holds thousands of our invoices, so "will it fit?" is rarely the problem;
  cost and attention are (Module 8)
- a tight output limit gives finish_reason="length": a cut-off answer that still looks like an
  answer. Always check finish_reason.
"""

import litellm

from documind.config import DATA_DIR, get_settings
from documind.llm import chat

TIGHT_LIMIT = 60
QUESTION = "List ten things every invoice should contain, one per line."

settings = get_settings()
invoice = (DATA_DIR / "invoices" / "INV-1001-acme-supplies.txt").read_text()

print("── 1. How big is the desk? ──")
for name in ("fast", "smart"):
    model = settings.gateway.model_for(name)
    info = litellm.get_model_info(model)
    per_invoice = litellm.token_counter(model=model, text=invoice)
    print(
        f"  {model:<30} reads up to {info['max_input_tokens']:>9,} tokens, writes up to "
        f"{info['max_output_tokens']:>7,}  ≈ {info['max_input_tokens'] // per_invoice:,} invoices"
    )
print(
    f"  DocuMind's own guardrail: documents over {settings.documents.max_chars:,} chars are refused"
)

print(f"\n── 2. Output limit: {TIGHT_LIMIT} tokens ──")
short = chat([{"role": "user", "content": QUESTION}], max_output_tokens=TIGHT_LIMIT)
print(f"  {short.stats()}")
print(f"  text: {short.text!r}")

print("\n── 3. Same question, enough room ──")
full = chat([{"role": "user", "content": QUESTION}], max_output_tokens=2000)
print(f"  {full.stats()}")
print("  " + full.text.replace("\n", "\n  "))
