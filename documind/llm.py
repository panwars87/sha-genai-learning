"""The AI gateway: the only door between DocuMind and any model vendor.

Concepts taught:
- **Module 0, what a call is:** messages in, one message out, plus token counts and a
  ``finish_reason``. ``chat()`` returns all of that as an ``LLMReply``.
- **Module 2, the AI gateway pattern:** feature code never names a vendor or touches an API key.
  It asks for an *alias* ("fast", "smart", "local") and the gateway picks the real model, retries
  transient errors, falls back to another vendor when one fails, prices every call and enforces
  a spend cap.

LiteLLM does the heavy lifting. Its ``Router`` maps aliases to models, speaks one format to every
vendor and prices each call. In a company the same job is done by a shared gateway *server*; the
idea is identical.

Added in Module 0. Extended in Module 1 (structured output) and Module 2 (aliases, fallbacks,
spend cap).
"""

from __future__ import annotations

import logging
import time
import warnings
from functools import lru_cache
from typing import Any

# LiteLLM's dependencies emit a harmless typing warning on import; hide it so lesson output
# stays readable.
warnings.filterwarnings("ignore", message=".*ReadOnly.*", category=UserWarning)

import litellm  # noqa: E402
from litellm import Router  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from documind.config import Settings, get_settings  # noqa: E402

litellm.suppress_debug_info = True  # no promotional/debug banners in our output
logger = logging.getLogger(__name__)


# ── Errors that say what went wrong and how to fix it ────────────────────────────────


class LLMError(RuntimeError):
    """Base class for every gateway problem."""


class UnknownAliasError(LLMError):
    """The app asked for a model name that settings.yaml does not approve."""


class BudgetExceededError(LLMError):
    """The session spend cap was reached; the call was not made."""


class LLMAuthError(LLMError):
    """A vendor rejected the API key."""


class LLMRequestError(LLMError):
    """The request was invalid for this model (for example, an unsupported parameter)."""


class LLMUnavailableError(LLMError):
    """The vendor could not be reached, even after retries and fallbacks."""


# ── What every call returns ──────────────────────────────────────────────────────────


class LLMReply(BaseModel):
    """One answer, plus who produced it, what it cost and how fast it was."""

    text: str
    alias: str  # what we asked for, e.g. "fast"
    model: str  # what actually answered, e.g. "anthropic/claude-haiku-5-5"
    finish_reason: str | None  # "stop" = finished; "length" = cut off at the limit
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int | None  # "thinking" tokens, when the vendor reports them
    cost_usd: float
    latency_ms: float

    def stats(self) -> str:
        """One line for humans: who answered, tokens, cost, speed."""
        return (
            f"[{self.alias} → {self.model} | in={self.input_tokens} out={self.output_tokens} "
            f"| ${self.cost_usd:.6f} | {self.latency_ms:,.0f} ms | finish={self.finish_reason}]"
        )


class SpendTracker(BaseModel):
    """Running cost of this session, checked *before* each call (Module 2).

    A small version of what a company gateway does with per-team budgets.
    """

    limit_usd: float
    spent_usd: float = 0.0
    calls: int = 0

    def check(self) -> None:
        """Refuse to make another call once the cap is reached."""
        if self.spent_usd >= self.limit_usd:
            raise BudgetExceededError(
                f"Spend cap reached: ${self.spent_usd:.6f} spent, cap ${self.limit_usd:g}. "
                "Raise gateway.max_spend_usd in settings.yaml to continue."
            )

    def record(self, cost_usd: float) -> None:
        """Add one call's cost."""
        self.spent_usd += cost_usd
        self.calls += 1


# ── The gateway ──────────────────────────────────────────────────────────────────────


class Gateway(BaseModel):
    """A configured LiteLLM router plus the session's spend tracker."""

    model_config = {"arbitrary_types_allowed": True}

    router: Router
    settings: Settings
    spend: SpendTracker


