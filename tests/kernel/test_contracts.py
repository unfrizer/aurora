from __future__ import annotations

import ast
import importlib
import inspect
from abc import ABC
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import get_type_hints
from uuid import UUID, uuid4

import pytest

from src.core.types import (
    DIScope,
    EventId,
    EventPriority,
    HealthStatus,
    Metadata,
    ModuleId,
    Payload,
    PipelineId,
    RuntimeLayer,
    RuntimeStatus,
    ServiceId,
    SessionId,
    TraceId,
)
from src.kernel import contracts
from src.kernel.contracts import RuntimeContract
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.contracts.lifecycle import LifecycleContract, LifecycleState
from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor


def _trace() -> TraceContext:
    return TraceContext(trace_id=TraceId(uuid4()))


def test_contracts_are_immutable_and_complete() -> None:
    assert inspect.isabstract(RuntimeContract)
    manifest = RuntimeModuleManifest(
        module_id=ModuleId("kernel"),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        depends_on=(),
        provides=("runtime",),
        version="1.0",
    )
    assert manifest.provides == ("runtime",)
    assert manifest.depends_on == ()
    with pytest.raises(FrozenInstanceError):
        manifest.version = "changed"  # type: ignore[misc]
    state = LifecycleState(
        current=RuntimeStatus.CREATED,
        previous=None,
        entered_at=datetime.now(UTC),
        transition_count=0,
    )
    assert not state.is_terminal
    assert tuple(item.name for item in fields(LifecycleState)) == (
        "current",
        "previous",
        "entered_at",
        "transition_count",
    )
    with pytest.raises(FrozenInstanceError):
        state.current = RuntimeStatus.READY  # type: ignore[misc]


def test_runtime_context_and_event_are_frozen() -> None:
    context = RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=_trace(),
    )
    with pytest.raises(FrozenInstanceError):
        context.metadata = {}  # type: ignore[misc]
    event = RuntimeEvent(
        event_id=EventId(uuid4()),
        event_type="test.event",
        session_id=context.session_id,
        trace=context.trace,
        priority=EventPriority.HIGH,
    )
    assert event.priority is EventPriority.HIGH


class _Service(ServiceContract):
    def __init__(self) -> None:
        raise AssertionError("Contract must not construct services")

    async def initialize(self) -> None:
        raise AssertionError("Contract must not initialize services")

    async def shutdown(self) -> None:
        raise AssertionError("Contract must not dispose services")


def _descriptor() -> ServiceDescriptor:
    return ServiceDescriptor(
        service_id=ServiceId("service"), scope=DIScope.APPLICATION, implementation=_Service
    )


def _context() -> RuntimeContext:
    return RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=_trace(),
    )


def _event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id=EventId(uuid4()),
        event_type="test.event",
        session_id=SessionId(uuid4()),
        trace=_trace(),
    )


def test_service_descriptor_schema_and_annotations() -> None:
    schema = fields(ServiceDescriptor)
    assert tuple(item.name for item in schema) == (
        "service_id",
        "scope",
        "implementation",
        "eager",
        "dependencies",
    )
    annotations = get_type_hints(ServiceDescriptor)
    assert annotations["implementation"] == type[ServiceContract]
    assert annotations["dependencies"] == tuple[tuple[str, ServiceId], ...]
    assert all(item.default is MISSING for item in schema[:3])
    assert schema[3].default is False
    assert schema[4].default == ()


def test_descriptor_backward_compatibility_without_construction() -> None:
    descriptor = _descriptor()
    assert descriptor.implementation is _Service
    assert not descriptor.eager
    assert descriptor.dependencies == ()
    assert not hasattr(descriptor, "__dict__")


def test_descriptor_explicit_bindings_and_replace() -> None:
    shared = ServiceId("shared")
    bindings = (("first", shared), ("second", shared))
    descriptor = replace(_descriptor(), eager=True, dependencies=bindings)
    assert descriptor.dependencies == bindings
    assert descriptor.eager
    assert isinstance(descriptor.dependencies, tuple)
    assert all(isinstance(binding, tuple) for binding in descriptor.dependencies)
    assert replace(descriptor, service_id=ServiceId("other")).dependencies == bindings


