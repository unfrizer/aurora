"""
AURORA Runtime Engine — KR-003 Logging Runtime
Module: KR-003
File: src/core/logging_config.py

Canonical logging configuration.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final

from src.core.constants import DEFAULT_LOG_LEVEL, LOGGER_NAME

# ============================================================================
# Runtime Logging Context
# ============================================================================

_correlation_id: ContextVar[str | None] = ContextVar(
    "aurora_correlation_id",
    default=None,
)

_session_id: ContextVar[str | None] = ContextVar(
    "aurora_session_id",
    default=None,
)


def set_correlation_id(correlation_id: str | None) -> None:
    """Set correlation ID for the current execution context."""
    _correlation_id.set(correlation_id)


def get_correlation_id() -> str | None:
    """Return the current correlation ID."""
    return _correlation_id.get()


def clear_correlation_id() -> None:
    """Clear correlation ID from the current execution context."""
    _correlation_id.set(None)


def set_session_id(session_id: str | None) -> None:
    """Set session ID for the current execution context."""
    _session_id.set(session_id)


def get_session_id() -> str | None:
    """Return the current session ID."""
    return _session_id.get()


def clear_session_id() -> None:
    """Clear session ID from the current execution context."""
    _session_id.set(None)


def clear_logging_context() -> None:
    """Clear all logging context values."""
    clear_correlation_id()
    clear_session_id()


# ============================================================================
# Logging Filter
# ============================================================================


class RuntimeContextFilter(logging.Filter):
    """
    Inject runtime context into every log record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id() or "-"
        record.session_id = get_session_id() or "-"
        return True


# ============================================================================
# Console Formatter
# ============================================================================


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable console formatter.
    """

    default_time_format = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, UTC).strftime(
            self.default_time_format,
        )

        correlation_id = getattr(record, "correlation_id", "-")
        session_id = getattr(record, "session_id", "-")

        return (
            f"{timestamp} | "
            f"{record.levelname:<8} | "
            f"{record.name} | "
            f"cid={correlation_id} | "
            f"sid={session_id} | "
            f"{record.getMessage()}"
        )


# ============================================================================
# JSON Formatter
# ============================================================================


class JsonFormatter(logging.Formatter):
    """
    Structured JSON formatter.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                UTC,
            ).isoformat(),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "session_id": getattr(record, "session_id", None),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


# ============================================================================
# Logging Configuration
# ============================================================================


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """
    Immutable logging configuration.
    """

    logger_name: str = LOGGER_NAME
    level: str = DEFAULT_LOG_LEVEL
    json_logs: bool = False


DEFAULT_LOGGING_CONFIG: Final[LoggingConfig] = LoggingConfig()
DEFAULT_CONTEXT_FILTER: Final[RuntimeContextFilter] = RuntimeContextFilter()
