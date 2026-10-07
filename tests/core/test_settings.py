from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast, get_args

import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from src.core.config import get_settings, validate_configuration
from src.core.exceptions import InvalidConfigurationError
from src.core.settings import Environment, Settings


def _from_input(values: dict[str, object]) -> Settings:
    # External Pydantic input intentionally includes aliases and invalid values.
    constructor = cast(Callable[..., Settings], Settings)
    return constructor(**values)


def test_settings_are_immutable_and_cached(settings: Settings) -> None:
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert isinstance(first, Settings)
    assert first is second
    assert first.log_level == "INFO"
    assert settings == first
    with pytest.raises(ValidationError, match="frozen"):
        first.log_level = "DEBUG"
    assert first.log_level == "INFO"


def test_exact_model_schema_and_defaults(settings: Settings) -> None:
    assert isinstance(settings, BaseSettings)
    assert get_args(Environment.__value__) == ("development", "testing", "production")
    assert tuple(Settings.model_fields) == (
        "app_name",
        "environment",
        "log_level",
        "timezone",
        "config_path",
        "data_path",
        "cache_path",
        "logs_path",
    )
    assert settings.model_dump() == {
        "app_name": "AURORA",
        "environment": "development",
        "log_level": "INFO",
        "timezone": "UTC",
        "config_path": Path("config"),
        "data_path": Path("data"),
        "cache_path": Path(".cache"),
        "logs_path": Path("logs"),
    }
    assert tuple(Settings.model_fields[name].alias for name in Settings.model_fields) == (
        None,
        "AURORA_ENV",
        "AURORA_LOG_LEVEL",
        None,
        "AURORA_CONFIG_PATH",
        None,
        None,
        None,
    )
    assert all(not field.is_required() for field in Settings.model_fields.values())
    assert Settings.model_config.get("frozen") is True
    assert Settings.model_config.get("extra") == "ignore"
    assert Settings.model_config.get("case_sensitive") is False
    assert Settings.model_config.get("env_file") == ".env"
    assert Settings.model_config.get("env_file_encoding") == "utf-8"


@pytest.mark.parametrize("empty_env", [False, True])
def test_missing_or_empty_dotenv_is_valid(
    settings: Settings,
    tmp_path: Path,
    empty_env: bool,
) -> None:
    if empty_env:
        (tmp_path / ".env").write_text("", encoding="utf-8")
    assert Settings() == settings
    assert validate_configuration() == settings
    assert tuple(tmp_path.iterdir()) == ((tmp_path / ".env",) if empty_env else ())


