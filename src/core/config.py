"""
AURORA Runtime Engine — KR-002 Configuration Runtime
File: src/core/config.py

Immutable runtime configuration loader.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import ValidationError

from src.core.exceptions import InvalidConfigurationError
from src.core.settings import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Create and return the immutable Application-scope Settings instance.

    The instance is created exactly once and cached for the lifetime of the
    application process. Configuration validation is performed during
    Settings initialization.
    """
    try:
        return Settings()
    except ValidationError as exc:
        raise InvalidConfigurationError(
            "Runtime configuration validation failed.",
            errors=exc.errors(),
        ) from exc


def validate_configuration() -> Settings:
    """
    Validate configuration before Kernel Runtime startup.

    This function is intended to be called by the bootstrap sequence before
    any runtime modules are initialized.
    """
    return get_settings()
