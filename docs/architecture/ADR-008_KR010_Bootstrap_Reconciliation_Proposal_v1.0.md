# AURORA — KR-010 Bootstrap Reconciliation Proposal v1.0

**Document ID:** ADR-008
**Status:** APPROVED — CANONICAL KR-010 RECONCILIATION DECISION
**Date:** 2026-10-06
**Active task:** KR-010 — Runner / Bootstrap reconciliation
**Repository baseline:** `e4c6e28d9c6bdd02d6e039bb2e13dfacae8c0940`
**Implementation authority:** B-01–B-05 approved; compile contract/registries before source edits.

## Purpose and Approval Boundary

Complete the exact composition contract for approved ADR-004 P-05. Do not
change L0–L8, a Runtime owner, a DI scope, contract dataclass, event vocabulary
or the AB-00B lifecycle transition matrix. KR-009 and its narrow O-05 Bootstrap
constructor migration are accepted; they are not reopened.

## Explicit Approval Record — 2026-10-06

The Architecture Authority directly stated:

> Утверждаю ADR-008 полностью, включая B-01–B-05

This approves every proposed B-01–B-05 decision, including the narrow Session
composition import/new API exception and exact production/canonical test scope.
The earlier generic KR-009 acceptance did not supply these decisions; this direct
reply does. It is not an independent human implementation review. ADR-003 governs
routine PR/merge, not architecture approval. Compile contract/registries before code.

## Sources Actually Inspected

- AGENTS.md; AB-00A, its reconciliation resolution and Build Protocol amendment;
  complete Wave 1 implementation handoff; AB-00B and AB-00D.
- ADR-001/003/004, approved ADR-006 C-01–C-04 and ADR-007 O-01–O-05;
  the compiled KR-006 lifecycle contract and the KR-010 staging contract.
- Complete M-00 navigation; relevant KR-010 M-01/M-02/M-03/M-03A/M-04/M-06
  construction, API, import, startup/shutdown and ownership declarations.
- M-05 Bootstrap events/root-context, lifecycle and Session/DI lifetime entries;
  M-07 ownership/testing rules; M-08 runtime exceptions; M-09 KR-010 acceptance;
  PATCH_ERRATA. Unrelated later-Wave architecture is not redesigned.
- Current bootstrap.py, runtime/runtime.py, src/main.py and both canonical
  KR-010 test files. Read-only inspection of Container/Lifecycle/Session APIs,
  DI pending-disposal bookkeeping, Foundation contracts/types/exceptions and
  existing Configuration/Logging implementations and callers.

## Observed Findings

| ID | Actual evidence | Classification |
| --- | --- | --- |
| B-01 | M-01/M-02/M-06 construct Context before Container, EventBus, Orchestrator and Lifecycle. M-04 prescribes Container, Lifecycle, EventBus, Context, Orchestrator and calls that order immutable. M-03/M-03A expose public builders; M-06 calls differently named builders private. M-06 refers to nonexistent configure_logging; M-03 directory validation refers to nonexistent DirectoryValidationError. M-05 requires Bootstrap events/root context, while M-06/current build performs construction only. | Architecture / public contract conflict |
| B-02 | P-05 requires composed Session-scoped DI removal. M-04 explicitly forbids BootstrapRuntime and RuntimeKernel importing SessionRuntime; current graph contains no SessionRuntime reference or removal composition API. ADR-006 correctly leaves SessionRuntime independent of DI. | Import / ownership-composition / missing public contract |
| B-03 | RuntimeKernel.execute only awaits Orchestrator; no finally cleanup. An in-memory Pipeline-scoped service has zero disposal calls after successful execution, then one at full shutdown. A new facade-level rejection must not accidentally clear another active execution's scope. | Confirmed local defect plus exact admission/cleanup decision |
| B-04 | M-08 disallows execution before RUNNING, but current Kernel executes successfully in CREATED. Existing component guards do not cover the entire Kernel operation plus subsequent DI cleanup. Partial-startup cleanup through Kernel needs exact legal-state and error/cancellation behavior. | Confirmed defect plus missing public guard/error policy |
| B-05 | M-01/M-06 require waiting for a shutdown signal; M-03 waits for runtime completion; M-03A/M-04 require an inputless execute call. Current main is bounded startup/shutdown smoke. M-06 forbids escaping exceptions; M-03 explicitly allows process termination by exceptions. Current main skips FAILED cleanup and a stop failure can prevent shutdown or hide startup failure. | Public process contract conflict and confirmed local defects |

