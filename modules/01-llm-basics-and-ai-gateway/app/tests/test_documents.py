"""Document guardrails reject bad inputs before any model call."""

from __future__ import annotations

from pathlib import Path

import pytest
from documind.config import Settings
from documind.documents import DocumentError, load_document


def test_loads_text_document(tmp_path: Path, settings: Settings) -> None:
    doc = tmp_path / "invoice.txt"
    doc.write_text("INVOICE INV-1\nTotal: $10.00\n")
    loaded = load_document(doc, settings)
    assert loaded.name == "invoice.txt"
    assert "Total" in loaded.text


@pytest.mark.parametrize(
    ("filename", "content", "error"),
    [
        ("scan.pdf", "x", "Unsupported file type"),
        ("empty.txt", "   \n", "empty"),
        ("huge.txt", "x" * 60_000, "limit"),
    ],
)
def test_rejects_bad_documents(
    tmp_path: Path, settings: Settings, filename: str, content: str, error: str
) -> None:
    doc = tmp_path / filename
    doc.write_text(content)
    with pytest.raises(DocumentError, match=error):
        load_document(doc, settings)


def test_missing_file(settings: Settings) -> None:
    with pytest.raises(DocumentError, match="not found"):
        load_document(Path("does-not-exist.txt"), settings)
