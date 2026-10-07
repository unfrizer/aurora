# KR-003 — Logging Runtime Contract v1.0

**Status:** APPROVED — ADR-009 T-03/T-04/T-05, 2026-10-06
**Layer / owner:** L0 Kernel / KR-003
**Authority:** Architecture Freeze v1.0, AB-00A and explicit ADR-009 approval.

## Ownership and active narrow repair

KR-003 owns src/core/logging_config.py and src/core/logger.py.
This task may modify ONLY src/core/logger.py and tests/core/test_logger.py.
The test owner remains KR-011; ADR-009 explicitly permits active KR-003 acceptance
adjustments. logging_config.py and all other source/test files remain frozen.

logger.py imports Foundation's existing InvalidConfigurationError and sibling
logging_config primitives; logging_config.py imports Foundation constants only.
Standard-library logging/cache/ContextVar/UTC/dataclass infrastructure is permitted.
No Configuration import is required by the current implementation. No reverse,
contract/ContextRuntime/SessionRuntime/higher-layer import, DI, lifecycle owner,
root configurator, new dependency or second logging subsystem.

## Exact public surface

| Owner file | Public symbol |
| --- | --- |
| logger.py | get_logger(name: str, config: LoggingConfig \| None = None) -> logging.Logger |
| logger.py | LOGGER: Final[logging.Logger] |
| logging_config.py | LoggingConfig |
| logging_config.py | RuntimeContextFilter.filter(record: logging.LogRecord) -> bool |
| logging_config.py | ConsoleFormatter.format(record: logging.LogRecord) -> str |
| logging_config.py | JsonFormatter.format(record: logging.LogRecord) -> str |
| logging_config.py | set_correlation_id(correlation_id: str \| None) -> None |
| logging_config.py | get_correlation_id() -> str \| None |
| logging_config.py | clear_correlation_id() -> None |
| logging_config.py | set_session_id(session_id: str \| None) -> None |
| logging_config.py | get_session_id() -> str \| None |
| logging_config.py | clear_session_id() -> None |
| logging_config.py | clear_logging_context() -> None |
| logging_config.py | DEFAULT_LOGGING_CONFIG: Final[LoggingConfig] |
| logging_config.py | DEFAULT_CONTEXT_FILTER: Final[RuntimeContextFilter] |

Fifteen module-level symbols: eight functions, four classes and three constants.
Class methods/properties are additionally verified as public API. Imported stdlib
types are not newly owned AURORA exports. Foundation constants retain KR-001
ownership; imported defaults are not KR-003-owned duplicates.

LoggingConfig remains frozen=True, slots=True, NOT keyword-only; existing positional
and keyword construction stays compatible. Exactly three fields, in order:
logger_name: str = LOGGER_NAME, level: str = DEFAULT_LOG_LEVEL,
json_logs: bool = False. No constructor validation or additional fields are added.
The factory's name argument chooses the namespace; config.logger_name is not a
replacement namespace. DEFAULT_LOGGING_CONFIG is LoggingConfig(); LOGGER uses
LoggingConfig().logger_name. No configure_logging, reset_logging, ContextFilter
alias, build_logging_config, trace/pipeline/runtime fields or live-reload API.

## Factory guards, cache and handlers

Before ANY logging.getLogger call or logger mutation:
reject name == "" with existing InvalidConfigurationError and fixed safe message;
reject EXACT name == "root" with InvalidConfigurationError before registry access,
using a fixed safe message (explicit Authority clarification, 2026-10-07);
reject unsupported config.level with that same exception and fixed safe message.
Do not include arbitrary invalid input in error context or logs.
Supported levels are exactly DEBUG/INFO/WARNING/ERROR/CRITICAL, normalized with
upper() as before. NOTSET/WARN/FATAL/custom levels are not additions to vocabulary.
Do not trim, rename or reject otherwise valid named namespaces.

Preserve @cache and its existing argument-key semantics. A cache hit returns the
cached object; standard-library logging owns namespace identity. A cache miss
sets the normalized level and propagate=False. Install one StreamHandler with
DEFAULT_CONTEXT_FILTER only when that namespace has no handlers; choose JSON
when json_logs=True, otherwise Console. Existing handlers/formatters are never
replaced by a later config. No root mutation, basicConfig or global reset.
Tests must not claim a live-reconfiguration API from cache-miss behavior.

## Context and formatting

ContextVar stores explicitly supplied correlation_id and session_id per execution
context. Set/get/clear functions preserve existing semantics; clear_logging_context
clears both. RuntimeContextFilter writes both fields using "-" for missing/empty
IDs and returns True. It does not infer TraceId, generate IDs or consult runtime.

Console emits UTC "%Y-%m-%d %H:%M:%S", padded level, namespace, cid/sid and message,
separated by " | "; missing record attributes use "-". No color/redaction promise.
JSON emits in order timestamp (UTC ISO), logger, level, message, correlation_id,
session_id, and optional exception when exc_info is supplied. Unfiltered missing
IDs are None; filtered records use "-". Preserve Unicode (ensure_ascii=False)
and standard-library exception formatting. No additional serialization schema.

## Acceptance

Canonical file: tests/core/test_logger.py. All public symbols and class methods,
frozen/slotted schema and constructor compatibility, named/default acquisition,
all supported levels/case normalization, cache/stdlib identity, root
non-interference, zero registry calls on rejected admission, unchanged existing
named logger on bad level, fixed messages without input disclosure, handler
creation/filter/first-installed behavior, both exact formatter schemas,
exception branch, missing IDs, set/get/clear and execution-context isolation.
Require 100% executable-line coverage of both owned files plus public API
assertions; do not claim branch coverage from lines. No skips/xfail/exclusions.
Full Ruff, scoped format, strict Windows/Linux Pyright, full discovered Pytest,
bounded Kernel smoke and latest-head required CI must pass.

## Supersession / stop gate

Only incompatible KR-003 legacy Master APIs, root configuration/reset policies,
formatter/context/schema/import and acceptance statements are superseded.
L0–L8, lower ownership, all vocabulary and approved KR-004–010 remain unchanged.
After this narrow repair: one report and STOP for review before KR-011.
