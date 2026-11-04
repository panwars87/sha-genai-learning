"""Typed application settings, loaded from YAML and overridden by the environment.

Concept taught: **configuration as code, secrets outside code.**
Every value the app can change lives in ``config/settings.yaml``. Environment variables
override it (useful for Colab or production). Secrets such as ``DOCUMIND_API_KEY``
come only from the environment or the git-ignored ``.env`` file.

Precedence, highest first:
    1. Environment variables   (DOCUMIND_GATEWAY__BASE_URL=...)
    2. ``.env`` file at the repo root
    3. ``config/settings.yaml``

Note: the vendor keys (ANTHROPIC_API_KEY, OPENAI_API_KEY) are deliberately *not* fields
here. Even though they sit in the same ``.env`` file, the app cannot load them. Only
the gateway reads them.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

# Folder layout: app/src/documind/config.py → APP_DIR is "app/", REPO_ROOT is the repo.
APP_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = APP_DIR.parents[2]

# These two locations can themselves be overridden, e.g. in tests or Colab.
SETTINGS_FILE = Path(os.getenv("DOCUMIND_SETTINGS_FILE", APP_DIR / "config" / "settings.yaml"))
ENV_FILE = Path(os.getenv("DOCUMIND_ENV_FILE", REPO_ROOT / ".env"))


class GatewaySettings(BaseModel):
    """Where the AI gateway lives and how patiently we wait for it."""

    base_url: str
    timeout_seconds: float = Field(gt=0)
    client_max_retries: int = Field(ge=0)


class ModelSettings(BaseModel):
    """Which gateway model alias each feature uses."""

    summarize: str


class GenerationSettings(BaseModel):
    """Limits on what the model may generate."""

    max_output_tokens: int = Field(gt=0)


class DocumentSettings(BaseModel):
    """Guardrails for the documents we accept."""

    allowed_extensions: list[str]
    max_chars: int = Field(gt=0)
    encoding: str


class PromptSettings(BaseModel):
    """Where prompt templates are stored (relative to the app folder)."""

    directory: Path

    @property
    def path(self) -> Path:
        """Absolute path to the prompt folder."""
        return self.directory if self.directory.is_absolute() else APP_DIR / self.directory


class LoggingSettings(BaseModel):
    """Log level and line format."""

    level: str
    format: str


class Settings(BaseSettings):
    """All DocuMind settings in one validated object."""

    model_config = SettingsConfigDict(
        env_prefix="DOCUMIND_",
        env_nested_delimiter="__",
        env_file=ENV_FILE,
        extra="ignore",  # ignore unrelated .env entries, including the vendor keys
        yaml_file=SETTINGS_FILE,
    )

    runtime: Literal["local", "colab"]
    gateway: GatewaySettings
    models: ModelSettings
    generation: GenerationSettings
    documents: DocumentSettings
    prompts: PromptSettings
    logging: LoggingSettings

    # The gateway-issued *virtual* key (env: DOCUMIND_API_KEY). SecretStr hides it in logs.
    api_key: SecretStr | None = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set the precedence order: init args > env vars > .env > YAML."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process and reuse them."""
    return Settings()  # type: ignore[call-arg]  # values come from the sources above
