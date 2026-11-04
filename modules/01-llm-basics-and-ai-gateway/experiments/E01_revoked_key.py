"""E01 · Break it: revoke a key and watch the app lose access instantly.

Run from the module folder (gateway running):
    uv run --project app python experiments/E01_revoked_key.py

Why it matters: with vendor keys in apps, a leaked key means rotating it everywhere.
With a gateway, you revoke one virtual key centrally and nothing else is affected.
"""

from __future__ import annotations

import _path  # noqa: F401  (makes ../lessons importable)
from _shared import banner, create_key, delete_key, lesson_config
from documind.config import get_settings
from documind.gateway import GatewayError, build_client, chat
from pydantic import SecretStr


def main() -> None:
    cfg = lesson_config()["experiments"]
    settings = get_settings()
    key = create_key(models=[cfg["alias"]], key_alias=None, metadata={"purpose": "E01 demo"})
    client = build_client(settings.model_copy(update={"api_key": SecretStr(key)}))
    messages = [{"role": "user", "content": cfg["probe_prompt"]}]

    banner("E01 · 1. Call with a fresh key")
    print(
        "  ✓",
        chat(
            client,
            model=cfg["alias"],
            messages=messages,
            max_output_tokens=cfg["probe_max_output_tokens"],
        ).text,
    )

    banner("E01 · 2. Admin revokes the key, then the same call again")
    delete_key(key)
    try:
        chat(
            client,
            model=cfg["alias"],
            messages=messages,
            max_output_tokens=cfg["probe_max_output_tokens"],
        )
        print("  ? Unexpected: the call still worked.")
    except GatewayError as exc:
        print(f"  ✗ Blocked, as expected: {exc}")


if __name__ == "__main__":
    main()
