"""Settings load from YAML, environment variables win, and vendor keys stay out."""

from __future__ import annotations

import pytest
from documind.config import Settings


def test_yaml_values_are_loaded(settings: Settings) -> None:
    assert settings.gateway.base_url.startswith("http")
    assert settings.models.summarize == "fast"
    assert settings.prompts.path.is_dir()


def test_environment_overrides_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCUMIND_GATEWAY__BASE_URL", "http://gateway.internal:4100")
    monkeypatch.setenv("DOCUMIND_MODELS__SUMMARIZE", "smart")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.gateway.base_url == "http://gateway.internal:4100"
    assert s.models.summarize == "smart"


def test_vendor_keys_are_never_loaded(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("ANTHROPIC_API_KEY=sk-ant-secret\nDOCUMIND_API_KEY=sk-virtual\n")
    s = Settings(_env_file=env_file)  # type: ignore[call-arg]
    dumped = repr(s.model_dump())
    assert "sk-ant-secret" not in dumped
    assert s.api_key is not None and s.api_key.get_secret_value() == "sk-virtual"
    assert "sk-virtual" not in repr(s)  # SecretStr hides the key in logs
