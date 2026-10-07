"""
AURORA Runtime Engine — KR-003 Logging Runtime
Module: KR-003
File: src/core/logger.py

Canonical Logger Factory.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

import logging
from functools import cache
from logging import Handler, Logger, StreamHandler
from typing import Final

from src.core.exceptions import InvalidConfigurationError
from src.core.logging_config import (
    DEFAULT_CONTEXT_FILTER,
    ConsoleFormatter,
    JsonFormatter,
    LoggingConfig,
)

# ============================================================================
# Internal Helpers
# ============================================================================


def _build_handler(config: LoggingConfig) -> Handler:
    """
    Create a configured stream handler.
    """
    handler = StreamHandler()

    if config.json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())

    handler.addFilter(DEFAULT_CONTEXT_FILTER)
    return handler


def _configure_logger(name: str, config: LoggingConfig) -> Logger:
    """
    Configure a logger instance without touching the root logger.
    """
    logger = logging.getLogger(name)

    logger.setLevel(config.level.upper())
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(_build_handler(config))

    return logger


# ============================================================================
# Logger Factory
# ============================================================================


@cache
def get_logger(
    name: str,
    config: LoggingConfig | None = None,
) -> Logger:
    """
    Return a configured logger for the requested namespace.

    Logger instances are cached for the lifetime of the application.
    """
    if not name:
        raise InvalidConfigurationError("Logger name must not be empty.")

    if name == "root":
        raise InvalidConfigurationError("Root logger namespace is not allowed.")

    if config is None:
        config = LoggingConfig()

    if config.level.upper() not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise InvalidConfigurationError("Invalid log level.")

    return _configure_logger(name, config)


# ============================================================================
# Default Runtime Logger
# ============================================================================

LOGGER: Final[Logger] = get_logger(LoggingConfig().logger_name)
