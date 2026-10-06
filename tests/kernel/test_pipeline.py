"""Canonical KR-009 acceptance: graphs, real work, snapshots and failure semantics."""

from __future__ import annotations

import ast
import asyncio
import inspect
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import (
    ContractValidationError,
    EventHandlerError,
    InvalidManifestError,
    RuntimeDependencyError,
    RuntimeLayerError,
    RuntimeStateError,
)
from src.core.types import (
    EventPriority,
    HealthStatus,
    JSONValue,
    Metadata,
    ModuleId,
    Payload,
    PipelineId,
    RuntimeLayer,
    SessionId,
    TraceId,
)
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime import executor, manifest, orchestrator, pipeline
from src.kernel.runtime.bootstrap import BootstrapRuntime
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.executor import ExecutorRuntime
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.orchestrator import OrchestratorRuntime
from src.kernel.runtime.pipeline import PipelineDefinition, PipelineStage


class RecordingBus(EventBusRuntime):
    """Use the real Publisher factory; inject deterministic delivery/creation faults."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[RuntimeEvent] = []
        self.attempts: list[str] = []
        self.failures: dict[str, list[BaseException]] = {}
        self.creation_failures: dict[str, list[BaseException]] = {}

    def create_for_runtime(
        self,
        *,
        event_type: str,
        payload: Payload,
        context: RuntimeContext,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> RuntimeEvent:
        self.attempts.append(event_type)
        failures = self.creation_failures.get(event_type, [])
        if failures:
            raise failures.pop(0)
        return super().create_for_runtime(
            event_type=event_type, payload=payload, context=context, priority=priority
        )

    async def publish(self, event: RuntimeEvent) -> None:
        self.events.append(event)
        failures = self.failures.get(event.event_type, [])
        if failures:
            raise failures.pop(0)
        await super().publish(event)


class Collector(EventHandlerContract):
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    async def handle(self, event: RuntimeEvent) -> None:
        self.events.append(event)


class FailingHandler(EventHandlerContract):
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def handle(self, event: RuntimeEvent) -> None:
        raise self.error


class CallableOperation:
    def __init__(self) -> None:
        self.contexts: list[RuntimeContext] = []

    async def __call__(self, context: RuntimeContext) -> None:
        self.contexts.append(context)


def make_context(metadata: Metadata | None = None) -> RuntimeContext:
    return RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=TraceContext(
            trace_id=TraceId(uuid4()), parent_trace_id=TraceId(uuid4()), correlation_id=uuid4()
        ),
        metadata={} if metadata is None else metadata,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        expires_at=datetime(2026, 1, 2, tzinfo=UTC),
    )


def make_stage(
    name: str = "a", *, module: str | None = None, depends: tuple[str, ...] = ()
) -> PipelineStage:
    return PipelineStage(
        stage_id=name, module_id=ModuleId(name if module is None else module), depends_on=depends
    )


def make_pipeline(context: RuntimeContext, *stages: PipelineStage) -> PipelineDefinition:
    return PipelineDefinition(pipeline_id=context.pipeline_id, stages=stages or (make_stage(),))


def make_manifest(
    name: str = "a", *, depends: tuple[str, ...] = (), layer: RuntimeLayer = RuntimeLayer.L0_KERNEL
) -> RuntimeModuleManifest:
    return RuntimeModuleManifest(
        module_id=ModuleId(name),
        runtime_layer=layer,
        depends_on=tuple(ModuleId(item) for item in depends),
        provides=(),
        version="opaque",
    )


async def noop(context: RuntimeContext) -> None:
    del context


def prepare(
    *,
    operation: Callable[[RuntimeContext], Awaitable[None]] = noop,
) -> tuple[OrchestratorRuntime, RecordingBus]:
    bus = RecordingBus()
    runtime = OrchestratorRuntime(bus)
    runtime.register_module(make_manifest(), operation=operation)
    return runtime, bus


def event_types(bus: RecordingBus) -> list[str]:
    return [event.event_type for event in bus.events]


def group_errors(error: BaseException) -> tuple[BaseException, ...]:
    assert isinstance(cast(object, error.__cause__), BaseExceptionGroup)
    pending = list(cast(BaseExceptionGroup[BaseException], error.__cause__).exceptions)
    ordered: list[BaseException] = []
    while pending:
        current = pending.pop(0)
        if isinstance(current, BaseExceptionGroup):
            pending[:0] = cast(BaseExceptionGroup[BaseException], current).exceptions
        else:
            ordered.append(current)
    return tuple(ordered)


def test_models_exports_and_retained_properties() -> None:
    stage = make_stage()
    dependent = make_stage("b", depends=("a", "a"))
    context = make_context()
    definition = make_pipeline(context, stage, dependent)
    empty = PipelineDefinition(pipeline_id=context.pipeline_id, stages=())
    assert stage.dependency_count == 0 and not stage.has_dependencies
    assert dependent.dependency_count == 2 and dependent.has_dependencies
    assert definition.stage_count == 2 and not definition.is_empty
    assert empty.stage_count == 0 and empty.is_empty
    assert [field.name for field in fields(stage)] == ["stage_id", "module_id", "depends_on"]
    assert [field.name for field in fields(definition)] == ["pipeline_id", "stages"]
    field_name = "stage_id"
    with pytest.raises(FrozenInstanceError):
        setattr(stage, field_name, "other")
    assert not hasattr(stage, "__dict__")
    assert pipeline.__all__ == ["PipelineDefinition", "PipelineStage"]
    assert manifest.__all__ == ["ManifestRuntime"]
    assert executor.__all__ == ["ExecutorRuntime"]
    assert orchestrator.__all__ == ["OrchestratorRuntime"]
    assert not issubclass(ExecutorRuntime, RuntimeContract)
    assert not hasattr(ExecutorRuntime, "health")


@pytest.mark.parametrize(
    "method",
    [
        "validate",
        "validate_stage_ids",
        "validate_dependencies",
        "validate_dag",
    ],
)
@pytest.mark.parametrize(
    "case",
    [
        "object",
        "id",
        "empty",
        "list",
        "stage",
        "stage-id",
        "module-id",
        "unicode",
        "dependencies-list",
        "dependency-empty",
        "dependency-unicode",
        "duplicate",
    ],
)
def test_manifest_public_methods_reject_malformed_shape(method: str, case: str) -> None:
    context = make_context()
    definition = make_pipeline(context)
    stage = definition.stages[0]
    if case == "object":
        definition = cast(PipelineDefinition, object())
    elif case == "id":
        definition = replace(definition, pipeline_id=cast(PipelineId, "invalid"))
    elif case == "empty":
        definition = replace(definition, stages=())
    elif case == "list":
        definition = replace(definition, stages=cast(tuple[PipelineStage, ...], [stage]))
    elif case == "stage":
        definition = replace(definition, stages=(cast(PipelineStage, object()),))
    elif case == "stage-id":
        definition = replace(definition, stages=(replace(stage, stage_id=""),))
    elif case == "module-id":
        definition = replace(definition, stages=(replace(stage, module_id=ModuleId("")),))
    elif case == "unicode":
        definition = replace(definition, stages=(replace(stage, stage_id="\ud800"),))
    elif case == "dependencies-list":
        definition = replace(
            definition, stages=(replace(stage, depends_on=cast(tuple[str, ...], ["a"])),)
        )
    elif case == "dependency-empty":
        definition = replace(definition, stages=(replace(stage, depends_on=("",)),))
    elif case == "dependency-unicode":
        definition = replace(definition, stages=(replace(stage, depends_on=("\ud800",)),))
    else:
        definition = replace(definition, stages=(stage, stage))
    validator = ManifestRuntime()
    methods: dict[str, Callable[[PipelineDefinition], object]] = {
        "validate": validator.validate,
        "validate_stage_ids": validator.validate_stage_ids,
        "validate_dependencies": validator.validate_dependencies,
        "validate_dag": validator.validate_dag,
    }
    with pytest.raises(InvalidManifestError):
        methods[method](definition)


@pytest.mark.parametrize("depends", [("a",), ("missing",)])
@pytest.mark.parametrize("method", ["validate", "validate_dependencies", "validate_dag"])
def test_invalid_dependency_references(depends: tuple[str, ...], method: str) -> None:
    definition = make_pipeline(make_context(), make_stage(depends=depends))
    validator = ManifestRuntime()
    methods = {
        "validate": validator.validate,
        "validate_dependencies": validator.validate_dependencies,
        "validate_dag": validator.validate_dag,
    }
    with pytest.raises(InvalidManifestError):
        methods[method](definition)


def test_same_object_redundant_edges_unicode_and_stable_wavefront() -> None:
    context = make_context()
    stages = (make_stage(" A "), make_stage("B", depends=(" A ", " A ")), make_stage("Я"))
    definition = make_pipeline(context, *stages)
    assert ManifestRuntime().validate(definition) is definition
    assert ExecutorRuntime(EventBusRuntime()).execution_order(definition) == (
        stages[0],
        stages[2],
        stages[1],
    )
    assert definition.stages == stages
    assert stages[1].depends_on == (" A ", " A ")


def test_cycle_and_deep_dag_are_iterative() -> None:
    context = make_context()
    cycle = make_pipeline(context, make_stage("a", depends=("b",)), make_stage("b", depends=("a",)))
    for validate in (ManifestRuntime().validate, ManifestRuntime().validate_dag):
        with pytest.raises(RuntimeDependencyError):
            validate(cycle)
    with pytest.raises(RuntimeDependencyError):
        ExecutorRuntime(EventBusRuntime()).execution_order(cycle)
    stages = tuple(make_stage(str(i), depends=() if i == 0 else (str(i - 1),)) for i in range(1100))
    definition = make_pipeline(context, *reversed(stages))
    assert ManifestRuntime().validate(definition) is definition
    assert ExecutorRuntime(EventBusRuntime()).execution_order(definition) == stages


@pytest.mark.parametrize(
    "case",
    [
        "object",
        "id-empty",
        "id-unicode",
        "version-empty",
        "version-unicode",
        "version-object",
        "layer",
        "depends-list",
        "provides-list",
        "dependency-empty",
        "provides-empty",
        "dependency-unicode",
        "provides-unicode",
    ],
)
def test_registration_rejects_invalid_manifest_without_mutation(case: str) -> None:
    runtime, _ = prepare()
    value = make_manifest("other")
    if case == "object":
        value = cast(RuntimeModuleManifest, object())
    elif case == "id-empty":
        value = replace(value, module_id=ModuleId(""))
    elif case == "id-unicode":
        value = replace(value, module_id=ModuleId("\ud800"))
    elif case == "version-empty":
        value = replace(value, version="")
    elif case == "version-unicode":
        value = replace(value, version="\ud800")
    elif case == "version-object":
        value = replace(value, version=cast(str, 12))
    elif case == "layer":
        value = replace(value, runtime_layer=cast(RuntimeLayer, "L0_KERNEL"))
    elif case == "depends-list":
        value = replace(value, depends_on=cast(tuple[ModuleId, ...], []))
    elif case == "provides-list":
        value = replace(value, provides=cast(tuple[str, ...], []))
    elif case == "dependency-empty":
        value = replace(value, depends_on=(ModuleId(""),))
    elif case == "provides-empty":
        value = replace(value, provides=("",))
    elif case == "dependency-unicode":
        value = replace(value, depends_on=(ModuleId("\ud800"),))
    else:
        value = replace(value, provides=("\ud800",))
    before = runtime.modules()
    with pytest.raises(InvalidManifestError):
        runtime.register_module(value, operation=noop)
    assert runtime.modules() == before


async def test_registration_lifecycle_shutdown_and_instance_ownership() -> None:
    runtime, bus = prepare()
    other = OrchestratorRuntime(bus)
    assert isinstance(runtime, RuntimeContract)
    assert (
        runtime.runtime_name == "orchestrator" and runtime.runtime_layer is RuntimeLayer.L0_KERNEL
    )
    assert runtime.health() is HealthStatus.OK
    assert runtime.contains(ModuleId("a")) and not other.contains(ModuleId("a"))
    with pytest.raises(InvalidManifestError):
        runtime.register_module(make_manifest(), operation=noop)
    with pytest.raises(InvalidManifestError):
        runtime.register_module(
            make_manifest("bad"), operation=cast(Callable[[RuntimeContext], Awaitable[None]], 1)
        )
    with pytest.raises(InvalidManifestError):
        runtime.unregister_module(ModuleId("absent"))
    assert len(runtime.modules()) == 1
    runtime.unregister_module(ModuleId("a"))
    assert not runtime.contains(ModuleId("a"))
    runtime.register_module(make_manifest())
    runtime.unregister_module(ModuleId("a"))
    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    await runtime.shutdown()
    await runtime.shutdown()
    assert runtime.modules() == ()
    runtime.register_module(make_manifest(), operation=noop)
    context = make_context()
    await runtime.execute(make_pipeline(context), context=context)


async def test_real_work_event_schema_context_isolation_and_repeated_module() -> None:
    original: Metadata = {"nested": {"values": [1]}, "shared": {"label": "original"}}
    context = make_context(original)
    effects: list[str] = []
    received: list[RuntimeContext] = []

    async def operation(snapshot: RuntimeContext) -> None:
        effects.append(cast(str, snapshot.metadata["stage_id"]))
        received.append(snapshot)
        nested = cast(Metadata, snapshot.metadata["nested"])
        cast(list[JSONValue], nested["values"]).append(2)
        cast(Metadata, original["shared"])["label"] = "caller edit"

    runtime, bus = prepare(operation=operation)
    stages = (
        make_stage("a"),
        make_stage("b", module="a", depends=("a",)),
        make_stage("c", module="a"),
    )
    definition = make_pipeline(context, *stages)
    assert await runtime.execute(definition, context=context) is None
    assert effects == ["a", "c", "b"]
    assert event_types(bus) == [
        "pipeline.started",
        "pipeline.stage.started",
        "pipeline.stage.completed",
        "pipeline.stage.started",
        "pipeline.stage.completed",
        "pipeline.stage.started",
        "pipeline.stage.completed",
        "pipeline.completed",
    ]
    assert [item.metadata["stage_index"] for item in received] == [0, 1, 2]
    for snapshot in received:
        assert snapshot is not context
        assert (
            snapshot.session_id == context.session_id
            and snapshot.pipeline_id == context.pipeline_id
        )
        assert snapshot.trace == context.trace and snapshot.created_at == context.created_at
        assert snapshot.expires_at == context.expires_at and snapshot.is_expired
        assert snapshot.runtime_layer is context.runtime_layer
        assert cast(Metadata, snapshot.metadata["shared"])["label"] == "original"
        assert cast(list[JSONValue], cast(Metadata, snapshot.metadata["nested"])["values"]) == [
            1,
            2,
        ]
        assert snapshot.metadata["module_id"] == "a" and snapshot.metadata["stage_count"] == 3
        assert isinstance(snapshot.metadata["execution_started_at"], str)
    assert original["nested"] == {"values": [1]}
    assert "stage_id" not in context.metadata
    assert bus.events[0].payload == {
        "pipeline_id": str(context.pipeline_id),
        "session_id": str(context.session_id),
    }
    for event in bus.events:
        assert event.priority is EventPriority.NORMAL
        assert event.trace == context.trace and event.session_id == context.session_id
        if ".stage." in event.event_type:
            assert set(event.payload) == {
                "pipeline_id",
                "stage_id",
                "module_id",
                "duration_ms",
                "reason",
            }
            assert event.payload["module_id"] == "a" and event.payload["reason"] is None
            if event.event_type.endswith("started"):
                assert event.payload["duration_ms"] is None
            else:
                duration = cast(float, event.payload["duration_ms"])
                assert isinstance(duration, float) and isfinite(duration) and duration >= 0
    terminal = bus.events[-1]
    assert set(terminal.payload) == {"pipeline_id", "duration_ms", "stage_count"}
    assert terminal.payload["stage_count"] == 3


@pytest.mark.parametrize("case", ["missing", "metadata-only", "id", "context"])
async def test_orchestrator_preflight_has_no_events_or_effects(case: str) -> None:
    operation = CallableOperation()
    runtime, bus = prepare(operation=operation)
    context = make_context()
    definition = make_pipeline(context)
    error: type[Exception] = InvalidManifestError
    if case == "missing":
        runtime.unregister_module(ModuleId("a"))
    elif case == "metadata-only":
        runtime.unregister_module(ModuleId("a"))
        runtime.register_module(make_manifest())
    elif case == "id":
        definition = replace(definition, pipeline_id=PipelineId(uuid4()))
    else:
        context = cast(RuntimeContext, object())
        error = ContractValidationError
    with pytest.raises(error):
        await runtime.execute(definition, context=context)
    assert not bus.attempts and not operation.contexts
    if not runtime.contains(ModuleId("a")):
        runtime.register_module(make_manifest(), operation=operation)
    elif case == "metadata-only":
        runtime.unregister_module(ModuleId("a"))
        runtime.register_module(make_manifest(), operation=operation)
    good = make_context()
    await runtime.execute(make_pipeline(good), context=good)
    assert len(operation.contexts) == 1


@pytest.mark.parametrize("case", ["missing", "cycle", "layer", "self"])
async def test_module_graph_preflight_errors(case: str) -> None:
    bus = RecordingBus()
    runtime = OrchestratorRuntime(bus)
    runtime.register_module(
        make_manifest("a", depends=("a",) if case == "self" else ("b",)), operation=noop
    )
    expected: type[Exception] = RuntimeDependencyError
    if case == "cycle":
        runtime.register_module(make_manifest("b", depends=("a",)))
    elif case == "layer":
        runtime.register_module(make_manifest("b", layer=RuntimeLayer.L1_STATE))
        expected = RuntimeLayerError
    context = make_context()
    with pytest.raises(expected):
        await runtime.execute(make_pipeline(context), context=context)
    assert bus.attempts == []


async def test_forward_dependencies_metadata_only_and_unregister_without_cascade() -> None:
    bus = RecordingBus()
    runtime = OrchestratorRuntime(bus)
    runtime.register_module(make_manifest("a", depends=("b", "b", "c")), operation=noop)
    runtime.register_module(make_manifest("b", depends=("c",)))
    runtime.register_module(make_manifest("c"))
    context = make_context()
    await runtime.execute(make_pipeline(context), context=context)
    assert len(bus.events) == 4
    runtime.unregister_module(ModuleId("c"))
    assert runtime.contains(ModuleId("a")) and runtime.contains(ModuleId("b"))
    before = len(bus.events)
    with pytest.raises(RuntimeDependencyError):
        await runtime.execute(make_pipeline(context), context=context)
    assert len(bus.events) == before
    runtime.register_module(make_manifest("c"))
    await runtime.execute(make_pipeline(context), context=context)


async def test_deep_module_graph_and_unreachable_invalid_module() -> None:
    runtime, _ = prepare()
    for i in range(1100):
        runtime.register_module(
            make_manifest(str(i), depends=() if i == 0 else (str(i - 1),)),
            operation=noop if i == 1099 else None,
        )
    runtime.register_module(make_manifest("unreachable", depends=("missing",)))
    context = make_context()
    await runtime.execute(make_pipeline(context, make_stage(module="1099")), context=context)


@pytest.mark.parametrize(
    "case",
    [
        "object",
        "trace",
        "session",
        "pipeline",
        "layer",
        "trace-id",
        "parent",
        "correlation",
        "created-none",
        "created-object",
        "created-naive",
        "expires-naive",
        "expires-object",
        "created-offset",
        "expires-offset",
    ],
)
async def test_context_validation_and_guard_recovery(case: str) -> None:
    context = make_context()
    if case == "object":
        context = cast(RuntimeContext, object())
    elif case == "trace":
        context = replace(context, trace=cast(TraceContext, object()))
    elif case == "session":
        context = replace(context, session_id=cast(SessionId, "bad"))
    elif case == "pipeline":
        context = replace(context, pipeline_id=cast(PipelineId, "bad"))
    elif case == "layer":
        context = replace(context, runtime_layer=cast(RuntimeLayer, "bad"))
    elif case == "trace-id":
        context = replace(context, trace=replace(context.trace, trace_id=cast(TraceId, "bad")))
    elif case == "parent":
        context = replace(
            context, trace=replace(context.trace, parent_trace_id=cast(TraceId, "bad"))
        )
    elif case == "correlation":
        context = replace(context, trace=replace(context.trace, correlation_id=cast(UUID, "bad")))
    elif case == "created-none":
        context = replace(context, created_at=cast(datetime, None))
    elif case == "created-object":
        context = replace(context, created_at=cast(datetime, "bad"))
    elif case == "created-naive":
        context = replace(context, created_at=datetime(2026, 1, 1))
    elif case == "expires-naive":
        context = replace(context, expires_at=datetime(2026, 1, 1))
    elif case == "expires-object":
        context = replace(context, expires_at=cast(datetime, "bad"))
    elif case == "created-offset":
        context = replace(
            context, created_at=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1)))
        )
    else:
        context = replace(
            context, expires_at=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1)))
        )
    bus = RecordingBus()
    runner = ExecutorRuntime(bus)
    good = make_context()
    with pytest.raises(ContractValidationError):
        await runner.execute(make_pipeline(good), context=context, operations={ModuleId("a"): noop})
    assert not bus.attempts
    await runner.execute(make_pipeline(good), context=good, operations={ModuleId("a"): noop})


@pytest.mark.parametrize("bad", [float("inf"), float("nan"), object(), "\ud800", (1,), {1: 2}])
async def test_invalid_metadata_is_rejected_without_events(bad: object) -> None:
    context = make_context({"bad": cast(JSONValue, bad)})
    runtime, bus = prepare()
    with pytest.raises(ContractValidationError):
        await runtime.execute(make_pipeline(context), context=context)
    assert not bus.attempts


async def test_json_cycles_repeated_references_and_depth_boundary() -> None:
    runtime, bus = prepare()
    cyclic: Metadata = {}
    cyclic["cycle"] = cyclic
    context = make_context(cyclic)
    with pytest.raises(ContractValidationError):
        await runtime.execute(make_pipeline(context), context=context)
    assert not bus.attempts
    for depth in (256, 257):
        root: Metadata = {}
        cursor = root
        for _ in range(depth - 1):
            child: Metadata = {}
            cursor["child"] = child
            cursor = child
        context = make_context(root)
        if depth == 256:
            await runtime.execute(make_pipeline(context), context=context)
        else:
            before = len(bus.events)
            with pytest.raises(ContractValidationError):
                await runtime.execute(make_pipeline(context), context=context)
            assert len(bus.events) == before
    shared: Metadata = {"value": []}
    context = make_context({"one": shared, "two": shared})
    operation = CallableOperation()
    runtime, _ = prepare(operation=operation)
    await runtime.execute(make_pipeline(context), context=context)
    captured = operation.contexts[0].metadata
    assert captured["one"] == captured["two"]
    assert captured["one"] is not captured["two"]
    assert captured["one"] is not shared


@pytest.mark.parametrize("case", ["mapping", "empty", "binding"])
async def test_direct_executor_binding_validation(case: str) -> None:
    context = make_context()
    bus = RecordingBus()
    runner = ExecutorRuntime(bus)
    bindings: Mapping[ModuleId, Callable[[RuntimeContext], Awaitable[None]]] = {ModuleId("a"): noop}
    if case == "mapping":
        bindings = cast(Mapping[ModuleId, Callable[[RuntimeContext], Awaitable[None]]], [])
    elif case == "empty":
        bindings = {}
    else:
        bindings = {ModuleId("a"): cast(Callable[[RuntimeContext], Awaitable[None]], 4)}
    with pytest.raises(InvalidManifestError):
        await runner.execute(make_pipeline(context), context=context, operations=bindings)
    assert not bus.attempts


async def test_direct_stage_and_binding_capture() -> None:
    context = make_context()
    bus = RecordingBus()
    runner = ExecutorRuntime(bus)
    operation = CallableOperation()
    await runner.execute_stage(
        make_stage(depends=("external",)), context=context, operation=operation
    )
    assert operation.contexts[0].metadata["stage_index"] == 0
    assert event_types(bus) == ["pipeline.stage.started", "pipeline.stage.completed"]
    with pytest.raises(InvalidManifestError):
        await runner.execute_stage(
            make_stage(),
            context=context,
            operation=cast(Callable[[RuntimeContext], Awaitable[None]], None),
        )
    bindings: dict[ModuleId, Callable[[RuntimeContext], Awaitable[None]]] = {}

    async def mutate(snapshot: RuntimeContext) -> None:
        del snapshot
        bindings.clear()

    bindings.update({ModuleId("a"): mutate, ModuleId("b"): operation})
    await runner.execute(
        make_pipeline(context, make_stage(), make_stage("b")), context=context, operations=bindings
    )
    assert len(operation.contexts) == 2


@pytest.mark.parametrize("notification_errors", [False, True])
async def test_primary_failure_abort_secondary_order_and_safe_messages(
    notification_errors: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    primary = ValueError("SECRET raw callback text")
    earlier = KeyError("SECRET earlier")
    primary.__cause__ = earlier

    async def fail(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=fail)
    context = make_context({"password": "SECRET payload"})
    definition = make_pipeline(context, make_stage(), make_stage("later", module="a"))
    stage_error, pipeline_error = RuntimeError("SECRET stage"), LookupError("SECRET terminal")
    if notification_errors:
        bus.failures["pipeline.stage.failed"] = [stage_error]
        bus.failures["pipeline.failed"] = [pipeline_error]
    with pytest.raises(ValueError) as caught:
        await runtime.execute(definition, context=context)
    assert caught.value is primary
    assert event_types(bus) == [
        "pipeline.started",
        "pipeline.stage.started",
        "pipeline.stage.failed",
        "pipeline.failed",
    ]
    assert (
        group_errors(primary) == (earlier, stage_error, pipeline_error)
        if (notification_errors)
        else primary.__cause__ is earlier
    )
    assert all("SECRET" not in str(event.payload) for event in bus.events)
    assert "SECRET" not in caplog.text
    assert bus.events[-1].priority is EventPriority.HIGH
    assert set(bus.events[-1].payload) == {
        "pipeline_id",
        "failed_stage",
        "reason",
        "exception_type",
    }
    assert bus.events[-1].payload["failed_stage"] == "a"
    assert bus.events[-1].payload["exception_type"] == "ValueError"
    assert bus.events[-2].priority is EventPriority.HIGH
    duration = cast(float, bus.events[-2].payload["duration_ms"])
    assert isfinite(duration) and duration >= 0
    runtime.unregister_module(ModuleId("a"))
    runtime.register_module(make_manifest(), operation=noop)
    await runtime.execute(definition, context=context)


@pytest.mark.parametrize(
    "event_type",
    [
        "pipeline.started",
        "pipeline.stage.started",
        "pipeline.stage.completed",
        "pipeline.completed",
    ],
)
@pytest.mark.parametrize("creation", [False, True])
async def test_event_failures_exact_terminal_attempt(event_type: str, creation: bool) -> None:
    operation = CallableOperation()
    runtime, bus = prepare(operation=operation)
    primary = RuntimeError("sensitive delivery")
    target = bus.creation_failures if creation else bus.failures
    target[event_type] = [primary]
    context = make_context()
    with pytest.raises(RuntimeError) as caught:
        await runtime.execute(make_pipeline(context), context=context)
    assert caught.value is primary
    terminals = [
        name
        for name in bus.attempts
        if name
        in (
            "pipeline.completed",
            "pipeline.failed",
            "pipeline.cancelled",
        )
    ]
    assert terminals == [
        "pipeline.completed" if event_type == "pipeline.completed" else "pipeline.failed"
    ]
    if event_type == "pipeline.stage.completed":
        assert ("pipeline.stage.failed" in bus.attempts) is creation
    if event_type == "pipeline.started":
        assert not operation.contexts and bus.events[-1].payload["failed_stage"] == ""
    if event_type == "pipeline.stage.started":
        assert not operation.contexts
    await runtime.execute(make_pipeline(context), context=context)


async def test_real_event_handler_failure_is_not_masked() -> None:
    runtime, bus = prepare()
    original = ValueError("secret handler")
    failing = FailingHandler(original)
    collector = Collector()
    bus.subscribe("pipeline.stage.started", failing)
    bus.subscribe("pipeline.failed", collector)
    context = make_context()
    with pytest.raises(EventHandlerError) as caught:
        await runtime.execute(make_pipeline(context), context=context)
    assert caught.value.__cause__ is original
    assert len(collector.events) == 1 and collector.events[0].event_type == "pipeline.failed"
    bus.unsubscribe("pipeline.stage.started", failing)
    await runtime.execute(make_pipeline(context), context=context)


@pytest.mark.parametrize(
    "where", ["operation", "start", "stage-start", "stage-complete", "terminal"]
)
@pytest.mark.parametrize("secondary", ["none", "error", "cancel"])
async def test_cancellation_preserved_and_no_second_terminal(where: str, secondary: str) -> None:
    primary = asyncio.CancelledError("SECRET cancellation")

    async def cancel(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=cancel if where == "operation" else noop)
    if where != "operation":
        event = {
            "start": "pipeline.started",
            "stage-start": "pipeline.stage.started",
            "stage-complete": "pipeline.stage.completed",
            "terminal": "pipeline.completed",
        }[where]
        bus.failures[event] = [primary]
    notification: BaseException | None = None
    if secondary != "none":
        notification = (
            RuntimeError("SECRET notification")
            if secondary == "error"
            else (asyncio.CancelledError("SECRET second cancellation"))
        )
        bus.failures["pipeline.cancelled"] = [notification]
    context = make_context()
    with pytest.raises(asyncio.CancelledError) as caught:
        await runtime.execute(make_pipeline(context), context=context)
    assert caught.value is primary
    terminals = [
        item
        for item in bus.attempts
        if item
        in (
            "pipeline.completed",
            "pipeline.cancelled",
            "pipeline.failed",
        )
    ]
    assert terminals == ["pipeline.completed" if where == "terminal" else "pipeline.cancelled"]
    assert "pipeline.stage.failed" not in bus.attempts
    if where != "terminal":
        assert bus.events[-1].priority is EventPriority.HIGH
        assert set(bus.events[-1].payload) == {"pipeline_id", "reason"}
        if notification is not None:
            assert group_errors(primary) == (notification,)
    runtime.unregister_module(ModuleId("a"))
    runtime.register_module(make_manifest(), operation=noop)
    await runtime.execute(make_pipeline(context), context=context)


async def test_secondary_cancellation_does_not_replace_ordinary_failure() -> None:
    primary = ValueError("primary")
    cancelled = asyncio.CancelledError("secondary")

    async def fail(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=fail)
    bus.failures["pipeline.stage.failed"] = [cancelled]
    context = make_context()
    with pytest.raises(ValueError) as caught:
        await runtime.execute(make_pipeline(context), context=context)
    assert caught.value is primary and group_errors(primary) == (cancelled,)
    assert event_types(bus)[-1] == "pipeline.failed"


async def test_notification_same_primary_never_groups_itself() -> None:
    primary = ValueError("same")

    async def fail(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=fail)
    bus.failures["pipeline.stage.failed"] = [primary]
    bus.failures["pipeline.failed"] = [RuntimeError("other")]
    context = make_context()
    with pytest.raises(ValueError) as caught:
        await runtime.execute(make_pipeline(context), context=context)
    assert caught.value is primary
    assert primary not in group_errors(primary) and len(group_errors(primary)) == 1


@pytest.mark.parametrize("error", [KeyboardInterrupt, SystemExit])
async def test_process_control_exceptions_not_business_failures(error: type[BaseException]) -> None:
    primary = error()

    async def fail(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=fail)
    context = make_context()
    with pytest.raises(error):
        await runtime.execute(make_pipeline(context), context=context)
    assert event_types(bus) == ["pipeline.started", "pipeline.stage.started"]
    runtime.unregister_module(ModuleId("a"))


async def test_callable_nonawaitable_result_is_not_success() -> None:
    def invalid(context: RuntimeContext) -> None:
        del context

    runtime, bus = prepare(operation=cast(Callable[[RuntimeContext], Awaitable[None]], invalid))
    context = make_context()
    with pytest.raises(TypeError):
        await runtime.execute(make_pipeline(context), context=context)
    assert event_types(bus)[-2:] == ["pipeline.stage.failed", "pipeline.failed"]


async def test_reentrant_orchestrator_read_only_and_mutation_guards() -> None:
    context = make_context()
    runtime, bus = prepare()
    definition = make_pipeline(context)

    async def reenter(snapshot: RuntimeContext) -> None:
        assert snapshot.pipeline_id == context.pipeline_id
        assert runtime.contains(ModuleId("a")) and len(runtime.modules()) == 1
        assert runtime.health() is HealthStatus.OK
        with pytest.raises(RuntimeStateError):
            runtime.register_module(make_manifest("other"), operation=noop)
        with pytest.raises(RuntimeStateError):
            runtime.unregister_module(ModuleId("a"))
        with pytest.raises(RuntimeStateError):
            await runtime.shutdown()
        with pytest.raises(RuntimeStateError):
            await runtime.execute(definition, context=context)

    runtime.unregister_module(ModuleId("a"))
    runtime.register_module(make_manifest(), operation=reenter)
    await runtime.execute(definition, context=context)
    assert event_types(bus)[-1] == "pipeline.completed"
    assert not runtime.contains(ModuleId("other"))
    await runtime.shutdown()


@pytest.mark.parametrize("direct", [False, True])
async def test_concurrent_execution_cancellation_releases_guards(direct: bool) -> None:
    entered, release = asyncio.Event(), asyncio.Event()
    context = make_context()
    definition = make_pipeline(context)

    async def block(snapshot: RuntimeContext) -> None:
        del snapshot
        entered.set()
        await release.wait()

    bus = RecordingBus()
    runner = ExecutorRuntime(bus)
    runtime = OrchestratorRuntime(bus)
    runtime.register_module(make_manifest(), operation=block)
    task = asyncio.create_task(
        runner.execute(definition, context=context, operations={ModuleId("a"): block})
        if direct
        else runtime.execute(definition, context=context)
    )
    await asyncio.wait_for(entered.wait(), timeout=5)
    if direct:
        with pytest.raises(RuntimeStateError):
            await runner.execute(definition, context=context, operations={ModuleId("a"): noop})
        with pytest.raises(RuntimeStateError):
            await runner.execute_stage(make_stage(), context=context, operation=noop)
    else:
        with pytest.raises(RuntimeStateError):
            await runtime.execute(definition, context=context)
        with pytest.raises(RuntimeStateError):
            runtime.register_module(make_manifest("other"), operation=noop)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    if direct:
        await runner.execute_stage(make_stage(), context=context, operation=noop)
        await runner.execute(definition, context=context, operations={ModuleId("a"): noop})
    else:
        runtime.unregister_module(ModuleId("a"))
        runtime.register_module(make_manifest(), operation=noop)
        await runtime.execute(definition, context=context)


async def test_standalone_stage_failure_cancellation_and_validation_release() -> None:
    bus = RecordingBus()
    runner = ExecutorRuntime(bus)
    context = make_context()
    for primary in (ValueError("failure"), asyncio.CancelledError("cancel")):

        async def fail(snapshot: RuntimeContext, *, error: BaseException = primary) -> None:
            del snapshot
            raise error

        with pytest.raises(type(primary)) as caught:
            await runner.execute_stage(make_stage(), context=context, operation=fail)
        assert caught.value is primary
        await runner.execute_stage(make_stage(), context=context, operation=noop)
    with pytest.raises(InvalidManifestError):
        await runner.execute_stage(make_stage(""), context=context, operation=noop)
    await runner.execute_stage(make_stage(), context=context, operation=noop)


async def test_minimal_bootstrap_migration_same_bus_and_no_internal_executor_import() -> None:
    bus = RecordingBus()
    runtime = BootstrapRuntime().build_orchestrator(bus)
    runtime.register_module(make_manifest(), operation=noop)
    context = make_context()
    await runtime.execute(make_pipeline(context), context=context)
    assert event_types(bus)[0] == "pipeline.started"
    source = Path(inspect.getfile(BootstrapRuntime)).read_text(encoding="utf-8")
    imports = [
        node.module for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ImportFrom)
    ]
    assert "src.kernel.runtime.executor" not in imports


def test_owned_import_boundaries_no_direct_event_factory_or_hidden_owner() -> None:
    forbidden = (
        "src.kernel.runtime.container",
        "src.kernel.runtime.context",
        "src.kernel.runtime.session",
        "src.kernel.runtime.publisher",
        "src.kernel.runtime.dispatcher",
        "src.kernel.runtime.subscriber",
    )
    for module in (pipeline, manifest, executor, orchestrator):
        source = Path(inspect.getfile(module)).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        assert not any(item in forbidden for item in imports)
        assert all(
            item is None
            or not item.startswith(
                (
                    "src.state",
                    "src.layout",
                    "src.theme",
                    "src.motion",
                    "src.interaction",
                    "src.accessibility",
                    "src.platform",
                    "src.render",
                )
            )
            for item in imports
        )
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "RuntimeEvent"
            for node in ast.walk(tree)
        )
        assert "Any" not in source and "type: ignore" not in source


@pytest.mark.parametrize("kind", ["error", "cancel"])
async def test_creation_failure_of_terminal_notification_preserves_primary(kind: str) -> None:
    primary: BaseException = (
        ValueError("primary")
        if kind == "error"
        else (asyncio.CancelledError("primary cancellation"))
    )
    secondary = LookupError("notification construction")

    async def fail(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=fail)
    terminal = "pipeline.failed" if kind == "error" else "pipeline.cancelled"
    bus.creation_failures[terminal] = [secondary]
    context = make_context()
    with pytest.raises(type(primary)) as caught:
        await runtime.execute(make_pipeline(context), context=context)
    assert caught.value is primary and group_errors(primary) == (secondary,)
    assert [
        item
        for item in bus.attempts
        if item
        in (
            "pipeline.failed",
            "pipeline.completed",
            "pipeline.cancelled",
        )
    ] == [terminal]


async def test_original_explicit_group_retained_even_with_matching_message() -> None:
    original = ExceptionGroup("Pipeline notification failures", [KeyError("earlier")])
    primary = ValueError("primary")
    primary.__cause__ = original
    secondary = RuntimeError("secondary")

    async def fail(context: RuntimeContext) -> None:
        del context
        raise primary

    runtime, bus = prepare(operation=fail)
    bus.failures["pipeline.stage.failed"] = [secondary]
    context = make_context()
    with pytest.raises(ValueError):
        await runtime.execute(make_pipeline(context), context=context)
    cause = cast(BaseExceptionGroup[BaseException], primary.__cause__)
    assert cause.exceptions == (original, secondary)


async def test_standalone_reentry_and_valid_downward_module_edge() -> None:
    context = make_context()
    bus = RecordingBus()
    runner = ExecutorRuntime(bus)

    async def reenter(snapshot: RuntimeContext) -> None:
        assert snapshot.trace == context.trace
        with pytest.raises(RuntimeStateError):
            await runner.execute_stage(make_stage(), context=context, operation=noop)
        with pytest.raises(RuntimeStateError):
            await runner.execute(
                make_pipeline(context), context=context, operations={ModuleId("a"): noop}
            )

    await runner.execute_stage(make_stage(), context=context, operation=reenter)
    runtime = OrchestratorRuntime(bus)
    runtime.register_module(
        make_manifest("a", depends=("base",), layer=RuntimeLayer.L8_RENDER), operation=noop
    )
    runtime.register_module(replace(make_manifest("base"), provides=("service",)))
    await runtime.execute(make_pipeline(context), context=context)
