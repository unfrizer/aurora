# AURORA — KR-011 Test Suite Reconciliation Proposal v1.0

**Document ID:** ADR-009
**Status:** APPROVED — EXPLICIT ARCHITECTURE AUTHORITY DECISION
**Date:** 2026-10-06
**Purpose:** Resolve the remaining Foundation/configuration/logging acceptance
conflicts before compiling and implementing KR-011.
**Repository baseline:** `62ab24d7a3e426a220fefb9613256ca40aa7ed54`

## Approval boundary

On 2026-10-06 the Architecture Authority explicitly approved this entire document,
including T-01–T-05, with the following message:

> Утверждаю ADR-009 полностью, включая T-01–T-05.

This supplies the previously missing decisions; it is not automatic approval from
ADR-001 or routine merge permission from ADR-003. T-05 authorizes only the phased
contract compilation, separate narrow KR-003 repair and later KR-011 test task.

No independent human review or first usable Windows product acceptance is claimed.

## Sources and observed state

Inputs: AGENTS.md; M-00; AB-00A, its reconciliation resolution and Build Protocol
Amendment; Wave 1 Implementation Handoff; approved KR-001 reconciliation;
AB-00B/C/D and ADR-004–008; the scoped M-01/M-03/M-06 test and core declarations;
M-07 testing/implementation rules; complete M-09, M-10 test checklist and M-11;
current KR-002/KR-003 source and canonical core tests.

Existing code is evidence, not architecture authority. The proposed explicit
decisions below are needed precisely because the documents do not agree.

| Finding | Evidence | Classification |
| --- | --- | --- |
| KR-011 contract not compiled | `wave1/KR-011_KERNEL_TEST_SUITE.md` says CONTRACT STAGING ONLY | Missing authority |
| Inconsistent test count/paths | M-01 lists 11 executable modules plus conftest; M-06 says ten despite listing those same modules; M-09/M-10 still list additional/obsolete split paths | Mechanical count; contract-location conflict |
| Configuration surfaces conflict | M-03 specifies a large dataclass with provider/version/repository fields and four functions; M-06 specifies BaseSettings with another field set; actual BaseSettings has eight fields and two loader functions | Contract Conflict |
| Missing configuration APIs | `reload_settings`, `clear_settings_cache`, `validate_settings` absent; actual `validate_configuration` exists | Contract Conflict |
| Configuration validation conflicts | Source has defaults, relative Path conversion, extra=ignore and no timezone/existence checks; legacy matrix requires missing-env, directory/timezone errors and M-06 extra=forbid | Contract Conflict |
| Logging surfaces conflict | M-03 puts configure_logging(settings) in logging_config.py and configures root; M-06 puts configure_logging(config) in logger.py and prohibits root; neither function exists | Contract Conflict |
| Logging context/schema conflict | Legacy ContextFilter/trace/pipeline/runtime fields versus actual RuntimeContextFilter/correlation/session fields | Contract Conflict |
| Empty logger name accesses root | Isolated probe: get_logger("") is logging.getLogger(); root level/propagation/handlers change | Local Implementation Defect in frozen KR-003 |
| Acceptance incomplete | Only 4 discovered core tests; settings test does not attempt mutation; conftest.py absent | Missing tests/fixtures |

ADR-008 explicitly preserves existing configuration/logging facades for KR-010.
It does not globally resolve the other modules' public schemas or all their
legacy testing obligations. Passing KR-010 must not be used as such a waiver.

## Frozen invariants

- No ownership or dependency-direction change, L0–L8 extension or new runtime.
- No DI scope, RuntimeStatus, EventPhase or EventPriority change.
- No provider, persistence, network, production background task or new dependency.
- No addition of OpenRouter settings to Foundation; no legacy provider fields
  imported into Kernel solely to satisfy an obsolete test list.
- One module per implementation task/branch/report and Tech Lead review gate.
- KR-004–010 approved behavior and all existing required acceptance remain.
- Existing Waves 2–9/product tests are regression-only in KR-011, not editable.

## T-01 — Canonical test layout and authority

**Decision — APPROVED by explicit Architecture Authority approval.**

Use the named M-01/M-06 paths and approved ADR-004 module test mapping:

