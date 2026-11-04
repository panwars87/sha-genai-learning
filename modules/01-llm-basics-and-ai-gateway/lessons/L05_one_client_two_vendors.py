"""L05 · One client, two vendors: the same request to Anthropic and OpenAI.

Chapter section 5. Run from the module folder (gateway running, DOCUMIND_API_KEY set):
    uv run --project app python lessons/L05_one_client_two_vendors.py

What you'll see:
    The SAME code and the SAME key send the SAME prompt to two vendors. Only the alias
    string changes. Compare answers, tokens, cost and speed side by side.
"""

from __future__ import annotations

from _shared import banner, lesson_config, show_reply
from documind.config import get_settings
from documind.gateway import GatewayError, build_client, chat


def main() -> None:
    cfg = lesson_config()["two_vendors"]
    settings = get_settings()
    client = build_client(settings)  # one client, pointed at the gateway

    banner(f"L05 · Prompt: {cfg['prompt']}")
    for alias in cfg["aliases"]:
        print(f"\n--- alias: {alias} " + "-" * 50)
        try:
            reply = chat(
                client,
                model=alias,  # ← the only thing that changes
                messages=[{"role": "user", "content": cfg["prompt"]}],
                max_output_tokens=cfg["max_output_tokens"],
            )
            show_reply(reply)
        except GatewayError as exc:
            print(f"  ✗ {exc}")
    print(
        "\n  Takeaway: switching vendor is a config change, not a code change. That is\n"
        "  vendor independence, and it is what makes fallbacks possible (Module 04)."
    )


if __name__ == "__main__":
    main()