def test_descriptor_validation_remains_owned_by_di() -> None:
    # KR-005 owns shape/graph validation, not this contract constructor.
    duplicate = (("dependency", ServiceId("missing")),) * 2
    assert replace(_descriptor(), dependencies=duplicate).dependencies == duplicate


def test_descriptor_frozen_keyword_only_and_required_fields() -> None:
    descriptor = _descriptor()
    with pytest.raises(FrozenInstanceError):
        descriptor.dependencies = ()  # type: ignore[misc]
    parameters = inspect.signature(ServiceDescriptor).parameters
    assert all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in parameters.values())
    assert all(
        parameters[name].default is inspect.Parameter.empty
        for name in ("service_id", "scope", "implementation")
    )


@pytest.mark.parametrize(
    ("contract", "names"),
    [
        (ServiceContract, frozenset({"initialize", "shutdown"})),
        (EventHandlerContract, frozenset({"handle"})),
        (LifecycleContract, frozenset({"transition", "state"})),
        (
            RuntimeContract,
            frozenset(
                {
                    "runtime_name",
                    "runtime_layer",
                    "initialize",
                    "start",
                    "stop",
                    "shutdown",
                    "health",
                }
            ),
        ),
    ],
)
def test_abstract_contract_surfaces(contract: type[ABC], names: frozenset[str]) -> None:
    assert inspect.isabstract(contract)
    assert contract.__abstractmethods__ == names
    with pytest.raises(TypeError, match="abstract"):
        contract()


def test_async_contract_methods() -> None:
    assert inspect.iscoroutinefunction(ServiceContract.initialize)
    assert inspect.iscoroutinefunction(ServiceContract.shutdown)
    assert inspect.iscoroutinefunction(EventHandlerContract.handle)
    assert inspect.iscoroutinefunction(LifecycleContract.transition)
    assert not inspect.iscoroutinefunction(LifecycleContract.state)
    assert not inspect.iscoroutinefunction(RuntimeContract.health)
    assert all(
        inspect.iscoroutinefunction(method)
        for method in (
            RuntimeContract.initialize,
            RuntimeContract.start,
            RuntimeContract.stop,
            RuntimeContract.shutdown,
        )
    )


@pytest.mark.parametrize(
    "contract",
    [
        ServiceDescriptor,
        RuntimeContext,
        TraceContext,
        RuntimeEvent,
        RuntimeModuleManifest,
        LifecycleState,
    ],
)
def test_snapshot_contracts_are_slotted_keyword_only(contract: type[object]) -> None:
    assert "__slots__" in vars(contract)
    assert all(
        item.kind is inspect.Parameter.KEYWORD_ONLY
        for item in inspect.signature(contract).parameters.values()
    )


def test_manifest_required_schema() -> None:
    schema = fields(RuntimeModuleManifest)
    assert tuple(item.name for item in schema) == (
        "module_id",
        "runtime_layer",
        "depends_on",
        "provides",
        "version",
    )
    assert all(item.default is MISSING and item.default_factory is MISSING for item in schema)


def test_context_and_trace_schema_and_properties() -> None:
    assert tuple(item.name for item in fields(RuntimeContext)) == (
        "session_id",
        "pipeline_id",
        "runtime_layer",
        "trace",
        "metadata",
        "created_at",
        "expires_at",
    )
    assert tuple(item.name for item in fields(TraceContext)) == (
        "trace_id",
        "parent_trace_id",
        "correlation_id",
    )
    context = _context()
    assert context.created_at.tzinfo is UTC
    assert not context.is_expired
    assert context.trace_id == context.root_trace_id == context.trace.trace_id
    assert context.depth == 0
    parent = TraceId(uuid4())
    child = replace(context, trace=replace(context.trace, parent_trace_id=parent))
    assert child.root_trace_id == parent and child.depth == 1
    assert replace(context, expires_at=datetime.now(UTC) - timedelta(days=1)).is_expired
    assert not replace(context, expires_at=datetime.now(UTC) + timedelta(days=1)).is_expired