```text
tests/conftest.py
tests/core/test_types.py
tests/core/test_settings.py
tests/core/test_logger.py
tests/kernel/test_contracts.py
tests/kernel/test_container.py
tests/kernel/test_lifecycle.py
tests/kernel/test_event_bus.py
tests/kernel/test_context.py
tests/kernel/test_pipeline.py
tests/kernel/test_bootstrap.py
tests/integration/test_runtime_startup.py
```

There are ELEVEN executable test modules and ONE shared-fixture file. This count
is Wave 1-specific, not a restriction on approved later-Wave/product regression.
Registry, Scope, Resolver and Provider acceptance belongs in test_container.py;
Executor acceptance in test_pipeline.py; Kernel/Main integration in the two
existing KR-010 paths. Do not create tests/runtime or duplicate compatibility
test modules. Correct the count and compile matching M-09/M-10 location tables.

Shared function-scoped fixtures in conftest.py are exactly the existing M-01/
M-06 fixture vocabulary: settings, trace_context, runtime_context, container,
event_bus, lifecycle and orchestrator. Fresh objects, dependency wiring and
completed teardown; no business fixture, assertion or test logic in conftest.

## T-02 — Preserve and explicitly canonicalize current KR-002

**Decision — APPROVED; no KR-002 source change authorized.**

Keep immutable Pydantic BaseSettings rather than inventing a replacement dataclass.
Its eight fields are app_name, environment, log_level, timezone, config_path,
data_path, cache_path and logs_path. Preserve existing defaults and the three
is_development/is_testing/is_production properties. Environment remains exactly
development/testing/production; existing AURORA_ENV, AURORA_LOG_LEVEL and
AURORA_CONFIG_PATH aliases remain unchanged. Keep UTF-8 .env loading,
case-insensitive keys, extra=ignore and frozen=True.

Canonical loader API is exactly get_settings()->Settings and
validate_configuration()->Settings. Keep lru_cache(maxsize=1). Do not introduce
reload_settings, clear_settings_cache, validate_settings, DI infrastructure,
separate registries or a new configuration abstraction. Tests may clear the
existing decorator cache through its standard-library cache_clear API for
setup/teardown; this is not a new AURORA production reload contract.

All current settings have defaults, so a missing/empty .env is valid. Relative
paths are accepted and converted to Path without creating directories or
asserting their existence. Timezone remains a descriptive string with UTC
default; no timezone database validation is promised by Wave 1 configuration.
Any future tighter policy needs its owning module's explicit contract.

Preserve existing error boundaries: direct invalid Settings.environment raises
Pydantic ValidationError; get_settings wraps Pydantic ValidationError in existing
InvalidConfigurationError with cause. Invalid log_level is rejected by the
existing Settings validator with InvalidConfigurationError. No new exception,
mandatory secret, missing-env policy or filesystem validation is introduced.

Supersede only contradictory KR-002 schemas/functions/validation/test obligations
in M-01/M-03/M-03A/M-05/M-06/M-07/M-08/M-09/M-10 and compile KR-002's exact
contract before declaring its test acceptance complete. Do not silently rename
Settings fields to reconcile the two incompatible Master alternatives.

## T-03 — Preserve KR-003 surface; repair only unsafe acquisition

**Decision — APPROVED, including the narrow KR-003 repair.**

Keep get_logger(name:str, config:LoggingConfig|None=None)->logging.Logger,
the cache, named standard-library registry ownership, existing LOGGER and
default constants. Keep LoggingConfig frozen/slotted with exactly logger_name,
level and json_logs; preserve existing constructor compatibility. No DI,
global root configurator, configure_logging/reset_logging, new ContextFilter
alias, second logging subsystem or additional context fields.

Preserve RuntimeContextFilter.filter, ConsoleFormatter.format and
JsonFormatter.format. Context API remains set/get/clear_correlation_id,
set/get/clear_session_id and clear_logging_context. Correlation ID is explicit
logging context, not an automatically inferred TraceId. No hidden import of
ContextRuntime, SessionRuntime or higher layer is added.

Console output retains its UTC timestamp, level, namespace, cid/sid and message.
JSON retains timestamp/logger/level/message/correlation_id/session_id and the
optional exception field. Missing filtered IDs use the existing '-' fallback;
unfiltered JSON records retain the existing None fallback. No claim of new
redaction, deep runtime tracing or trace/pipeline/runtime fields is made.

