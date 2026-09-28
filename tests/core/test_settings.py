from __future__ import annotations

from src.core.config import get_settings
from src.core.settings import Settings


def test_settings_are_immutable_and_cached() -> None:
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert isinstance(first, Settings)
    assert first is second
    assert first.log_level == "INFO"
