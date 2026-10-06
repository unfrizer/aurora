# AURORA — KR-009 Pipeline Reconciliation Proposal v1.0

**Document ID:** ADR-007
**Status:** APPROVED — CANONICAL KR-009 RECONCILIATION DECISION
**Date:** 2026-10-06
**Active task:** KR-009 — Pipeline Runtime implementation
**Repository baseline:** 3fba7a2dbce3b6b6842d67b65792f35dfa3755b1
**Implementation authority:** O-01–O-05 approved; compile contract/registries before source edits.

## Purpose and Approval Boundary

Complete the exact implementation contract for ADR-004 P-03/P-04 without inventing
a universal execute method, Runtime, layer, scope, provider or global registry.
## Explicit Approval Record — 2026-10-06

The Architecture Authority directly approved the complete decision:

> Утверждаю ADR-007 полностью, включая O-01–O-05 и минимальную миграцию Bootstrap. дальше

This supplies authority for O-01–O-05 and the precise two-line KR-010 caller
migration. It is not an independent human code review or a claim of acceptance
for an implementation not yet built. ADR-003 governs ordinary PR/merge handling.

Before implementation: compile the exact KR-009 contract and reconcile affected
Master entries. Then build one module, validate, publish and report. STOP before
full KR-010. No other architecture change or cross-module repair is authorized.

## Sources Actually Inspected

- AGENTS.md; AB-00A, reconciliation and Build Protocol amendment; complete Wave 1 handoff.
- Complete AB-00B/AB-00D, ADR-001 and ADR-004; relevant approved ADR-006 context behavior.
- Complete M-00 navigation; KR-009 sections of M-01/M-03/M-03A/M-04/M-06/M-09.
- M-05 pipeline event payloads/priorities, complete Pipeline Execution Timeline
  section, pipeline validation ownership; M-07 Pipeline Constitution and M-08
  pipeline exception propagation; PATCH_ERRATA.
- Four KR-009 source files, canonical test_pipeline.py; Foundation types/exceptions,
  RuntimeModuleManifest, EventBus/Publisher; read-only Bootstrap/RuntimeKernel and
  their canonical startup tests/call sites.

### Findings and Classification

| ID | Observed evidence | Classification |
| --- | --- | --- |
| O-01 | M-03 says Executor implements RuntimeContract and exposes health; M-03A lists health; M-06/current source define a plain executor with no lifecycle or health. M-03/current source expose execution_order; M-06 calls it private. Detached stage/context snapshots also need an explicit permitted JSON transformation edge, not a private KR-008 helper or new Context owner. | Public Contract / Import Conflict |
| O-02 | ADR-004 fixes operation binding and pipeline/context ID agreement but not all malformed input/module-dependency rules. Current validation is recursive and validates only the stage DAG; registration does not validate the manifest. Existing order for [A, B(dep A), C] is A, C, B; another stable topological algorithm would change observable order. | Missing Exact Public Boundary / Order Decision |
| O-03 | M-05 mandates request/create/validate/queue phases and Manifest-produced events, a queue, DI resolution, scope creation and duration metrics; M-04 forbids Manifest/EventBus and Orchestrator/Container interaction; M-06/M-07 use the smaller start/stage/terminal sequence. ADR-004 assigns callbacks to composition and DI scope cleanup to KR-010. Cancellation and failure during terminal-event delivery need exact behavior to avoid double terminal events. | Architecture / Event Contract Conflict |
| O-04 | Current execute_stage emits started/completed without executing work; register_module(..., operation=...) raises TypeError. Failure publication can mask the primary error; CancelledError has no handling; registry mutation/re-entrant execution are not guarded. Existing ADR-004 requirements need exact completion/error behavior consistent with O-03. | Confirmed Local Defects plus Public Error-policy Clarification |
| O-05 | Approved ADR-004 P-03 requires OrchestratorRuntime(event_bus), but frozen KR-010 Bootstrap imports Executor and calls OrchestratorRuntime(ExecutorRuntime(event_bus)). Changing KR-009 alone would introduce a NEW KR-010 typing/construction failure. A compatibility shim would violate the approved composition decision. | Cross-module Scope / Migration Blocker |

