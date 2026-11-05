"""Module 0 · Section 1: what an LLM call is.

Explain like I'm 10: an LLM is a super-autocomplete. It reads your words as small pieces called
tokens and keeps guessing the next piece until the answer is done.

Run:   uv run modules/00-how-llms-work/01_first_call.py

This is the bare call, with no app around it: a list of messages goes in, one message comes out.
We use LiteLLM, a library that speaks one format to every vendor, and name one vendor's model
directly. (From Module 2 the app never names a model; it asks the gateway for an alias.)

Look for:
- the reply text, and the role it comes back with ("assistant")
- finish_reason: "stop" means the model finished; "length" means it was cut off
- usage: input (prompt) tokens, output (completion) tokens, and how many were "thinking"
"""

import litellm

from documind.config import get_settings

MODEL = "anthropic/claude-haiku-5-5"  # vendor/model: the one place a raw model ID appears
SYSTEM = "You are a concise assistant for a finance team."
QUESTION = "In one sentence, what is an invoice?"

settings = get_settings()  # loads your keys from .env into the environment for LiteLLM

messages = [
    {"role": "system", "content": SYSTEM},  # the rules
    {"role": "user", "content": QUESTION},  # the task
]
print("── Messages in ──")
for m in messages:
    print(f"  {m['role']:>6}: {m['content']}")

try:
    response = litellm.completion(
        model=MODEL,
        messages=messages,
        max_tokens=1000,  # the most the model may generate, thinking included
        mock_response=settings.gateway.mock_response,  # None unless you are in practice mode
    )
except litellm.AuthenticationError:
    raise SystemExit(
        "✗ Anthropic rejected the key. Put a valid ANTHROPIC_API_KEY in .env."
    ) from None

choice = response.choices[0]
print("\n── Message out ──")
print(f"  {choice.message.role}: {choice.message.content}")
print(f"\n  finish_reason : {choice.finish_reason}")
print(f"  input tokens  : {response.usage.prompt_tokens}")
print(f"  output tokens : {response.usage.completion_tokens}")
details = getattr(response.usage, "completion_tokens_details", None)
print(f"  of which thinking: {getattr(details, 'reasoning_tokens', None)}")
print(f"  cost          : ${response._hidden_params.get('response_cost') or 0:.6f}")
print("\nThat is the whole interface. Every LLM feature, however clever, is built from this.")
