"""Load prompt templates from ``prompts/*.md`` and fill their placeholders.

Concept taught: **prompts are product text, not code.** Keeping them in files means they can
be reviewed, diffed and versioned like anything else, and changed without touching Python.

Added in Module 0.
"""

from __future__ import annotations

from documind.config import Settings, get_settings


class PromptError(LookupError):
    """A prompt template is missing or a placeholder has no value."""


def render_prompt(name: str, settings: Settings | None = None, **values: str) -> str:
    """Load ``prompts/<name>.md`` and fill its ``{placeholders}``.

    Values are inserted as-is, so braces inside a document are safe.
    """
    settings = settings or get_settings()
    path = settings.prompts_path / f"{name}.md"
    if not path.is_file():
        raise PromptError(f"Prompt template not found: {path}")
    try:
        return path.read_text(encoding="utf-8").format(**values).strip()
    except KeyError as exc:
        raise PromptError(f"Prompt '{name}' needs a value for {exc}") from exc
