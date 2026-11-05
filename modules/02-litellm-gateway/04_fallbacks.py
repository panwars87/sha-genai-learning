"""Module 2 · Section 4: fallbacks: when a vendor fails, the gateway tries another.

Explain like I'm 10: if one shop is shut, you walk to the next one, and still come home with
milk.

Run:   uv run modules/02-litellm-gateway/04_fallbacks.py

settings.yaml says: fast-anthropic → [fast-openai]. Three experiments:
1. A rehearsal: LiteLLM pretends the primary failed (no vendor is harmed).
2. A real failure: we point fast-anthropic at a model that does not exist.
3. The same failure with NO fallback configured.

Look for: in 1 and 2 the answer still arrives, and the stats line shows OpenAI answered (plus a
WARNING log line saying so). In 3 you get a clear error instead. Feature code never changed.
"""

from documind.config import Settings, get_settings
from documind.llm import LLMError, build_gateway, chat

HELLO = [{"role": "user", "content": "Say hello in five words."}]

settings = get_settings()

print("── 1. Rehearsal: pretend the primary failed ──")
reply = chat(HELLO, alias="fast-anthropic", mock_testing_fallbacks=True)
print(f"  {reply.text.strip()}\n  {reply.stats()}")

cfg = settings.gateway.model_dump()
broken_aliases = {**cfg["aliases"], "fast-anthropic": "anthropic/claude-does-not-exist"}

print("\n── 2. A real failure, with a fallback ──")
broken = build_gateway(Settings(gateway={**cfg, "aliases": broken_aliases}))
try:
    reply = chat(HELLO, alias="fast-anthropic", gateway=broken)
    print(f"  {reply.text.strip()}\n  {reply.stats()}")
except LLMError as error:
    print(f"  ✗ {str(error)[:200]}")

print("\n── 3. The same failure, no fallback ──")
no_backup = build_gateway(Settings(gateway={**cfg, "aliases": broken_aliases, "fallbacks": {}}))
try:
    reply = chat(HELLO, alias="fast-anthropic", gateway=no_backup)
    print(f"  {reply.stats()}  (practice mode never fails)")
except LLMError as error:
    print(f"  ✗ {type(error).__name__}: {str(error)[:200]}")
