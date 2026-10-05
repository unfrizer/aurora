# AURORA — Kernel Reconciliation Proposal v1.0

**Document ID:** ADR-004

**Status:** DRAFT — EXPLICIT ARCHITECTURE AUTHORITY APPROVAL REQUIRED

**Date:** 2026-10-05

**Task:** RCN-001 follow-up; documentation only

**Repository baseline:** `d72120536643725d10ffd51c298cb4ed2847d061`

**Implementation authority:** NONE while DRAFT

## Purpose and Dependencies

Propose one concrete resolution of K-01–K-05 instead of asking the project owner
to write technical contracts. This is a proposed implementation contract, not an
approved change to the current system. A routine GitHub approval/merge under
ADR-003 does not approve the decisions below.

Inputs: AGENTS.md; ADR-001/003; AB-00B/C/D; RCN-001; relevant M-04 DI/pipeline/
bootstrap boundaries, M-05 lifetime ownership and M-06 DI/pipeline specifications;
current Kernel source and tests. No production source or test is changed by this
document. The proposal deliberately identifies superseded APIs and limitations.

### Кратко для Architecture Authority

Предлагается утвердить пять связанных решений:

1. DI возвращает сервис только после `await initialize()`; зависимости
   конструктора задаются явно, без поиска по имени или скрытого реестра типов.
2. Удаление сервисов асинхронное: экземпляры больше нельзя получить из кэша,
   освобождение ресурсов обязательно, старый экземпляр не переживает повторную
   регистрацию того же ID.
3. Pipeline действительно вызывает зарегистрированную async-операцию, а не
   только публикует события. Универсальный RuntimeContract не расширяется.
4. Публичные context/event JSON-данные изолируются копированием на границах;
   идентичность context-снимков больше не гарантируется.
5. Cleanup пытается освободить всех затронутых участников, не превращая
   terminal FAILED в STOPPED или TERMINATED.

Это изменения публичного поведения, поэтому Codex не переводит этот документ
в APPROVED автоматически. Для утверждения достаточно явно указать ADR-004 v1.0;
пользователю не требуется создавать файлы или самостоятельно писать код.

## Frozen Invariants

- No new Runtime, layer, directory, package dependency, DI scope or vocabulary
  member.
- Foundation, contracts and KR-005–010 keep their existing owners and paths.
- RuntimeStatus and every legal transition remain exactly AB-00B.
- RuntimeContract remains exactly AB-00D: identity, async lifecycle, sync health;
  no universal execute, runtime_id, status, state or diagnostics method.
- PublisherRuntime remains the sole creator of new logical RuntimeEvents.
- Pipeline execution remains sequential and deterministically topological.
- No Kernel import of application code or a higher runtime layer; no globals,
  background workers, network, filesystem I/O or provider integrations.
- Python 3.13, uv and strict typing; no new Any/Unknown in public contracts.

## P-01 — Async DI and Explicit Constructor Dependencies

### Public acquisition API

Proposed ContainerRuntime methods:

```python
async def resolve(
    self, service_id: ServiceId, *, context: RuntimeContext | None = None
) -> ServiceContract: ...

async def remove(self, service_id: ServiceId) -> None: ...

async def release(self, service: ServiceContract) -> None: ...

async def clear_session(self, session_id: SessionId) -> None: ...

async def clear_pipeline(self, pipeline_id: PipelineId) -> None: ...
```

Register, contains and descriptors remain synchronous with their existing
signatures. ContainerRuntime's RuntimeContract lifecycle surface is unchanged.
There is no synchronous resolution shim, asyncio.run bridge or implicit task.

ResolverRuntime.resolve and ProviderRuntime.provide become asynchronous.
Resolver validates/resolves the dependency graph; Provider constructs the
implementation with resolved keyword arguments and awaits initialize exactly
once per successfully constructed instance before that instance is published
to a scope cache or returned. Provider.dispose remains async and calls shutdown.

Proposed internal signatures (not new external facades):

```python
class ResolverRuntime:
    async def resolve(
        self, descriptor: ServiceDescriptor, *, context: RuntimeContext | None
    ) -> ServiceContract: ...

class ProviderRuntime:
    async def provide(
        self,
        descriptor: ServiceDescriptor,
        *,
        context: RuntimeContext | None,
        dependencies: Mapping[str, ServiceContract],
    ) -> ServiceContract: ...
```

