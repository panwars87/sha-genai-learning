"""Test setup: no network, no real keys, no surprises from the developer's environment."""

from __future__ import annotations

import os

# Use LiteLLM's bundled price list instead of downloading it (tests stay offline), and put the
# whole app in mock mode before anything loads settings.
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["DOCUMIND_GATEWAY__MOCK_RESPONSE"] = "- Invoice INV-1 from Acme, total $10.00"

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402

from documind.config import get_settings  # noqa: E402
from documind.llm import get_gateway  # noqa: E402

MOCK_TEXT = os.environ["DOCUMIND_GATEWAY__MOCK_RESPONSE"]


@pytest.fixture(autouse=True)
def fresh_app(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Every test starts with freshly loaded settings and a new gateway (spend = $0)."""
    monkeypatch.setenv("DOCUMIND_GATEWAY__MOCK_RESPONSE", MOCK_TEXT)
    get_settings.cache_clear()
    get_gateway.cache_clear()
    yield
    get_settings.cache_clear()
    get_gateway.cache_clear()


def use_mock(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """Make every model call return ``text`` for the rest of the test."""
    monkeypatch.setenv("DOCUMIND_GATEWAY__MOCK_RESPONSE", text)
    get_settings.cache_clear()
    get_gateway.cache_clear()