Already resolved: async construction without initialization (AB-00D-005);
five existing facade references; async lifecycle surface; StateRuntime alone
owns status; detached JSON; actual Orchestrator work; the same EventBus wired
through Orchestrator rather than a Bootstrap-created Executor. No new exception
class, compatibility shim, loop/thread, service locator or generic helper is proposed.

## B-01 — Proposed Exact Construction, Builders and Prerequisites

Select M-01/M-02/M-06 and the existing construction order, narrowly superseding
the contradictory M-04 order. Retain the current public builder methods and
their current parameter signatures, reconciling M-06's private-only alternative:

```python
class BootstrapRuntime:
    async def build(self) -> RuntimeKernel: ...
    def validate_environment(self) -> None: ...
    def build_context(self) -> ContextRuntime: ...
    def build_container(self) -> ContainerRuntime: ...
    def build_event_bus(self) -> EventBusRuntime: ...
    def build_orchestrator(self, event_bus: EventBusRuntime) -> OrchestratorRuntime: ...
    def build_lifecycle(
        self,
        container: ContainerRuntime,
        event_bus: EventBusRuntime,
        context: ContextRuntime,
        orchestrator: OrchestratorRuntime,
    ) -> LifecycleRuntime: ...
```

Build sequence: configuration validation/cached Settings, existing Logging,
Context, Container, EventBus, Orchestrator, Lifecycle, then RuntimeKernel.
B-02 inserts only the existing Session storage collaborator immediately after
its Context dependency; it is not an additional lifecycle Runtime or layer.
Lifecycle registers Context, Container, EventBus, Orchestrator in that order.
Initialize/start use forward registration order; stop/shutdown reverse touched
order. Never register Lifecycle in itself or bypass its participant bookkeeping.

Use only the existing KR-002 validate_configuration/get_settings cache and KR-003
get_logger/LoggingConfig APIs; explicitly pass Settings.log_level to the existing
LoggingConfig.level at composition. No new configure_logging function, settings
model, logging implementation, root logger configuration or directory validator.
validate_environment validates configuration, not a hard-coded repository layout;
it creates no directories/files and requires no new environment variable.

ConfigurationError propagates unchanged before graph construction. Other ordinary
construction errors become existing RuntimeInitializationError with the original
cause and a safe fixed message. Cancellation/SystemExit/KeyboardInterrupt are not
converted. Constructors/builders perform no lifecycle/service initialization;
therefore an unsuccessful build has no touched participants to dispose. Settings
and logging retain their already approved process ownership. Every successful
build returns a new independent, wired but CREATED graph; no cached Kernel.

No root RuntimeContext, trace IDs, logical Bootstrap events, services or business
pipeline are fabricated during build. Select the construction-only M-06/AB-00D
boundary; conflicting M-05 Bootstrap-emission/root-context prose is reserved,
not a requirement to invent event input, trace factory or a new public API here.
This does not change event vocabulary or implement another module's events.

## B-02 — Proposed Explicit Session Composition Exception

Permit the narrow KR-010 imports of the EXISTING SessionRuntime in bootstrap.py
and runtime/runtime.py only for construction, typed reference and composition
through its existing public APIs. Bootstrap constructs SessionRuntime(context)
once and passes it explicitly to Kernel; Kernel does not construct it. No new
Session owner, facade class, callback bridge or DI import in KR-008 is added.

The proposed exact new/changed surface is:

```python
class RuntimeKernel:
    def __init__(
        self,
        *,
        container: ContainerRuntime,
        lifecycle: LifecycleRuntime,
        event_bus: EventBusRuntime,
        context: ContextRuntime,
        orchestrator: OrchestratorRuntime,
        session: SessionRuntime,
    ) -> None: ...
    @property
    def session(self) -> SessionRuntime: ...
    async def remove_session(self, session_id: SessionId) -> None: ...
```