Retain first-installed-handler behavior: the factory installs one stream handler
only if a namespace has none; a cache miss applies the supplied normalized level
but does not replace existing handlers/formatters. Cache identity is by the
existing name/config arguments; standard-library logger identity is by name.
Tests must not certify a live reconfiguration facility that does not exist.

Narrow production repair in logger.py ONLY:

1. Reject an empty namespace before any logging.getLogger call or root mutation,
   with existing InvalidConfigurationError. Do not trim/rename valid names.
2. Reject invalid configuration levels with existing InvalidConfigurationError
   before logger mutation, rather than leaking stdlib ValueError. Supported
   levels stay DEBUG/INFO/WARNING/ERROR/CRITICAL, case-normalized as today;
   no custom levels, NOTSET, WARN or FATAL vocabulary is introduced.
3. Keep error summaries fixed; do not put arbitrary supplied invalid values into
   logs. Do not redesign formatters, ContextVars or cache ownership.

**Approved admission clarification — 2026-10-07:** The Authority explicitly
accepted rejecting EXACT name == "root" with existing InvalidConfigurationError
before any logging.getLogger call. Preserve all other valid names, the existing
empty-name message, configuration and cache. Use a fixed safe error summary.
This closes the additional admission ambiguity documented in the follow-up below;
no case-insensitive name rejection, trimming or new logger abstraction is approved.

No root configuration or global reset is permitted. Reconcile conflicting
logging schemas, names, configure_logging ownership/signatures, error declarations
and test assertions in the affected Master entries and exact KR-003 contract.
This is not authorization to restore either legacy root-configuration design.

## T-04 — Complete real acceptance, not merely a green baseline

**Decision — APPROVED by explicit Architecture Authority approval.**

Compile KR-011 only after T-01–T-03 have authoritative decisions. Preserve all
approved ADR-004–008 tests and expand the canonical suite without skips/xfail,
source exclusions or placeholder assertions.

- Foundation: exact vocabularies/UUID-backed IDs/JSON aliases, constants,
  version ownership, package exports and exception hierarchy. Preserve EventPhase
  without inventing behavior; AB-00B and AB-00C define Status/Priority.
- Configuration: isolated .env/environment/default/override cases, invalid
  environment and log level, paths, actual frozen-assignment rejection, cache
  identity/invalidation and validation/error boundaries defined in T-02.
- Logging: valid named acquisition and cache identity, root non-interference,
  empty-name/invalid-level rejection, exact handler/filter/formatter behavior,
  exception formatting, missing context, context set/get/clear and independent
  execution contexts. Do not substitute correlation ID for an unimplemented
  automatic trace-ID field.
- Contracts: exact frozen/slotted schemas/exports/abstract boundaries/default
  factories and derived properties; no dispatch/validation implementation added.
- Kernel/integration: all approved DI, lifecycle, event, context, pipeline,
  Bootstrap, Kernel/Main acceptance and fresh shared-fixture wiring/teardown.

Coverage evidence must distinguish API assertions, physical executable lines and
branches. Foundation/contracts require 100% of public symbols/APIs exercised or
contract-verified (abstract contract stubs are checked as contracts, not invoked
to inflate body coverage). Configuration/logging require 100% executable-line
coverage plus all public API assertions. Preserve stricter approved per-file
runtime gates: KR-005/006/008 at least 95%; KR-007/009/010 100%. Overall public API
coverage remains at least 97%, with every required API covered. No branch-coverage
claim follows from line counts. Report measured deficits rather than lowering a
gate. Standard-library measurement is allowed; no new dependency is required.

Run Ruff, scoped format check, strict Windows/Linux Pyright, the entire discovered
Pytest suite, bounded Kernel smoke and required latest-head hosted CI. Tests use
synthetic data and controlled temporary paths, not paid APIs/live credentials.

## T-05 — Exact phased repair and build boundary

**Decision — APPROVED by explicit Architecture Authority approval.**

After explicit approval of this document:

1. Record approval; compile the exact KR-002/KR-003/KR-011 contracts and only
   affected Master entries. No other module's authority is changed.
2. Reopen KR-003 as ONE separate narrow module task/branch. Production scope:
   src/core/logger.py only. Acceptance scope: tests/core/test_logger.py only.
   Apply T-03 guards/error normalization, preserve all other behavior, validate,
   publish through ADR-003 when latest-head CI passes, report and STOP for review.
