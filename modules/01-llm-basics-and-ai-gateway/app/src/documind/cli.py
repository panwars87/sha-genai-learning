"""Command line entry point: ``documind summarize <file>``.

The CLI is a thin shell: it parses arguments, calls a feature, and prints the result.
All logic lives in the feature modules, so the same code can later sit behind an API
(FastAPI) or a UI (React) unchanged.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from documind.config import get_settings
from documind.documents import DocumentError
from documind.gateway import GatewayError, build_client
from documind.logging_setup import configure_logging
from documind.prompts import PromptError
from documind.summarize import summarize_document

logger = logging.getLogger("documind")


def _format_metrics(summary) -> str:
    """One line a manager can read: which model, tokens, cost, speed."""
    r = summary.reply
    cost = f"${r.cost_usd:.6f}" if r.cost_usd is not None else "n/a"
    latency = f"{r.latency_ms:,.0f} ms" if r.latency_ms is not None else "n/a"
    return (
        f"alias={r.model_alias} → {r.provider_model} | tokens in={r.input_tokens} "
        f"out={r.output_tokens} | cost={cost} | latency={latency}"
    )


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code (0 = success)."""
    parser = argparse.ArgumentParser(prog="documind", description="DocuMind document assistant")
    commands = parser.add_subparsers(dest="command", required=True)
    summarize_cmd = commands.add_parser("summarize", help="Summarize a document")
    summarize_cmd.add_argument("file", type=Path, help="Path to a .txt or .md document")
    args = parser.parse_args(argv)

    settings = get_settings()
    configure_logging(settings)

    try:
        client = build_client(settings)
        if args.command == "summarize":
            summary = summarize_document(args.file, client, settings)
            print(f"\n{summary.document_name}\n{'-' * len(summary.document_name)}")
            print(summary.text)
            print(f"\n[{_format_metrics(summary)}]")
    except (DocumentError, GatewayError, PromptError) as exc:
        logger.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