def test_all_fields_load_from_case_insensitive_environment(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    values = {
        "aPp_NaMe": "Пример",
        "aUrOrA_EnV": "testing",
        "AuRoRa_LoG_LeVeL": "debug",
        "tImEzOnE": "descriptive/nonexistent",
        "AuRoRa_CoNfIg_PaTh": "relative/config",
        "DaTa_PaTh": "relative/data",
        "CaChE_PaTh": "relative/cache",
        "LoGs_PaTh": "relative/logs",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    loaded = Settings()
    assert loaded.app_name == "Пример" and loaded.environment == "testing"
    assert loaded.log_level == "DEBUG" and loaded.timezone == "descriptive/nonexistent"
    assert (loaded.config_path, loaded.data_path, loaded.cache_path, loaded.logs_path) == (
        Path("relative/config"),
        Path("relative/data"),
        Path("relative/cache"),
        Path("relative/logs"),
    )
    assert settings.environment == "development"
    assert not tuple(tmp_path.iterdir())


def test_utf8_dotenv_all_fields_unknown_extras_and_environment_precedence(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / ".env").write_text(
        "aPp_NaMe=Бренд\naUrOrA_EnV=testing\naUrOrA_LoG_LeVeL=warning\n"
        "TiMeZoNe=descriptive\naUrOrA_CoNfIg_PaTh=relative/config\n"
        "DaTa_PaTh=relative/data\nCaChE_PaTh=relative/cache\nLoGs_PaTh=relative/logs\n"
        "UNRELATED_EXTRA=ignored\n",
        encoding="utf-8",
    )
    dotenv = Settings()
    assert dotenv.model_dump() == {
        "app_name": "Бренд",
        "environment": "testing",
        "log_level": "WARNING",
        "timezone": "descriptive",
        "config_path": Path("relative/config"),
        "data_path": Path("relative/data"),
        "cache_path": Path("relative/cache"),
        "logs_path": Path("relative/logs"),
    }
    monkeypatch.setenv("AURORA_ENV", "production")
    monkeypatch.setenv("AURORA_LOG_LEVEL", "critical")
    monkeypatch.setenv("AURORA_CONFIG_PATH", "environment/config")
    overridden = Settings()
    assert overridden.environment == "production" and overridden.log_level == "CRITICAL"
    assert overridden.config_path == Path("environment/config")
    assert overridden.app_name == "Бренд"
    assert settings.app_name == "AURORA"
    assert not hasattr(overridden, "unrelated_extra")


def test_initializer_aliases_override_environment_and_unknown_extras_are_ignored(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AURORA_ENV", "production")
    loaded = _from_input(
        {
            "AURORA_ENV": "testing",
            "AURORA_LOG_LEVEL": "error",
            "AURORA_CONFIG_PATH": "custom",
            "app_name": "synthetic",
            "timezone": "arbitrary",
            "unused_extra": "ignored",
        }
    )
    assert loaded.environment == "testing" and loaded.log_level == "ERROR"
    assert loaded.config_path == Path("custom") and loaded.app_name == "synthetic"
    assert loaded.timezone == "arbitrary" and not hasattr(loaded, "unused_extra")
    assert settings.environment == "development"


@pytest.mark.parametrize("environment", ["development", "testing", "production"])
def test_every_environment_helper(settings: Settings, environment: str) -> None:
    loaded = _from_input({"AURORA_ENV": environment})
    assert loaded.is_development is (environment == "development")
    assert loaded.is_testing is (environment == "testing")
    assert loaded.is_production is (environment == "production")
    assert settings.is_development


@pytest.mark.parametrize("level", ["debug", "Info", "warning", "ERROR", "critical"])
def test_log_level_validator_and_model_normalize_supported_levels(
    settings: Settings,
    level: str,
) -> None:
    assert Settings.validate_log_level(level) == level.upper()
    assert _from_input({"AURORA_LOG_LEVEL": level}).log_level == level.upper()
    assert settings.log_level == "INFO"


@pytest.mark.parametrize("level", ["", "WARN", "FATAL", "NOTSET", "verbose", " INFO "])
def test_invalid_level_preserves_existing_validator_boundary(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
    level: str,
) -> None:
    with pytest.raises(InvalidConfigurationError, match="Invalid log level") as direct:
        Settings.validate_log_level(level)
    assert direct.value.context == {"log_level": level}
    with pytest.raises(InvalidConfigurationError):
        _from_input({"AURORA_LOG_LEVEL": level})
    monkeypatch.setenv("AURORA_LOG_LEVEL", level)
    with pytest.raises(InvalidConfigurationError) as loaded:
        get_settings()
    assert loaded.value.message == "Invalid log level."
    assert loaded.value.__cause__ is None
    assert settings.log_level == "INFO"


@pytest.mark.parametrize("path", ["relative/new", Path("relative/new")])
def test_path_validator_converts_without_creating_directories(
    settings: Settings,
    tmp_path: Path,
    path: str | Path,
) -> None:
    assert Settings.validate_path(path) == Path("relative/new")
    loaded = _from_input(
        {
            "AURORA_CONFIG_PATH": path,
            "data_path": path,
            "cache_path": path,
            "logs_path": path,
        }
    )
    assert all(
        value == Path("relative/new")
        for value in (
            loaded.config_path,
            loaded.data_path,
            loaded.cache_path,
            loaded.logs_path,
        )
    )
    assert settings.config_path == Path("config")
    assert not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("field", list(Settings.model_fields))
def test_actual_assignment_to_every_field_is_rejected(settings: Settings, field: str) -> None:
    before = settings.model_dump()
    with pytest.raises(ValidationError) as rejected:
        setattr(settings, field, before[field])
    assert rejected.value.errors()[0]["type"] == "frozen_instance"
    assert settings.model_dump() == before


@pytest.mark.parametrize("environment", ["", "invalid", "Testing", " production "])
def test_invalid_environment_direct_and_loader_error_causes(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
) -> None:
    with pytest.raises(ValidationError) as direct:
        _from_input({"AURORA_ENV": environment})
    assert direct.value.errors()[0]["type"] == "literal_error"
    monkeypatch.setenv("AURORA_ENV", environment)
    with pytest.raises(InvalidConfigurationError) as loaded:
        validate_configuration()
    cause = loaded.value.__cause__
    assert isinstance(cause, ValidationError)
    assert cause.errors() == direct.value.errors()
    assert loaded.value.message == "Runtime configuration validation failed."
    assert loaded.value.context == {"errors": cause.errors()}
    assert get_settings.cache_info().currsize == 0
    monkeypatch.setenv("AURORA_ENV", "development")
    assert get_settings() == settings


def test_cached_loader_validation_identity_and_test_only_invalidation(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = get_settings()
    assert first == settings and get_settings.cache_parameters() == {"maxsize": 1, "typed": False}
    assert validate_configuration() is first
    monkeypatch.setenv("AURORA_ENV", "production")
    assert get_settings() is first and first.environment == "development"
    get_settings.cache_clear()
    second = validate_configuration()
    assert second is not first and second.environment == "production"
    assert get_settings() is second
