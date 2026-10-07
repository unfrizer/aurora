"""Canonical KR-010 integration: scoped DI disposal, cancellation and Main finalization."""

from __future__ import annotations

import asyncio
import importlib
import logging
import runpy
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import cast
from uuid import uuid4

import pytest

import src.main as entry
from src.core.exceptions import (
    EventHandlerError,
    InvalidManifestError,
    RuntimeInitializationError,
    RuntimeShutdownError,
    RuntimeStateError,
)
from src.core.logger import get_logger
from src.core.settings import Settings
from src.core.types import (
    DIScope,
    HealthStatus,
    ModuleId,
    RuntimeLayer,
    RuntimeStatus,
    ServiceId,
    SessionId,
    TraceId,
)
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.bootstrap import BootstrapRuntime
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
from src.kernel.runtime.pipeline import PipelineDefinition, PipelineStage
from src.kernel.runtime.runtime import RuntimeKernel


class Service(ServiceContract):
    def __init__(self) -> None:
        self.initializations = 0
        self.shutdowns = 0

    async def initialize(self) -> None:
        self.initializations += 1

    async def shutdown(self) -> None:
        self.shutdowns += 1


class Collector(EventHandlerContract):
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    async def handle(self, event: RuntimeEvent) -> None:
        self.events.append(event)


class DeliveryFailure(EventHandlerContract):
    async def handle(self, event: RuntimeEvent) -> None:
        raise ValueError("handler secret")


class LogCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


@pytest.mark.parametrize("round_number", range(4))
async def test_shared_fixtures_are_fresh_and_execute_real_bound_work(
    settings: Settings,
    trace_context: TraceContext,
    runtime_context: RuntimeContext,
    container: ContainerRuntime,
    event_bus: EventBusRuntime,
    lifecycle: LifecycleRuntime,
    orchestrator: OrchestratorRuntime,
    round_number: int,
) -> None:
    assert settings.environment == "development" and settings.log_level == "INFO"
    assert lifecycle.status is RuntimeStatus.RUNNING
    assert container.descriptors() == () and orchestrator.modules() == ()
    assert not event_bus.contains("pipeline.completed")
    assert runtime_context.trace is trace_context and runtime_context.metadata == {}
    assert runtime_context.trace_id == trace_context.trace_id
    assert runtime_context.session_id != runtime_context.pipeline_id
    service_id = ServiceId("fixture.service")
    container.register(
        ServiceDescriptor(service_id=service_id, scope=DIScope.APPLICATION, implementation=Service)
    )
    service = await container.resolve(service_id)
    assert isinstance(service, Service) and service.initializations == 1
    collector = Collector()
    event_bus.subscribe("pipeline.completed", collector)
    effects: list[int] = []

    async def operation(context: RuntimeContext) -> None:
        assert context.session_id == runtime_context.session_id
        assert await container.resolve(service_id) is service
        effects.append(round_number)

    module_id = ModuleId("fixture.module")
    orchestrator.register_module(
        RuntimeModuleManifest(
            module_id=module_id,
            runtime_layer=RuntimeLayer.L0_KERNEL,
            depends_on=(),
            provides=(),
            version="fixture",
        ),
        operation=operation,
    )
    await orchestrator.execute(
        PipelineDefinition(
            pipeline_id=runtime_context.pipeline_id,
            stages=(PipelineStage(stage_id="fixture.stage", module_id=module_id, depends_on=()),),
        ),
        context=runtime_context,
    )
    assert effects == [round_number]
    assert [event.event_type for event in collector.events] == ["pipeline.completed"]
    assert collector.events[0].trace == trace_context
    assert runtime_context.metadata == {} and lifecycle.status is RuntimeStatus.RUNNING


