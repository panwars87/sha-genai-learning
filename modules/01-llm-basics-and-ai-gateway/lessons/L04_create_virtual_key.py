"""L04 · Issue DocuMind its own virtual key, with a budget.

Chapter section 4. Run from the module folder (gateway running):
    uv run --project app python lessons/L04_create_virtual_key.py

What you'll see:
    You act as the platform admin. Using the master key, you issue a *virtual key* for
    one app: which aliases it may use, how much it may spend, when the budget resets.
    The app gets this key, never the vendor keys.

After running:
    Copy the printed key into .env as DOCUMIND_API_KEY=...  Every later lesson uses it.

Lost the key? Revoke it and issue a new one:
    uv run --project app python lessons/L04_create_virtual_key.py --replace
"""

from __future__ import annotations

import argparse

from _shared import (
    AdminError,
    admin_request,
    banner,
    create_key,
    delete_key_by_alias,
    lesson_config,
    show,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--replace", action="store_true", help="revoke the old key first")
    args = parser.parse_args()

    cfg = lesson_config()["virtual_key"]
    banner("L04 · Issuing a virtual key for DocuMind")

    if args.replace:
        try:
            delete_key_by_alias(cfg["key_alias"])
            print(f"  Revoked the old '{cfg['key_alias']}' key.")
        except AdminError as exc:
            print(f"  No old key to revoke ({exc}).")

    try:
        key = create_key(
            key_alias=cfg["key_alias"],
            models=cfg["models"],
            max_budget=cfg["max_budget_usd"],
            budget_duration=cfg["budget_duration"],
            metadata=cfg["metadata"],
        )
    except AdminError as exc:
        raise SystemExit(
            f"  ✗ {exc}\n  A key with alias '{cfg['key_alias']}' may already exist. "
            "Re-run with --replace to revoke it and issue a new one."
        ) from exc

    # Ask the gateway what it now knows about this key.
    info = admin_request("GET", "/key/info", params={"key": key}).json()["info"]
    show("key name (masked)", info.get("key_name"))
    show("alias", info.get("key_alias"))
    show("allowed models", ", ".join(info.get("models", [])))
    show("budget (USD)", info.get("max_budget"))
    show("budget resets", cfg["budget_duration"])
    show("spent so far", info.get("spend"))

    print(
        "\n  Add this line to your .env file (it is shown only once):\n"
        f"\n      DOCUMIND_API_KEY={key}\n"
        "\n  Lost it? Re-run this lesson with --replace: the old key is revoked and a\n"
        "  new one issued. Revocation is instant (experiments/E01 shows it)."
    )


if __name__ == "__main__":
    main()
