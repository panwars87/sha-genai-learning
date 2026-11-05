"""Feature: summarize one document.

Concept taught: **an LLM feature is messages in, text out.** We fill two prompt
templates (the rules, and the document), send them through the gateway, and return the
summary with its cost and speed.

Prompts live in ``prompts/*.md`` rather than in Python, so they can be reviewed and
versioned like any other product text.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from documind.config import Settings
from documind.documents import load_document
from documind.llm import Gateway, LLMReply, chat


class PromptError(LookupError):
    """A prompt template is missing or a placeholder has no value."""


class Summary(BaseModel):
    """A document's summary and the metrics of the call that produced it."""

    document_name: str
    text: str
    reply: LLMReply


def render_prompt(name: str, settings: Settings, **values: str) -> str:
    """Load ``prompts/<name>.md`` and fill its ``{placeholders}``."""
    path = settings.prompts_path / f"{name}.md"
    if not path.is_file():
        raise PromptError(f"Prompt template not found: {path}")
    try:
        return path.read_text(encoding="utf-8").format(**values).strip()
    except KeyError as exc:
        raise PromptError(f"Prompt '{name}' needs a value for {exc}") from exc


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


def summarize_document(path: Path, gateway: Gateway) -> Summary:
    """Load a document, summarize it through the gateway, and return the result."""
    settings = gateway.settings
    document = load_document(path, settings)
    reply = chat(
        gateway,
        alias=settings.features.summarize_alias,
        messages=build_messages(document.name, document.text, settings),
        max_output_tokens=settings.features.max_output_tokens,
    )
    return Summary(document_name=document.name, text=reply.text, reply=reply)