async def test_shared_fixture_teardown_completes_real_cleanup_in_dependency_order(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    container: ContainerRuntime,
    event_bus: EventBusRuntime,
    lifecycle: LifecycleRuntime,
    orchestrator: OrchestratorRuntime,
) -> None:
    assert settings.environment == "development"
    service_id = ServiceId("fixture.cleanup")
    container.register(
        ServiceDescriptor(service_id=service_id, scope=DIScope.APPLICATION, implementation=Service)
    )
    service = await container.resolve(service_id)
    assert isinstance(service, Service)
    event_bus.subscribe("fixture.cleanup", Collector())
    orchestrator.register_module(
        RuntimeModuleManifest(
            module_id=ModuleId("fixture.cleanup"),
            runtime_layer=RuntimeLayer.L0_KERNEL,
            depends_on=(),
            provides=(),
            version="fixture",
        )
    )
    completed: list[str] = []
    close_container, close_bus = container.shutdown, event_bus.shutdown
    close_orchestrator, close_lifecycle = orchestrator.shutdown, lifecycle.shutdown

    async def checked_orchestrator_shutdown() -> None:
        await close_orchestrator()
        assert orchestrator.modules() == ()
        if "orchestrator" not in completed:
            completed.append("orchestrator")

    async def checked_bus_shutdown() -> None:
        await close_bus()
        assert event_bus.handlers("fixture.cleanup") == ()
        if "event_bus" not in completed:
            completed.append("event_bus")

    async def checked_container_shutdown() -> None:
        await close_container()
        assert service.shutdowns == 1
        assert container.contains(service_id)  # Descriptor observation survives shutdown.
        with pytest.raises(RuntimeStateError):
            await container.resolve(service_id)
        if "container" not in completed:
            completed.append("container")
        else:
            assert completed == ["orchestrator", "event_bus", "container", "lifecycle"]

    async def checked_lifecycle_shutdown() -> None:
        await close_lifecycle()
        assert lifecycle.status is RuntimeStatus.TERMINATED
        assert completed == ["orchestrator", "event_bus", "container"]
        completed.append("lifecycle")

    # monkeypatch is created first and restored last, after all fixture finalizers.
    # Assertions run after actual awaited cleanup, not in shared fixture bodies.
    monkeypatch.setattr(orchestrator, "shutdown", checked_orchestrator_shutdown)
    monkeypatch.setattr(event_bus, "shutdown", checked_bus_shutdown)
    monkeypatch.setattr(container, "shutdown", checked_container_shutdown)
    monkeypatch.setattr(lifecycle, "shutdown", checked_lifecycle_shutdown)


def traced_service(
    name: str,
    events: list[str],
    *,
    shutdown: Callable[[], Awaitable[None]] | None = None,
) -> type[Service]:
    class TracedService(Service):
        async def initialize(self) -> None:
            events.append("initialize:" + name)
            await super().initialize()

        async def shutdown(self) -> None:
            events.append("shutdown:" + name)
            await super().shutdown()
            if shutdown is not None:
                await shutdown()

    return TracedService


def register(
    runtime: RuntimeKernel,
    name: str,
    scope: DIScope = DIScope.PIPELINE,
    *,
    implementation: type[ServiceContract] = Service,
) -> ServiceId:
    service_id = ServiceId(name)
    runtime.container.register(
        ServiceDescriptor(
            service_id=service_id,
            scope=scope,
            implementation=implementation,
        )
    )
    return service_id


def session(runtime: RuntimeKernel) -> RuntimeContext:
    return runtime.session.create(
        session_id=SessionId(uuid4()),
        trace=TraceContext(trace_id=TraceId(uuid4())),
        metadata={"nested": {"original": True}},
    )


async def kernel() -> RuntimeKernel:
    runtime = await BootstrapRuntime().build()
    await runtime.initialize()
    await runtime.start()
    return runtime


async def finish(runtime: RuntimeKernel) -> None:
    await runtime.stop()
    await runtime.shutdown()


def pipeline(
    runtime: RuntimeKernel,
    context: RuntimeContext,
    operation: Callable[[RuntimeContext], Awaitable[None]] | None,
) -> PipelineDefinition:
    name = ModuleId("business")
    runtime.orchestrator.register_module(
        RuntimeModuleManifest(
            module_id=name,
            runtime_layer=RuntimeLayer.L0_KERNEL,
            depends_on=(),
            provides=(),
            version="integration",
        ),
        operation=operation,
    )
    return PipelineDefinition(
        pipeline_id=context.pipeline_id,
        stages=(PipelineStage(stage_id="generate", module_id=name, depends_on=()),),
    )


