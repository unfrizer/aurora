# KR-005 — Dependency Injection Contract v1.0

**Status:** APPROVED — ADR-004 P-01/P-02 and DI cleanup requirements of P-05.

**Authority:** Architecture Freeze v1.0, AB-00A/B/D, ADR-001 and explicitly
approved ADR-004. Tech Lead accepted KR-004 and authorized the next module with
“утверждаю, дальше”. This compiles that authority, not a new architecture decision.

## Purpose, Dependencies and Scope

Deterministic asynchronous DI: explicit constructor injection, ready instances,
exclusive scope ownership and best-effort cleanup. Dependencies: Foundation
KR-001 and approved KR-004 ServiceContract/ServiceDescriptor/RuntimeContext.

Production files (existing, KR-005-owned):

- `src/kernel/runtime/container.py`
- `src/kernel/runtime/registry.py`
- `src/kernel/runtime/resolver.py`
- `src/kernel/runtime/provider.py`
- `src/kernel/runtime/scope.py`

Only `tests/kernel/test_container.py` may be adjusted for this module under
ADR-004's explicit canonical test permission; its architectural owner remains
KR-011. No other source/test/configuration/dependency file may change. Governance
registry reconciliation under ADR-001 is permitted. No new production file.

## Exact Public Facade — ContainerRuntime

Retain RuntimeContract's runtime_name/runtime_layer, async initialize/start/stop/
shutdown and sync health; retain existing names/layer/health vocabulary. No new
public properties exposing the registry, resolver, provider or scope.

```python
def __init__(self) -> None: ...
def register(self, descriptor: ServiceDescriptor) -> None: ...
def contains(self, service_id: ServiceId) -> bool: ...
def descriptors(self) -> tuple[ServiceDescriptor, ...]: ...
async def resolve(
    self, service_id: ServiceId, *, context: RuntimeContext | None = None
) -> ServiceContract: ...
async def remove(self, service_id: ServiceId) -> None: ...
async def release(self, service: ServiceContract) -> None: ...
async def clear_session(self, session_id: SessionId) -> None: ...
async def clear_pipeline(self, pipeline_id: PipelineId) -> None: ...
```

These exact approved names supersede old M-01/M-03 unregister/has/property examples.
No synchronous shim, event-loop bridge, background task or inferred injection.
Only ContainerRuntime is an external DI API. Read-only contains/descriptors remain
available during cleanup and after shutdown. Mutating operations are sequential;
concurrent/re-entrant calls fail with RuntimeStateError, never wait on a lock.
resolve/register/remove fail after shutdown begins. Repeated completed initialize
and shutdown are no-ops. Interrupted cleanup retains ownership for explicit retry.

## RegistryRuntime — Descriptor Ownership

Keep sync register(descriptor), unregister(service_id), get(service_id),
contains(service_id), list() -> tuple[ServiceDescriptor, ...]. Descriptor storage
is private. Duplicate/shape errors use ServiceRegistrationError; missing IDs use
ServiceResolutionError. Forward references are allowed at registration.

## ResolverRuntime — Graph and Transient Ownership

Construct with existing RegistryRuntime, ProviderRuntime and
ScopeRuntime[ServiceContract], not a second registry or instance cache.

```python
async def resolve(
    self, descriptor: ServiceDescriptor, *, context: RuntimeContext | None
) -> ServiceContract: ...
def validate(self, descriptor: ServiceDescriptor) -> None: ...
```

validate checks registration/constructor shape without rejecting forward IDs.
Resolution validates the entire reachable graph before any constructor:
missing IDs, cycles, constructor bindings and the ADR-004 scope matrix. Eager
initialization validates the complete registered graph before constructing its
APPLICATION-only eager roots. Traversal and construction order are deterministic;
annotation expressions are never evaluated. Private iterative traversal/build
helpers are permitted; no resolver dependency graph API is added.

Each binding is a unique non-empty keyword-addressable constructor parameter.
Reject unknown names, duplicate parameters, variadic injection, required
positional-only arguments and missing required bindings; permit unbound declared
defaults. Distinct parameters may bind the same ID; cached dependencies reuse the
ready instance, transient dependencies are separate resolutions.

APPLICATION may depend only on APPLICATION; SESSION on APPLICATION/same SESSION;
PIPELINE on APPLICATION/same SESSION/same PIPELINE; TRANSIENT on any scope with
required context. Reject captive shorter-lifetime dependencies. Context uses
canonical UUID-backed IDs. A PipelineId cannot bind to two SessionIds within the
container. No primitives, settings, contexts or Container are implicitly injected.

An acquisition uses private temporary working records, not a reusable resolver
cache. Newly constructed services are tracked before initialize is awaited and
only committed to ScopeRuntime or transient ownership after the acquisition
succeeds. Failed acquisitions roll back new instances in reverse order; previously
ready shared instances survive. Ordinary construction/initialize errors retain
their original cause. Cancellation is re-raised after cleanup attempts. If a
second cancellation interrupts disposal, remaining private records survive for
later cleanup; successful disposal is not repeated.

