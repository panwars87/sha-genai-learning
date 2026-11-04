"""The only door to the AI gateway, and the only file that talks to it.

Concept taught: **the AI gateway pattern.**
DocuMind never calls Anthropic or OpenAI directly. It sends every request to the LiteLLM
proxy using the standard OpenAI-compatible format, a *virtual key* and a model *alias*
(``fast``, ``smart``…). The gateway holds the real vendor keys, picks the real model,
enforces budgets and records cost.

The gateway also reports useful facts in HTTP response headers, such as which real model
answered and what the call cost. We collect those into an ``LLMReply`` so every feature
can show the cost and speed of each call.
"""

from __future__ import annotations

import logging
from typing import Any

import openai
from openai import OpenAI
from pydantic import BaseModel

from documind.config import Settings

logger = logging.getLogger(__name__)

# Response headers the LiteLLM gateway adds to every successful call.
HEADER_COST_USD = "x-litellm-response-cost"
HEADER_PROVIDER_MODEL = "x-litellm-model-name"
HEADER_DURATION_MS = "x-litellm-response-duration-ms"
HEADER_KEY_SPEND = "x-litellm-key-spend"
HEADER_KEY_BUDGET = "x-litellm-key-max-budget"


class GatewayError(RuntimeError):
    """Base class for gateway problems, each with a message that says how to fix it."""


class GatewayUnavailableError(GatewayError):
    """The gateway could not be reached."""


class GatewayAuthError(GatewayError):
    """The virtual key is missing, wrong, revoked, or not allowed this model."""


class GatewayRequestError(GatewayError):
    """The gateway or the vendor rejected the request (bad params, budget exceeded…)."""


class LLMReply(BaseModel):
    """One model answer plus the facts a manager cares about: who, how much, how fast."""

    text: str
    model_alias: str  # what we asked for, e.g. "fast"
    provider_model: str | None  # what actually answered, e.g. "anthropic/claude-haiku-5-5"
    finish_reason: str | None  # "stop" = finished; "length" = hit max_output_tokens
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int | None  # "thinking" tokens, if the model reports them
    cost_usd: float | None
    latency_ms: float | None
    key_spend_usd: float | None  # running total for this virtual key
    key_budget_usd: float | None


def build_client(settings: Settings) -> OpenAI:
    """Create an OpenAI-compatible client pointed at the gateway (not at OpenAI).

    Raises:
        GatewayAuthError: if no virtual key is configured.
    """
    if settings.api_key is None or not settings.api_key.get_secret_value().strip():
        raise GatewayAuthError(
            "DOCUMIND_API_KEY is not set. Create a virtual key with "
            "lessons/L04_create_virtual_key.py and add it to .env."
        )
    return OpenAI(
        base_url=settings.gateway.base_url,
        api_key=settings.api_key.get_secret_value(),
        timeout=settings.gateway.timeout_seconds,
        max_retries=settings.gateway.client_max_retries,
    )


def chat(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    max_output_tokens: int,
    **extra: Any,
) -> LLMReply:
    """Send one chat request through the gateway and return the answer plus its metrics.

    Args:
        client: A client from ``build_client``.
        model: A gateway alias such as ``"fast"``. Never a vendor model ID.
        messages: The full conversation. The model remembers nothing between calls.
        max_output_tokens: Upper limit on generated tokens (thinking + answer).
        **extra: Optional extra parameters (lessons use this to experiment).

    Raises:
        GatewayUnavailableError, GatewayAuthError, GatewayRequestError.
    """
    try:
        raw = client.chat.completions.with_raw_response.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_output_tokens,
            **extra,
        )
    except openai.APIConnectionError as exc:
        raise GatewayUnavailableError(
            f"Cannot reach the AI gateway at {client.base_url}. "
            "Is it running? Start it with: make gateway MODULE=01"
        ) from exc
    except (openai.AuthenticationError, openai.PermissionDeniedError) as exc:
        raise GatewayAuthError(f"Gateway refused the key: {_error_message(exc)}") from exc
    except openai.APIStatusError as exc:
        raise GatewayRequestError(
            f"Gateway returned HTTP {exc.status_code}: {_error_message(exc)}"
        ) from exc

    completion = raw.parse()
    headers = raw.headers
    choice = completion.choices[0]
    usage = completion.usage
    details = getattr(usage, "completion_tokens_details", None) if usage else None

    reply = LLMReply(
        text=choice.message.content or "",
        model_alias=model,
        provider_model=headers.get(HEADER_PROVIDER_MODEL),
        finish_reason=choice.finish_reason,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        reasoning_tokens=getattr(details, "reasoning_tokens", None) if details else None,
        cost_usd=_header_float(headers, HEADER_COST_USD),
        latency_ms=_header_float(headers, HEADER_DURATION_MS),
        key_spend_usd=_header_float(headers, HEADER_KEY_SPEND),
        key_budget_usd=_header_float(headers, HEADER_KEY_BUDGET),
    )
    logger.info(
        "llm_call alias=%s model=%s in=%d out=%d cost_usd=%s latency_ms=%s finish=%s",
        reply.model_alias,
        reply.provider_model,
        reply.input_tokens,
        reply.output_tokens,
        reply.cost_usd,
        reply.latency_ms,
        reply.finish_reason,
    )
    if reply.finish_reason == "length":
        logger.warning("Answer was cut off at max_output_tokens=%d", max_output_tokens)
    return reply


def _header_float(headers: Any, name: str) -> float | None:
    """Read a numeric gateway header; ``None`` if absent or not a number."""
    value = headers.get(name)
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def _error_message(exc: openai.APIStatusError) -> str:
    """Pull the human-readable message out of a gateway error response."""
    body = exc.body
    if isinstance(body, dict):
        error = body.get("error", body)
        if isinstance(error, dict) and "message" in error:
            return str(error["message"])
    return str(exc)