Retain all existing Kernel properties/methods, arguments, None results and
exports. The required session argument is explicit, not an optional hidden
constructor, factory or compatibility overload. Current repository callers
construct Kernel only through Bootstrap, so no frozen-module migration is needed.
The property is read-only and exposes the same existing registry, not a copy or
another owner. Session creation/updates still follow ADR-006 without new wrappers.

remove_session validates a UUID-backed SessionId (invalid input uses existing
ContractValidationError), confirms SessionRuntime.get first (missing session
retains RuntimeStateError), then awaits Container.clear_session(session_id).
After a completed ordinary DI attempt, remove the Session snapshot/its matching
active context even if DI reports disposal errors, and propagate that error under
B-04. Container remains the only service-disposal owner and already clears every
matching Pipeline/Transient resource belonging to that session. Other sessions
and Application services are unaffected. Cancellation/interruption during DI
disposal keeps the Session snapshot/context for explicit retry; completed service
attempts are not repeated by the existing Container bookkeeping.

Full Kernel shutdown delegates DI/lifecycle teardown first, then synchronously
drains its Session registry using list/remove, including after FAILED cleanup or
interrupted lifecycle teardown. Remaining DI ownership is retained by Container/
Lifecycle for later explicit shutdown, not by Session metadata. This Session drain
must not call clear_session after Container has closed. Context.shutdown remains
unchanged; it does not secretly own/delete a separate Session registry.

The composed removal guarantee belongs to Kernel.remove_session. Direct use of
the lower-level SessionRuntime.remove API is still a registry-only operation;
it is not retroactively turned into DI disposal. As with existing exposed
Container/Lifecycle/Orchestrator references, a caller bypassing Kernel composition
must explicitly obey those lower-level contracts and cannot claim Kernel's guard
or cleanup guarantee. No new post-shutdown gate is added to KR-008.

## B-03 — Proposed Pipeline Admission and Finally Cleanup

Keep `async execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext)
-> None`. Accept it only in RUNNING, after acquiring the Kernel operation guard.
Rejected lifecycle/busy calls execute no callback/event and perform no DI cleanup.

Capture the actual PipelineDefinition's UUID-backed pipeline_id before executing.
Invalid definition/ID uses the existing InvalidManifestError and invokes no scope
disposal with a malformed/guessed ID. Full stage/binding/context/dependency/DAG
validation remains Orchestrator/Manifest ownership, not another validator in Kernel.
For every admitted execution with a valid captured ID, await
Container.clear_pipeline(captured_id) in finally, including Orchestrator preflight
failure, callback/publication failure and cancellation. Use the definition ID,
not a regenerated ID or a potentially disagreeing context ID.

The guard stays held until cleanup finishes or is interrupted. A recursive or
concurrent rejected Kernel.execute must never dispose the accepted execution's
resources. Pipeline completion does not remove its Session context or Application
services. Container owns linked Transient disposal and reverse dependency order.
Kernel does not resolve/register services, emit new events, modify the pipeline,
change lifecycle status on a business failure or store an execution history.

## B-04 — Proposed Kernel Guards, Legal Cleanup and Error Preservation

Use one instance-local operation guard covering initialize/start/stop/shutdown/
execute/remove_session, including awaited teardown. Concurrent/re-entrant Kernel
mutation raises existing RuntimeStateError before any delegated mutation or scope
clear. All read-only properties/status/state/health/diagnostics remain available.
Release the guard in finally after every validation/error/cancellation path. This
is not a second RuntimeStatus owner, process-global lock or background executor.

Normal lifecycle calls continue through LifecycleRuntime and AB-00B's unchanged
matrix. To abort an idle partial startup in INITIALIZING, READY or STARTING,
Kernel.stop/shutdown first delegates the ALREADY LEGAL transition to FAILED through
LifecycleRuntime.transition, then runs cleanup-only stop/shutdown. Do not mutate
StateRuntime directly or invent READY-to-STOPPED/FAILED-to-TERMINATED. A busy
Lifecycle rejects transition without interference. CREATED cleanup does not invent
a transition or initialize resources just to dispose them; it retains the existing
illegal-operation error. RUNNING shutdown still requires stop first. FAILED cleanup
and completed idempotent cleanup retain KR-006 semantics. No reset/recovery API.