TRANSIENT instances are owned only by ResolverRuntime, never cached for reuse.
release tears down the selected instance's owned transient descendants in reverse
construction order, not separately acquired instances or cached dependencies.
Context-bound transients are included in matching pipeline/session cleanup.
Unknown/cached release raises ScopeViolationError; a released transient is a no-op.
Weak identity tombstones may recognize a released instance without retaining it.

## ProviderRuntime — Construction and Hook Execution

```python
async def provide(
    self,
    descriptor: ServiceDescriptor,
    *,
    context: RuntimeContext | None,
    dependencies: Mapping[str, ServiceContract],
) -> ServiceContract: ...
async def dispose(self, service: ServiceContract) -> None: ...
```

Construct from explicitly resolved keyword arguments; await initialize once before
return. dispose awaits shutdown. No descriptor registry or stored service instance.
As a private composition detail, a typed construction-notification callback may
notify Resolver's current acquisition immediately after successful construction
and before awaiting initialize. This supplies the already-required partial-start
ownership/rollback guarantee, does not expose a new facade API and does not give
Provider ownership of the instance. Provider still imports Foundation/Contracts
only; the callback introduces no reverse runtime import or additional Runtime.

## ScopeRuntime[T] — Cached Lifetime Ownership

Scope stores APPLICATION/SESSION/PIPELINE only. Its generic disposal callback is
Callable[[T], Awaitable[None]]. No ProviderRuntime, ServiceDescriptor, RegistryRuntime
or RuntimeContext import. Cache keys use ServiceId, DIScope, SessionId/PipelineId.
Typed private storage may namespace these keys in one ordered mapping; no external
generic cache abstraction is introduced. TRANSIENT get/put is rejected.

```python
def __init__(self, *, dispose: Callable[[T], Awaitable[None]]) -> None: ...
def get(
    self,
    service_id: ServiceId,
    *,
    scope: DIScope,
    session_id: SessionId | None = None,
    pipeline_id: PipelineId | None = None,
) -> T | None: ...
def put(
    self,
    service_id: ServiceId,
    service: T,
    *,
    scope: DIScope,
    session_id: SessionId | None = None,
    pipeline_id: PipelineId | None = None,
) -> None: ...
async def remove(
    self,
    service_id: ServiceId,
    *,
    scope: DIScope,
    session_id: SessionId | None = None,
    pipeline_id: PipelineId | None = None,
) -> None: ...
async def remove_all(self, service_id: ServiceId) -> None: ...
async def clear_session(self, session_id: SessionId) -> None: ...
async def clear_pipeline(self, pipeline_id: PipelineId) -> None: ...
async def clear_application(self) -> None: ...
async def shutdown(self) -> None: ...
```

Detach selected cache references before invoking any disposal callback. Session
clear includes its pipelines; shutdown clears pipelines, sessions, then Application.
Attempt every eligible disposal despite ordinary errors; interrupted callbacks
retain pending ownership. Empty scopes are a no-op. Never overwrite a live cache
entry or reuse an instance detached by remove/clear, including disposal failures.

## Removal, Failure Reporting and Frozen Boundaries

Reject missing removal with ServiceResolutionError; reject a registered consumer
of the target with ServiceRegistrationError. Unregister and evict before disposal;
attempt all detached instances in reverse construction order. Disposal failures
raise RuntimeShutdownError with ordered ExceptionGroup cause, preserving effective
eviction and same-ID re-registration. Cleanup cannot mask an acquisition failure;
its cause group records the original operation error first, then cleanup failures.
CancelledError is never wrapped as success; interrupted teardown is resumable.

Use only existing Foundation exceptions from ADR-004. No new Runtime/layer/scope/
status/event vocabulary, globals, network, filesystem, settings/logging redesign,
business logic, public contract change outside the approved ADR or higher imports.
ServiceContract/ServiceDescriptor remain untouched by KR-005. No lifecycle status
transitions are performed here; cleanup-only bookkeeping is private DI state.

## Validation and Acceptance

Canonical tests cover lazy/eager initialize-once, async injection, forward refs,
missing IDs, cycles, all 16 scope edges, scoped identities, preflight-before-side-
effects, defaults/constructor shape, rollback/retry, cancellation and interrupted
cleanup, transient descendants, scope/remove eviction, consumer guards, same-ID
re-registration, multiple disposal errors, reverse dependency order, idempotency,
re-entrancy/concurrency rejection, and unchanged external module regressions.

Run uv run pyright, uv run ruff check ., uv run pytest, scoped format check and
Kernel startup smoke. No skips/xfail/empty collection. Hosted latest-commit Linux
and Windows checks must pass before ordinary merge under ADR-003. Report unrelated
formatting failures separately; no repairs outside this module. Stop after one
module report for Tech Lead review.
