"""Canonical KR-010 acceptance: graph assembly, facade surface and guarded lifecycle."""

from __future__ import annotations

import ast
import asyncio
import inspect
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Never, cast
from uuid import uuid4

import pytest

from src.core.exceptions import (
    ConfigurationError,
    ContractValidationError,
    InvalidManifestError,
    RuntimeInitializationError,
    RuntimeStateError,
)
from src.core.logging_config import LoggingConfig
from src.core.settings import Settings
from src.core.types import (
    HealthStatus,
    PipelineId,
    RuntimeLayer,
    RuntimeStatus,
    SessionId,
    TraceId,
)
from src.core.version import ARCHITECTURE_VERSION, KERNEL_RUNTIME_VERSION
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime import bootstrap
from src.kernel.runtime import runtime as kernel_module
from src.kernel.runtime.bootstrap import BootstrapRuntime
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.lifecycle import LifecycleRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
from src.kernel.runtime.pipeline import PipelineDefinition
from src.kernel.runtime.runtime import RuntimeKernel
from src.kernel.runtime.session import SessionRuntime


def context(runtime: RuntimeKernel) -> RuntimeContext:
    return runtime.session.create(
        session_id=SessionId(uuid4()), trace=TraceContext(trace_id=TraceId(uuid4()))
    )


def mutations(runtime: RuntimeKernel) -> tuple[Callable[[], Awaitable[None]], ...]:
    captured = context(runtime)
    definition = PipelineDefinition(pipeline_id=captured.pipeline_id, stages=())
    return (
        runtime.initialize,
        runtime.start,
        runtime.stop,
        runtime.shutdown,
        lambda: runtime.execute(definition, context=captured),
        lambda: runtime.remove_session(captured.session_id),
    )


async def running() -> RuntimeKernel:
    runtime = await BootstrapRuntime().build()
    await runtime.initialize()
    await runtime.start()
    return runtime


async def finish(runtime: RuntimeKernel) -> None:
    await runtime.stop()
    await runtime.shutdown()


async def test_bootstrap_builds_and_runs_runtime_graph() -> None:
    runtime = await BootstrapRuntime().build()
    assert isinstance(runtime, RuntimeContract)
    assert isinstance(runtime.container, ContainerRuntime)
    assert isinstance(runtime.lifecycle, LifecycleRuntime)
    assert isinstance(runtime.event_bus, EventBusRuntime)
    assert isinstance(runtime.context, ContextRuntime)
    assert isinstance(runtime.orchestrator, OrchestratorRuntime)
    assert isinstance(runtime.session, SessionRuntime)
    assert runtime.status() is RuntimeStatus.CREATED
    assert runtime.state().current is RuntimeStatus.CREATED
    assert not runtime.context.has_context() and not runtime.session.list()
    assert not runtime.container.descriptors() and not runtime.orchestrator.modules()
    assert not runtime.event_bus.contains("bootstrap.completed")
    assert runtime.runtime_name == "kernel"
    assert runtime.runtime_layer is RuntimeLayer.L0_KERNEL
    assert runtime.version == KERNEL_RUNTIME_VERSION
    assert runtime.architecture_version == ARCHITECTURE_VERSION
    assert runtime.health() is HealthStatus.OK
    before = runtime.state()
    diagnostics = runtime.diagnostics()
    assert diagnostics == {
        "architecture_version": ARCHITECTURE_VERSION,
        "runtime_layer": RuntimeLayer.L0_KERNEL.value,
        "runtime_status": RuntimeStatus.CREATED.value,
        "version": KERNEL_RUNTIME_VERSION,
    }
    diagnostics["version"] = "caller edit"
    assert runtime.diagnostics()["version"] == KERNEL_RUNTIME_VERSION
    assert runtime.state() == before
    await runtime.initialize()
    assert runtime.status() is RuntimeStatus.READY
    await runtime.start()
    assert runtime.status() is RuntimeStatus.RUNNING
    await finish(runtime)
    assert runtime.status() is RuntimeStatus.TERMINATED
    await runtime.stop()
    await runtime.shutdown()
    with pytest.raises(RuntimeStateError):
        await runtime.initialize()
    with pytest.raises(RuntimeStateError):
        await runtime.start()


