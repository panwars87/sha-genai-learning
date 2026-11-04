"""E02 · Break it: give a key a $0 budget and watch the gateway refuse to spend.

Run from the module folder (gateway running):
    uv run --project app python experiments/E02_budget_exceeded.py

Why it matters: the budget is enforced BEFORE the vendor is called, so a runaway loop
or a bug cannot run up a bill past the cap.
"""

from __future__ import annotations

import _path  # noqa: F401
from _shared import banner, create_key, delete_key, lesson_config
from documind.config import get_settings
from documind.gateway import GatewayError, build_client, chat
from pydantic import SecretStr


def main() -> None:
    cfg = lesson_config()["experiments"]
    key = create_key(models=[cfg["alias"]], max_budget=0.0, metadata={"purpose": "E02 demo"})
    client = build_client(get_settings().model_copy(update={"api_key": SecretStr(key)}))

    banner("E02 · A call with a key whose budget is $0.00")
    try:
        chat(
            client,
            model=cfg["alias"],
            messages=[{"role": "user", "content": cfg["probe_prompt"]}],
            max_output_tokens=cfg["probe_max_output_tokens"],
        )
        print("  ? Unexpected: the call went through.")
    except GatewayError as exc:
        print(f"  ✗ Refused: {exc}")
    finally:
        delete_key(key)  # tidy up the demo key


if __name__ == "__main__":
    main()
