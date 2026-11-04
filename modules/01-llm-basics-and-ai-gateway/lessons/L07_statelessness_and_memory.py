"""L07 · The model remembers nothing. "Memory" is the app resending the conversation.

Chapter section 7. Run from the module folder (gateway running, DOCUMIND_API_KEY set):
    uv run --project app python lessons/L07_statelessness_and_memory.py

What you'll see:
    1. We tell the model a fact.
    2. In a NEW request we ask about it: it has no idea.
    3. We resend the whole conversation: now it "remembers". And it costs more tokens,
       because memory = re-reading everything, every time.
"""

from __future__ import annotations

from _shared import banner, lesson_config, show
from documind.config import get_settings
from documind.gateway import build_client, chat


def main() -> None:
    cfg = lesson_config()["memory"]
    client = build_client(get_settings())

    def send(messages):
        return chat(
            client,
            model=cfg["alias"],
            messages=messages,
            max_output_tokens=cfg["max_output_tokens"],
        )

    banner("1 · Tell the model a fact")
    first = send([{"role": "user", "content": cfg["fact"]}])
    show("you", cfg["fact"])
    show("model", first.text.strip())

    banner("2 · Ask in a brand-new request (no history sent)")
    second = send([{"role": "user", "content": cfg["question"]}])
    show("you", cfg["question"])
    show("model", second.text.strip())
    show("input tokens", second.input_tokens)

    banner("3 · Ask again, resending the conversation so far")
    history = [
        {"role": "user", "content": cfg["fact"]},
        {"role": "assistant", "content": first.text},
        {"role": "user", "content": cfg["question"]},
    ]
    third = send(history)
    show("you", cfg["question"])
    show("model", third.text.strip())
    show("input tokens", f"{third.input_tokens}  (vs {second.input_tokens} without history)")

    print(
        "\n  Every chat app works this way: it resends the history on each turn. Long chats\n"
        "  get slower and pricier, and eventually overflow the context window. Managing\n"
        "  what goes into that window is 'context engineering' (Module 08)."
    )


if __name__ == "__main__":
    main()