Resolver receives the existing RegistryRuntime, ProviderRuntime and typed
ScopeRuntime through construction; it does not acquire a second descriptor store.

### Descriptor extension — KR-004 owns the contract

The four existing ServiceDescriptor fields keep their names and types. Add only:

```python
dependencies: tuple[tuple[str, ServiceId], ...] = ()
```

Each pair explicitly binds a constructor keyword parameter to a registered
ServiceId. It is an immutable tuple, not a mutable dictionary or inferred type
registry. Implementation remains type[ServiceContract]. ServiceContract retains
async initialize and async shutdown; no universal service execute is added.

Rules:

- A bound name must be a unique, non-empty keyword-addressable constructor
  parameter. Binding one parameter twice is invalid. Two parameters may refer
  to the same service ID; cached resolution reuses the scoped instance.
- Positional-only required parameters, variadic injection, unknown parameter
  names and missing required bindings are rejected before construction.
- Unbound parameters may use declared defaults. No settings/configuration
  object, primitive value, context or Container is implicitly injected.
- Registration checks descriptor/constructor shape and duplicates. Forward
  references between descriptors are permitted; the complete reachable graph
  is validated before initialize or any resolution constructs a service.
- Missing IDs, dependency cycles and inadmissible scope edges fail before any
  constructor in that acquisition runs. No annotation expression is evaluated
  to guess a ServiceId.
- Eager descriptors are allowed only for APPLICATION. initialize prepares them
  once in dependency order. Calling container.initialize again is a no-op after
  successful initialization; it never reinitializes cached instances.
- A failure removes unpublished/newly prepared acquisition instances and tries
  to dispose them in reverse construction order. Previously ready shared
  instances remain owned by their original scopes. A later explicit resolve
  may retry; it never retrieves a partially initialized instance.

### Allowed dependency scopes

This conservative rule rejects captive shorter-lifetime dependencies:

| Consumer scope | Allowed dependency scopes |
| --- | --- |
| APPLICATION | APPLICATION |
| SESSION | APPLICATION, same SESSION |
| PIPELINE | APPLICATION, same SESSION, same PIPELINE |
| TRANSIENT | APPLICATION, SESSION, PIPELINE, TRANSIENT, with required context |

SESSION/PIPELINE acquisitions require the canonical RuntimeContext and matching
IDs. A PipelineId cannot be associated with two SessionIds in one container.
Transient dependencies are never injected into cached services in this version.

ScopeRuntime owns cached APPLICATION/SESSION/PIPELINE lifetimes. ResolverRuntime
retains the TRANSIENT ownership specified by M-04/M-05. Transient instances are
tracked for disposal, never reused as a cache; context-bound transients are
released when their pipeline/session is cleared. Context-free transients last
until explicit release or container shutdown. release rejects unknown or cached
instances with ScopeViolationError; a previously released transient is a no-op.

When a transient depends on another transient, dependency teardown is reverse
construction order and does not dispose an independently acquired instance.

### Execution model

DI operations are sequentially awaited by the caller. Concurrent/re-entrant
mutating acquisition/removal/cleanup is rejected with RuntimeStateError rather
than racing, deadlocking or creating duplicate instances. Internal recursive
dependency traversal is part of the one acquisition, not a second public call.
No background task or cross-thread access is added.

After container shutdown, resolve/register/remove fail with RuntimeStateError.
Read-only contains/descriptors remain available; repeated shutdown is a no-op
after resource-disposal attempts have completed.

Error mapping uses only the existing Foundation exceptions: invalid registration/
bindings use ServiceRegistrationError; missing services and constructor/initialize
failures use ServiceResolutionError; cycles use CircularDependencyError; scope
violations use ScopeViolationError; lifecycle/re-entrancy violations use
RuntimeStateError. Original constructor/initialize errors remain chained, with
ordered cleanup failures grouped as in P-05. CancelledError is re-raised after
rollback, not wrapped as a successful resolution.

## P-02 — Removal, Scope Disposal and Failure Ordering

ContainerRuntime.remove is proposed to follow this exact order:

1. Reject missing IDs with ServiceResolutionError.
2. Reject removal when another registered descriptor depends on this ID with
   ServiceRegistrationError. Remove consumers first; no silent cascade is added.
3. Unregister the descriptor and detach every owned instance of that ID from
   Application/Session/Pipeline caches and Resolver's transient ownership lists.
4. Attempt shutdown on all detached instances in reverse construction order.
5. Raise RuntimeShutdownError if disposal failed, preserving the individual
   failures in an ExceptionGroup cause. Descriptor/instance eviction remains
   effective even when shutdown raises; re-registration never sees old caches.

Every scope clear detaches its references before disposal and continues after
ordinary disposal errors. Clearing a session also clears pipelines associated
with that session. Empty/already-cleared scopes are a no-op. Container shutdown
clears pipelines, sessions, then Application; dependents are released before
their dependencies, and transient ownership is included.

M-04's existing prohibition on ScopeRuntime importing ProviderRuntime is retained.
Scope storage is parameterized internally with a type parameter and receives a
typed async disposal callback; it does not import or instantiate ProviderRuntime,
ServiceDescriptor or RegistryRuntime. Container/Resolver translate context and
descriptor information into the existing Foundation IDs/scopes.

The proposed internal ScopeRuntime API uses ServiceId plus explicit DIScope,
SessionId/PipelineId keys, rather than a descriptor or RuntimeContext:

```python
class ScopeRuntime[T]:
    def __init__(self, *, dispose: Callable[[T], Awaitable[None]]) -> None: ...

    def get(
        self, service_id: ServiceId, *, scope: DIScope,
        session_id: SessionId | None = None, pipeline_id: PipelineId | None = None,
    ) -> T | None: ...

    def put(
        self, service_id: ServiceId, service: T, *, scope: DIScope,
        session_id: SessionId | None = None, pipeline_id: PipelineId | None = None,
    ) -> None: ...

    async def remove(
        self, service_id: ServiceId, *, scope: DIScope,
        session_id: SessionId | None = None, pipeline_id: PipelineId | None = None,
    ) -> None: ...

    async def remove_all(self, service_id: ServiceId) -> None: ...
    async def clear_session(self, session_id: SessionId) -> None: ...
    async def clear_pipeline(self, pipeline_id: PipelineId) -> None: ...
    async def clear_application(self) -> None: ...
    async def shutdown(self) -> None: ...
```

This supersedes the conflicting M-06 scope signatures but does not move cache
ownership. Provider still owns service initialize/shutdown hook execution;
Scope coordinates cached lifetime, Resolver coordinates transients. These typed
internals are not an externally supported generic cache abstraction. No outside
runtime may construct/access them. TRANSIENT get/put is rejected; Resolver owns
that scope, with no reusable cache.

## P-03 — Real Pipeline Work Without a Universal execute Method

Keep PipelineStage and PipelineDefinition fields unchanged. Do not put callables
inside serializable DAG definitions, extend RuntimeModuleManifest, or make Kernel
discover a business implementation from a module name.

Proposed OrchestratorRuntime registration API:

```python
def register_module(
    self,
    manifest: RuntimeModuleManifest,
    *,
    operation: Callable[[RuntimeContext], Awaitable[None]] | None = None,
) -> None: ...
```

The optional operation is explicitly provided by composition/application code.
One registered ModuleId has at most one operation; each stage referring to that
module invokes it once. Different operations use different registered module IDs.
Metadata-only registration remains possible, but such a module cannot execute.
Unregister removes both manifest and operation. No independent global binding
registry, plugin discovery, or new Runtime is introduced.

Before publishing pipeline.started, Orchestrator validates the DAG, context/
pipeline-ID agreement, every stage's registered module and every operation.
Missing/metadata-only modules raise InvalidManifestError. No start/completion
success event is emitted for a pipeline that fails this preflight.

Executor receives a detached operation-binding snapshot from Orchestrator for
one execution. For each topologically ordered stage it publishes stage.started,
awaits operation with a detached context snapshot, then publishes stage.completed
only on success. Payload edits in a callback do not implicitly update canonical
context/state. Business results are owned by explicitly supplied application
objects; Kernel execute keeps its None return contract.

Proposed internal Executor signatures:

```python
class ExecutorRuntime:
    async def execute(
        self, pipeline: PipelineDefinition, *, context: RuntimeContext,
        operations: Mapping[ModuleId, Callable[[RuntimeContext], Awaitable[None]]],
    ) -> None: ...

    async def execute_stage(
        self, stage: PipelineStage, *, context: RuntimeContext,
        operation: Callable[[RuntimeContext], Awaitable[None]],
    ) -> None: ...
```

The operations argument is a per-execution snapshot, not a registry owned by
Executor. Existing Orchestrator/RuntimeKernel execute signatures remain unchanged.

First failure aborts all remaining stages. Failure publication is best effort;
a secondary event-handler failure must not mask the original stage failure.
The original exception is re-raised; secondary failures are chained/grouped and
logged without including context payloads/secrets. Event types, event fields,
priority ordering and the Publisher creation boundary remain unchanged.

Concurrent/re-entrant execution or module-registry mutation during execution is
rejected with RuntimeStateError. One in-memory pipeline executes at a time.
Orchestrator shutdown clears bindings and manifests; no successful no-op stage
is substituted for missing work.

### Composition/import discrepancy that must be explicitly reconciled

Current Bootstrap imports/constructs ExecutorRuntime. M-04 forbids Bootstrap
imports of internal executors, while the existing M-06/bootstrap implementation
does so. The proposed repair is:

```python
class OrchestratorRuntime:
    def __init__(self, event_bus: EventBusRuntime) -> None: ...
```

Orchestrator constructs its internal Executor. Bootstrap constructs/wires only
the public Orchestrator facade with the existing EventBus facade; it no longer
imports ExecutorRuntime. No second EventBus is created.

This requires a narrow M-04 clarification permitting Orchestrator's EventBus
reference for construction/type annotation only. Runtime event interaction stays
in Executor through the EventBus facade. It adds no upward layer edge and follows
the existing Orchestrator-to-Executor-to-EventBus dependency direction, but it is
not silently deemed approved by this DRAFT. Architecture Authority must confirm
this clarification is compatible with the frozen baseline; otherwise P-03 stays
blocked and must be revised, not implemented through a hidden factory/import.

## P-04 — Detached Value Snapshots, Not Deeply Frozen JSON Types

Keep JSONPrimitive/JSONValue/JSONDict/Metadata/Payload aliases unchanged. Keep
the seven RuntimeContext fields, RuntimeEvent fields and frozen dataclass shells.
Do not add MappingProxyType, frozen JSON classes, fields or mutable globals.

Proposed public guarantee: **detached value snapshots**. Nested JSON dictionaries
and lists in a received snapshot can be edited locally, but those edits never
mutate active context/session storage, the publisher's captured event or another
handler's input. This explicitly replaces the ambiguous deep-immutability reading
of AB-00D/M-05/M-06 for JSON leaves; it is not a claim that dict/list become frozen.

- Metadata merge/put/remove return recursively detached data, preserving shallow
  key-update semantics (not a recursive merge). get also detaches a returned
  container or default; contains is read-only.
- Context create/replace validate and store a detached snapshot. create/current/
  replace return separately detached snapshots. Equality/field values are the
  guarantee; object identity is not. replace no longer stores/returns the exact
  supplied object. This expressly supersedes AB-00D Resolution-003 identity
  wording and the current identity assertion in test_context.
- Session creation/get/update keep and return detached snapshots; failed
  validation leaves existing session and active-context state unchanged.
- Publisher.create recursively copies input payload. Publication captures data
  before the first handler runs; each handler receives its own detached snapshot.
  A handler cannot change data observed by another handler or the caller.
- Event snapshot copying preserves event_id, timestamp, trace and priority;
  it creates no new logical event. Standard-library copying of an existing event
  is permitted inside dispatch and is not another event factory. Direct new
  RuntimeEvent construction remains exclusive to PublisherRuntime in production.

Boundary validation rejects non-string object keys, non-finite floats, invalid
Unicode, cycles and non-JSON objects without coercion. Maximum nesting is 256
dict/list levels (root container counts as one); excessive depth is a validation
failure, not RecursionError. Repeated non-cyclic references are accepted and
detached; exception messages must not dump user payloads.