@pytest.mark.parametrize("outcome", ("success", "operation", "preflight", "delivery", "cancel"))
async def test_real_pipeline_disposes_pipeline_and_transient_but_preserves_other_scopes(
    outcome: str,
) -> None:
    runtime = await kernel()
    first, other = session(runtime), session(runtime)
    application_id = register(runtime, "application", DIScope.APPLICATION)
    session_id = register(runtime, "session", DIScope.SESSION)
    scoped_id = register(runtime, "scoped")
    transient_id = register(runtime, "transient", DIScope.TRANSIENT)
    application = cast(Service, await runtime.container.resolve(application_id))
    first_session = cast(Service, await runtime.container.resolve(session_id, context=first))
    other_session = cast(Service, await runtime.container.resolve(session_id, context=other))
    scoped = cast(Service, await runtime.container.resolve(scoped_id, context=first))
    transient = cast(Service, await runtime.container.resolve(transient_id, context=first))
    other_pipeline = cast(Service, await runtime.container.resolve(scoped_id, context=other))
    effects: list[str] = []
    primary: BaseException = (
        asyncio.CancelledError("secret") if outcome == "cancel" else ValueError("business secret")
    )

    async def operation(context: RuntimeContext) -> None:
        effects.append("generated")
        context.metadata["caller_local"] = True
        assert await runtime.container.resolve(scoped_id, context=context) is scoped
        if outcome in {"operation", "cancel"}:
            raise primary

    definition = pipeline(runtime, first, None if outcome == "preflight" else operation)
    collector = Collector()
    for event_type in (
        "pipeline.started",
        "pipeline.stage.started",
        "pipeline.stage.completed",
        "pipeline.stage.failed",
        "pipeline.completed",
        "pipeline.failed",
        "pipeline.cancelled",
    ):
        runtime.event_bus.subscribe(event_type, collector)
    if outcome == "delivery":
        runtime.event_bus.subscribe("pipeline.stage.completed", DeliveryFailure())
    if outcome == "success":
        await runtime.execute(definition, context=first)
        assert collector.events[-1].event_type == "pipeline.completed"
    else:
        expected = {
            "operation": ValueError,
            "preflight": InvalidManifestError,
            "delivery": EventHandlerError,
            "cancel": asyncio.CancelledError,
        }[outcome]
        with pytest.raises(expected) as caught:
            await runtime.execute(definition, context=first)
        if outcome in {"operation", "cancel"}:
            assert caught.value is primary
        if outcome == "preflight":
            assert not collector.events
        elif outcome == "cancel":
            assert collector.events[-1].event_type == "pipeline.cancelled"
        else:
            assert collector.events[-1].event_type == "pipeline.failed"
    assert len(effects) == (0 if outcome == "preflight" else 1)
    assert scoped.shutdowns == transient.shutdowns == 1
    assert application.shutdowns == first_session.shutdowns == other_session.shutdowns == 0
    assert other_pipeline.shutdowns == 0
    assert "caller_local" not in runtime.session.get(first.session_id).metadata
    assert runtime.context.current().session_id == other.session_id
    assert runtime.status() is RuntimeStatus.RUNNING
    await finish(runtime)
    assert application.shutdowns == first_session.shutdowns == other_session.shutdowns == 1
    assert other_pipeline.shutdowns == 1
    assert scoped.shutdowns == transient.shutdowns == 1
    assert not runtime.session.list() and not runtime.context.has_context()
    assert not runtime.event_bus.contains("pipeline.started")


@pytest.mark.parametrize("has_primary", (False, True))
@pytest.mark.parametrize("cleanup_type", (ValueError, asyncio.CancelledError))
async def test_pipeline_first_error_prior_cause_and_cleanup_cancellation(
    has_primary: bool,
    cleanup_type: type[BaseException],
) -> None:
    runtime = await kernel()
    captured = session(runtime)
    original = ValueError("primary secret")
    old = ExceptionGroup("preexisting group", [LookupError("old secret")])
    original.__cause__ = old
    failure = cleanup_type("cleanup secret")
    faults: list[BaseException] = [failure]

    async def dispose() -> None:
        if faults:
            raise faults.pop(0)

    service_id = register(
        runtime,
        "fault",
        implementation=traced_service(
            "fault",
            [],
            shutdown=dispose,
        ),
    )
    owned = cast(Service, await runtime.container.resolve(service_id, context=captured))

    async def operation(_context: RuntimeContext) -> None:
        if has_primary:
            raise original

    definition = pipeline(runtime, captured, operation)
    expected = (
        ValueError
        if has_primary
        else (RuntimeShutdownError if cleanup_type is ValueError else asyncio.CancelledError)
    )
    with pytest.raises(expected) as caught:
        await runtime.execute(definition, context=captured)
    if has_primary:
        assert caught.value is original
        group = cast(BaseExceptionGroup[BaseException], original.__cause__)
        assert group.exceptions[0] is old
        secondary = group.exceptions[1]
        if cleanup_type is ValueError:
            assert isinstance(secondary, RuntimeShutdownError)
            assert cast(ExceptionGroup[Exception], secondary.__cause__).exceptions == (failure,)
        else:
            assert secondary is failure
    elif cleanup_type is ValueError:
        assert cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions == (failure,)
    else:
        assert caught.value is failure
    await finish(runtime)
    assert owned.shutdowns == (2 if cleanup_type is asyncio.CancelledError else 1)
    assert runtime.status() is RuntimeStatus.TERMINATED


