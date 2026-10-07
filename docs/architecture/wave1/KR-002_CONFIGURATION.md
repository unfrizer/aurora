# KR-002 — Configuration Runtime Contract v1.0

**Status:** APPROVED — ADR-009 T-02/T-04/T-05, 2026-10-06
**Layer / owner:** L0 Kernel / KR-002
**Authority:** Architecture Freeze v1.0, AB-00A and explicit ADR-009 approval.

## Scope and dependencies

Production ownership is exactly src/core/settings.py and src/core/config.py.
This reconciliation changes documentation only; KR-002 source remains frozen.
Settings owns environment/.env parsing and validation; config owns the immutable
Application-wide loader cache. Foundation imports only, plus existing Pydantic
and pydantic-settings dependencies. No logging, contracts, DI or higher-runtime
import, filesystem creation, secret/provider fields or new dependencies.

## Exact public model

`Environment = Literal["development", "testing", "production"]`.

Settings remains Pydantic BaseSettings, not a dataclass. Its model_config is
frozen=True, extra="ignore", case_sensitive=False, env_file=".env",
env_file_encoding="utf-8". Existing environment > .env > default precedence
and Pydantic construction compatibility remain unchanged.

| Field | Type | Default | Explicit alias |
| --- | --- | --- | --- |
| app_name | str | PROJECT_NAME | none |
| environment | Environment | development | AURORA_ENV |
| log_level | str | DEFAULT_LOG_LEVEL (INFO) | AURORA_LOG_LEVEL |
| timezone | str | DEFAULT_TIMEZONE (UTC) | none |
| config_path | Path | Path("config") | AURORA_CONFIG_PATH |
| data_path | Path | Path("data") | none |
| cache_path | Path | Path(".cache") | none |
| logs_path | Path | Path("logs") | none |

Exactly three read-only properties: is_development, is_testing, is_production,
each returning bool. Existing public class validators are
validate_log_level(cls, value: str) -> str and
validate_path(cls, value: str | Path) -> Path. Log levels normalize by upper()
and accept only DEBUG/INFO/WARNING/ERROR/CRITICAL. All four paths convert to Path;
relative/nonexistent paths are valid and no directory is created. Timezone is a
descriptive string; no timezone-database validation is promised. All fields have
defaults: missing/empty .env and unknown extra keys are accepted.

## Exact loader API and lifetime

`get_settings() -> Settings` uses lru_cache(maxsize=1).
`validate_configuration() -> Settings` delegates to get_settings and returns
the same cached validated immutable instance. No AURORA reload_settings,
clear_settings_cache or validate_settings API exists. Tests may use the existing
decorator's standard-library cache_clear for isolated setup/teardown; this is not
a production reload contract or DI ownership transfer.

Direct invalid environment construction raises pydantic.ValidationError.
get_settings wraps that ValidationError in existing InvalidConfigurationError,
preserving its cause and existing errors context. Invalid log_level raises
InvalidConfigurationError from the existing validator. No mandatory missing-env,
absolute/existing-directory, provider-key or new exception policy is introduced.

## Acceptance and superseded obligations

Canonical acceptance: tests/core/test_settings.py, owned by KR-011.
Exercise all fields, alias/default/.env/environment precedence, case-insensitive
loading, ignored extras, all helpers/validators, invalid environment/level,
Path conversion without I/O, actual rejected frozen assignment, cache identity,
test-isolated invalidation and exact error/cause boundaries. Require 100%
executable-line coverage of both source files plus all public API assertions;
line/API/branch evidence must be distinguished.

Only contradictory KR-002 legacy Master schemas, dataclass classification,
reload functions, required-field/path/timezone/provider policies and tests are
superseded. Ownership and unrelated modules remain unchanged. Source matching
this contract is not proof that the missing KR-011 acceptance is complete.
