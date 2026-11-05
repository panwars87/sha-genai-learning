"""Module 1 · Section 3: few-shot examples teach the format faster than rules do.

Explain like I'm 10: instead of explaining a game for ten minutes, play two rounds while they
watch.

Run:   uv run modules/01-prompts-and-structured-output/03_few_shot.py

The task: turn messy payment lines from receipts into one of four labels: card, cash, mobile,
other. Zero-shot gets only the rule. Few-shot also gets three worked examples, as fake earlier
turns of the conversation.

Look for: zero-shot answers that are right but in the wrong *shape* ("Card.", "This is a card
payment"). Few-shot answers come back as exactly one label.
"""

from documind.config import get_settings
from documind.llm import chat

LINES = [
    "MASTERCARD ****5511  CHIP  APPROVED",
    "INTERAC DEBIT  ****0321",
    "PAID: APPLE PAY ••••8890",
    "CASH 120.00  CHANGE 1.93",
    "Paid via UPI to merchant@bank",
    "Gift voucher GV-2231 redeemed",
]
RULE = "Classify the payment method as card, cash, mobile or other."
EXAMPLES = [
    {"role": "user", "content": "VISA ****4242 APPROVED"},
    {"role": "assistant", "content": "card"},
    {"role": "user", "content": "GOOGLE PAY"},
    {"role": "assistant", "content": "mobile"},
    {"role": "user", "content": "STORE CREDIT"},
    {"role": "assistant", "content": "other"},
]

get_settings()
print(f"{'payment line':<38} {'zero-shot':<28} few-shot")
for line in LINES:
    zero = chat([{"role": "system", "content": RULE}, {"role": "user", "content": line}])
    few = chat([{"role": "system", "content": RULE}, *EXAMPLES, {"role": "user", "content": line}])
    print(f"{line:<38} {zero.text.strip()[:26]!r:<28} {few.text.strip()[:26]!r}")
