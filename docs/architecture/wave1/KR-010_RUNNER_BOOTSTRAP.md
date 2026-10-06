# KR-010 — Runner / Bootstrap Contract v1.0

**Status:** APPROVED — compiled ADR-008 B-01–B-05.
**Authority:** Architecture Freeze v1.0; AB-00A/B/D; explicitly approved
ADR-004 P-05 and ADR-008. ADR-007 O-05's constructor migration is preserved.

## Purpose, Dependencies and Scope

Compose the completed Kernel through explicit existing owners, perform bounded
startup/shutdown, release Pipeline/Session DI and preserve first errors/cancellation.
Dependencies: Foundation KR-001, Configuration KR-002, Logging KR-003,
contracts KR-004 and the public KR-005–KR-009 collaborators. SessionRuntime
is the sole explicitly permitted internal composition exception (ADR-008 B-02).
No layer, owner, model, scope, event vocabulary or dependency package changes.

Authorized production:

- src/kernel/runtime/bootstrap.py
- src/kernel/runtime/runtime.py
- src/main.py

Authorized canonical acceptance (KR-011 ownership, ADR-004 permission):

- tests/kernel/test_bootstrap.py
- tests/integration/test_runtime_startup.py

Governance may reconcile only affected KR-010 Master entries under ADR-001/008.
Other production/tests/dependencies/workflows remain frozen.

## Exact Public Surface

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


class RuntimeKernel(RuntimeContract):
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
    def container(self) -> ContainerRuntime: ...
    @property
    def lifecycle(self) -> LifecycleRuntime: ...
    @property
    def event_bus(self) -> EventBusRuntime: ...
    @property
    def context(self) -> ContextRuntime: ...
    @property
    def orchestrator(self) -> OrchestratorRuntime: ...
    @property
    def session(self) -> SessionRuntime: ...
    @property
    def runtime_name(self) -> str: ...
    @property
    def runtime_layer(self) -> RuntimeLayer: ...
    @property
    def version(self) -> str: ...
    @property
    def architecture_version(self) -> str: ...
    async def initialize(self) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def shutdown(self) -> None: ...
    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None: ...
    async def remove_session(self, session_id: SessionId) -> None: ...
    def status(self) -> RuntimeStatus: ...
    def state(self) -> LifecycleState: ...
    def health(self) -> HealthStatus: ...
    def diagnostics(self) -> Metadata: ...


