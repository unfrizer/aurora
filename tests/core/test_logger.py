from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import copy_context
from dataclasses import FrozenInstanceError, fields
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

import pytest

from src.core.constants import DEFAULT_LOG_LEVEL, LOGGER_NAME
from src.core.exceptions import InvalidConfigurationError
from src.core.logger import LOGGER, get_logger
from src.core.logging_config import (
    DEFAULT_CONTEXT_FILTER,
    DEFAULT_LOGGING_CONFIG,
    ConsoleFormatter,
    JsonFormatter,
    LoggingConfig,
    RuntimeContextFilter,
    clear_correlation_id,
    clear_logging_context,
    clear_session_id,
    get_correlation_id,
    get_session_id,
    set_correlation_id,
    set_session_id,
)


@contextmanager
def _logger_namespace(prefix: str = "aurora.tests.kr003") -> Generator[logging.Logger]:
    logger = logging.getLogger(f"{prefix}.{uuid4()}")
    previous_level, previous_propagate = logger.level, logger.propagate
    try:
        yield logger
    finally:
        for handler in tuple(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


@contextmanager
def _logging_context() -> Generator[None]:
    previous_correlation, previous_session = get_correlation_id(), get_session_id()
    clear_logging_context()
    try:
        yield
    finally:
        set_correlation_id(previous_correlation)
        set_session_id(previous_session)


def _record() -> logging.LogRecord:
    record = logging.LogRecord(
        "aurora.tests.record", logging.INFO, __file__, 1, "Привет %s", ("мир",), None
    )
    record.created = 0.0
    return record


def _decode(encoded: str) -> dict[str, object]:
    return cast(dict[str, object], json.loads(encoded))


def _root_snapshot() -> tuple[int, bool, bool, tuple[logging.Handler, ...], tuple[object, ...]]:
    root = logging.getLogger()
    return root.level, root.propagate, root.disabled, tuple(root.handlers), tuple(root.filters)


@pytest.mark.parametrize("name", ["", "root"])
@pytest.mark.parametrize("config", [None, LoggingConfig(level="synthetic-invalid")])
def test_root_aliases_rejected_before_registry_access(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    config: LoggingConfig | None,
) -> None:
    before = _root_snapshot()

    def forbidden_acquisition(name: str | None = None) -> logging.Logger:
        raise AssertionError("Rejected input must not reach the logger registry.")

    with monkeypatch.context() as admission_guard:
        admission_guard.setattr(logging, "getLogger", forbidden_acquisition)
        with pytest.raises(InvalidConfigurationError) as failure:
            get_logger(name, config)
    expected = (
        "Logger name must not be empty." if name == "" else "Root logger namespace is not allowed."
    )
    assert str(failure.value) == expected
    assert failure.value.context == {}
    assert _root_snapshot() == before


@pytest.mark.parametrize(
    "level", ["", "NOTSET", "WARN", "FATAL", "synthetic-secret", " INFO", "INFO "]
)
def test_invalid_level_rejected_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
    level: str,
) -> None:
    before = _root_snapshot()
    with _logger_namespace() as existing:
        existing.setLevel(logging.ERROR)
        existing.propagate = True
        handler = logging.NullHandler()
        existing.addHandler(handler)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        snapshot = existing.level, existing.propagate, tuple(existing.handlers)

        def forbidden_acquisition(name: str | None = None) -> logging.Logger:
            raise AssertionError("Rejected input must not reach the logger registry.")

        with monkeypatch.context() as admission_guard:
            admission_guard.setattr(logging, "getLogger", forbidden_acquisition)
            with pytest.raises(InvalidConfigurationError) as failure:
                get_logger(existing.name, LoggingConfig(level=level))
        assert str(failure.value) == "Invalid log level."
        assert failure.value.context == {}
        assert (existing.level, existing.propagate, tuple(existing.handlers)) == snapshot
        assert handler.formatter is formatter
    assert _root_snapshot() == before


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
@pytest.mark.parametrize("case", ["upper", "lower", "mixed"])
def test_supported_levels_preserve_name_and_root(level: str, case: str) -> None:
    configured_level = (
        level if case == "upper" else level.lower() if case == "lower" else level.title()
    )
    before = _root_snapshot()
    with _logger_namespace(" Root ") as existing:
        config = LoggingConfig(logger_name="not-the-requested-name", level=configured_level)
        logger = get_logger(existing.name, config)
        assert logger is existing
        assert logger is get_logger(existing.name, config)
        assert logger.name == existing.name
        assert logger.level == getattr(logging, level)
        assert logger.propagate is False
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[0].formatter, ConsoleFormatter)
        assert logger.handlers[0].filters == [DEFAULT_CONTEXT_FILTER]
    assert _root_snapshot() == before