Preserve the FIRST error as the same exception object. If execution/startup/stop
already failed, later ordinary cleanup errors OR cancellation do not replace it;
attach them in attempt order in an ExceptionGroup/BaseExceptionGroup cause while
preserving its prior explicit cause as a nested entry. Do not insert the primary
into its own cause or flatten away previous groups. A primary CancelledError is
re-raised as that same cancellation; it is not an ordinary success/runtime error.
If work succeeded and cleanup alone failed/cancelled, propagate that cleanup error
unchanged. KeyboardInterrupt/SystemExit are not converted into business failures.
This explicitly extends ADR-007's first-error policy to Kernel composition; it is
not an assertion that every secondary-cancellation choice was specified by P-05.

No shield/task/unbounded retry. Interrupted Container/Lifecycle disposal remains
owned there for later explicit shutdown/removal; completed attempts are not repeated.
Safe summaries/type names only in logs, never exception text, traceback payloads,
metadata, credentials or raw input. Kernel health uses the existing ERROR > WARNING
> OK aggregation without mutation; diagnostics returns fresh existing metadata.
Kernel implements the existing AB-00D RuntimeContract explicitly; add no universal
execute/status/diagnostics member to that contract.

## B-05 — Proposed Bounded Kernel Entrypoint and Reliable Finalization

Select the existing bounded Wave 1 smoke entrypoint, not an unspecified signal
server or fabricated business execution. Keep `async main() -> None` and exactly
one `asyncio.run(main())` boundary. Build once, initialize, start, then immediately
perform stop/shutdown in finally. No arguments, network service, wait loop, hidden
pipeline, signal hook, thread or task. Long-lived desktop-web/UI hosting belongs
to a separately approved application/platform composition task, not KR-010.

This explicitly supersedes conflicting KR-010 wait-for-signal/mandatory inputless
execute prose in M-01/M-03/M-03A/M-04/M-06 only. Main imports Bootstrap, permitted
Foundation status/error vocabulary and optional existing Logger, never a Runtime
implementation/internal, contract or service. It does not reach through Kernel
into participants or force their lifecycle transitions.

After a Kernel is returned, stop and shutdown are independent best-effort facade
attempts: a stop error cannot skip shutdown. Apply B-04 to preserve startup failure
or cancellation across both attempts. Partial INITIALIZING/READY/STARTING/FAILED
uses B-04's legal cleanup path; STOPPED proceeds to shutdown; completed teardown
is idempotent. No illegal CREATED transition is forced. A failed build has no Kernel
to tear down and propagates its error. A normal smoke run ends TERMINATED; earlier
failure cannot become a successful terminal status.

Select M-03/current source's error propagation after cleanup: failure can terminate
the process with a nonzero exit, cancellation remains cancellation, no fabricated
success/exit suppression. This narrowly supersedes M-06's conflicting promise that
exceptions never escape asyncio.run. Logs are safe; original exceptions/cause
groups remain available to the caller. Do not redefine CLI flags or a new exit API.

## Proposed Scope and Registry Reconciliation

On explicit approval, compile wave1/KR-010_RUNNER_BOOTSTRAP.md as APPROVED and
reconcile only affected KR-010 construction/API/import/lifetime/error/test entries
in M-01/M-02/M-03/M-03A/M-04/M-05/M-06/M-07/M-08/M-09 BEFORE code changes.
Record B-02's limited Session import exception and B-04's existing Contract/runtime
Foundation imports; do not broadly lift the internal-runtime import prohibition.

Only these production files may change in one KR-010 task/branch:

- src/kernel/runtime/bootstrap.py
- src/kernel/runtime/runtime.py
- src/main.py

Only these canonical tests may change under ADR-004's explicit permission;
ownership remains KR-011:

- tests/kernel/test_bootstrap.py
- tests/integration/test_runtime_startup.py

No KR-001–KR-009 implementation/test, higher Wave/product code, dependency,
workflow, protection rule, configuration or unresolved vocabulary changes.
No second test_runtime.py at an obsolete tests/runtime path. Any further
contradiction beyond B-01–B-05 still requires STOP and explicit Authority decision.

## Required Acceptance After Approval — Not Yet Implemented

- Exact existing builders/properties/exports and B-02's approved new surface;
  explicit RuntimeContract implementation, read-only references and independent builds.
- Exact construction, participant initialize/start, reverse stop/shutdown order;
  settings/logging delegated once; invalid config/construction failures; build
  stays CREATED and creates no active context/event/service or directory.
- Real operation and Pipeline-scoped DI release on success, preflight rejection,
  callback/publication failures and cancellation; Session/Application isolation,
  ordered multi-disposal failure, original cause preservation and interrupted retry.
- Session removal via Container, active/non-active removal, missing/invalid IDs,
  multiple scoped resources, ordinary disposal error, cancellation/retry, independent
  registries and full shutdown clearing registry without a new KR-008 lifetime gate.
- Busy guard spans operation AND cleanup, including recursive disposal calls;
  no rejected contender scope disposal; read-only APIs stay usable; guard restored.
- Every legal facade path and unchanged AB-00B transition pairs; partial startup,
  FAILED remains terminal, completed cleanup idempotent, interrupted ownership retry.
- Main independently attempts stop/shutdown after initialize/start/stop failure
  or cancellation, never masks first error, has no wait loop or arbitrary execute.
- Every public API exercised and 100% executable-line coverage target for the
  three KR-010 source files (not a branch-coverage claim); no skips/xfail or source
  exclusions. Canonical tests only; in-memory mocked errors, no paid/live API calls.
- Ruff, strict Pyright Windows/Linux, full discovered Pytest, scoped formatter,
  Kernel smoke and required latest-head hosted CI before ordinary merge under
  ADR-003. Full module report and stop before KR-011; no usable Windows MVP claim.

## Actual Read-Only Preflight Evidence — 2026-10-06

| Check | Observed result |
| --- | --- |
| uv run ruff check . | PASS |
| uv run pyright | 0 errors, 0 warnings, 0 informations |
| uv run pyright --pythonplatform Linux | 0 errors, 0 warnings, 0 informations |
| uv run pytest -q | 1020 passed |
| uv run python -m src.main | PASS, exit 0 |
| Current canonical KR-010 tests | Two total: normal bootstrap lifecycle and initial health |

An ephemeral read-only in-memory probe, not an added acceptance test, confirmed:

- A real callback executes through RuntimeKernel in CREATED.
- Its previously resolved Pipeline-scoped service is not disposed at execute return
  (0 calls), but is disposed at normal full shutdown (1 call).
- A FAILED-startup facade supplied to main receives no stop/shutdown call; the
  original initialization failure propagates. The probe uses a fake facade to
  isolate Main's conditional path; it does not claim a new real Lifecycle test.
- Kernel has neither session nor remove_session; no existing public composition
  route was overlooked in the current source/call-site search.

Pyright's available-update notice is informational and not a typing diagnostic;
no version/dependency was changed. Green baseline regression does not prove new
cleanup/guard acceptance or resolve these document conflicts.

After adding this draft, Ruff passed again, strict Windows Pyright again reported
zero errors/warnings/informations, and full Pytest again passed 1020 tests. Both
proposed Python signature blocks parse successfully; this is syntax checking,
not implementation/type validation of the proposed API.

During this DRAFT task only this document is added. No source/test, APPROVED
contract, registry, Git branch/commit/push/PR/merge or repository protection is
changed. No independent human code review or completed KR-010 build is claimed.

## Next Authorized Action

Compile the approved exact KR-010 contract and affected Master entries, implement
only the three production files and two canonical tests, validate, publish under
ADR-003, report and stop before KR-011. Other modules remain frozen. The historical
DRAFT evidence above is not acceptance evidence for the forthcoming implementation.