3. After that module's acceptance, implement KR-011 as ONE separate task/branch.
   Authorized implementation files are only the twelve T-01 paths. No src file,
   dependency file, workflow or later-Wave/product test may be changed.
4. If tests expose another production defect, preserve the failing evidence and
   STOP; do not repair a different owner or weaken an acceptance assertion.
5. Validate/report KR-011 and STOP for Tech Lead review before any next Wave/task.

Approval does not mean these tasks are complete or grant multi-module batching.

## Alternatives not implemented

Rebuilding configuration/logging to either inconsistent legacy Master model
would require separate authority, broader production scope, compatibility and
migration decisions. This proposal instead preserves the existing small model
and proven Kernel facade, while explicitly addressing the confirmed unsafe
logger behavior. Neither alternative is silently chosen by the Build agent.

## Preflight validation — not implementation acceptance

On the baseline above, before any source/test modification:

- uv run ruff check .: passed.
- uv run pyright: 0 errors, 0 warnings, 0 informations.
- uv run pyright --pythonplatform Linux: same zero result.
- uv run pytest: 1177 collected and passed on Python 3.13.15 / Windows.
- uv run pytest tests/core: 4 collected and passed.
- uv run ruff format --check tests/core tests/kernel
  tests/integration/test_runtime_startup.py: 11 files already formatted.
- uv run python -m src.main: exit 0.
- tests/conftest.py: absent.
- No coverage percentage was measured in this preflight; green regression is
  not a claim of KR-011 coverage/contract completion.

The root-logger probe ran in an isolated short-lived Python process. Its logging
state did not alter the user application's process or write source/test files.
No live credential/provider/network request was made. Pyright's tool update
notice is not a diagnostic; no package upgrade was performed.

## Current gate

**DECISIONS APPROVED; IMPLEMENTATION ACCEPTANCE STILL REQUIRED.**

Compile the exact KR-002/KR-003/KR-011 contracts and affected Master entries.
Only src/core/logger.py and tests/core/test_logger.py are reopened for the first
narrow KR-003 task. KR-002 and all other production remain frozen. KR-011 source
acceptance is not claimed: its separate test-only task waits for KR-003 review.
The preflight results above remain historical baseline evidence, not post-repair
validation. Publication/validation evidence belongs in the completed module report.

### Implementation follow-up — 2026-10-07

Read-only standard-library identity checks confirmed that both "" and "root"
resolve to the root logger. The approved empty-name guard does not reject "root".
T-03 forbids root mutation but explicitly defines only empty-name admission;
the additional rejected public input requires Authority clarification before
extending the guard. This is not a new decision or an approval of that extension.

Implementation is STOPPED pending that admission decision. A tripwire regression
in tests/core/test_logger.py detects root acquisition before any level/propagation/
handler mutation. The confirmed empty-name and invalid-level repairs remain
local, uncommitted work. Exact Wave contracts were compiled, but affected Master
reconciliation and complete KR-003 acceptance/publication are not finished.
KR-011 implementation has not begun.

The Authority subsequently answered "утверждаю" to the exact root-admission
clarification. The admission blocker is therefore resolved; completion still
requires scoped Master reconciliation, full KR-003 acceptance and validation.
The earlier stopped state and failed test remain historical evidence, not the
current authority gate or a claim of final acceptance.

### Scoped compilation and KR-003 local validation — 2026-10-07

The exact KR-002/KR-003/KR-011 contracts and affected Master entries are now
compiled from the approved decisions. The narrow KR-003 implementation changes
only src/core/logger.py and tests/core/test_logger.py. Empty and exact "root"
names, and unsupported levels, reject before registry access/mutation; all other
approved logging/configuration behavior is preserved.

Local evidence on Python 3.13.15 / Windows: Ruff passes; strict Pyright passes
in Windows and Linux platform modes; 1216 discovered tests pass, including 40
KR-003 cases; the scoped formatter check passes; bounded Kernel smoke exits 0.
Standard-library line tracing measures logger.py at 37/37 and logging_config.py
at 75/75 executable lines. This is line evidence, not branch coverage, hosted CI,
an actual Linux execution or first usable Windows product acceptance.

Publication requires latest-head hosted CI and the normal ADR-003 protected
workflow. KR-011 implementation remains unstarted and awaits this separate
KR-003 task's report/review. No other production owner is reopened.
