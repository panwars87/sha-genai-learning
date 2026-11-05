"""Feature: summarize one document.

Concept taught: **an LLM feature is messages in, text out.** We fill two prompt templates (the
rules, and the document), send them to a model, and return the summary with its cost and speed.

Added in Module 0. From Module 2 the call goes through an alias (``features.summarize_alias``).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from documind.config import Settings, get_settings
from documind.documents import load_document
from documind.llm import LLMReply, chat
from documind.prompting import render_prompt


class Summary(BaseModel):
    """A document's summary and the metrics of the call that produced it."""

    document_name: str
    text: str
    reply: LLMReply


def build_messages(document_name: str, document_text: str, settings: Settings) -> list[dict]:
    """The conversation for a summary: a system message with rules, a user message with the doc."""
    return [
        {"role": "system", "content": render_prompt("summarize_system", settings)},
        {
            "role": "user",
            "content": render_prompt(
                "summarize_user",
                settings,
                document_name=document_name,
                document_text=document_text,
            ),
        },
    ]


def summarize_document(path: Path, *, alias: str | None = None) -> Summary:
    """Load a document, summarize it, and return the result.

    Args:
        path: A .txt or .md document.
        alias: Override ``features.summarize_alias`` for this call (Module 2).
    """
    settings = get_settings()
    document = load_document(path, settings)
    reply = chat(
        build_messages(document.name, document.text, settings),
        alias=alias or settings.features.summarize_alias,
    )
    return Summary(document_name=document.name, text=reply.text, reply=reply)
