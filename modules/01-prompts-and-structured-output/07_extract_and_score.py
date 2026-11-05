"""Module 1 · Section 7: the app extracts all 10 documents, and we score it.

Run:   uv run modules/01-prompts-and-structured-output/07_extract_and_score.py
One document from the command line:
       uv run python -m documind extract data/invoices/INV-0457-umbrella-print.txt

documind/extract.py makes two calls per document: classify (invoice / receipt / other), then
extract with the matching schema. data/golden/ holds the hand-checked right answer for each.

Look for:
- which fields go wrong, and on which documents (UK dates? GST tax? a missing due date?)
- a single accuracy number. It is the start of evals (Module 9): change a prompt, rerun this,
  and you know whether you made things better or worse.
"""

import json
from datetime import date

from documind.config import DATA_DIR, get_settings
from documind.extract import ExtractionError, extract_document

get_settings()


def same(expected: object, actual: object) -> bool:
    """Field match: numbers to the cent, text ignoring case and spaces."""
    if isinstance(actual, date):
        actual = actual.isoformat()
    if isinstance(expected, int | float) and isinstance(actual, int | float):
        return abs(expected - actual) < 0.005
    if isinstance(expected, str) and isinstance(actual, str):
        return expected.strip().lower() == actual.strip().lower()
    return expected == actual


checked = correct = 0
total_cost = 0.0
for golden_path in sorted((DATA_DIR / "golden").glob("*.json")):
    golden = json.loads(golden_path.read_text())
    folder = "invoices" if golden["document"].startswith("INV") else "receipts"
    try:
        result = extract_document(DATA_DIR / folder / golden["document"])
    except ExtractionError as error:
        print(f"✗ {golden['document']}: {error}")
        continue
    total_cost += result.cost_usd
    misses = []
    checked += 1
    correct += result.doc_type == golden["doc_type"]
    if result.doc_type != golden["doc_type"]:
        misses.append(f"doc_type={result.doc_type}")
    elif result.fields is not None:
        got = result.fields.model_dump()
        for field, expected in golden["fields"].items():
            if field in ("line_items", "items"):  # count the lines; Module 9 scores them properly
                expected, actual = len(expected), len(got[field])
            else:
                actual = got[field]
            checked += 1
            if same(expected, actual):
                correct += 1
            else:
                misses.append(f"{field}: expected {expected!r}, got {actual!r}")
    mark = "✓" if not misses else "✗"
    shown = "; ".join(misses[:3]) + (f" (+{len(misses) - 3} more)" if len(misses) > 3 else "")
    print(f"{mark} {golden['document']:<34} {result.doc_type:<8} {shown}")

if checked:
    print(f"\nScore: {correct}/{checked} fields ({correct / checked:.0%}), cost ${total_cost:.4f}")
