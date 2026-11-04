"""One place to configure logging for the whole app.

Concept taught: **production code logs; it doesn't print.** Logs carry a level and a
timestamp, and can be shipped to a log system later (Module 03 adds tracing).
"""

from __future__ import annotations

import logging

from documind.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure the root logger from settings. Safe to call more than once."""
    logging.basicConfig(level=settings.logging.level, format=settings.logging.format, force=True)
    # The HTTP libraries are chatty at INFO; keep them quiet unless we are debugging.
    for noisy in ("httpx", "httpx2", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
