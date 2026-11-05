"""Feature: classify a document, then extract its fields as validated JSON.

Concepts taught:
- **Two small, focused prompts beat one big one.** First a cheap call decides *what* the document
  is; then a second call extracts fields using the schema for that type.
- **Structured output.** Each call passes a Pydantic schema as ``response_format``; the vendor
  returns JSON in that shape and we validate it before anyone uses it.

Added in Module 1. Module 13 turns these two steps into nodes of the upload agent.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic import BaseModel, ValidationError

from documind.config import get_settings
from documind.documents import Document, load_document
from documind.llm import LLMError, LLMReply, chat
from documind.prompting import render_prompt
from documind.schemas import SCHEMAS, Classification, Invoice, Receipt

logger = logging.getLogger(__name__)


class ExtractionError(LLMError):
    """The model's answer did not match the schema, or the document type is unsupported."""


class Extraction(BaseModel):
    """The result for one document: its type, its fields, and what the calls cost."""

    document_name: str
    doc_type: str
    reason: str
    fields: Invoice | Receipt | None
    replies: list[LLMReply]

    @property
    def cost_usd(self) -> float:
        """Total cost of every call made for this document."""
        return sum(r.cost_usd for r in self.replies)


def _ask(prompt: str, document: Document, schema: type[BaseModel], alias: str):
    """One structured call: system rules + the document, answered in ``schema``'s shape."""
    settings = get_settings()
    messages = [
        {"role": "system", "content": render_prompt(prompt, settings)},
        {
            "role": "user",
            "content": render_prompt(
                "document_user", settings, document_name=document.name, document_text=document.text
            ),
        },
    ]
    reply = chat(messages, alias=alias, response_format=schema)
    try:
        return schema.model_validate_json(reply.text), reply
    except ValidationError as exc:
        # Show the first problem only: enough to debug, short enough to read.
        raise ExtractionError(
            f"{document.name}: the model's answer did not match {schema.__name__}: "
            f"{exc.errors()[0]['loc']} {exc.errors()[0]['msg']}"
        ) from exc


def classify(document: Document, *, alias: str | None = None) -> tuple[Classification, LLMReply]:
    """Decide whether a document is an invoice, a receipt or something else."""
    return _ask(
        "classify_system", document, Classification, alias or get_settings().features.classify_alias
    )


def extract_document(path: Path, *, alias: str | None = None) -> Extraction:
    """Load a document, classify it, then extract its fields with the matching schema.

    Args:
        path: A .txt or .md document.
        alias: Use this model for both calls instead of the configured ones (Module 2).
    """
    settings = get_settings()
    document = load_document(path, settings)
    label, first = classify(document, alias=alias)
    logger.info("classified %s as %s (%s)", document.name, label.doc_type, label.reason)
    if label.doc_type not in SCHEMAS:
        return Extraction(
            document_name=document.name,
            doc_type=label.doc_type,
            reason=label.reason,
            fields=None,
            replies=[first],
        )
    fields, second = _ask(
        f"extract_{label.doc_type}_system",
        document,
        SCHEMAS[label.doc_type],
        alias or settings.features.extract_alias,
    )
    return Extraction(
        document_name=document.name,
        doc_type=label.doc_type,
        reason=label.reason,
        fields=fields,
        replies=[first, second],
    )
