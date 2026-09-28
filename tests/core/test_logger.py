from __future__ import annotations

import json
import logging

from src.core.logger import get_logger
from src.core.logging_config import JsonFormatter, clear_logging_context, set_correlation_id


def test_logger_is_cached_and_json_formatter_includes_context() -> None:
    logger = get_logger("aurora.tests")
    assert logger is get_logger("aurora.tests")
    set_correlation_id("trace-1")
    record = logging.LogRecord("aurora.tests", logging.INFO, __file__, 1, "message", (), None)
    record.correlation_id = "trace-1"
    encoded = JsonFormatter().format(record)
    assert json.loads(encoded)["correlation_id"] == "trace-1"
    clear_logging_context()
