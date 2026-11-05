"""The AI gateway: the only door between DocuMind and any model vendor.

Concept taught: **the AI gateway pattern.**
Feature code never names a vendor or touches an API key. It asks for an *alias*
("fast", "smart") and gets back an answer plus the facts a manager cares about: which
real model answered, how many tokens it used, what it cost and how long it took.

LiteLLM does the heavy lifting. Its ``Router`` maps aliases to real models, speaks one
format to every vendor, retries transient errors, and prices every call. In a company
the same job is done by a shared gateway *server*; the idea is identical.
"""

from __future__ import annotations

import logging
import time
import warnings
from typing import Any

# LiteLLM's own dependencies emit a harmless typing warning on import; hide it so lesson
# output stays readable. It does not affect behaviour.
warnings.filterwarnings("ignore", message=".*ReadOnly.*", category=UserWarning)

import litellm  # noqa: E402

litellm.suppress_debug_info = True  # no promotional/debug banners in our output
from litellm import Router  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from documind.config import Settings  # noqa: E402

logger = logging.getLogger(__name__)


# ── Errors that say what went wrong and how to fix it ────────────────────────────────


class LLMError(RuntimeError):
    """Base class for every gateway problem."""


class UnknownAliasError(LLMError):
    """The app asked for an alias that settings.yaml does not define."""


class BudgetExceededError(LLMError):
    """The session spend cap was reached; the call was not made."""


class LLMAuthError(LLMError):
    """A vendor rejected the API key."""


class LLMRequestError(LLMError):
    """The request was invalid for this model (for example, an unsupported parameter)."""


class LLMUnavailableError(LLMError):
    """The vendor could not be reached, timed out, or is overloaded."""


# ── What every call returns ──────────────────────────────────────────────────────────


class LLMReply(BaseModel):
    """One answer, plus who produced it, what it cost and how fast it was."""

    text: str
    alias: str  # what we asked for, e.g. "fast"
    model: str  # what answered, e.g. "anthropic/claude-haiku-5-5"
    finish_reason: str | None  # "stop" = finished; "length" = cut off at the limit
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int | None  # "thinking" tokens, when the vendor reports them
    cost_usd: float
    latency_ms: float


class SpendTracker(BaseModel):
    """Running cost of this session, checked *before* each call.

    A small version of what a company gateway does with per-team budgets.
    """

    limit_usd: float
    spent_usd: float = 0.0
    calls: int = 0

    def check(self) -> None:
        """Refuse to make another call once the cap is reached."""
        if self.spent_usd >= self.limit_usd:
            raise BudgetExceededError(
                f"Spend cap reached: ${_usd(self.spent_usd)} spent, cap ${_usd(self.limit_usd)}. "
                "Raise gateway.max_spend_usd in settings.yaml to continue."
            )

    def record(self, cost_usd: float) -> None:
        """Add one call's cost."""
        self.spent_usd += cost_usd
        self.calls += 1


def _usd(amount: float) -> str:
    """Format dollars without hiding tiny amounts: 1 → '1', 0.000011 → '0.000011'."""
    return f"{amount:.6f}".rstrip("0").rstrip(".") or "0"


# ── The gateway ──────────────────────────────────────────────────────────────────────


class Gateway(BaseModel):
    """A configured LiteLLM router plus the session's spend tracker."""

    model_config = {"arbitrary_types_allowed": True}

    router: Router
    settings: Settings
    spend: SpendTracker


def build_gateway(settings: Settings) -> Gateway:
    """Create the gateway from settings.yaml: aliases, shortcuts, retries, spend cap."""
    model_list = [
        {"model_name": alias, "litellm_params": {"model": model}}
        for alias, model in settings.gateway.aliases.items()
    ]
    router = Router(
        model_list=model_list,
        model_group_alias=settings.gateway.shortcuts,
        num_retries=settings.gateway.num_retries,
        timeout=settings.gateway.timeout_seconds,
    )
    return Gateway(
        router=router,
        settings=settings,
        spend=SpendTracker(limit_usd=settings.gateway.max_spend_usd),
    )


def chat(
    gateway: Gateway,
    *,
    alias: str,
    messages: list[dict[str, str]],
    max_output_tokens: int,
    **extra: Any,
) -> LLMReply:
    """Send one conversation through the gateway and return the answer with its metrics.

    Args:
        gateway: From ``build_gateway``.
        alias: A name from settings.yaml (e.g. "fast"). Never a vendor model ID.
        messages: The whole conversation. The model remembers nothing between calls.
        max_output_tokens: Limit on generated tokens, thinking included.
        **extra: Optional vendor parameters, for experiments.

    Raises:
        UnknownAliasError, BudgetExceededError, LLMAuthError, LLMRequestError,
        LLMUnavailableError.
    """
    known = gateway.settings.gateway.known_aliases()
    if alias not in known:
        raise UnknownAliasError(f"Unknown alias '{alias}'. Known: {', '.join(known)}")
    gateway.spend.check()

    if gateway.settings.gateway.mock_response is not None:
        extra.setdefault("mock_response", gateway.settings.gateway.mock_response)

    started = time.perf_counter()
    try:
        response = gateway.router.completion(
            model=alias, messages=messages, max_tokens=max_output_tokens, **extra
        )
    except litellm.AuthenticationError as exc:
        raise LLMAuthError(f"The vendor rejected the API key. Check .env. ({exc})") from exc
    except litellm.BadRequestError as exc:
        raise LLMRequestError(f"The model rejected the request: {exc}") from exc
    except (litellm.APIConnectionError, litellm.Timeout, litellm.ServiceUnavailableError) as exc:
        raise LLMUnavailableError(f"Could not reach the model vendor: {exc}") from exc
    latency_ms = (time.perf_counter() - started) * 1000

    choice = response.choices[0]
    usage = response.usage
    details = getattr(usage, "completion_tokens_details", None)
    cost = float(response._hidden_params.get("response_cost") or 0.0)
    reply = LLMReply(
        text=choice.message.content or "",
        alias=alias,
        model=response._hidden_params.get("litellm_model_name") or response.model,
        finish_reason=choice.finish_reason,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        reasoning_tokens=getattr(details, "reasoning_tokens", None),
        cost_usd=cost,
        latency_ms=latency_ms,
    )
    gateway.spend.record(cost)

    logger.info(
        "llm_call alias=%s model=%s in=%d out=%d cost_usd=%.6f latency_ms=%.0f finish=%s",
        reply.alias,
        reply.model,
        reply.input_tokens,
        reply.output_tokens,
        reply.cost_usd,
        reply.latency_ms,
        reply.finish_reason,
    )
    if reply.finish_reason == "length":
        logger.warning("Answer cut off at max_output_tokens=%d", max_output_tokens)
    return reply
