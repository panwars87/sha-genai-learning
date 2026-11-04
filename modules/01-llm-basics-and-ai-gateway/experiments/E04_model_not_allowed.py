"""E04 · Break it: a key that may only use "fast" tries to call "smart".

Run from the module folder (gateway running):
    uv run --project app python experiments/E04_model_not_allowed.py

Why it matters: least privilege. A team can be limited to cheap models, or kept away
from a vendor that is not approved for its data, centrally and without code changes.
"""

from __future__ import annotations

import _path  # noqa: F401
from _shared import banner, create_key, delete_key, lesson_config
from documind.config import get_settings
from documind.gateway import GatewayError, build_client, chat
from pydantic import SecretStr


def main() -> None:
    cfg = lesson_config()["experiments"]
    key = create_key(models=[cfg["alias"]], metadata={"purpose": "E04 demo"})
    client = build_client(get_settings().model_copy(update={"api_key": SecretStr(key)}))
    messages = [{"role": "user", "content": cfg["probe_prompt"]}]

    try:
        banner(f"E04 · Key allows only '{cfg['alias']}'. Calling '{cfg['alias']}':")
        print(
            "  ✓",
            chat(
                client,
                model=cfg["alias"],
                messages=messages,
                max_output_tokens=cfg["probe_max_output_tokens"],
            ).text,
        )

        banner(f"E04 · Same key calling '{cfg['restricted_alias']}':")
        chat(
            client,
            model=cfg["restricted_alias"],
            messages=messages,
            max_output_tokens=cfg["probe_max_output_tokens"],
        )
        print("  ? Unexpected: the call went through.")
    except GatewayError as exc:
        print(f"  ✗ Refused: {exc}")
    finally:
        delete_key(key)


if __name__ == "__main__":
    main()
