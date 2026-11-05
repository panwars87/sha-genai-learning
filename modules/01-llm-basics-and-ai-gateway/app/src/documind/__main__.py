"""Command line: ``python -m documind summarize <file>``.

A thin shell over the feature, so the same code can later sit behind an API or a UI.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from documind.config import get_settings
from documind.documents import DocumentError
from documind.llm import LLMError, build_gateway
from documind.summarize import PromptError, summarize_document

logger = logging.getLogger("documind")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an exit code (0 = success)."""
    parser = argparse.ArgumentParser(prog="documind", description="DocuMind document assistant")
    commands = parser.add_subparsers(dest="command", required=True)
    summarize_cmd = commands.add_parser("summarize", help="Summarize a document")
    summarize_cmd.add_argument("file", type=Path, help="Path to a .txt or .md document")
    args = parser.parse_args(argv)

    gateway = build_gateway(get_settings())
    try:
        summary = summarize_document(args.file, gateway)
    except (DocumentError, PromptError, LLMError) as exc:
        logger.error("%s", exc)
        return 1

    r = summary.reply
    print(f"\n{summary.document_name}\n{'-' * len(summary.document_name)}\n{summary.text}")
    print(
        f"\n[{r.alias} → {r.model} | tokens in={r.input_tokens} out={r.output_tokens} "
        f"| ${r.cost_usd:.6f} | {r.latency_ms:,.0f} ms]"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