Metadata/context/session invalid data raises existing ContractValidationError;
missing active context/session retains RuntimeStateError. Event data validation
uses existing EventValidationError. No new exception class or core vocabulary is
introduced. Direct contract dataclass construction does not become a hidden
runtime validator; owning runtime boundaries perform these checks.

## P-05 — Best-Effort Cleanup, Terminal FAILED Preserved

Lifecycle tracks participants whose initialize/start were attempted separately
from lifecycle state. StateRuntime remains the only status owner. Track an
attempt before invoking the participant so partially initialized resources can
be cleaned up; a participant's cleanup must tolerate its own partial startup.

- Initialization failure sets FAILED via its existing legal transition, then
  attempts shutdown of every touched participant in reverse order.
- Start failure sets FAILED, then attempts stop of start-touched participants
  and shutdown of initialize-touched participants in reverse order.
- Normal stop/shutdown attempts every eligible participant despite ordinary
  hook/participant errors, releases references, then reports failures. Normal
  successful transitions remain AB-00B; any operation failure keeps FAILED.
- Existing stop/shutdown methods can be called in FAILED as resource-cleanup
  operations without any status transition. They never transition FAILED to
  STOPPED, SHUTTING_DOWN or TERMINATED. Repeated completed cleanup is a no-op.
- No public recover/reset method, additional hook or new RuntimeStatus is added.
  initialize/start in FAILED still reject with RuntimeStateError.
- BEFORE/AFTER_STOP hooks are attempted once around stop cleanup; an ordinary
  hook error cannot skip participant cleanup. Hook references are cleared after
  final shutdown attempts, including failures. No new shutdown-hook vocabulary.

RuntimeInitializationError retains the operation failure as its cause. If cleanup
also fails, an ExceptionGroup cause records the original error first, then cleanup
errors in attempt order. Shutdown-only failures use RuntimeShutdownError with
the same ordered error-group mechanism. Successful cleanup attempts are never
reported as a successful lifecycle after an earlier failure.

Cancellation is not converted into success or an ordinary RuntimeError. On
asyncio.CancelledError, transition to FAILED when legally possible, attempt the
same cleanup, then re-raise cancellation. Repeated external cancellation can
interrupt cleanup; remaining ownership must stay tracked for a later explicit
shutdown. No shielded background task is created, and completed disposal is not
repeated. Ordinary cleanup errors are preserved/logged without secrets.

Container cleanup from P-02 follows the same best-effort/idempotent rules.
RuntimeKernel.execute releases Pipeline-scoped resources in finally through the
Container facade; cleanup errors cannot hide the original execution error.
Session-removal composition clears Session-scoped DI through the Container facade;
SessionRuntime does not import ContainerRuntime. Main always attempts cleanup
through the facade after partial startup; it does not force illegal transitions.

## Proposed Precedence and Migration — Effective Only After Approval

| Subject | Explicit declarations to reconcile |
| --- | --- |
| Async DI | M-03/M-06 synchronous Container.resolve/remove, Resolver.resolve and Provider.provide; affected call sites must await. |
| Constructor mapping | M-03/M-06 four-field ServiceDescriptor gains dependencies; existing zero-argument descriptors keep the default empty tuple. |
| Scope removal | M-06 descriptor/context-based Scope API examples become ID/scope-key-based typed internals; cached/transient ownership stays M-04/M-05. |
| Pipeline work | M-03/M-06 module registration gains operation; execution rejects missing bindings rather than pretending completion. |
| Pipeline composition | M-04 Bootstrap executor prohibition is enforced; its Orchestrator import wording needs the narrow P-03 clarification. |
| Snapshot guarantee | AB-00D Resolution-003 identity semantics and M-05/M-06 deep-immutability prose for mutable JSON become P-04 detached value semantics. |
| Failure cleanup | M-06 first-error cleanup and obsolete FAILED-to-STOPPED examples yield to P-05; AB-00B's transition matrix is unchanged. |

No other AB-00B/C/D resolution is superseded. No core identifier/model policy,
configuration cache, logging implementation, higher Wave or MVP adapter is
redesigned. Defaults cannot be used to auto-approve these breaking semantics.

## Proposed Module/File Ownership and Build Order

After explicit approval, reconcile the affected API/import/test registries and
compile exact module contracts before any corresponding code change. Preserve
one module per implementation task/branch and its report/review gate.

