"""Module 2 · Break it. Predict what happens before you read each result.

Run:   uv run modules/02-litellm-gateway/99_break_it.py

1. A batch with a budget: extract all 10 documents with a $0.0005 cap.
                                → it stops partway, and you know exactly where
2. Every vendor down at once (both keys wrong).
                                → fallbacks can't help; one clear error
3. Ask the local model when Ollama isn't running.
                                → "could not reach", not a hang

Write down which result surprised you.
"""

import os

from documind.config import DATA_DIR, Settings, get_settings
from documind.extract import extract_document
from documind.llm import BudgetExceededError, LLMError, build_gateway, chat, get_gateway

BATCH_CAP_USD = 0.0005
HELLO = [{"role": "user", "content": "hi"}]

settings = get_settings()

print(f"── 1. Ten documents, a ${BATCH_CAP_USD} budget ──")
get_gateway().spend.limit_usd = BATCH_CAP_USD
for path in sorted((DATA_DIR / "invoices").glob("*.txt")) + sorted(
    (DATA_DIR / "receipts").glob("*.txt")
):
    try:
        result = extract_document(path)
        print(
            f"  ✓ {path.name:<34} ${result.cost_usd:.6f}"
            f"  (total ${get_gateway().spend.spent_usd:.6f})"
        )
    except BudgetExceededError as error:
        print(f"  ✗ {path.name:<34} {error}")
        break
    except LLMError as error:
        print(f"  ✗ {path.name:<34} {str(error)[:100]}")

print("\n── 2. Every vendor down ──")
saved = {k: os.environ.get(k) for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")}
os.environ.update(ANTHROPIC_API_KEY="wrong", OPENAI_API_KEY="wrong")
cfg = settings.gateway.model_dump() | {
    "mock_response": None
}  # a real attempt, even in practice mode
try:
    chat(HELLO, alias="fast", gateway=build_gateway(Settings(gateway=cfg)))
except LLMError as error:
    print(f"  ✗ {type(error).__name__}: {str(error)[:160]}")
finally:
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

print("\n── 3. The local model, with Ollama off ──")
try:
    reply = chat(HELLO, alias="local", gateway=build_gateway(Settings(gateway=cfg)), timeout=5)
    print(f"  ✓ Ollama is running: {reply.stats()}")
except LLMError as error:
    print(f"  ✗ {type(error).__name__}: {str(error)[:160]}")