async def main() -> None: ...
```

Exports remain BootstrapRuntime and RuntimeKernel in their respective files;
main is the existing single entry function. Kernel name "kernel", L0_KERNEL,
version facts from core/version.py, existing ERROR > WARNING > OK aggregation.
References are read-only, diagnostics fresh; no universal execution on RuntimeContract.

## Construction and Ownership — B-01/B-02

Build validates configuration through KR-002's unchanged immutable cache,
uses existing get_logger/LoggingConfig with Settings.log_level, constructs Context,
its SessionRuntime(context) collaborator, Container, EventBus, Orchestrator(event_bus),
Lifecycle, Kernel. One new independent graph per build. Lifecycle registers Context,
Container, EventBus, Orchestrator; startup is forward and teardown reverse touched
order. No lifecycle initialization, service resolution/registration, context/trace
factory, event publication, directory creation or business operation in build.

ConfigurationError propagates unchanged; other ordinary construction failure
uses RuntimeInitializationError with the original cause and safe message.
Cancellation/SystemExit/KeyboardInterrupt propagate, no uninitialized participant
cleanup or cached Kernel. Existing Settings/Logging retain process ownership.

Bootstrap/Kernel may import SessionRuntime only to compose its existing public
API; never KR-008 internals or DI internals. Session/Context ownership is unchanged.
Kernel imports existing Foundation/version, RuntimeContext/LifecycleState,
RuntimeContract, PipelineDefinition and the allowed collaborators. Main imports
Bootstrap, Foundation vocabulary and optional existing Logger only, no internal
runtime or direct RuntimeKernel import.

## Admission, Cleanup and Errors — B-02/B-03/B-04

One Kernel-local guard spans initialize/start/stop/shutdown/execute/remove_session
and awaited cleanup. Busy/re-entrant mutation rejects before side effects; read-only
APIs remain available; always release in finally. Lower-level exposed references
retain their own contracts; bypassing Kernel cannot claim its composition guarantee.

execute requires RUNNING and a real PipelineDefinition with UUID-backed ID before
scope admission. Invalid definition/ID uses InvalidManifestError with no DI clear.
Every admitted valid ID is captured, then Orchestrator performs full validation/work;
Container.clear_pipeline(captured_id) runs in finally even on preflight/business/
event failure or cancellation. Never dispose an accepted contender's scope from
a rejected busy/state call. Session/Application context/services survive Pipeline
cleanup; no lifecycle-status change on business failure.

remove_session requires UUID-backed SessionId (ContractValidationError otherwise)
and existing Session.get (missing retains RuntimeStateError) before DI action.
Await Container.clear_session; after completed ordinary disposal attempt remove
the Session even on a disposal error. Cancellation/interruption retains Session/
active context for retry; Container owns pending disposal. Other sessions and
Application remain unaffected. Direct Session.remove stays registry-only.

stop/shutdown abort idle partial INITIALIZING/READY/STARTING only through the
existing legal Lifecycle.transition(FAILED), then cleanup. CREATED cannot invent
a transition; RUNNING shutdown requires stop. FAILED stays FAILED; completed
cleanup is idempotent. Busy Lifecycle rejects without interference. Full admitted
shutdown delegates Lifecycle then drains Session.list/remove synchronously in
finally, even after error/cancellation, without clearing a closed Container.
Remaining DI/lifecycle ownership survives there for an explicit retry.

First failure is re-raised as the SAME object. Later cleanup errors/cancellation
are ordered cause-group entries preserving any existing explicit cause as a
nested entry, never the primary itself or flattened old groups. Successful work
with cleanup-only failure propagates that failure unchanged. Primary cancellation
stays cancellation; SystemExit/KeyboardInterrupt are not converted. No shield/
background task/unbounded retry or new exception class. Only safe type/summary
logging, no exception strings/traceback metadata/credentials.

## Process Boundary — B-05

main builds once, initializes, starts and immediately finishes bounded Kernel
smoke through finally. No wait-for-signal/inputless execute/network server/business
pipeline/task/CLI flags. After a returned Kernel, stop and shutdown are independent
best-effort attempts selected by legal status; stop error cannot prevent shutdown.
Partial/FAILED paths use facade cleanup; no forced CREATED transition. First
startup/stop/cancellation error survives all cleanup under B-04. Build failure has
no returned Kernel. Success ends TERMINATED; earlier failure cannot become success.
Errors may terminate the process nonzero after cleanup; no fake success suppression.
Long-lived desktop-web hosting is another approved composition task, not this module.

## Precedence and Acceptance

ADR-008 explicitly resolves conflicting KR-010 order/builders, directory/error/
Bootstrap-event/root-context demands, Session import/API, admission/guard/error
semantics and wait/inputless execution/process exception prose. It does not change
another module or AB-00B's matrix. M-01–M-09 KR-010 entries point to this exact contract.

Canonical tests exercise ALL public APIs and B-01–B-05 acceptance listed in ADR-008:
real scoped resources/work, malformed admission, isolation, multi-disposal errors,
primary cause/cancellation, rejection spanning cleanup, partial startup, FAILED,
idempotency, interrupted retry and Main failure paths. Target 100% executable-line
coverage per three source files with no skips/xfail/exclusions; not branch coverage.
Run Ruff, scoped format check, strict Pyright Windows/Linux, full discovered Pytest,
Kernel smoke and latest-head required Windows/Linux CI. Report outside failures
without repairs. Publish normally under ADR-003, full module report and STOP at
the KR-010 review gate before KR-011; this is not a usable Windows MVP certification.