| Order | Module | Production scope | Required canonical tests |
| --- | --- | --- | --- |
| 1 | KR-004 | contracts/service.py; contract docstrings in contracts/context.py and contracts/events.py; exports only if needed | tests/kernel/test_contracts.py |
| 2 | KR-005 | runtime/container.py, registry.py, resolver.py, provider.py, scope.py | tests/kernel/test_container.py |
| 3 | KR-006 | runtime/lifecycle.py, state.py only if needed, hooks.py | tests/kernel/test_lifecycle.py |
| 4 | KR-007 | runtime/bus.py, publisher.py, dispatcher.py, subscriber.py only if needed | tests/kernel/test_event_bus.py |
| 5 | KR-008 | runtime/context.py, metadata.py, session.py | tests/kernel/test_context.py |
| 6 | KR-009 | runtime/pipeline.py only if needed; manifest.py, executor.py, orchestrator.py | tests/kernel/test_pipeline.py |
| 7 | KR-010 | runtime/bootstrap.py, runtime/runtime.py, src/main.py | tests/kernel/test_bootstrap.py; tests/integration/test_runtime_startup.py |
| 8 | KR-011 | Canonical Wave 1 test suite and integration acceptance only | Full Wave 1 suite; existing Wave 2–9/product regression suite |

All production paths above are below src/kernel/ except the existing src/main.py.
Tests remain owned by KR-011. Approval must explicitly allow contract-required
canonical test adjustments with each active module, as the Build Protocol permits;
no unrelated production module may be repaired as part of one module task.

### Required acceptance evidence

- DI: lazy/eager initialization once, explicit keyword injection, forward
  references, missing IDs, cycles, scope matrix, rollback, transient release,
  re-entrancy rejection and no partially initialized cache entries.
- Removal: all active scopes, consumer-removal guard, same-ID re-registration,
  multiple disposal failures, cleared references and reverse dependency order.
- Pipeline: actual observable business callback, topological order, binding
  preflight, callback failure abort, cancellation, failing event handlers,
  original failure preservation and Pipeline scope release in finally.
- Snapshots: nested ingress/egress mutation, sibling handler isolation, session
  updates, value equality without identity assumptions, cyclic/invalid/deep JSON,
  preserved schemas and unchanged event priority/FIFO behavior.
- Lifecycle: partial initialize/start failures, multiple teardown/hook errors,
  terminal FAILED retained, retry cleanup after cancellation, idempotent cleanup
  and all 100 source/target transition pairs unchanged.
- M-04: no Scope-to-Provider import; no Bootstrap-to-Executor import; no upward
  L0–L8 imports or cycles; any approved P-03 clarification is recorded explicitly.
- Ruff, strict Pyright (Windows/Linux modes), discovered Pytest tests, Kernel
  smoke and latest-head required Windows/Linux CI all pass without skips/xfail
  that hide required acceptance behavior or paid/live credential requests.

The existing 337 passing tests are a regression baseline, not evidence that these
new acceptance conditions pass. This DRAFT is not a claim of a usable Windows MVP.

### Documentation-task validation — 2026-10-05

Only this DRAFT and the RCN-001 follow-up link/status were edited. Pyright reported
zero errors; Ruff passed; Pytest discovered and passed 337 tests on Python 3.13.15
Windows. All seven Python signature blocks parse successfully; this is syntax
validation, not implementation/type checking of those proposed signatures.
No new acceptance test or production implementation is claimed by these results.

## Alternatives and Approval Gate

Rejected recommendations: blocking sync DI on an event loop; guessing constructor
IDs from annotations/names; silent cached-instance leaks; universal execute;
fake successful pipeline work; introducing frozen JSON types without an approved
new model; FAILED-to-STOPPED recovery; disposal stopping at the first error.

The Authority may approve ADR-004 v1.0 as a whole, request named changes, or defer
one decision. Partial approval must identify P-01–P-05 and the P-03 M-04
clarification explicitly; dependent implementation stays blocked until its
required decisions and exact module contracts are approved.

Until then: no source/test change, no registry supersession, and no automatic
APPROVED stamp. Codex may save/publish this DRAFT for review under ADR-001/003;
that workflow action must never be represented as architecture acceptance.
