"""Document guardrails and the summarize feature (Module 0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from documind.config import get_settings
from documind.documents import DocumentError, load_document
from documind.summarize import build_messages, summarize_document

from .conftest import MOCK_TEXT


@pytest.mark.parametrize(
    ("filename", "content", "error"),
    [
        ("scan.pdf", "x", "Unsupported"),
        ("empty.txt", "  \n", "empty"),
        ("big.txt", "x" * 60_000, "limit"),
    ],
)
def test_bad_documents_are_rejected(
    tmp_path: Path, filename: str, content: str, error: str
) -> None:
    (tmp_path / filename).write_text(content)
    with pytest.raises(DocumentError, match=error):
        load_document(tmp_path / filename, get_settings())


def test_messages_have_rules_then_document() -> None:
    messages = build_messages("INV-1.txt", "Total {not a placeholder}", get_settings())
    assert [m["role"] for m in messages] == ["system", "user"]
    assert '<document name="INV-1.txt">' in messages[1]["content"]
    assert "{not a placeholder}" in messages[1]["content"]  # braces in documents are safe


def test_summarize_end_to_end(tmp_path: Path) -> None:
    doc = tmp_path / "INV-1.txt"
    doc.write_text("ACME INVOICE INV-1 total $10.00")
    summary = summarize_document(doc)
    assert summary.document_name == "INV-1.txt"
    assert summary.text == MOCK_TEXT
    assert summary.reply.alias == "fast"
