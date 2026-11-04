"""L01 · What an LLM call is, done "the old way" (directly to one vendor).

Chapter section 1. Run from the module folder:
    uv run --project app python lessons/L01_direct_call_the_old_way.py

What you'll see:
    One request to Anthropic using its own SDK: messages in, text out, plus token usage.

Why it's here:
    This is the ONLY place in the course where code holds a vendor key and names a vendor
    model. Notice what that costs you: the key sits in your app, the code only works with
    one vendor, and nobody else can see or cap the spend. Section 2 fixes all three.
"""

from __future__ import annotations

import anthropic
from _shared import banner, lesson_config, read_secret, show


def main() -> None:
    cfg = lesson_config()["direct_call"]
    banner("L01 · A direct call to one vendor (the way we will NOT build DocuMind)")

    # ⚠ The app is holding a real vendor key. In every later lesson, only the gateway does.
    client = anthropic.Anthropic(api_key=read_secret(cfg["vendor_key_env"]))

    # An LLM call is just a list of messages in and a message out. Nothing is remembered.
    response = client.messages.create(
        model=cfg["vendor_model"],
        max_tokens=cfg["max_output_tokens"],
        messages=[{"role": "user", "content": cfg["prompt"]}],
    )

    # Modern models may "think" first; the visible answer is in the text blocks.
    answer = "".join(block.text for block in response.content if block.type == "text")
    print(f"\n  Prompt: {cfg['prompt']}\n  Answer: {answer.strip()}\n")
    show("model", response.model)
    show("stop reason", response.stop_reason)
    show("input tokens", response.usage.input_tokens)
    show("output tokens", response.usage.output_tokens)
    print(
        "\n  Notice: no cost figure. The vendor bills you later. Nothing here stops a bug\n"
        "  from spending $1,000 overnight. The gateway (next lessons) fixes that."
    )


if __name__ == "__main__":
    main()
