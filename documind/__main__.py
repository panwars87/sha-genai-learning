"""Command line: ``python -m documind summarize|extract <file> [--alias NAME]``.

A thin shell over the features, so the same code can later sit behind an API or a UI.

Added in Module 0 (summarize). Module 1 adds ``extract``; Module 2 adds ``--alias``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from documind.config import get_settings
from documind.documents import DocumentError
from documind.extract import extract_document
from documind.llm import LLMError
from documind.prompting import PromptError
from documind.summarize import summarize_document

logger = logging.getLogger("documind")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an exit code (0 = success)."""
    parser = argparse.ArgumentParser(prog="documind", description="DocuMind document assistant")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("summarize", "Summarize a document"),
        ("extract", "Classify a document and extract its fields as JSON"),
    ):
        cmd = commands.add_parser(name, help=help_text)
        cmd.add_argument("file", type=Path, help="Path to a .txt or .md document")
        cmd.add_argument("--alias", help="Model alias from settings.yaml, e.g. fast-openai")
    args = parser.parse_args(argv)

    get_settings()  # loads .env and configures logging
    try:
        if args.command == "summarize":
            result = summarize_document(args.file, alias=args.alias)
            print(f"\n{result.document_name}\n{'-' * len(result.document_name)}\n{result.text}")
            print(f"\n{result.reply.stats()}")
        else:
            result = extract_document(args.file, alias=args.alias)
            print(f"\n{result.document_name}: {result.doc_type} ({result.reason})")
            if result.fields is not None:
                print(result.fields.model_dump_json(indent=2))
            for reply in result.replies:
                print(reply.stats())
    except (DocumentError, PromptError, LLMError) as exc:
        logger.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
