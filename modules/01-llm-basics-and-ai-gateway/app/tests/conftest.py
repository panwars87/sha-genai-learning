"""Test setup: no network, no real keys, no surprises from the developer's environment."""

from __future__ import annotations

import os

# Use LiteLLM's bundled price list instead of downloading it (tests stay offline).
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

import pytest  # noqa: E402

from documind.config import Settings  # noqa: E402
from documind.llm import Gateway, build_gateway  # noqa: E402

MOCK_TEXT = "- Invoice INV-1 from Acme, total $10.00"


@pytest.fixture
def settings() -> Settings:
    """The real settings.yaml, in mock mode so no vendor is ever called."""
    return Settings(gateway={**_yaml_gateway(), "mock_response": MOCK_TEXT})  # type: ignore[call-arg]


@pytest.fixture
def gateway(settings: Settings) -> Gateway:
    return build_gateway(settings)


def _yaml_gateway() -> dict:
    return Settings().gateway.model_dump()  # type: ignore[call-arg]
