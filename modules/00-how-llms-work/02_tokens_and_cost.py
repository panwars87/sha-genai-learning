"""Module 0 · Section 2: tokens are the unit of everything (cost, speed, limits).

Explain like I'm 10: the model doesn't read letters or words. It reads chunks called tokens,
roughly ¾ of a word each, and every token in and out has a price.

Run:   uv run modules/00-how-llms-work/02_tokens_and_cost.py

Look for:
- English is about 4 characters per token; numbers, codes and other languages cost more
- output tokens cost about 5× input tokens, so long answers are the expensive part
- the same job on the "smart" model costs ~20× more: picking the model is a cost decision
(Practice mode reports made-up token counts; run with real keys for real numbers.)
"""

import litellm

from documind.config import DATA_DIR, get_settings
from documind.llm import chat

MONTHLY_DOCUMENTS = 10_000
SAMPLES = {
    "a word": "invoice",
    "a sentence": "Please pay this invoice within thirty days.",
    "an amount": "Total due: $1,101.60 (USD) by 2026-10-15",
    "German": "Rechnung Nr. 2047, zahlbar innerhalb von 30 Tagen.",
    "a whole invoice": (DATA_DIR / "invoices" / "INV-1001-acme-supplies.txt").read_text(),
}

settings = get_settings()
fast_model = settings.gateway.model_for("fast")
smart_model = settings.gateway.model_for("smart")

print(f"── 1. Counting tokens (estimated locally for {fast_model}) ──")
for label, text in SAMPLES.items():
    tokens = litellm.token_counter(model=fast_model, text=text)
    print(
        f"  {label:<16} {len(text):>5} chars → {tokens:>4} tokens"
        f"  ({len(text) / tokens:.1f} chars/token)"
    )

print("\n── 2. A real call reports the true count ──")
invoice = SAMPLES["a whole invoice"]
reply = chat([{"role": "user", "content": f"Summarize in 3 bullets:\n{invoice}"}])
print(f"  {reply.stats()}")
print(f"  thinking tokens (billed as output): {reply.reasoning_tokens}")

print(f"\n── 3. What {MONTHLY_DOCUMENTS:,} documents a month would cost ──")
print(f"  using this call's size: {reply.input_tokens} tokens in, {reply.output_tokens} out")
for label, model in (("fast", fast_model), ("smart", smart_model)):
    price = litellm.get_model_info(model)  # LiteLLM's built-in price list
    per_call = (
        reply.input_tokens * price["input_cost_per_token"]
        + reply.output_tokens * price["output_cost_per_token"]
    )
    ratio = price["output_cost_per_token"] / price["input_cost_per_token"]
    print(
        f"  {label:<5} {model:<30} ${price['input_cost_per_token'] * 1e6:.2f}/"
        f"${price['output_cost_per_token'] * 1e6:.2f} per 1M in/out (output {ratio:.0f}× dearer)"
        f"  → ${per_call:.5f}/doc, ${per_call * MONTHLY_DOCUMENTS:,.2f}/month"
    )