async def test_pipeline_multiple_disposal_failures_reverse_attempt_order() -> None:
    runtime = await kernel()
    captured = session(runtime)
    events: list[str] = []
    first, second = ValueError("one"), LookupError("two")

    async def fail_one() -> None:
        raise first

    async def fail_two() -> None:
        raise second

    one = register(runtime, "one", implementation=traced_service("one", events, shutdown=fail_one))
    two = register(runtime, "two", implementation=traced_service("two", events, shutdown=fail_two))
    owned_one = cast(Service, await runtime.container.resolve(one, context=captured))
    owned_two = cast(Service, await runtime.container.resolve(two, context=captured))

    async def operation(_context: RuntimeContext) -> None:
        pass

    definition = pipeline(runtime, captured, operation)
    with pytest.raises(RuntimeShutdownError) as caught:
        await runtime.execute(definition, context=captured)
    assert cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions == (second, first)
    assert events[-2:] == ["shutdown:two", "shutdown:one"]
    assert owned_one.shutdowns == owned_two.shutdowns == 1
    await finish(runtime)
    assert owned_one.shutdowns == owned_two.shutdowns == 1


@pytest.mark.parametrize("action", range(6))
async def test_busy_guard_remains_held_after_orchestrator_finishes_during_real_di_cleanup(
    action: int,
) -> None:
    runtime = await kernel()
    captured = session(runtime)
    entered, release = asyncio.Event(), asyncio.Event()
    owned: list[Service] = []

    async def dispose() -> None:
        entered.set()
        await release.wait()

    service_id = register(
        runtime,
        "blocked",
        implementation=traced_service(
            "blocked",
            [],
            shutdown=dispose,
        ),
    )

    async def operation(context: RuntimeContext) -> None:
        owned.append(cast(Service, await runtime.container.resolve(service_id, context=context)))

    definition = pipeline(runtime, captured, operation)
    actions: tuple[Callable[[], Awaitable[None]], ...] = (
        runtime.initialize,
        runtime.start,
        runtime.stop,
        runtime.shutdown,
        lambda: runtime.execute(definition, context=captured),
        lambda: runtime.remove_session(captured.session_id),
    )
    task = asyncio.create_task(runtime.execute(definition, context=captured))
    try:
        await entered.wait()
        with pytest.raises(RuntimeStateError):
            await actions[action]()
        assert len(owned) == 1 and owned[0].shutdowns == 1
        assert runtime.session.contains(captured.session_id)
        assert runtime.status() is RuntimeStatus.RUNNING
        assert runtime.health() is HealthStatus.OK
    finally:
        release.set()
        await task
    await runtime.execute(definition, context=captured)
    assert len(owned) == 2 and owned[0] is not owned[1]
    assert all(service.shutdowns == 1 for service in owned)
    await finish(runtime)


async def test_external_pipeline_cancellation_still_releases_resource_and_restores_guard() -> None:
    runtime = await kernel()
    captured = session(runtime)
    entered = asyncio.Event()
    service_id = register(runtime, "owned")
    owned = cast(Service, await runtime.container.resolve(service_id, context=captured))

    async def operation(_context: RuntimeContext) -> None:
        entered.set()
        await asyncio.Event().wait()

    definition = pipeline(runtime, captured, operation)
    task = asyncio.create_task(runtime.execute(definition, context=captured))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert owned.shutdowns == 1
    await finish(runtime)


@pytest.mark.parametrize("active", (False, True))
@pytest.mark.parametrize("outcome", ("success", "error", "cancel"))
async def test_composed_session_removal_scopes_active_context_errors_and_retry(
    active: bool,
    outcome: str,
) -> None:
    runtime = await kernel()
    other, removed = session(runtime), session(runtime)
    if not active:
        runtime.context.replace(other)
    events: list[str] = []
    faults: list[BaseException] = []
    if outcome != "success":
        faults.append(
            asyncio.CancelledError("secret") if outcome == "cancel" else ValueError("secret")
        )

    async def dispose() -> None:
        if faults:
            raise faults.pop(0)

    service_id = register(
        runtime,
        "session",
        DIScope.SESSION,
        implementation=traced_service(
            "session",
            events,
            shutdown=dispose,
        ),
    )
    pipeline_id = register(runtime, "pipeline")
    transient_id = register(runtime, "transient", DIScope.TRANSIENT)
    application_id = register(runtime, "application", DIScope.APPLICATION)
    owned = cast(Service, await runtime.container.resolve(service_id, context=removed))
    sibling = cast(Service, await runtime.container.resolve(service_id, context=other))
    scoped = cast(Service, await runtime.container.resolve(pipeline_id, context=removed))
    transient = cast(Service, await runtime.container.resolve(transient_id, context=removed))
    application = cast(Service, await runtime.container.resolve(application_id))
    if outcome == "success":
        await runtime.remove_session(removed.session_id)
    elif outcome == "error":
        with pytest.raises(RuntimeShutdownError):
            await runtime.remove_session(removed.session_id)
    else:
        with pytest.raises(asyncio.CancelledError):
            await runtime.remove_session(removed.session_id)
        assert runtime.session.contains(removed.session_id)
        assert runtime.context.current().session_id == (
            removed.session_id if active else other.session_id
        )
        await runtime.remove_session(removed.session_id)
    assert not runtime.session.contains(removed.session_id)
    assert runtime.session.contains(other.session_id)
    assert (
        (not runtime.context.has_context())
        if active
        else (runtime.context.current().session_id == other.session_id)
    )
    assert scoped.shutdowns == transient.shutdowns == 1
    assert owned.shutdowns == (2 if outcome == "cancel" else 1)
    assert sibling.shutdowns == application.shutdowns == 0
    with pytest.raises(RuntimeStateError):
        await runtime.remove_session(removed.session_id)
    await finish(runtime)
    assert sibling.shutdowns == application.shutdowns == 1


