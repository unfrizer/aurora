"""
AURORA Runtime Engine — KR-002 Configuration Runtime
File: src/core/settings.py

Canonical immutable runtime settings.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_TIMEZONE,
    ENV_APP_ENV,
    ENV_CONFIG_PATH,
    ENV_FILENAME,
    ENV_LOG_LEVEL,
    PROJECT_NAME,
)
from src.core.exceptions import InvalidConfigurationError

type Environment = Literal["development", "testing", "production"]


_ALLOWED_LOG_LEVELS: Final[frozenset[str]] = frozenset(
    {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
)


class Settings(BaseSettings):
    """
    Immutable runtime configuration.

    Configuration is loaded from environment variables and `.env`
    before the Kernel Runtime starts. Validation is performed during
    model initialization.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILENAME,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    # --------------------------------------------------------------------- #
    # Application
    # --------------------------------------------------------------------- #

    app_name: str = PROJECT_NAME

    environment: Environment = Field(
        default="development",
        alias=ENV_APP_ENV,
    )

    # --------------------------------------------------------------------- #
    # Logging
    # --------------------------------------------------------------------- #

    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        alias=ENV_LOG_LEVEL,
    )

    # --------------------------------------------------------------------- #
    # Runtime
    # --------------------------------------------------------------------- #

    timezone: str = DEFAULT_TIMEZONE

    config_path: Path = Field(
        default=Path("config"),
        alias=ENV_CONFIG_PATH,
    )

    data_path: Path = Path("data")
    cache_path: Path = Path(".cache")
    logs_path: Path = Path("logs")

    # --------------------------------------------------------------------- #
    # Validators
    # --------------------------------------------------------------------- #

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        level = value.upper()

        if level not in _ALLOWED_LOG_LEVELS:
            raise InvalidConfigurationError(
                "Invalid log level.",
                log_level=value,
            )

        return level

    @field_validator(
        "config_path",
        "data_path",
        "cache_path",
        "logs_path",
        mode="before",
    )
    @classmethod
    def validate_path(cls, value: str | Path) -> Path:
        return Path(value)

    # --------------------------------------------------------------------- #
    # Environment Helpers
    # --------------------------------------------------------------------- #

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"
