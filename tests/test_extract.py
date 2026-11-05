"""Structured output: classify, extract, validate (Module 1), and the golden set."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from documind.config import DATA_DIR
from documind.extract import ExtractionError, extract_document
from documind.schemas import SCHEMAS

from .conftest import use_mock

GOLDEN = sorted((DATA_DIR / "golden").glob("*.json"))
INVOICE = DATA_DIR / "invoices" / "INV-1001-acme-supplies.txt"


def test_there_are_ten_golden_answers_and_each_fits_its_schema() -> None:
    assert len(GOLDEN) == 10
    for path in GOLDEN:
        golden = json.loads(path.read_text())
        SCHEMAS[golden["doc_type"]].model_validate(golden["fields"])
        assert any((DATA_DIR / d / golden["document"]).is_file() for d in ("invoices", "receipts"))


def test_extract_returns_validated_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    golden = json.loads((DATA_DIR / "golden" / "INV-1001-acme-supplies.json").read_text())
    # One mock answer serves both calls: the classifier reads doc_type/reason, the extractor
    # reads the invoice fields; each schema ignores the other's keys.
    use_mock(monkeypatch, json.dumps({"doc_type": "invoice", "reason": "mock", **golden["fields"]}))
    result = extract_document(INVOICE)
    assert result.doc_type == "invoice"
    assert result.fields is not None and result.fields.total == 1101.60
    assert len(result.replies) == 2 and result.cost_usd > 0


def test_answer_that_breaks_the_schema_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    use_mock(monkeypatch, json.dumps({"doc_type": "invoice", "reason": "mock", "vendor": "Acme"}))
    with pytest.raises(ExtractionError, match="did not match Invoice"):
        extract_document(INVOICE)


def test_other_documents_get_no_fields(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    use_mock(monkeypatch, json.dumps({"doc_type": "other", "reason": "a poem"}))
    poem = tmp_path / "poem.txt"
    poem.write_text("Roses are red")
    result = extract_document(poem)
    assert result.fields is None and len(result.replies) == 1