async def test_preflight_cleanup_uses_definition_id_not_disagreeing_context_id() -> None:
    runtime = await kernel()
    first, other = session(runtime), session(runtime)
    service_id = register(runtime, "owned")
    first_owned = cast(Service, await runtime.container.resolve(service_id, context=first))
    other_owned = cast(Service, await runtime.container.resolve(service_id, context=other))

    async def operation(_context: RuntimeContext) -> None:
        raise AssertionError("must not execute")

    definition = pipeline(runtime, first, operation)
    with pytest.raises(InvalidManifestError):
        await runtime.execute(definition, context=other)
    assert first_owned.shutdowns == 1 and other_owned.shutdowns == 0
    await finish(runtime)
    assert other_owned.shutdowns == 1


async def test_real_partial_initialize_failure_stays_failed_and_kernel_drains_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    captured = session(runtime)
    original = ValueError("initialize secret")

    async def fail() -> None:
        raise original

    monkeypatch.setattr(runtime.container, "initialize", fail)
    with pytest.raises(RuntimeInitializationError) as caught:
        await runtime.initialize()
    assert caught.value.__cause__ is original
    assert runtime.status() is RuntimeStatus.FAILED
    await runtime.stop()
    await runtime.shutdown()
    assert runtime.status() is RuntimeStatus.FAILED
    assert not runtime.session.contains(captured.session_id)


async def test_full_shutdown_multiple_di_errors_and_session_drain_retains_primary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await kernel()
    first = session(runtime)
    session(runtime)
    original_remove = runtime.session.remove
    drain_one, drain_two = ValueError("session one"), LookupError("session two")

    def remove(session_id: SessionId) -> None:
        original_remove(session_id)
        raise drain_one if session_id == first.session_id else drain_two

    monkeypatch.setattr(runtime.session, "remove", remove)
    await runtime.stop()
    with pytest.raises(ValueError) as caught:
        await runtime.shutdown()
    assert caught.value is drain_one
    assert cast(ExceptionGroup[Exception], drain_one.__cause__).exceptions == (drain_two,)
    assert not runtime.session.list()
    await runtime.shutdown()

    runtime = await kernel()
    captured = session(runtime)
    failure = ValueError("service failure")

    async def dispose() -> None:
        raise failure

    service_id = register(
        runtime,
        "broken",
        DIScope.APPLICATION,
        implementation=traced_service("broken", [], shutdown=dispose),
    )
    await runtime.container.resolve(service_id)
    original_remove = runtime.session.remove

    def fail_remove(session_id: SessionId) -> None:
        original_remove(session_id)
        raise drain_one

    monkeypatch.setattr(runtime.session, "remove", fail_remove)
    await runtime.stop()
    with pytest.raises(RuntimeShutdownError) as caught_shutdown:
        await runtime.shutdown()
    group = cast(ExceptionGroup[Exception], caught_shutdown.value.__cause__)
    assert isinstance(group.exceptions[0], ExceptionGroup)
    assert group.exceptions[1] is drain_one
    assert not runtime.session.contains(captured.session_id)
    assert runtime.status() is RuntimeStatus.FAILED
    await runtime.shutdown()


