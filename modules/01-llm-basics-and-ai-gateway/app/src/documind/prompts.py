"""Load prompt templates from files.

Concept taught: **prompts are product code.** Keeping them in their own files (not as
strings buried in Python) makes them easy to review, diff and version, and later
(Module 03) to manage in a prompt registry.
"""

from __future__ import annotations

from documind.config import Settings


class PromptError(LookupError):
    """A prompt template is missing or was rendered without a required value."""


def render_prompt(name: str, settings: Settings, **values: str) -> str:
    """Load ``prompts/<name>.md`` and fill in ``{placeholders}`` with ``values``.

    Values are inserted as plain text, so braces inside a document are safe.

    Raises:
        PromptError: if the file is missing or a placeholder has no value.
    """
    path = settings.prompts.path / f"{name}.md"
    if not path.is_file():
        raise PromptError(f"Prompt template not found: {path}")
    template = path.read_text(encoding="utf-8")
    try:
        return template.format(**values).strip()
    except KeyError as exc:
        raise PromptError(f"Prompt '{name}' needs a value for {exc}") from exc