def build_gateway(settings: Settings) -> Gateway:
    """Create a gateway from settings: aliases, shortcuts, fallbacks, retries, spend cap."""
    g = settings.gateway
    model_list = [
        {"model_name": alias, "litellm_params": {"model": model}}
        for alias, model in g.aliases.items()
    ]
    # LiteLLM looks fallbacks up by the name the app asked for, so a shortcut ("fast") needs the
    # same fallbacks as the alias it points at ("fast-anthropic").
    fallbacks = dict(g.fallbacks)
    for short, alias in g.shortcuts.items():
        if alias in g.fallbacks:
            fallbacks[short] = g.fallbacks[alias]
    router = Router(
        model_list=model_list,
        model_group_alias=g.shortcuts,  # "fast" → "fast-anthropic"
        fallbacks=[{name: backups} for name, backups in fallbacks.items()],
        num_retries=g.num_retries,
        timeout=g.timeout_seconds,
    )
    return Gateway(router=router, settings=settings, spend=SpendTracker(limit_usd=g.max_spend_usd))


@lru_cache(maxsize=1)
def get_gateway() -> Gateway:
    """The session's shared gateway, built once from settings.yaml."""
    return build_gateway(get_settings())


def chat(
    messages: list[dict[str, Any]],
    *,
    alias: str | None = None,
    max_output_tokens: int | None = None,
    response_format: type[BaseModel] | None = None,
    gateway: Gateway | None = None,
    **extra: Any,
) -> LLMReply:
    """Send one conversation through the gateway and return the answer with its metrics.

    Args:
        messages: The whole conversation. The model remembers nothing between calls.
        alias: A name from settings.yaml (e.g. "fast"). Never a vendor model ID.
            Defaults to ``gateway.default_alias``.
        max_output_tokens: Limit on generated tokens, thinking included.
            Defaults to ``gateway.max_output_tokens``.
        response_format: A Pydantic model. The vendor is told to return JSON in exactly this
            shape (Module 1). ``reply.text`` is then that JSON.
        gateway: A gateway from ``build_gateway``; defaults to the shared one.
        **extra: Optional vendor parameters, for experiments.

    Raises:
        UnknownAliasError, BudgetExceededError, LLMAuthError, LLMRequestError,
        LLMUnavailableError.
    """
    gw = gateway or get_gateway()
    cfg = gw.settings.gateway
    alias = alias or cfg.default_alias
    if alias not in cfg.known_aliases():
        raise UnknownAliasError(
            f"'{alias}' is not an approved model. Approved: {', '.join(cfg.known_aliases())}. "
            "Add it to gateway.aliases in settings.yaml."
        )
    limit = max_output_tokens or cfg.max_output_tokens
    gw.spend.check()
    if cfg.mock_response is not None:
        extra.setdefault("mock_response", cfg.mock_response)
    if response_format is not None:
        extra["response_format"] = response_format

    started = time.perf_counter()
    try:
        response = gw.router.completion(
            model=alias,
            messages=messages,
            max_tokens=limit,
            **extra,
        )
    except litellm.AuthenticationError as exc:
        raise LLMAuthError(f"A vendor rejected the API key. Check .env. ({exc})") from exc
    except litellm.BadRequestError as exc:
        raise LLMRequestError(f"The model rejected the request: {exc}") from exc
    except (litellm.APIConnectionError, litellm.Timeout, litellm.ServiceUnavailableError) as exc:
        raise LLMUnavailableError(f"Could not reach the model vendor: {exc}") from exc
    except litellm.APIError as exc:  # anything else the vendor reports, after fallbacks
        raise LLMUnavailableError(f"The model call failed: {exc}") from exc
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
    gw.spend.record(cost)

    logger.info("llm_call %s", reply.stats())
    primary = cfg.aliases.get(cfg.shortcuts.get(alias, alias), "")
    if primary and not primary.endswith(reply.model.split("/")[-1]):
        logger.warning("Fallback: asked for %s (%s), answered by %s", alias, primary, reply.model)
    if reply.finish_reason == "length":
        logger.warning("Answer cut off at max_output_tokens=%d", limit)
    return reply