async def test_interrupted_full_shutdown_drains_session_but_retains_pending_di_for_retry() -> None:
    runtime = await kernel()
    captured = session(runtime)
    faults: list[BaseException] = [
        asyncio.CancelledError("first"),
        asyncio.CancelledError("second"),
    ]

    async def dispose() -> None:
        if faults:
            raise faults.pop(0)

    service_id = register(
        runtime,
        "interrupted",
        DIScope.SESSION,
        implementation=traced_service("interrupted", [], shutdown=dispose),
    )
    owned = cast(Service, await runtime.container.resolve(service_id, context=captured))
    await runtime.stop()
    with pytest.raises(asyncio.CancelledError):
        await runtime.shutdown()
    assert runtime.status() is RuntimeStatus.FAILED and not runtime.session.list()
    assert owned.shutdowns == 2
    await runtime.shutdown()
    assert owned.shutdowns == 3
    assert not runtime.context.has_context()
    await runtime.shutdown()
    assert owned.shutdowns == 3


async def test_same_primary_secondary_object_cannot_form_kernel_cause_self_cycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await kernel()
    captured = session(runtime)
    original = ValueError("shared")
    old = LookupError("existing")
    original.__cause__ = old

    async def operation(_context: RuntimeContext) -> None:
        raise original

    async def clear(_pipeline_id: object) -> None:
        raise original

    monkeypatch.setattr(runtime.container, "clear_pipeline", clear)
    definition = pipeline(runtime, captured, operation)
    with pytest.raises(ValueError) as caught:
        await runtime.execute(definition, context=captured)
    assert caught.value is original and original.__cause__ is old
    await finish(runtime)


async def test_session_di_primary_is_not_masked_by_registry_cleanup_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await kernel()
    captured = session(runtime)
    primary, secondary = ValueError("DI secret"), LookupError("registry secret")

    async def clear(_session_id: SessionId) -> None:
        raise primary

    def remove(_session_id: SessionId) -> None:
        raise secondary

    monkeypatch.setattr(runtime.container, "clear_session", clear)
    monkeypatch.setattr(runtime.session, "remove", remove)
    with pytest.raises(ValueError) as caught:
        await runtime.remove_session(captured.session_id)
    assert caught.value is primary
    assert cast(ExceptionGroup[Exception], primary.__cause__).exceptions == (secondary,)
    monkeypatch.undo()
    await finish(runtime)


class MainProbe:
    """An isolated facade test double; real graph/resource scenarios are tested above."""

    def __init__(
        self,
        failures: dict[str, BaseException] | None = None,
        *,
        failure_state: RuntimeStatus = RuntimeStatus.FAILED,
    ) -> None:
        self.phase = RuntimeStatus.CREATED
        self.failures = {} if failures is None else failures
        self.failure_state = failure_state
        self.calls: list[str] = []

    def status(self) -> RuntimeStatus:
        return self.phase

    async def initialize(self) -> None:
        self.calls.append("initialize")
        self.phase = self.failure_state if "initialize" in self.failures else RuntimeStatus.READY
        if "initialize" in self.failures:
            raise self.failures["initialize"]

    async def start(self) -> None:
        self.calls.append("start")
        self.phase = self.failure_state if "start" in self.failures else RuntimeStatus.RUNNING
        if "start" in self.failures:
            raise self.failures["start"]

    async def stop(self) -> None:
        self.calls.append("stop")
        if self.phase is not RuntimeStatus.FAILED:
            self.phase = RuntimeStatus.FAILED if "stop" in self.failures else RuntimeStatus.STOPPED
        if "stop" in self.failures:
            raise self.failures["stop"]

    async def shutdown(self) -> None:
        self.calls.append("shutdown")
        if self.phase is not RuntimeStatus.FAILED:
            self.phase = (
                RuntimeStatus.FAILED if "shutdown" in self.failures else RuntimeStatus.TERMINATED
            )
        if "shutdown" in self.failures:
            raise self.failures["shutdown"]


def use_main_probe(probe: MainProbe, monkeypatch: pytest.MonkeyPatch) -> None:
    async def build(_self: BootstrapRuntime) -> RuntimeKernel:
        probe.calls.append("build")
        return cast(RuntimeKernel, probe)

    monkeypatch.setattr(BootstrapRuntime, "build", build)


