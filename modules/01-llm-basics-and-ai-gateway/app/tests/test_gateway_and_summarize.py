"""The gateway wrapper and the summarize feature, against a fake gateway."""

from __future__ import annotations

import json
from pathlib import Path

import httpx2
import pytest
from documind.config import Settings
from documind.gateway import (
    GatewayAuthError,
    GatewayRequestError,
    GatewayUnavailableError,
    build_client,
    chat,
)
from documind.summarize import summarize_document
from pydantic import SecretStr

from .conftest import completion_response, make_client


def test_summarize_sends_alias_and_reads_metrics(tmp_path: Path, settings: Settings) -> None:
    seen: dict = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen["body"] = json.loads(request.content)
        seen["auth"] = request.headers["authorization"]
        return completion_response("- Invoice from Acme, total $1,101.60")

    doc = tmp_path / "INV-1.txt"
    doc.write_text("ACME INVOICE total $1,101.60")
    summary = summarize_document(doc, make_client(handler, settings), settings)

    # The app asks for the alias, never a vendor model, and uses the virtual key.
    assert seen["body"]["model"] == "fast"
    assert seen["auth"] == "Bearer sk-test-virtual-key"
    # System prompt first, then the document wrapped in tags.
    roles = [m["role"] for m in seen["body"]["messages"]]
    assert roles == ["system", "user"]
    assert '<document name="INV-1.txt">' in seen["body"]["messages"][1]["content"]
    # Metrics come from the gateway's headers and the usage block.
    r = summary.reply
    assert summary.text.startswith("- Invoice")
    assert r.provider_model == "anthropic/claude-haiku-5-5"
    assert r.cost_usd == pytest.approx(0.000123)
    assert (r.input_tokens, r.output_tokens) == (120, 45)


def test_auth_error_is_explained(settings: Settings) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(401, json={"error": {"message": "Invalid API key provided."}})

    with pytest.raises(GatewayAuthError, match="Invalid API key"):
        chat(make_client(handler, settings), model="fast", messages=[], max_output_tokens=10)


def test_budget_error_is_explained(settings: Settings) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(422, json={"error": {"message": "Budget has been exceeded!"}})

    with pytest.raises(GatewayRequestError, match="Budget has been exceeded"):
        chat(make_client(handler, settings), model="fast", messages=[], max_output_tokens=10)


def test_unreachable_gateway_says_how_to_fix(settings: Settings) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("connection refused")

    with pytest.raises(GatewayUnavailableError, match="make gateway"):
        chat(make_client(handler, settings), model="fast", messages=[], max_output_tokens=10)


@pytest.mark.parametrize("key", [None, "", "   "])
def test_missing_virtual_key_is_explained(settings: Settings, key: str | None) -> None:
    no_key = settings.model_copy(update={"api_key": SecretStr(key) if key is not None else None})
    with pytest.raises(GatewayAuthError, match="DOCUMIND_API_KEY"):
        build_client(no_key)