Already resolved, not reopened: operation registration signatures and None return,
manifest/context/event schemas, async RuntimeContract, Publisher-only event factory,
sequential execution, supplied trace propagation, detached JSON and terminal lifecycle
status ownership. These do not require another Foundation/KR-004/KR-007/KR-008 edit.

## Frozen Invariants

- Exactly four existing KR-009 files and five existing exported classes/dataclasses.
- Same PipelineStage (stage_id, module_id, depends_on) and PipelineDefinition
  (pipeline_id, stages) fields and existing derived properties; no dataclass validator.
- Same RuntimeModuleManifest five fields; no callables inside serializable models.
- L0–L8, RuntimeStatus, EventPhase, EventPriority and DI scopes unchanged.
- Manifest validates; Executor orders/awaits stages; Orchestrator owns module
  registration, per-module bindings and execution coordination.
- Publisher alone creates logical RuntimeEvents, via the existing EventBus facade.
- No DI acquisition/disposal inside KR-009, service locator, universal execute,
  runtime discovery, new identifier/exception/helper abstraction or higher-layer import.
- Python 3.13, uv, strict typing, standard library only; in-memory sequential work,
  no network, persistence, background task, mutable global state or new dependency.

## O-01 — Approved Exact Executor Surface and Snapshot Import Boundary

Select M-06/current source's plain internal ExecutorRuntime, not a RuntimeContract
participant. It has no new health, lifecycle, runtime_name or runtime_layer API.
Keep the existing public execution_order method for canonical tests; explicitly
supersede M-06's private-only spelling, not add both names or a compatibility alias.

Orchestrator continues to implement AB-00D RuntimeContract: read-only identity,
async initialize/start/stop/shutdown and sync health. Name "orchestrator", L0_KERNEL,
health OK; initialize/start/stop remain no-op. shutdown clears manifests/bindings
when idle; no new lifecycle state, reset or post-shutdown registration gate.

Exact changed APIs are the already approved ADR-004 signatures:

```python
class OrchestratorRuntime:
    def __init__(self, event_bus: EventBusRuntime) -> None: ...
    def register_module(
        self,
        manifest: RuntimeModuleManifest,
        *,
        operation: Callable[[RuntimeContext], Awaitable[None]] | None = None,
    ) -> None: ...
    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None: ...


class ExecutorRuntime:
    def __init__(self, event_bus: EventBusRuntime) -> None: ...
    async def execute(
        self,
        pipeline: PipelineDefinition,
        *,
        context: RuntimeContext,
        operations: Mapping[ModuleId, Callable[[RuntimeContext], Awaitable[None]]],
    ) -> None: ...
    async def execute_stage(
        self,
        stage: PipelineStage,
        *,
        context: RuntimeContext,
        operation: Callable[[RuntimeContext], Awaitable[None]],
    ) -> None: ...
    def execution_order(self, pipeline: PipelineDefinition) -> tuple[PipelineStage, ...]: ...
```

Retain all existing Manifest methods and Orchestrator unregister_module/modules/
contains and RuntimeContract methods. No new public alias, operation accessor or
execute result type. Operation mappings are independently captured per execution;
callable objects remain explicitly owned by application/composition, not cloned.

Explicitly permit Executor and Orchestrator to use the existing stateless
MetadataRuntime for JSON validation/detachment; no import/access of ContextRuntime
or SessionRuntime storage or private copying helpers. This is a limited additional
downward KR-009 → KR-008 transformation edge, with no ownership transfer or cycle.
Orchestrator's EventBus reference remains construction-only as ADR-004 requires;
all event creation/publication remains in Executor through the facade.

## O-02 — Approved Validation, Module Dependencies and Stable Order

Manifest.validate keeps AB-00D's same-object pass-through. Validate actual
PipelineDefinition/PipelineStage instances, UUID-backed pipeline_id, actual tuple
stages/dependencies, valid non-empty Unicode string stage/module identifiers,
unique stage IDs, existing dependency references, no self-dependency and an acyclic
DAG. Whitespace is not silently trimmed; no new identifier pattern/length policy.
Repeated references to the same valid dependency are redundant edges, not a new error.
No arbitrary stage-count cap; deep valid DAGs must not fail with RecursionError.
Other public Manifest methods remain stateless and validate their relevant input
shape/references before traversal. Invalid structure uses InvalidManifestError;
cycles use existing RuntimeDependencyError, not nonexistent PipelineCycleError.

