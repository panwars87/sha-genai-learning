"""Module 0 · Section 4: the model has no memory.

Explain like I'm 10: every message is a phone call to someone with no memory. If you want them
to know something, you have to say it again on every call.

Run:   uv run modules/00-how-llms-work/04_no_memory.py

Three requests:
1. Tell the model a fact.
2. Ask about it in a NEW request: it has no idea.
3. Ask again, but resend the earlier messages (the "history"): now it knows.

Look for: input tokens grow in request 3. Chat apps "remember" only by resending everything,
so long chats get slower and dearer, and eventually overflow the context window (Module 8).
"""

from documind.config import get_settings
from documind.llm import chat

FACT = "Remember this: invoice INV-1001 from Acme has a total of $1,101.60."
QUESTION = "What is the total of invoice INV-1001? Answer in one short sentence."

get_settings()

print("── Request 1: tell it a fact ──")
first = chat([{"role": "user", "content": FACT}])
print(f"  {first.text}\n  {first.stats()}")

print("\n── Request 2: a new request, no history ──")
second = chat([{"role": "user", "content": QUESTION}])
print(f"  {second.text}\n  {second.stats()}")

print("\n── Request 3: resend the history with the question ──")
history = [
    {"role": "user", "content": FACT},
    {"role": "assistant", "content": first.text},
    {"role": "user", "content": QUESTION},
]
third = chat(history)
print(f"  {third.text}\n  {third.stats()}")
print(f"\n  Input tokens: {second.input_tokens} without history → {third.input_tokens} with it.")
