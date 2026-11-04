"""Feature: summarize one document.

Concept taught: **an LLM feature is just messages in, text out.** We build the
conversation (a system prompt with the rules plus a user message with the document),
send it through the gateway, and return the answer with its cost and speed.
"""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from documind.config import Settings
from documind.documents import load_document
from documind.gateway import LLMReply, chat
from documind.prompts import render_prompt


class Summary(BaseModel):
    """The summary of one document and the metrics of the call that produced it."""

    document_name: str
    text: str
    reply: LLMReply


def build_messages(document_name: str, document_text: str, settings: Settings) -> list[dict]:
    """Build the system + user messages for a summary request."""
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


def summarize_document(path: Path, client: OpenAI, settings: Settings) -> Summary:
    """Load a document, summarize it through the gateway, and return the result."""
    document = load_document(path, settings)
    reply = chat(
        client,
        model=settings.models.summarize,
        messages=build_messages(document.name, document.text, settings),
        max_output_tokens=settings.generation.max_output_tokens,
    )
    return Summary(document_name=document.name, text=reply.text, reply=reply)
