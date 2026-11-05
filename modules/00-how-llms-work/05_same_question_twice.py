"""Module 0 · Section 5: same question, different answers.

Explain like I'm 10: the model rolls dice when it picks each next word, so it rarely says
exactly the same thing twice.

Run:   uv run modules/00-how-llms-work/05_same_question_twice.py

Look for:
- three different answers to one prompt. "I tried it once and it worked" proves little.
- older tutorials turned randomness down with temperature=0. Current Claude models reject the
  parameter. Consistency now comes from clear prompts and structured output (Module 1), and you
  prove it with evals (Module 9), not with a knob.
"""

import litellm

from documind.config import get_settings
from documind.llm import chat

PROMPT = "Give me a creative one-line name for a receipt-scanning app. Just the name."
RUNS = 3

settings = get_settings()

print(f"── The same prompt, {RUNS} times ──")
for run in range(1, RUNS + 1):
    print(f"  {run}. {chat([{'role': 'user', 'content': PROMPT}]).text.strip()}")
if settings.gateway.mock_response is not None:
    print("  (practice mode returns the same canned text every time)")

print("\n── The retired knob: temperature ──")
try:
    litellm.completion(
        model=settings.gateway.model_for("fast"),
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0,
        max_tokens=500,
        mock_response=settings.gateway.mock_response,
    )
    print("  accepted (practice mode, or this model still takes temperature)")
except (litellm.BadRequestError, litellm.UnsupportedParamsError) as error:
    print(f"  ✗ rejected: {str(error)[:160]}")
except litellm.AuthenticationError:
    print("  (skipped: this needs a valid ANTHROPIC_API_KEY)")
