"""Module 1 · Section 1: anatomy of a prompt, and why specific beats vague.

Explain like I'm 10: asking "tell me about this" gets you a ramble. Asking "three bullets, for
my boss, totals first" gets you exactly what you need.

Run:   uv run modules/01-prompts-and-structured-output/01_system_and_user.py

A prompt has two parts:
- system: who the model is, the rules, the output format. Same for every document.
- user:   the task and the data. Changes every time.

Look for: the vague prompt's answer is longer, slower and dearer, and you can't predict its
shape. The specific one is short and has the same shape every run.
"""

from documind.config import DATA_DIR, get_settings
from documind.llm import chat

DOCUMENT = (DATA_DIR / "invoices" / "INV-2047-globex-cloud.txt").read_text()
VAGUE = [{"role": "user", "content": f"Tell me about this.\n\n{DOCUMENT}"}]
SPECIFIC = [
    {
        "role": "system",
        "content": (
            "You are an accounts-payable assistant. Reply with exactly three bullets, in this "
            "order: who must be paid, how much (with currency), and by when. "
            "Use only facts in the document. No other text."
        ),
    },
    {"role": "user", "content": DOCUMENT},
]

get_settings()
for label, messages in (("VAGUE", VAGUE), ("SPECIFIC", SPECIFIC)):
    reply = chat(messages)
    print(f"── {label} ──\n{reply.text.strip()}\n{reply.stats()}\n")