Select the EXISTING stable wavefront order: at each pass capture all currently
ready stages in their original tuple order, then execute that wave sequentially.
Newly-ready stages wait until the next pass. Thus [A, B(dep A), C] executes A, C, B.
Do not silently replace it with lexicographic sorting or one-at-a-time ready selection.
No pipeline/stage mutation, parallelism, queue or stored execution history.

Registration validates actual RuntimeModuleManifest, non-empty Unicode ModuleId
and version strings, existing RuntimeLayer member, tuple dependencies/provides
with valid non-empty Unicode strings; empty tuples remain allowed. Version is an
opaque non-empty string, not a new invented SemVer/version-negotiation contract.
Duplicate module IDs and malformed bindings use InvalidManifestError. operation
is None or callable under the typed Callable → Awaitable[None] contract; do not
call operations during preflight or reject callable objects by async-def inspection.

Forward module dependency references may be registered. Before execution validate
the registered manifest graph reachable from stage modules: dependency existence,
cycles and no dependency on a higher RuntimeLayer. Missing/cyclic module dependencies
use RuntimeDependencyError; upward layer edges use existing RuntimeLayerError.
ModuleManifest.depends_on describes static module dependencies, NOT an implicit
stage edge: it does not generate/reorder stages or require a callback for a
metadata-only dependency absent from the stage DAG. Stage ordering is exclusively
PipelineStage.depends_on. Unregister removes that manifest/binding without cascade;
an affected future execution must fail preflight if its dependency is now missing.

Before any start event or callback, validate every stage module/operation and
capture valid detached context. Use the existing KR-008 field rules: actual
RuntimeContext/TraceContext, UUID-backed IDs, existing RuntimeLayer, aware UTC
created_at/present expires_at, and canonical JSON through MetadataRuntime. Require
pipeline.pipeline_id == context.pipeline_id; never generate a replacement ID.
Invalid context uses ContractValidationError; ID disagreement/missing stage
module or operation uses InvalidManifestError. Preflight failure emits no pipeline
or stage event and has no business side effect. Expiry remains observational.

Execution preserves supplied context identity fields, trace and timestamps.
Detached per-execution metadata may add execution_started_at (UTC ISO string) and
stage_count. Each callback receives another detached snapshot with stage_id,
module_id (string), stage_index (zero-based execution-order index). For the standalone
execute_stage call the index is zero. Caller/previous-stage mutations do not alter
canonical Context/Session storage or the next stage; no owner reference is installed.

## O-03 — Approved Exact Sequential Event Timeline

Select M-06/M-07's synchronous sequential execution semantics over M-05's conflicting
mandatory queue/DI/service-resolution timeline. Reserved request/created/validated/
queued/skipped/orchestrator-registration types are not emitted by this KR-009 API.
No queue, execution-object registry, public pipeline state machine, conditional stage,
retry policy or timeout is introduced; timeout remains future-only as M-05 specifies.
This is an explicit limited timeline reconciliation, not an inferred implementation default.

Keep existing registered string event types and M-05 priorities/payload meanings.
IDs are JSON strings at the event payload boundary, not raw UUID values or new aliases.

| Event | Priority | Exact payload keys |
| --- | --- | --- |
| pipeline.started | NORMAL | pipeline_id, session_id |
| pipeline.stage.started | NORMAL | pipeline_id, stage_id, module_id, duration_ms, reason |
| pipeline.stage.completed | NORMAL | pipeline_id, stage_id, module_id, duration_ms, reason |
| pipeline.stage.failed | HIGH | pipeline_id, stage_id, module_id, duration_ms, reason |
| pipeline.completed | NORMAL | pipeline_id, duration_ms, stage_count |
| pipeline.failed | HIGH | pipeline_id, failed_stage, reason, exception_type |
| pipeline.cancelled | HIGH | pipeline_id, reason |

Started stage duration/reason are None; completed duration is a finite nonnegative
float and reason None; failed duration is nonnegative and reason is a safe fixed
failure summary. Use standard-library monotonic elapsed time in milliseconds.
Pipeline failed_stage is the current stage_id or empty string when no stage entered.
Failure/cancellation reason strings and logs must not dump callback exception
messages, context metadata, payloads, credentials or other raw input values.
The original exception still propagates to its caller as ADR-004 requires.