def test_event_schema_defaults_and_frozen_trace() -> None:
    schema = fields(RuntimeEvent)
    assert tuple(item.name for item in schema) == (
        "event_id",
        "event_type",
        "session_id",
        "trace",
        "priority",
        "timestamp",
        "payload",
    )
    assert all(item.default is MISSING and item.default_factory is MISSING for item in schema[:4])
    event = _event()
    assert event.priority is EventPriority.NORMAL
    assert event.timestamp.tzinfo is UTC
    assert event.payload == {} and not hasattr(event, "__dict__")
    with pytest.raises(FrozenInstanceError):
        event.payload = {}  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        event.trace.trace_id = TraceId(uuid4())  # type: ignore[misc]


def test_json_defaults_are_independent_not_deep_freezing() -> None:
    first, second = _context(), _context()
    event, other = _event(), _event()
    first.metadata["nested"] = {"items": ["local"]}
    event.payload["nested"] = {"items": ["local"]}
    assert second.metadata == {} and other.payload == {}
    assert first.metadata is not second.metadata and event.payload is not other.payload
    # Boundary detachment belongs to KR-007/KR-008, not dataclass construction.
    assert first.metadata["nested"] == {"items": ["local"]}


@pytest.mark.parametrize("status", list(RuntimeStatus))
def test_lifecycle_snapshot_properties(status: RuntimeStatus) -> None:
    state = LifecycleState(
        current=status, previous=None, entered_at=datetime.now(UTC), transition_count=0
    )
    assert state.is_running == (status is RuntimeStatus.RUNNING)
    assert state.is_ready == (status is RuntimeStatus.READY)
    assert state.is_failed == (status is RuntimeStatus.FAILED)
    assert state.is_terminal == (status in {RuntimeStatus.FAILED, RuntimeStatus.TERMINATED})


def test_package_exports_unchanged() -> None:
    assert set(contracts.__all__) == {
        "EventHandlerContract",
        "LifecycleContract",
        "LifecycleState",
        "RuntimeContext",
        "RuntimeContract",
        "RuntimeEvent",
        "RuntimeModuleManifest",
        "ServiceContract",
        "ServiceDescriptor",
        "TraceContext",
    }


@pytest.mark.parametrize(
    ("contract", "annotations"),
    [
        (
            TraceContext,
            {"trace_id": TraceId, "parent_trace_id": TraceId | None, "correlation_id": UUID | None},
        ),
        (
            RuntimeContext,
            {
                "session_id": SessionId,
                "pipeline_id": PipelineId,
                "runtime_layer": RuntimeLayer,
                "trace": TraceContext,
                "metadata": Metadata,
                "created_at": datetime,
                "expires_at": datetime | None,
            },
        ),
        (
            RuntimeEvent,
            {
                "event_id": EventId,
                "event_type": str,
                "session_id": SessionId,
                "trace": TraceContext,
                "priority": EventPriority,
                "timestamp": datetime,
                "payload": Payload,
            },
        ),
        (
            RuntimeModuleManifest,
            {
                "module_id": ModuleId,
                "runtime_layer": RuntimeLayer,
                "depends_on": tuple[ModuleId, ...],
                "provides": tuple[str, ...],
                "version": str,
            },
        ),
        (
            LifecycleState,
            {
                "current": RuntimeStatus,
                "previous": RuntimeStatus | None,
                "entered_at": datetime,
                "transition_count": int,
            },
        ),
        (
            ServiceDescriptor,
            {
                "service_id": ServiceId,
                "scope": DIScope,
                "implementation": type[ServiceContract],
                "eager": bool,
                "dependencies": tuple[tuple[str, ServiceId], ...],
            },
        ),
    ],
)
def test_exact_dataclass_annotations_and_default_order(
    contract: type[object],
    annotations: dict[str, object],
) -> None:
    assert get_type_hints(contract) == annotations
    assert is_dataclass(contract)
    default_seen = False
    for item in fields(contract):
        has_default = item.default is not MISSING or item.default_factory is not MISSING
        assert not default_seen or has_default
        default_seen |= has_default
        assert item.kw_only
        assert not isinstance(item.default, (dict, list, set))


