"""Module 2 · Section 5: spend caps and approved models.

Explain like I'm 10: pocket money. When it's spent, it's spent, however nicely you ask.

Run:   uv run modules/02-litellm-gateway/05_spend_cap_and_approved_models.py

Two gateway guarantees, both checked BEFORE any vendor is called:
1. Spend cap: the gateway adds up every call's cost and refuses the next call once
   max_spend_usd is reached. (Here a cap of a tiny fraction of a cent.)
2. Approved models: only names in settings.yaml work. Asking for "gpt-4" is refused.

In a company, both live on a *virtual key* that the shared gateway issues to each app.

Look for: call 1 is allowed (nothing spent yet) and pushes spend past the cap; call 2 is refused
with no money spent.
"""

from documind.config import get_settings
from documind.llm import BudgetExceededError, UnknownAliasError, build_gateway, chat

TINY_CAP_USD = 0.000001
HELLO = [{"role": "user", "content": "hi"}]

tiny = build_gateway(get_settings())
tiny.spend.limit_usd = TINY_CAP_USD

print(f"── 1. Spend cap of ${TINY_CAP_USD} ──")
for attempt in (1, 2):
    try:
        reply = chat(HELLO, gateway=tiny)
        print(
            f"  call {attempt}: ✓ ${reply.cost_usd:.6f} → session total ${tiny.spend.spent_usd:.6f}"
        )
    except BudgetExceededError as error:
        print(f"  call {attempt}: ✗ {error}")

print("\n── 2. An unapproved model ──")
try:
    chat(HELLO, alias="gpt-4")
except UnknownAliasError as error:
    print(f"  ✗ {error}")
