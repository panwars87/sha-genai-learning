"""Settings come from YAML, and environment variables override them."""

from __future__ import annotations

import pytest

from documind.config import Settings


def test_yaml_is_loaded() -> None:
    s = Settings()  # type: ignore[call-arg]
    assert s.features.summarize_alias == "fast"
    assert s.gateway.shortcuts["fast"] in s.gateway.aliases
    assert s.prompts_path.is_dir()


def test_environment_overrides_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCUMIND_FEATURES__SUMMARIZE_ALIAS", "smart")
    monkeypatch.setenv("DOCUMIND_GATEWAY__MAX_SPEND_USD", "0.25")
    s = Settings()  # type: ignore[call-arg]
    assert s.features.summarize_alias == "smart"
    assert s.gateway.max_spend_usd == 0.25
