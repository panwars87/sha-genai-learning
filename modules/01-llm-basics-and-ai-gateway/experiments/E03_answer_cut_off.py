"""E03 · Break it: set max_output_tokens far too low and watch the answer get cut off.

Run from the module folder (gateway running, DOCUMIND_API_KEY set):
    uv run --project app python experiments/E03_answer_cut_off.py

Why it matters: a cut-off answer looks like a normal answer unless you check
finish_reason. With thinking models the visible answer can even be empty, because the
budget ran out while the model was still thinking.

Needs real models: the mock gateway always returns its full canned reply.
"""

from __future__ import annotations

import _path  # noqa: F401
from _shared import banner, lesson_config, show_reply
from documind.config import get_settings
from documind.gateway import build_client, chat


def main() -> None:
    cfg = lesson_config()["experiments"]
    client = build_client(get_settings())

    limit = cfg["tiny_max_output_tokens"]
    banner(f"E03 · '{cfg['long_answer_prompt']}' with max_output_tokens={limit}")
    reply = chat(
        client,
        model=cfg["alias"],
        messages=[{"role": "user", "content": cfg["long_answer_prompt"]}],
        max_output_tokens=limit,
    )
    show_reply(reply)
    if reply.finish_reason == "length":
        print(
            "\n  finish_reason='length' → the model was stopped mid-answer. Production code\n"
            "  must check this. DocuMind logs a warning when it happens."
        )


if __name__ == "__main__":
    main()