def test_default_factory_cache_and_constants() -> None:
    assert LoggingConfig() == DEFAULT_LOGGING_CONFIG
    assert DEFAULT_LOGGING_CONFIG.logger_name == LOGGER_NAME
    assert DEFAULT_LOGGING_CONFIG.level == DEFAULT_LOG_LEVEL
    assert isinstance(DEFAULT_CONTEXT_FILTER, RuntimeContextFilter)
    assert LOGGER is get_logger(LOGGER_NAME)
    assert LOGGER.name == LOGGER_NAME
    with _logger_namespace() as existing:
        before = get_logger.cache_info()
        logger = get_logger(existing.name)
        after_miss = get_logger.cache_info()
        assert after_miss.misses == before.misses + 1
        assert get_logger(existing.name) is logger
        assert get_logger.cache_info().hits == after_miss.hits + 1
        assert logger.level == logging.INFO
        assert isinstance(logger.handlers[0].formatter, ConsoleFormatter)


@pytest.mark.parametrize("json_logs", [False, True])
def test_installed_handler_format_and_context(
    capsys: pytest.CaptureFixture[str],
    json_logs: bool,
) -> None:
    with _logging_context(), _logger_namespace() as existing:
        set_correlation_id("correlation-1")
        set_session_id("session-1")
        logger = get_logger(existing.name, LoggingConfig(json_logs=json_logs))
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, JsonFormatter if json_logs else ConsoleFormatter)
        logger.info("Привет %s", "мир")
        output = capsys.readouterr().err
        if json_logs:
            payload = _decode(output)
            assert payload["logger"] == existing.name
            assert payload["level"] == "INFO"
            assert payload["message"] == "Привет мир"
            assert payload["correlation_id"] == "correlation-1"
            assert payload["session_id"] == "session-1"
        else:
            assert (
                f"| INFO     | {existing.name} | cid=correlation-1 | sid=session-1 | Привет мир"
                in output
            )


def test_cache_miss_does_not_replace_first_installed_handler() -> None:
    with _logger_namespace() as existing:
        logger = get_logger(existing.name, LoggingConfig(level="INFO", json_logs=False))
        handler = logger.handlers[0]
        formatter = handler.formatter
        assert get_logger(existing.name, LoggingConfig(level="DEBUG", json_logs=True)) is logger
        assert logger.level == logging.DEBUG
        assert logger.handlers == [handler]
        assert handler.formatter is formatter
        assert isinstance(formatter, ConsoleFormatter)
        # The old cache entry is a hit, not a live reconfiguration request.
        assert get_logger(existing.name, LoggingConfig(level="INFO", json_logs=False)) is logger
        assert logger.level == logging.DEBUG


def test_existing_stdlib_handler_is_preserved() -> None:
    with _logger_namespace() as existing:
        handler = logging.NullHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        existing.addHandler(handler)
        logger = get_logger(existing.name, LoggingConfig(level="warning", json_logs=True))
        assert logger is existing
        assert logger.level == logging.WARNING
        assert logger.handlers == [handler]
        assert handler.formatter is formatter
        assert handler.filters == []


