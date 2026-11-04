"""Load documents safely before they go anywhere near a model.

Concept taught: **guardrails before the LLM.** Cheap checks in plain code (file type,
size) stop bad or oversized inputs before they cost money or fill the context window.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from documind.config import Settings


class DocumentError(ValueError):
    """The document cannot be processed (missing, wrong type, too large, empty)."""


class Document(BaseModel):
    """A loaded document, ready to put into a prompt."""

    name: str
    path: Path
    text: str

    @property
    def char_count(self) -> int:
        """Number of characters, a rough guide to token count (about 4 chars per token)."""
        return len(self.text)


def load_document(path: Path, settings: Settings) -> Document:
    """Read a text document and check it against the configured guardrails.

    Raises:
        DocumentError: with a message explaining what is wrong.
    """
    rules = settings.documents
    if not path.is_file():
        raise DocumentError(f"File not found: {path}")
    if path.suffix.lower() not in rules.allowed_extensions:
        raise DocumentError(
            f"Unsupported file type '{path.suffix}'. Allowed: {', '.join(rules.allowed_extensions)}"
        )

    text = path.read_text(encoding=rules.encoding).strip()
    if not text:
        raise DocumentError(f"Document is empty: {path}")
    if len(text) > rules.max_chars:
        raise DocumentError(
            f"Document has {len(text):,} characters; the limit is {rules.max_chars:,}. "
            "Raise documents.max_chars in settings.yaml if this is intended."
        )
    return Document(name=path.name, path=path, text=text)
