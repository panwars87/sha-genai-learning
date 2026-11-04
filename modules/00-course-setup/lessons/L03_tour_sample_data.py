"""L03 · A tour of the sample documents.

Chapter section 4. Run from the repo root:
    python3 modules/00-course-setup/lessons/L03_tour_sample_data.py

Shows what DocuMind will process: made-up invoices and receipts, as plain text for now.
"""

from __future__ import annotations

from _common import REPO_ROOT, load_checks


def main() -> None:
    cfg = load_checks()["data"]
    for folder in cfg["folders"]:
        files = sorted((REPO_ROOT / "data" / folder).glob("*.txt"))
        print(f"\n{folder}/  ({len(files)} files)")
        for path in files:
            text = path.read_text(encoding="utf-8")
            print(f"\n  ── {path.name}  ({len(text):,} characters, ~{len(text) // 4} tokens)")
            for line in text.strip().splitlines()[: cfg["preview_lines"]]:
                print(f"     {line}")
            print("     …")
    print(
        "\n  Notice how different they look: tidy invoices, cramped receipts, two\n"
        "  currencies, discounts, tips. That variety is why we use an LLM, not a template."
    )


if __name__ == "__main__":
    main()