@pytest.mark.parametrize("phase", ("initialize", "start", "stop", "shutdown"))
@pytest.mark.parametrize(
    "error_type",
    (
        ValueError,
        asyncio.CancelledError,
        KeyboardInterrupt,
        SystemExit,
    ),
)
async def test_main_preserves_every_primary_and_always_attempts_final_cleanup(
    phase: str,
    error_type: type[BaseException],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = error_type("process secret")
    probe = MainProbe({phase: original})
    use_main_probe(probe, monkeypatch)
    with pytest.raises(error_type) as caught:
        await entry.main()
    assert caught.value is original
    assert probe.calls == (
        ["build", "initialize", "stop", "shutdown"]
        if phase == "initialize"
        else ["build", "initialize", "start", "stop", "shutdown"]
    )
    assert probe.status() is RuntimeStatus.FAILED


@pytest.mark.parametrize(
    "state",
    (
        RuntimeStatus.CREATED,
        RuntimeStatus.INITIALIZING,
        RuntimeStatus.READY,
        RuntimeStatus.STARTING,
        RuntimeStatus.FAILED,
    ),
)
async def test_main_partial_startup_statuses_never_force_created_transition(
    state: RuntimeStatus,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = ValueError("startup")
    probe = MainProbe({"initialize": original}, failure_state=state)
    use_main_probe(probe, monkeypatch)
    with pytest.raises(ValueError):
        await entry.main()
    assert probe.calls == (
        ["build", "initialize"]
        if state is RuntimeStatus.CREATED
        else ["build", "initialize", "stop", "shutdown"]
    )


@pytest.mark.parametrize("secondary_type", (ValueError, asyncio.CancelledError))
async def test_main_preserves_primary_prior_group_and_ordered_secondary_causes_safely(
    secondary_type: type[BaseException],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = ValueError("API_KEY=must_not_log")
    prior = ExceptionGroup("preexisting", [LookupError("old secret")])
    original.__cause__ = prior
    second, third = secondary_type("token=must_not_log"), LookupError("credential=must_not_log")
    probe = MainProbe({"start": original, "stop": second, "shutdown": third})
    use_main_probe(probe, monkeypatch)
    handler = LogCapture()
    logger = get_logger("aurora")
    logger.addHandler(handler)
    try:
        with pytest.raises(ValueError) as caught:
            await entry.main()
    finally:
        logger.removeHandler(handler)
    assert caught.value is original
    group = cast(BaseExceptionGroup[BaseException], original.__cause__)
    first_group = cast(BaseExceptionGroup[BaseException], group.exceptions[0])
    assert first_group.exceptions == (prior, second)
    assert group.exceptions[1] is third
    assert len(handler.messages) == 2
    assert not any("must_not_log" in message or "secret" in message for message in handler.messages)


async def test_main_stop_failure_remains_primary_if_shutdown_also_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, second = ValueError("stop"), asyncio.CancelledError("shutdown")
    probe = MainProbe({"stop": first, "shutdown": second})
    use_main_probe(probe, monkeypatch)
    with pytest.raises(ValueError) as caught:
        await entry.main()
    assert caught.value is first
    assert cast(BaseExceptionGroup[BaseException], first.__cause__).exceptions == (second,)
    assert probe.calls[-2:] == ["stop", "shutdown"]


async def test_main_shared_error_object_preserves_existing_cause_without_self_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = ValueError("shared")
    old = LookupError("old")
    original.__cause__ = old
    probe = MainProbe({"start": original, "stop": original})
    use_main_probe(probe, monkeypatch)
    with pytest.raises(ValueError) as caught:
        await entry.main()
    assert caught.value is original and original.__cause__ is old


async def test_main_build_failure_has_no_returned_kernel_to_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = ValueError("build")

    async def fail(_self: BootstrapRuntime) -> RuntimeKernel:
        raise original

    monkeypatch.setattr(BootstrapRuntime, "build", fail)
    with pytest.raises(ValueError) as caught:
        await entry.main()
    assert caught.value is original


async def test_main_real_startup_teardown_and_single_bounded_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    actual_build = BootstrapRuntime.build
    built: list[RuntimeKernel] = []

    async def build(self: BootstrapRuntime) -> RuntimeKernel:
        runtime = await actual_build(self)
        session(runtime)
        built.append(runtime)
        return runtime

    monkeypatch.setattr(BootstrapRuntime, "build", build)
    await entry.main()
    assert len(built) == 1 and built[0].status() is RuntimeStatus.TERMINATED
    assert not built[0].context.has_context() and not built[0].session.list()


def test_single_process_asyncio_boundary_executes_without_waiting_for_a_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    probe = MainProbe()
    use_main_probe(probe, monkeypatch)
    runpy.run_path(entry.__file__, run_name="__main__")
    assert probe.calls == ["build", "initialize", "start", "stop", "shutdown"]
    assert probe.status() is RuntimeStatus.TERMINATED
    importlib.reload(entry)
    assert Path(entry.__file__).name == "main.py"


@pytest.mark.parametrize("phase", ("initialize", "start"))
@pytest.mark.parametrize(
    "error_type",
    (
        ValueError,
        asyncio.CancelledError,
        KeyboardInterrupt,
        SystemExit,
    ),
)
async def test_real_main_partial_startup_failure_cleans_di_without_forcing_success(
    phase: str,
    error_type: type[BaseException],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    captured = session(runtime)
    service_id = register(runtime, "application", DIScope.APPLICATION)
    owned = cast(Service, await runtime.container.resolve(service_id))
    original = error_type("startup secret")

    async def fail() -> None:
        raise original

    async def build(_self: BootstrapRuntime) -> RuntimeKernel:
        return runtime

    monkeypatch.setattr(runtime.event_bus, phase, fail)
    monkeypatch.setattr(BootstrapRuntime, "build", build)
    expected = RuntimeInitializationError if error_type is ValueError else error_type
    with pytest.raises(expected) as caught:
        await entry.main()
    if error_type is ValueError:
        assert caught.value.__cause__ is original
    else:
        assert caught.value is original
    assert runtime.status() is RuntimeStatus.FAILED
    assert owned.shutdowns == 1
    assert not runtime.session.contains(captured.session_id)
    assert not runtime.context.has_context()
    await runtime.shutdown()
    assert owned.shutdowns == 1


@pytest.mark.parametrize("error_type", (ValueError, asyncio.CancelledError))
async def test_real_main_stop_failure_still_disposes_application_and_drains_sessions(
    error_type: type[BaseException],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    session(runtime)
    service_id = register(runtime, "application", DIScope.APPLICATION)
    owned = cast(Service, await runtime.container.resolve(service_id))
    original = error_type("stop secret")
    faults: list[BaseException] = [original]

    async def fail() -> None:
        if faults:
            raise faults.pop(0)

    async def build(_self: BootstrapRuntime) -> RuntimeKernel:
        return runtime

    monkeypatch.setattr(runtime.event_bus, "stop", fail)
    monkeypatch.setattr(BootstrapRuntime, "build", build)
    expected = RuntimeShutdownError if error_type is ValueError else error_type
    with pytest.raises(expected) as caught:
        await entry.main()
    if error_type is ValueError:
        assert original in cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions
    else:
        assert caught.value is original
    assert owned.shutdowns == 1
    assert runtime.status() is RuntimeStatus.FAILED
    assert not runtime.session.list() and not runtime.context.has_context()


async def test_repeated_stop_cancellation_retains_di_for_explicit_shutdown_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    session(runtime)
    service_id = register(runtime, "application", DIScope.APPLICATION)
    owned = cast(Service, await runtime.container.resolve(service_id))
    original = asyncio.CancelledError("repeated interruption")
    actual_stop = runtime.event_bus.stop

    async def fail() -> None:
        raise original

    async def build(_self: BootstrapRuntime) -> RuntimeKernel:
        return runtime

    monkeypatch.setattr(runtime.event_bus, "stop", fail)
    monkeypatch.setattr(BootstrapRuntime, "build", build)
    with pytest.raises(asyncio.CancelledError) as caught:
        await entry.main()
    assert caught.value is original
    assert owned.shutdowns == 0
    assert runtime.status() is RuntimeStatus.FAILED
    assert not runtime.session.list()
    monkeypatch.setattr(runtime.event_bus, "stop", actual_stop)
    await runtime.shutdown()
    assert owned.shutdowns == 1
    assert not runtime.context.has_context()
    assert runtime.status() is RuntimeStatus.FAILED
    await runtime.shutdown()
    assert owned.shutdowns == 1


async def test_reentrant_business_and_disposal_calls_cannot_mutate_kernel() -> None:
    runtime = await kernel()
    captured = session(runtime)
    rejected: list[str] = []
    owned: list[Service] = []

    async def attempt(phase: str) -> None:
        actions: tuple[Callable[[], Awaitable[None]], ...] = (
            runtime.initialize,
            runtime.start,
            runtime.stop,
            runtime.shutdown,
            lambda: runtime.execute(definition, context=captured),
            lambda: runtime.remove_session(captured.session_id),
        )
        for action in actions:
            with pytest.raises(RuntimeStateError):
                await action()
            rejected.append(phase)

    async def dispose() -> None:
        await attempt("dispose")

    service_id = register(
        runtime,
        "reentrant",
        implementation=traced_service(
            "reentrant",
            [],
            shutdown=dispose,
        ),
    )

    async def operation(context: RuntimeContext) -> None:
        await attempt("business")
        owned.append(cast(Service, await runtime.container.resolve(service_id, context=context)))

    definition = pipeline(runtime, captured, operation)
    await runtime.execute(definition, context=captured)
    assert rejected == ["business"] * 6 + ["dispose"] * 6
    assert len(owned) == 1 and owned[0].shutdowns == 1
    await finish(runtime)