@pytest.mark.parametrize(
    "name",
    (
        "container",
        "lifecycle",
        "event_bus",
        "context",
        "orchestrator",
        "session",
        "runtime_name",
        "runtime_layer",
        "version",
        "architecture_version",
    ),
)
async def test_every_facade_reference_and_metadata_property_is_read_only(name: str) -> None:
    runtime = await BootstrapRuntime().build()
    with pytest.raises(AttributeError):
        setattr(runtime, name, None)


async def test_independent_builds_do_not_share_runtime_or_session_owners() -> None:
    first, second = await BootstrapRuntime().build(), await BootstrapRuntime().build()
    assert first is not second
    assert first.container is not second.container
    assert first.lifecycle is not second.lifecycle
    assert first.event_bus is not second.event_bus
    assert first.context is not second.context
    assert first.orchestrator is not second.orchestrator
    assert first.session is not second.session
    captured = context(first)
    assert not second.session.contains(captured.session_id)
    assert not second.context.has_context()


async def test_build_order_logging_settings_and_no_initialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    settings = Settings.model_construct(log_level="WARNING")

    def validate() -> Settings:
        events.append("validation")
        return settings

    def get_settings() -> Settings:
        events.append("settings")
        return settings

    def logger(name: str, config: LoggingConfig) -> None:
        assert name == "aurora" and config.level == "WARNING"
        events.append("logging")

    def session_factory(owner: ContextRuntime) -> SessionRuntime:
        events.append("session")
        return SessionRuntime(owner)

    def kernel_factory(
        *,
        container: ContainerRuntime,
        lifecycle: LifecycleRuntime,
        event_bus: EventBusRuntime,
        context: ContextRuntime,
        orchestrator: OrchestratorRuntime,
        session: SessionRuntime,
    ) -> RuntimeKernel:
        events.append("kernel")
        return RuntimeKernel(
            container=container,
            lifecycle=lifecycle,
            event_bus=event_bus,
            context=context,
            orchestrator=orchestrator,
            session=session,
        )

    class OrderedBootstrap(BootstrapRuntime):
        def build_context(self) -> ContextRuntime:
            events.append("context")
            return super().build_context()

        def build_container(self) -> ContainerRuntime:
            events.append("container")
            return super().build_container()

        def build_event_bus(self) -> EventBusRuntime:
            events.append("bus")
            return super().build_event_bus()

        def build_orchestrator(self, event_bus: EventBusRuntime) -> OrchestratorRuntime:
            events.append("orchestrator")
            return super().build_orchestrator(event_bus)

        def build_lifecycle(
            self,
            container: ContainerRuntime,
            event_bus: EventBusRuntime,
            context: ContextRuntime,
            orchestrator: OrchestratorRuntime,
        ) -> LifecycleRuntime:
            events.append("lifecycle")
            return super().build_lifecycle(container, event_bus, context, orchestrator)

    monkeypatch.setattr(bootstrap, "validate_configuration", validate)
    monkeypatch.setattr(bootstrap, "get_settings", get_settings)
    monkeypatch.setattr(bootstrap, "get_logger", logger)
    monkeypatch.setattr(bootstrap, "SessionRuntime", session_factory)
    monkeypatch.setattr(bootstrap, "RuntimeKernel", kernel_factory)
    runtime = await OrderedBootstrap().build()
    assert events == [
        "validation",
        "settings",
        "logging",
        "context",
        "session",
        "container",
        "bus",
        "orchestrator",
        "lifecycle",
        "kernel",
    ]
    assert runtime.status() is RuntimeStatus.CREATED
    assert not runtime.context.has_context() and not runtime.session.list()


async def test_public_builders_and_exact_participant_forward_reverse_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    builder = BootstrapRuntime()
    builder.validate_environment()
    owners = (
        builder.build_context(),
        builder.build_container(),
        builder.build_event_bus(),
    )
    active_context, container, bus = owners
    orchestrator = builder.build_orchestrator(bus)
    lifecycle = builder.build_lifecycle(container, bus, active_context, orchestrator)
    events: list[str] = []

    def recorder(name: str) -> Callable[[], Awaitable[None]]:
        async def record() -> None:
            events.append(name)

        return record

    for name, owner in (
        ("context", active_context),
        ("container", container),
        ("bus", bus),
        ("orchestrator", orchestrator),
    ):
        for operation in ("initialize", "start", "stop", "shutdown"):
            monkeypatch.setattr(owner, operation, recorder(name + "." + operation))
    await lifecycle.initialize()
    await lifecycle.start()
    await lifecycle.stop()
    await lifecycle.shutdown()
    assert events == [
        *(name + ".initialize" for name in ("context", "container", "bus", "orchestrator")),
        *(name + ".start" for name in ("context", "container", "bus", "orchestrator")),
        *(name + ".stop" for name in ("orchestrator", "bus", "container", "context")),
        *(name + ".shutdown" for name in ("orchestrator", "bus", "container", "context")),
    ]