def test_all_dataclass_fields_are_frozen_not_only_selected_fields() -> None:
    snapshots = (
        _trace(),
        _context(),
        _event(),
        _descriptor(),
        RuntimeModuleManifest(
            module_id=ModuleId("synthetic"),
            runtime_layer=RuntimeLayer.L0_KERNEL,
            depends_on=(),
            provides=(),
            version="1.0",
        ),
        LifecycleState(
            current=RuntimeStatus.READY,
            previous=RuntimeStatus.INITIALIZING,
            entered_at=datetime.now(UTC),
            transition_count=2,
        ),
    )
    for snapshot in snapshots:
        assert not hasattr(snapshot, "__dict__")
        for item in fields(snapshot):
            original = getattr(snapshot, item.name)
            with pytest.raises(FrozenInstanceError):
                setattr(snapshot, item.name, original)
            assert getattr(snapshot, item.name) == original


@pytest.mark.parametrize(
    ("count", "timestamp", "message"),
    [
        (-1, datetime.now(UTC), "transition_count must be non-negative"),
        (0, datetime(2026, 1, 1), "entered_at must be timezone-aware"),
    ],
)
def test_lifecycle_snapshot_existing_invariants(
    count: int,
    timestamp: datetime,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        LifecycleState(
            current=RuntimeStatus.CREATED,
            previous=None,
            entered_at=timestamp,
            transition_count=count,
        )


def test_direct_contract_construction_does_not_validate_or_detach_json() -> None:
    metadata: Metadata = {"nested": ["synthetic"]}
    context = replace(_context(), metadata=metadata)
    payload: Payload = {"nested": ["synthetic"]}
    event = replace(_event(), payload=payload, event_type="")
    assert context.metadata is metadata and event.payload is payload
    assert event.event_type == ""
    assert "__post_init__" not in vars(RuntimeContext)
    assert "__post_init__" not in vars(RuntimeEvent)
    assert "__post_init__" not in vars(ServiceDescriptor)
    assert "__post_init__" not in vars(RuntimeModuleManifest)


@pytest.mark.parametrize(
    ("module", "exports"),
    [
        ("context", {"RuntimeContext", "TraceContext"}),
        ("events", {"EventHandlerContract", "RuntimeEvent"}),
        ("lifecycle", {"LifecycleContract", "LifecycleState"}),
        ("module", {"RuntimeModuleManifest"}),
        ("runtime", {"RuntimeContract"}),
        ("service", {"ServiceContract", "ServiceDescriptor"}),
    ],
)
def test_individual_contract_exports_and_downward_imports(module: str, exports: set[str]) -> None:
    imported = importlib.import_module("src.kernel.contracts." + module)
    assert set(imported.__all__) == exports
    for name in exports:
        assert getattr(imported, name) is getattr(contracts, name)
    assert imported.__file__ is not None
    tree = ast.parse(Path(imported.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module is not None and node.level == 0
            assert node.module.startswith(("src.core.", "src.kernel.contracts.")) or (
                node.module in {"__future__", "abc", "dataclasses", "datetime", "uuid"}
            )
        elif isinstance(node, ast.Import):
            pytest.fail("Contract imports must retain their explicit downward boundary")


def test_abstract_signatures_are_verified_without_invoking_stubs() -> None:
    signatures: tuple[tuple[object, dict[str, object]], ...] = (
        (ServiceContract.initialize, {"return": type(None)}),
        (ServiceContract.shutdown, {"return": type(None)}),
        (EventHandlerContract.handle, {"event": RuntimeEvent, "return": type(None)}),
        (LifecycleContract.transition, {"target": RuntimeStatus, "return": type(None)}),
        (LifecycleContract.state, {"return": LifecycleState}),
        (RuntimeContract.initialize, {"return": type(None)}),
        (RuntimeContract.start, {"return": type(None)}),
        (RuntimeContract.stop, {"return": type(None)}),
        (RuntimeContract.shutdown, {"return": type(None)}),
        (RuntimeContract.health, {"return": HealthStatus}),
    )
    for method, hints in signatures:
        assert get_type_hints(method) == hints
        assert tuple(inspect.signature(method).parameters) == (
            "self",
            *(name for name in hints if name != "return"),
        )
    for name, annotation in (("runtime_name", str), ("runtime_layer", RuntimeLayer)):
        descriptor = vars(RuntimeContract)[name]
        assert isinstance(descriptor, property) and descriptor.fget is not None
        assert get_type_hints(descriptor.fget) == {"return": annotation}
