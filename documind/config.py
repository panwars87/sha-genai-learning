"""Typed settings for DocuMind, loaded from YAML and overridden by the environment.

Concept taught: **configuration lives outside code, and secrets live outside config.**
Everything that can change is in ``documind/settings.yaml``. Environment variables
(``DOCUMIND_<SECTION>__<KEY>``) override it. API keys are loaded from the repo's ``.env`` into
the environment for LiteLLM to read; they are never fields here, so the app cannot print them.

Added in Module 0. Each module adds the settings its feature needs.
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

PACKAGE_DIR = Path(__file__).resolve().parent  # documind/
REPO_ROOT = PACKAGE_DIR.parent  # the course repo
DATA_DIR = REPO_ROOT / "data"
SETTINGS_FILE = Path(os.getenv("DOCUMIND_SETTINGS_FILE", PACKAGE_DIR / "settings.yaml"))
ENV_FILE = Path(os.getenv("DOCUMIND_ENV_FILE", REPO_ROOT / ".env"))


class GatewaySettings(BaseModel):
    """How model names map to real models, and the gateway's safety limits."""

    aliases: dict[str, str]  # alias → vendor model ID
    shortcuts: dict[str, str]  # short name → alias, e.g. fast → fast-anthropic
    default_alias: str
    fallbacks: dict[str, list[str]] = {}  # alias → aliases to try if it fails (Module 2)
    num_retries: int = Field(ge=0)
    timeout_seconds: float = Field(gt=0)
    max_output_tokens: int = Field(gt=0)
    max_spend_usd: float = Field(gt=0)
    mock_response: str | None = None

    def known_aliases(self) -> list[str]:
        """Every name the app may ask for: aliases plus shortcuts."""
        return [*self.aliases, *self.shortcuts]

    def model_for(self, name: str) -> str:
        """The real vendor model behind an alias or shortcut."""
        return self.aliases[self.shortcuts.get(name, name)]


class FeatureSettings(BaseModel):
    """Which alias each feature uses."""

    summarize_alias: str
    classify_alias: str
    extract_alias: str


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
        return (
            self.prompts_dir if self.prompts_dir.is_absolute() else PACKAGE_DIR / self.prompts_dir
        )

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
    # Libraries log every request (and every fallback attempt) loudly; our own gateway logs
    # one clear line per call instead.
    for noisy in ("LiteLLM", "LiteLLM Router", "LiteLLM Proxy", "litellm", "httpx"):
        logging.getLogger(noisy).setLevel(logging.CRITICAL)
    return settings