@pytest.mark.parametrize(
    "stage",
    (
        "validate_environment",
        "build_context",
        "build_container",
        "build_event_bus",
        "build_orchestrator",
        "build_lifecycle",
    ),
)
@pytest.mark.parametrize(
    "error_type",
    (
        ValueError,
        ConfigurationError,
        asyncio.CancelledError,
        KeyboardInterrupt,
        SystemExit,
    ),
)
async def test_build_failures_have_exact_cause_and_never_initialize(
    stage: str,
    error_type: type[BaseException],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = error_type("sensitive input must not appear in wrapper")

    def fail(_self: BootstrapRuntime, *_args: object) -> Never:
        raise original

    monkeypatch.setattr(BootstrapRuntime, stage, fail)
    if isinstance(original, Exception) and not isinstance(original, ConfigurationError):
        with pytest.raises(RuntimeInitializationError) as caught:
            await BootstrapRuntime().build()
        assert caught.value.__cause__ is original
        assert "sensitive" not in str(caught.value)
    else:
        with pytest.raises(error_type) as caught:
            await BootstrapRuntime().build()
        assert caught.value is original


@pytest.mark.parametrize("component", range(5))
@pytest.mark.parametrize("value", tuple(HealthStatus))
async def test_health_aggregates_without_mutation(
    component: int,
    value: HealthStatus,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    owners: tuple[RuntimeContract, ...] = (
        runtime.container,
        runtime.lifecycle,
        runtime.event_bus,
        runtime.context,
        runtime.orchestrator,
    )
    monkeypatch.setattr(owners[component], "health", lambda: value)
    before = runtime.state()
    assert runtime.health() is value
    assert runtime.state() == before


@pytest.mark.parametrize(
    "status", tuple(s for s in RuntimeStatus if s is not RuntimeStatus.RUNNING)
)
async def test_execute_rejects_every_non_running_state_without_disposal(
    status: RuntimeStatus,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    if status is RuntimeStatus.FAILED:
        await runtime.lifecycle.transition(RuntimeStatus.INITIALIZING)
        await runtime.lifecycle.transition(RuntimeStatus.FAILED)
    else:
        for target in tuple(RuntimeStatus)[:9][1:]:
            if runtime.status() is status:
                break
            await runtime.lifecycle.transition(target)
    calls: list[PipelineId] = []

    async def clear(pipeline_id: PipelineId) -> None:
        calls.append(pipeline_id)

    monkeypatch.setattr(runtime.container, "clear_pipeline", clear)
    captured = context(runtime)
    with pytest.raises(RuntimeStateError):
        await runtime.execute(
            PipelineDefinition(pipeline_id=captured.pipeline_id, stages=()), context=captured
        )
    assert not calls and runtime.status() is status


@pytest.mark.parametrize("invalid", (None, {}, "wrong", 3))
async def test_invalid_pipeline_object_or_id_does_not_dispose(
    invalid: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await running()
    captured = context(runtime)
    calls: list[PipelineId] = []

    async def clear(pipeline_id: PipelineId) -> None:
        calls.append(pipeline_id)

    monkeypatch.setattr(runtime.container, "clear_pipeline", clear)
    for value in (
        cast(PipelineDefinition, invalid),
        PipelineDefinition(pipeline_id=cast(PipelineId, invalid), stages=()),
    ):
        with pytest.raises(InvalidManifestError):
            await runtime.execute(value, context=captured)
    assert not calls
    await finish(runtime)


@pytest.mark.parametrize(
    "status",
    (
        RuntimeStatus.INITIALIZING,
        RuntimeStatus.READY,
        RuntimeStatus.STARTING,
    ),
)
@pytest.mark.parametrize("operation", ("stop", "shutdown"))
async def test_partial_startup_cleanup_uses_only_legal_failed_transition(
    status: RuntimeStatus,
    operation: str,
) -> None:
    runtime = await BootstrapRuntime().build()
    if status is RuntimeStatus.INITIALIZING:
        await runtime.lifecycle.transition(status)
    else:
        await runtime.initialize()
        if status is RuntimeStatus.STARTING:
            await runtime.lifecycle.transition(status)
    captured = context(runtime)
    before = runtime.state()
    if operation == "stop":
        await runtime.stop()
    else:
        await runtime.shutdown()
    after = runtime.state()
    assert after.current is RuntimeStatus.FAILED and after.previous is before.current
    assert after.transition_count == before.transition_count + 1
    await runtime.shutdown()
    assert runtime.status() is RuntimeStatus.FAILED
    assert not runtime.session.contains(captured.session_id)
    assert not runtime.context.has_context()
    await runtime.stop()
    await runtime.shutdown()
    assert runtime.state() == after


async def test_illegal_cleanup_admission_does_not_remove_sessions() -> None:
    runtime = await BootstrapRuntime().build()
    captured = context(runtime)
    with pytest.raises(RuntimeStateError):
        await runtime.stop()
    with pytest.raises(RuntimeStateError):
        await runtime.shutdown()
    assert runtime.session.contains(captured.session_id)
    await runtime.initialize()
    await runtime.start()
    with pytest.raises(RuntimeStateError):
        await runtime.shutdown()
    assert runtime.session.contains(captured.session_id)
    await finish(runtime)


@pytest.mark.parametrize("selected", range(6))
async def test_busy_kernel_rejects_all_mutations_and_keeps_read_only_apis(
    selected: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await BootstrapRuntime().build()
    actions = mutations(runtime)
    entered, release = asyncio.Event(), asyncio.Event()

    async def initialize() -> None:
        entered.set()
        await release.wait()

    monkeypatch.setattr(runtime.lifecycle, "initialize", initialize)
    task = asyncio.create_task(runtime.initialize())
    try:
        await entered.wait()
        with pytest.raises(RuntimeStateError):
            await actions[selected]()
        assert runtime.status() is RuntimeStatus.CREATED
        assert runtime.state().current is RuntimeStatus.CREATED
        assert runtime.health() is HealthStatus.OK
        assert runtime.diagnostics()["runtime_status"] == "CREATED"
        assert runtime.session.list()
    finally:
        release.set()
        await task
    # The guard is released; another initialize reaches the delegate again.
    await runtime.initialize()


@pytest.mark.parametrize("invalid", (None, "bad", 1, {}))
async def test_invalid_or_missing_session_has_no_di_action(
    invalid: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await running()
    captured = context(runtime)
    calls: list[SessionId] = []

    async def clear(session_id: SessionId) -> None:
        calls.append(session_id)

    monkeypatch.setattr(runtime.container, "clear_session", clear)
    with pytest.raises(ContractValidationError):
        await runtime.remove_session(cast(SessionId, invalid))
    with pytest.raises(RuntimeStateError):
        await runtime.remove_session(SessionId(uuid4()))
    assert not calls and runtime.session.contains(captured.session_id)
    await finish(runtime)


def test_export_api_async_boundaries_and_import_direction() -> None:
    assert bootstrap.__all__ == ["BootstrapRuntime"]
    assert kernel_module.__all__ == ["RuntimeKernel"]
    for name in ("initialize", "start", "stop", "shutdown", "execute", "remove_session"):
        assert inspect.iscoroutinefunction(getattr(RuntimeKernel, name))
    assert inspect.iscoroutinefunction(BootstrapRuntime.build)
    paths = (
        Path(bootstrap.__file__),
        Path(kernel_module.__file__),
    )
    forbidden = {
        "executor",
        "manifest",
        "metadata",
        "provider",
        "resolver",
        "registry",
        "scope",
        "publisher",
        "dispatcher",
        "subscriber",
        "state",
        "hooks",
    }
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        assert not any(
            module
            and module.startswith("src.kernel.runtime.")
            and module.rsplit(".", 1)[-1] in forbidden
            for module in modules
        )
        assert not any(
            module
            and module.startswith(
                (
                    "src.state",
                    "src.layout",
                    "src.theme",
                    "src.platform",
                    "src.render",
                )
            )
            for module in modules
        )
