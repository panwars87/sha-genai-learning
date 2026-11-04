"""Shared test fixtures. Tests never touch the network or the real .env file."""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx2
import pytest
from documind.config import Settings
from openai import OpenAI


@pytest.fixture(autouse=True)
def _isolate_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make sure a developer's real environment can't leak into a test."""
    for name in ("DOCUMIND_API_KEY", "DOCUMIND_GATEWAY__BASE_URL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def settings() -> Settings:
    """Settings from the real settings.yaml, with a fake key and no .env file."""
    return Settings(_env_file=None, api_key="sk-test-virtual-key")  # type: ignore[call-arg]


GATEWAY_HEADERS = {
    "x-litellm-response-cost": "0.000123",
    "x-litellm-model-name": "anthropic/claude-haiku-5-5",
    "x-litellm-response-duration-ms": "850.5",
    "x-litellm-key-spend": "0.42",
    "x-litellm-key-max-budget": "2.0",
}


def make_client(handler: Callable[[httpx2.Request], httpx2.Response], settings: Settings) -> OpenAI:
    """An OpenAI client whose HTTP traffic goes to ``handler`` instead of a real gateway."""
    return OpenAI(
        base_url=settings.gateway.base_url,
        api_key="sk-test-virtual-key",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )


def completion_response(text: str, finish_reason: str = "stop") -> httpx2.Response:
    """A minimal OpenAI-format chat completion, as the gateway would return it."""
    body = {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 0,
        "model": "fast",
        "choices": [
            {
                "index": 0,
                "finish_reason": finish_reason,
                "message": {"role": "assistant", "content": text},
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 45, "total_tokens": 165},
    }
    return httpx2.Response(200, headers=GATEWAY_HEADERS, content=json.dumps(body))