Success: pipeline.started, then for each stage stage.started → awaited operation
→ stage.completed, then pipeline.completed. No completion for a callback that fails.
All event construction goes through create_for_runtime; no direct RuntimeEvent,
Publisher, Dispatcher or Subscriber import/construction.

Ordinary failure before a stage completion publication: best-effort stage.failed
if a stage was entered, followed by pipeline.failed. Abort all remaining stages;
do not emit fake completions or run later callbacks. If stage.completed delivery
fails after its logical terminal event was created, abort the remaining pipeline
and attempt pipeline.failed, NOT a contradictory second terminal stage.failed.

Cancellation before a terminal pipeline event: best-effort pipeline.cancelled,
no pipeline.failed/completed and no later callback. Do not label cancellation as
ordinary success/failure or add a new stage-cancelled type.

Exactly one logical terminal PIPELINE event attempt per execution. If publication
of pipeline.completed/failed/cancelled fails or is cancelled, propagate/preserve
that error according to O-04, but never construct another terminal pipeline event.
Already observed terminal events cannot be undone by emitting a contradictory one.
Pipeline/context/session ownership and future KR-010 scope cleanup do not move
into the event runtime or Executor.

## O-04 — Approved Primary Error, Cancellation and Busy Guards

Every stage awaits its registered operation once; a module used by multiple
stages invokes its same supplied operation once per stage. No success substitute,
implicit discovery, universal RuntimeContract.execute or hidden DI resolution.
A metadata-only module is registerable but not directly executable.

The primary operation/publication error is re-raised as the same exception object,
not wrapped in a generic success or new PipelineExecutionError. Secondary failure
notification errors are retained in an ordered ExceptionGroup/BaseExceptionGroup
cause, preserving any earlier explicit primary cause. Do not include the primary
itself inside its new cause group. Log only safe summaries/types, not exception
text or traceback payload dumps. Failed notification attempts do not mask the primary.

If the primary is asyncio.CancelledError, attempt the single allowed cancellation
notification and re-raise that cancellation. Secondary ordinary errors or cancellation
during notification do not replace the primary; no shield/background task is added.
KeyboardInterrupt/SystemExit are not converted into business failures. Execution
guards must be released in finally even on validation, callback, event or cancellation
failure; a later explicit execution can retry with valid registered inputs.

One execution per Orchestrator instance. Concurrent/re-entrant execute, registration,
unregistration or shutdown during its execution raises RuntimeStateError before
mutation. Read-only modules/contains/health remain available. Executor also prevents
concurrent/re-entrant direct execute/execute_stage on the same internal instance;
its own sequential stage traversal is not a second public acquisition.
Keep no mutable process-wide lock, global registry, background queue or new status.

## O-05 — Approved Minimal Atomic Bootstrap Migration Exception

The approved constructor migration cannot be made green as a KR-009-only source
change while Bootstrap still passes ExecutorRuntime. Treat the resulting KR-010
failure as NEW, not falsely as a pre-existing error. Do not hide it with an overload,
compatibility constructor, type-ignore, cast, duck-typing adapter or CI waiver.

Approve this exact, one-time explicit scope exception for the KR-009 task:

- Remove Bootstrap's import of src.kernel.runtime.executor.ExecutorRuntime.
- Change only build_orchestrator's construction expression to
  OrchestratorRuntime(event_bus), preserving that method's existing signature.
- No other Bootstrap behavior, file ownership, lifecycle order, runtime construction
  or KR-010 production/test file is changed in this task.

The file remains owned by KR-010; this is a narrow approved caller migration,
not permission to implement two modules or transfer ownership. AGENTS/Build Protocol
are otherwise unchanged. Bootstrap no longer imports an internal Executor; the
public Orchestrator constructs its own Executor with the SAME supplied EventBus.

Full RuntimeKernel.execute Pipeline-scope finally cleanup, session/DI composition
and Main partial-startup cleanup remain the subsequent KR-010 task already
authorized by ADR-004 P-05. KR-009 must not import Container or claim that deferred
integration acceptance is already implemented. Existing bootstrap/startup regression
tests must still pass; no outside failure is hidden or repaired.