def test_logging_config_frozen_slotted_positional_compatibility() -> None:
    config = LoggingConfig("custom", "debug", True)
    assert config == LoggingConfig(logger_name="custom", level="debug", json_logs=True)
    assert tuple(field.name for field in fields(LoggingConfig)) == (
        "logger_name",
        "level",
        "json_logs",
    )
    assert hash(config) == hash(LoggingConfig("custom", "debug", True))
    assert not hasattr(config, "__dict__")
    with pytest.raises(FrozenInstanceError):
        field_name = fields(LoggingConfig)[1].name
        setattr(config, field_name, "ERROR")


def test_console_formatter_exact_utc_schema_with_and_without_context() -> None:
    record = _record()
    assert ConsoleFormatter.default_time_format == "%Y-%m-%d %H:%M:%S"
    assert ConsoleFormatter().format(record) == (
        "1970-01-01 00:00:00 | INFO     | aurora.tests.record | cid=- | sid=- | Привет мир"
    )
    record.correlation_id = "cid"
    record.session_id = "sid"
    assert ConsoleFormatter().format(record) == (
        "1970-01-01 00:00:00 | INFO     | aurora.tests.record | cid=cid | sid=sid | Привет мир"
    )


def test_json_formatter_exact_unfiltered_schema() -> None:
    encoded = JsonFormatter().format(_record())
    assert "Привет мир" in encoded
    payload = _decode(encoded)
    assert tuple(payload) == (
        "timestamp",
        "logger",
        "level",
        "message",
        "correlation_id",
        "session_id",
    )
    assert payload == {
        "timestamp": datetime.fromtimestamp(0, UTC).isoformat(),
        "logger": "aurora.tests.record",
        "level": "INFO",
        "message": "Привет мир",
        "correlation_id": None,
        "session_id": None,
    }


def test_json_formatter_exception_branch() -> None:
    error = ValueError("synthetic failure")
    record = _record()
    record.exc_info = (ValueError, error, None)
    payload = _decode(JsonFormatter().format(record))
    assert tuple(payload)[-1] == "exception"
    assert payload["exception"] == "ValueError: synthetic failure"


@pytest.mark.parametrize("correlation,session", [(None, None), ("", ""), ("cid", "sid")])
def test_context_filter_json_fallback_and_no_automatic_trace(
    correlation: str | None,
    session: str | None,
) -> None:
    with _logging_context():
        set_correlation_id(correlation)
        set_session_id(session)
        record = _record()
        assert RuntimeContextFilter().filter(record) is True
        payload = _decode(JsonFormatter().format(record))
        assert payload["correlation_id"] == (correlation or "-")
        assert payload["session_id"] == (session or "-")
        assert not hasattr(record, "trace_id")
        assert not hasattr(record, "pipeline_id")
        assert not hasattr(record, "runtime")


def test_context_set_get_clear_and_copy_isolation() -> None:
    with _logging_context():
        assert get_correlation_id() is None
        assert get_session_id() is None
        set_correlation_id("parent")
        set_session_id("session")
        child = copy_context()
        child.run(set_correlation_id, "child")
        child.run(clear_session_id)
        assert child.run(get_correlation_id) == "child"
        assert child.run(get_session_id) is None
        assert get_correlation_id() == "parent"
        assert get_session_id() == "session"
        clear_correlation_id()
        assert get_correlation_id() is None
        assert get_session_id() == "session"
        clear_logging_context()
        assert get_session_id() is None
        set_correlation_id(None)
        set_session_id(None)
        assert get_correlation_id() is None
        assert get_session_id() is None


@pytest.mark.asyncio
async def test_context_isolation_between_awaited_tasks() -> None:
    with _logging_context():
        set_correlation_id("parent")
        set_session_id("parent-session")

        async def observe(label: str) -> tuple[str | None, str | None]:
            set_correlation_id(label)
            set_session_id(label + "-session")
            await asyncio.sleep(0)
            return get_correlation_id(), get_session_id()

        results = await asyncio.gather(observe("first"), observe("second"))
        assert results == [("first", "first-session"), ("second", "second-session")]
        assert get_correlation_id() == "parent"
        assert get_session_id() == "parent-session"
