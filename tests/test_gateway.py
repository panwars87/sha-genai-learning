"""The gateway: aliases, metrics, fallbacks, spend cap and clear errors (Module 2, offline)."""

from __future__ import annotations

import pytest

from documind.config import get_settings
from documind.llm import BudgetExceededError, UnknownAliasError, build_gateway, chat, get_gateway

from .conftest import MOCK_TEXT

HELLO = [{"role": "user", "content": "hello"}]


def test_alias_resolves_to_real_model_with_metrics() -> None:
    reply = chat(HELLO, alias="fast")
    assert reply.text == MOCK_TEXT
    assert reply.model == get_settings().gateway.model_for("fast")
    assert reply.input_tokens > 0 and reply.cost_usd > 0
    assert get_gateway().spend.calls == 1


def test_same_code_other_vendor() -> None:
    assert chat(HELLO, alias="fast-openai").model.startswith("openai/")


@pytest.mark.parametrize("name", ["fast-anthropic", "fast"])  # by alias and by shortcut
def test_fallback_answers_when_the_primary_fails(name: str) -> None:
    reply = chat(HELLO, alias=name, mock_testing_fallbacks=True)
    assert reply.model.startswith("openai/")


def test_unknown_alias_is_refused() -> None:
    with pytest.raises(UnknownAliasError, match="Approved:"):
        chat(HELLO, alias="gpt-4")


def test_spend_cap_stops_calls() -> None:
    tiny = build_gateway(get_settings())
    tiny.spend.limit_usd = 0.000001
    chat(HELLO, gateway=tiny)  # allowed: nothing spent yet; spends past the cap
    with pytest.raises(BudgetExceededError):
        chat(HELLO, gateway=tiny)
