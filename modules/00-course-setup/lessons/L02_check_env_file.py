"""L02 · Is the .env file filled in? (Mac)

Chapter section 3. Run from the repo root:
    python3 modules/00-course-setup/lessons/L02_check_env_file.py

Checks that each required name has a value in .env. It only checks that a value is
present; it never prints or uses the secret itself. (In Colab, the notebook checks Colab
Secrets instead.)
"""

from __future__ import annotations

import sys

from _common import REPO_ROOT, load_checks, report


def parse_env_names(text: str) -> dict[str, bool]:
    """Map each NAME in a .env file to whether it has a non-empty value."""
    names: dict[str, bool] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        names[name.strip()] = bool(value.split("#")[0].strip())
    return names


def main() -> int:
    cfg = load_checks()["env_file"]
    env_file = REPO_ROOT / ".env"
    print(f"\n.env file: {env_file}")
    if not env_file.is_file():
        report(False, ".env exists", "missing. Run: cp .env.example .env")
        return 1

    text = env_file.read_text(encoding="utf-8")
    names = parse_env_names(text)
    ok = True
    for name in cfg["required"]:
        ok &= report(names.get(name, False), name, "set" if names.get(name) else "EMPTY")
    master_ok = f"LITELLM_MASTER_KEY={cfg['master_key_prefix']}" in text.replace(" ", "")
    ok &= report(master_ok, "master key format", f"must start with '{cfg['master_key_prefix']}'")
    for name in cfg["later"]:
        print(f"  · {name + ' (later)':<28} you create this in Module 01, lesson L04")
    print("\n  .env looks ready." if ok else "\n  Fill in the empty values, then re-run.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