## Approved Authorized Files

| File | Scope |
| --- | --- |
| src/kernel/runtime/pipeline.py | KR-009; unchanged schema, modify only if concretely needed |
| src/kernel/runtime/manifest.py | KR-009 validation |
| src/kernel/runtime/executor.py | KR-009 actual stage work/snapshots/events |
| src/kernel/runtime/orchestrator.py | KR-009 binding registry/preflight/guards |
| tests/kernel/test_pipeline.py | Canonical active KR-009 acceptance; KR-011 ownership |
| src/kernel/runtime/bootstrap.py | KR-010; ONLY O-05's import removal and constructor expression |

Architecture compilation may update ADR-007 approval, wave1/KR-009 contract and
only affected M-01/M-02/M-03/M-03A/M-04/M-05/M-06/M-07/M-08/M-09 KR-009 entries
and the directly affected Bootstrap composition edge. Unrelated clauses/modules,
Foundation/contracts/KR-007/KR-008, dependencies, workflows and security remain frozen.

## Required Acceptance

- Existing dataclass fields/properties/exports unchanged; every public KR-009 API tested.
- Same-object Manifest validation; malformed fields, empty/duplicate/missing/self/cyclic
  stages and deep DAGs; exact stable wavefront ordering, input tuples unchanged.
- Registered operations really execute and affect an explicit application-owned object.
  Metadata-only/missing module, invalid binding/context/ID/dependency/layer fail before
  any callback or event; forward references, repeated module stages, unregister behavior.
- Caller/result/context/stage nested JSON isolation, cycles/Unicode/nonfinite/depth
  256/257 handling, supplied IDs/trace/expiry preserved, expired context remains valid.
- Exact event sequence/schema/priority; no completion on failed work; stage/pipeline
  event-handler failures, secondary failures, terminal-delivery failure without double
  terminal events, cancellation and re-entry/concurrency/registry mutation.
- Busy guards restored after all failures/cancellation; separate instance ownership;
  shutdown removes manifests/bindings without introducing lifecycle states.
- Bootstrap uses the same EventBus through public Orchestrator, no internal Executor
  import; no new circular/upward import, duplicate JSON owner or event factory.
- Canonical tests/kernel/test_pipeline.py targets 100% executable-line coverage for
  all four owned production files, including properties of unchanged pipeline.py.
  No skips/xfail or executable-line exclusions; line coverage is not branch coverage.
- Ruff, strict Pyright Windows/Linux, full discovered Pytest, Kernel startup smoke
  and required latest-head hosted CI. Report and stop at this module's review gate.
- Do not certify KR-010 scope cleanup or the first usable Windows MVP as complete.

## Actual Preflight Evidence — 2026-10-06

On the unchanged source/test baseline:

| Check | Result |
| --- | --- |
| uv run ruff check . | PASS |
| uv run pyright | 0 errors, 0 warnings, 0 informations |
| uv run pyright --pythonplatform Linux | 0 errors, 0 warnings, 0 informations |
| uv run pytest -q | 873 passed |
| uv run pytest tests/kernel/test_pipeline.py -q | 2 passed, graph validation only |
| uv run python -m src.main | PASS, exit 0 |

A read-only in-memory probe confirmed:
- register_module(manifest, operation=...) raises TypeError.
- A metadata-only registered module executes without error while business effects
  remain zero; the existing executor does not invoke an operation.
- Existing wavefront order is A, C, B for input A, B(dep A), C.
- Orchestrator currently requires ExecutorRuntime, not EventBusRuntime.
- Executor currently is not a RuntimeContract and has no health method.

Green baseline regression does NOT demonstrate ADR-004's real work/error/snapshot
acceptance. No source/test edit, commit, push, PR or merge was made in the historical
preflight. The explicit approval recorded above now supplies O-01–O-05 authority;
this historical evidence is not acceptance of the forthcoming implementation.

## Next Authorized Action

Compile the approved exact KR-009 contract and affected Master entries, implement
only the authorized module plus O-05's caller migration, validate acceptance and
regression, publish under ADR-003, report and stop before full KR-010.
