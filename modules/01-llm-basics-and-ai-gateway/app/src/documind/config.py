"""Typed settings for DocuMind, loaded from YAML and overridden by the environment.

Concept taught: **configuration lives outside code, and secrets live outside config.**
Everything that can change is in ``config/settings.yaml``. Environment variables override
it, for example in Colab or production. API keys are loaded from ``.env`` into the
environment for LiteLLM to read; they are never fields here, so the app cannot print or log them.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

# app/src/documind/config.py → APP_DIR is "app/", REPO_ROOT is the course repo.
APP_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = APP_DIR.parents[2]
SETTINGS_FILE = Path(os.getenv("DOCUMIND_SETTINGS_FILE", APP_DIR / "config" / "settings.yaml"))
ENV_FILE = Path(os.getenv("DOCUMIND_ENV_FILE", REPO_ROOT / ".env"))


class GatewaySettings(BaseModel):
    """How the AI gateway maps aliases to models, and its safety limits."""

    aliases: dict[str, str]
    shortcuts: dict[str, str]
    num_retries: int = Field(ge=0)
    timeout_seconds: float = Field(gt=0)
    max_spend_usd: float = Field(gt=0)
    mock_response: str | None = None

    def known_aliases(self) -> list[str]:
        """Every name the app may ask for: aliases plus shortcuts."""
        return [*self.aliases, *self.shortcuts]


class FeatureSettings(BaseModel):
    """Which alias each feature uses, and its output limit."""

    summarize_alias: str
    max_output_tokens: int = Field(gt=0)


class DocumentSettings(BaseModel):
    """Guardrails for the documents we accept."""

    allowed_extensions: list[str]
    max_chars: int = Field(gt=0)
    encoding: str


class LoggingSettings(BaseModel):
    """Log level and line format."""

    level: str
    format: str


class Settings(BaseSettings):
    """All DocuMind settings, validated when loaded."""

    model_config = SettingsConfigDict(
        env_prefix="DOCUMIND_",
        env_nested_delimiter="__",
        extra="ignore",
        yaml_file=SETTINGS_FILE,
    )

    gateway: GatewaySettings
    features: FeatureSettings
    documents: DocumentSettings
    prompts_dir: Path
    logging: LoggingSettings

    @property
    def prompts_path(self) -> Path:
        """Absolute path to the prompt templates."""
        return self.prompts_dir if self.prompts_dir.is_absolute() else APP_DIR / self.prompts_dir

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Precedence: explicit arguments > environment variables > settings.yaml."""
        return init_settings, env_settings, YamlConfigSettingsSource(settings_cls)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load keys from .env into the environment (for LiteLLM), then load settings once."""
    load_dotenv(ENV_FILE, override=False)  # real environment variables win over .env
    settings = Settings()  # type: ignore[call-arg]  # values come from the sources above
    logging.basicConfig(level=settings.logging.level, format=settings.logging.format, force=True)
    # Libraries log every request at INFO; keep only their warnings so our own logs stand out.
    for noisy in ("LiteLLM", "LiteLLM Router", "litellm", "httpx", "httpx2"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return settings
