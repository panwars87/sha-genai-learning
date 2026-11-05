"""Module 2 · Section 2: aliases, shortcuts and fallbacks: the gateway's whole config.

Run:   uv run modules/02-litellm-gateway/02_aliases.py

documind/settings.yaml → gateway: is the only place that knows real model names.
- aliases:   a name per real model, e.g. fast-anthropic → anthropic/claude-haiku-5-5
- shortcuts: what feature code asks for, e.g. fast → fast-anthropic
- fallbacks: if an alias fails, which ones to try next

Look for: you ask for "fast" and the reply says which real model answered and what it cost.
The prices come from LiteLLM's built-in price list; the gateway prices every call.
"""

import litellm

from documind.config import get_settings
from documind.llm import chat

QUESTION = "In one sentence, what is an invoice?"

g = get_settings().gateway

print("── Aliases (alias → real model, $ per 1M tokens in / out) ──")
for alias, model in g.aliases.items():
    try:
        info = litellm.get_model_info(model)
        cost_in, cost_out = info["input_cost_per_token"], info["output_cost_per_token"]
        price = f"${cost_in * 1e6:.2f} / ${cost_out * 1e6:.2f}"
    except Exception:  # local models have no price list entry
        price = "free (runs on your Mac)"
    print(f"  {alias:<16} → {model:<30} {price}")
print("\n── Shortcuts (what feature code asks for) ──")
for short, alias in g.shortcuts.items():
    print(f"  {short:<6} → {alias}")
print("\n── Fallbacks (if this fails → try these) ──")
for alias, backups in g.fallbacks.items():
    print(f"  {alias:<16} → {', '.join(backups)}")

print("\n── Ask for 'fast' ──")
reply = chat([{"role": "user", "content": QUESTION}], alias="fast")
print(f"  {reply.text.strip()}\n  {reply.stats()}")
