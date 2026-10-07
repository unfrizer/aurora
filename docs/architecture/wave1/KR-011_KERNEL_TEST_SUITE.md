# KR-011 — Kernel Test Suite Contract v1.0

**Status:** APPROVED — ADR-009 T-01–T-05, 2026-10-06
**Owner / layer:** KR-011 / Validation
**Implementation gate:** AFTER separate narrow KR-003 repair acceptance.

## Exact authorized files

ELEVEN executable Wave 1 modules and ONE shared-fixture file:

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

No src, dependency, workflow or later-Wave/product test modification. Existing
later tests are full regression-only. No tests/runtime or duplicate split files.
Registry/Scope/Resolver/Provider -> test_container; Executor -> test_pipeline;
Kernel/Main -> test_bootstrap and test_runtime_startup. Test ownership does not
reopen frozen production modules. Another production defect requires failing
evidence and STOP, not cross-module repair or weakened assertions.

## Shared fixture contract

Exactly settings, trace_context, runtime_context, container, event_bus, lifecycle
and orchestrator in tests/conftest.py. Function-scoped fresh instances, explicit
approved dependency wiring and completed teardown; no business logic/assertions.
Controlled synthetic identities/data/temp paths and isolated environment/caches;
no cross-test mutable singleton, paid API/live credential or external service.
Other existing local helpers are not production or new runtime abstractions.

## Required acceptance matrix

| Canonical file | Mandatory verification |
| --- | --- |
| test_types.py | Exact Foundation enums/AB-00B status/AB-00C priority and unchanged EventPhase, four DI scopes, UUID-backed aliases including retained approved aliases, recursive JSON Metadata/Payload/Headers, constants/manifest fields, version ownership/package exports and exception hierarchy |
| test_settings.py | Every field/helper/validator/loader and ALL exact T-02 defaults/env/.env/alias/extra/frozen/cache/error policies in APPROVED KR-002 contract |
| test_logger.py | Every logging symbol/method and ALL exact T-03 factory guards/cache/handler/filter/context/formatter/error/isolation policies in APPROVED KR-003 contract |
| test_contracts.py | All seven KR-004 files' exact public schemas/exports/ABCs, frozen/slotted/keyword-only ordering, independent factories, Trace/Context/Event/Lifecycle/Manifest/Service derived properties; contract-only boundaries, no dispatch/DI/validation side effects |
| test_container.py | Preserve ALL ADR-004 P-01/P-02/P-03/P-06 and APPROVED KR-005 graph/scope/injection/readiness/eager/identity/rollback/cleanup/error/cancellation/retry/reentrancy acceptance |
| test_lifecycle.py | Preserve ALL AB-00B/ADR-004 P-05 and APPROVED KR-006 100 transition combinations, six hooks, touched participants, ordered errors/cancellation/resumable cleanup and terminal FAILED behavior |
| test_event_bus.py | Preserve ALL ADR-005 E-01–E-04/ADR-004 P-04 and APPROVED KR-007 exact event validation/depth/snapshots/five priorities/FIFO/subscription/nested/error/cancellation/lifecycle acceptance |
| test_context.py | Preserve ALL ADR-006 C-01–C-04/ADR-004 P-04 and APPROVED KR-008 JSON/depth/fields/detached context/session/atomicity/order/default/observational-expiry acceptance |
| test_pipeline.py | Preserve ALL ADR-007 O-01–O-05 and APPROVED KR-009 schema/graph/order/binding/preflight/awaited operation/event timeline/terminal/error/cancellation/busy/isolation acceptance |
| test_bootstrap.py | Preserve ALL ADR-008 B-01–B-05 and APPROVED KR-010 builder/composition/properties/health/construction/participant/error/legal cleanup/guard/isolation acceptance |
| test_runtime_startup.py | Preserve ALL ADR-008 real Pipeline/Session DI release on success/failure/cancellation, scoped isolation/ordered causes/interrupted retry/Main partial startup and bounded smoke acceptance |

Exact module contracts KR-001–010 and their cited approved decisions are normative,
not illustrative suggestions. All existing accepted cases remain; no skip, xfail,
placeholder, source exclusion or imported contract stub execution to inflate coverage.

## Coverage and validation

Distinguish verified public symbols/APIs, physical executable lines and branches.

| Module | Gate |
| --- | --- |
| KR-001 / KR-004 | 100% public symbols/APIs exercised or contract-verified; abstract stubs verified, not invoked for fake body coverage |
| KR-002 / KR-003 | 100% executable lines PER owned source file plus every public API asserted |
| KR-005 / KR-006 / KR-008 | At least 95% executable lines PER owned file, every public API exercised |
| KR-007 / KR-009 / KR-010 | 100% executable lines PER owned file, every public API exercised |
| Overall Wave 1 | At least 97% public API coverage with every required API covered |

Report actual uncovered lines/APIs; line counts are not branch-coverage evidence.
Standard-library measurement is allowed; no new dependency or relaxed gate.
Validate Ruff check ., scoped ruff format --check (NOT whole-repository rewriting),
strict Pyright Windows and Linux modes, whole discovered Pytest with nonzero
collection/no skips/xfail, python -m src.main bounded Kernel smoke and required
latest-head hosted CI. Failures belonging to another owner remain unfixed.

## Phased authority and completion

Approved by explicit ADR-009 T-01–T-05; this supersedes staging-only status and
obsolete test-location/count/config/logging requirements only. First compile
contracts and affected Master entries; finish/review narrow KR-003 in its own
branch/report. Then KR-011 is one separate test-only task/branch/report. Do not
implement both in one task. Missing acceptance/coverage is reported, not waived.
After KR-011 report STOP for Tech Lead review before any next Wave/task.
