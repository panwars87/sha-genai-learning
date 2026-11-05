"""The gateway: aliases, metrics, spend cap and clear errors (all offline, via mock mode)."""

from __future__ import annotations

import pytest

from documind.llm import BudgetExceededError, Gateway, UnknownAliasError, chat

from .conftest import MOCK_TEXT

HELLO = [{"role": "user", "content": "hello"}]


def test_alias_resolves_to_real_model_with_metrics(gateway: Gateway) -> None:
    reply = chat(gateway, alias="fast", messages=HELLO, max_output_tokens=50)
    assert reply.text == MOCK_TEXT
    assert reply.model == gateway.settings.gateway.aliases["fast-anthropic"]
    assert reply.input_tokens > 0 and reply.cost_usd > 0
    assert gateway.spend.calls == 1


def test_same_code_other_vendor(gateway: Gateway) -> None:
    reply = chat(gateway, alias="fast-openai", messages=HELLO, max_output_tokens=50)
    assert reply.model.startswith("openai/")


def test_unknown_alias_is_refused(gateway: Gateway) -> None:
    with pytest.raises(UnknownAliasError, match="Known:"):
        chat(gateway, alias="gpt-4", messages=HELLO, max_output_tokens=50)


def test_spend_cap_stops_calls(gateway: Gateway) -> None:
    gateway.spend.limit_usd = 0.000001
    chat(gateway, alias="fast", messages=HELLO, max_output_tokens=50)  # spends past the cap
    with pytest.raises(BudgetExceededError):
        chat(gateway, alias="fast", messages=HELLO, max_output_tokens=50)
