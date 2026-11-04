"""Helpers shared by the Module 01 lessons and experiments.

Lessons reuse the DocuMind app's own settings and gateway client, so what you learn here
is exactly what the app does. This file adds only demo conveniences: pretty printing and
the few *admin* calls (issuing and revoking keys) that need the gateway's master key.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx2
import yaml
from documind.config import ENV_FILE, get_settings
from documind.gateway import LLMReply
from dotenv import dotenv_values

LESSONS_DIR = Path(__file__).resolve().parent
LESSON_CONFIG_FILE = LESSONS_DIR / "lessons.yaml"


def lesson_config() -> dict[str, Any]:
    """Load lessons.yaml."""
    return yaml.safe_load(LESSON_CONFIG_FILE.read_text(encoding="utf-8"))


def resolve(relative: str) -> Path:
    """Resolve a path written in lessons.yaml relative to this folder."""
    return (LESSONS_DIR / relative).resolve()


def read_secret(name: str) -> str:
    """Read one named secret from the environment, falling back to the repo's .env file.

    Only lessons that genuinely need a secret call this, and they ask for it by name.

    Raises:
        SystemExit: with setup instructions if the secret is missing.
    """
    value = os.getenv(name) or dotenv_values(ENV_FILE).get(name)
    if not value:
        raise SystemExit(f"{name} is not set. Add it to {ENV_FILE} (see .env.example).")
    return value


# ── Admin calls (master key) ──────────────────────────────────────────────────────────


def admin_request(method: str, path: str, **kwargs: Any) -> httpx2.Response:
    """Call a gateway admin endpoint with the master key."""
    settings = get_settings()
    master_key = read_secret(lesson_config()["admin"]["master_key_env"])
    try:
        return httpx2.request(
            method,
            f"{settings.gateway.base_url}{path}",
            headers={"Authorization": f"Bearer {master_key}"},
            timeout=settings.gateway.timeout_seconds,
            **kwargs,
        )
    except httpx2.ConnectError as exc:
        raise SystemExit(
            f"Cannot reach the gateway at {settings.gateway.base_url}. "
            "Start it with: make gateway MODULE=01  (or make gateway-mock MODULE=01)"
        ) from exc


class AdminError(RuntimeError):
    """The gateway refused an admin request; the message says why."""


def _check(response: httpx2.Response) -> httpx2.Response:
    """Raise AdminError with the gateway's own explanation if the request failed."""
    if response.is_error:
        try:
            message = response.json()["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = response.text
        raise AdminError(f"HTTP {response.status_code}: {message}")
    return response


def create_key(**body: Any) -> str:
    """Issue a new virtual key and return it."""
    return _check(admin_request("POST", "/key/generate", json=body)).json()["key"]


def delete_key(key: str) -> None:
    """Revoke a virtual key immediately."""
    _check(admin_request("POST", "/key/delete", json={"keys": [key]}))


def delete_key_by_alias(alias: str) -> None:
    """Revoke the key that has this alias."""
    _check(admin_request("POST", "/key/delete", json={"key_aliases": [alias]}))


# ── Printing ──────────────────────────────────────────────────────────────────────────


def banner(title: str) -> None:
    """Print a section heading."""
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def show(label: str, value: Any) -> None:
    """Print one labelled value."""
    print(f"  {label:<22} {value}")


def show_reply(reply: LLMReply) -> None:
    """Print a model answer and the facts the gateway reported about it."""
    print(f"\n  Answer: {reply.text.strip() or '(empty)'}\n")
    show("alias asked for", reply.model_alias)
    show("model that answered", reply.provider_model)
    show("finish reason", reply.finish_reason)
    show("tokens in / out", f"{reply.input_tokens} / {reply.output_tokens}")
    if reply.reasoning_tokens:
        show("  of which thinking", reply.reasoning_tokens)
    show("cost (USD)", f"${reply.cost_usd:.6f}" if reply.cost_usd is not None else "n/a")
    show("latency", f"{reply.latency_ms:,.0f} ms" if reply.latency_ms is not None else "n/a")
