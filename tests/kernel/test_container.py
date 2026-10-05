from __future__ import annotations

import asyncio
import gc
import weakref
from collections.abc import Awaitable, Callable
from typing import cast
from uuid import uuid4

import pytest

from src.core.exceptions import (
    CircularDependencyError,
    RuntimeShutdownError,
    RuntimeStateError,
    ScopeViolationError,
    ServiceRegistrationError,
    ServiceResolutionError,
)
from src.core.types import DIScope, PipelineId, RuntimeLayer, ServiceId, SessionId, TraceId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.container import ContainerRuntime
from src.kernel.runtime.scope import ScopeRuntime


class ExampleService(ServiceContract):
    def __init__(self) -> None:
        self.ready = False
        self.initializations = 0
        self.shutdowns = 0

    async def initialize(self) -> None:
        self.initializations += 1
        self.ready = True

    async def shutdown(self) -> None:
        self.shutdowns += 1
        self.ready = False


class Consumer(ExampleService):
    def __init__(self, *, dependency: ServiceContract) -> None:
        super().__init__()
        self.dependency = dependency


class PairConsumer(ExampleService):
    def __init__(self, *, first: ServiceContract, second: ServiceContract) -> None:
        super().__init__()
        self.first = first
        self.second = second


def _context(
    session: SessionId | None = None, pipeline: PipelineId | None = None
) -> RuntimeContext:
    return RuntimeContext(
        session_id=session or SessionId(uuid4()),
        pipeline_id=pipeline or PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=TraceContext(trace_id=TraceId(uuid4())),
    )


def _descriptor(
    name: str,
    implementation: type[ServiceContract] = ExampleService,
    scope: DIScope = DIScope.APPLICATION,
    *,
    dependencies: tuple[tuple[str, ServiceId], ...] = (),
    eager: bool = False,
) -> ServiceDescriptor:
    return ServiceDescriptor(
        service_id=ServiceId(name),
        implementation=implementation,
        scope=scope,
        dependencies=dependencies,
        eager=eager,
    )


def _tracked(
    label: str,
    log: list[str],
    *,
    initialize: Callable[[], Awaitable[None]] | None = None,
    shutdown: Callable[[], Awaitable[None]] | None = None,
) -> type[ExampleService]:
    class Tracked(ExampleService):
        def __init__(self) -> None:
            super().__init__()
            log.append(f"construct:{label}")

        async def initialize(self) -> None:
            log.append(f"initialize:{label}")
            if initialize is not None:
                await initialize()
            await super().initialize()

        async def shutdown(self) -> None:
            log.append(f"shutdown:{label}")
            if shutdown is not None:
                await shutdown()
            await super().shutdown()

    return Tracked


async def test_application_service_is_ready_cached_and_removable() -> None:
    container = ContainerRuntime()
    descriptor = _descriptor("example")
    container.register(descriptor)
    first = cast(ExampleService, await container.resolve(descriptor.service_id))
    assert first.ready and first.initializations == 1
    assert await container.resolve(descriptor.service_id) is first
    await container.initialize()
    await container.initialize()
    assert first.initializations == 1
    await container.remove(descriptor.service_id)
    assert not container.contains(descriptor.service_id)
    assert first.shutdowns == 1
    container.register(descriptor)
    assert await container.resolve(descriptor.service_id) is not first
    await container.shutdown()
    await container.shutdown()


async def test_forward_explicit_bindings_and_cached_duplicate_parameters() -> None:
    container = ContainerRuntime()
    container.register(
        _descriptor(
            "pair",
            PairConsumer,
            dependencies=(("first", ServiceId("leaf")), ("second", ServiceId("leaf"))),
        )
    )
    container.register(_descriptor("leaf"))
    service = cast(PairConsumer, await container.resolve(ServiceId("pair")))
    assert service.ready and service.first is service.second
    assert cast(ExampleService, service.first).ready
    await container.shutdown()


@pytest.mark.parametrize("owner", tuple(DIScope))
@pytest.mark.parametrize("dependency_scope", tuple(DIScope))
async def test_all_sixteen_scope_edges(owner: DIScope, dependency_scope: DIScope) -> None:
    container = ContainerRuntime()
    container.register(_descriptor("leaf", scope=dependency_scope))
    container.register(
        _descriptor("owner", Consumer, owner, dependencies=(("dependency", ServiceId("leaf")),))
    )
    allowed = (
        owner is DIScope.TRANSIENT
        or dependency_scope is DIScope.APPLICATION
        or (owner is DIScope.SESSION and dependency_scope is DIScope.SESSION)
        or (owner is DIScope.PIPELINE and dependency_scope is not DIScope.TRANSIENT)
    )
    if allowed:
        service = cast(Consumer, await container.resolve(ServiceId("owner"), context=_context()))
        assert service.ready and cast(ExampleService, service.dependency).ready
    else:
        with pytest.raises(ScopeViolationError):
            await container.resolve(ServiceId("owner"), context=_context())
    await container.shutdown()


@pytest.mark.parametrize("scope", (DIScope.SESSION, DIScope.PIPELINE))
async def test_context_required_and_scoped_identities(scope: DIScope) -> None:
    container = ContainerRuntime()
    container.register(_descriptor("service", scope=scope))
    with pytest.raises(ScopeViolationError):
        await container.resolve(ServiceId("service"))
    one = _context()
    same_session = _context(one.session_id)
    other = _context()
    first = await container.resolve(ServiceId("service"), context=one)
    assert await container.resolve(ServiceId("service"), context=one) is first
    second = await container.resolve(ServiceId("service"), context=same_session)
    assert (second is first) is (scope is DIScope.SESSION)
    assert await container.resolve(ServiceId("service"), context=other) is not first
    with pytest.raises(ScopeViolationError):
        await container.resolve(
            ServiceId("service"), context=_context(other.session_id, one.pipeline_id)
        )
    await container.shutdown()


@pytest.mark.parametrize("problem", ("missing", "cycle", "scope"))
async def test_complete_preflight_precedes_every_constructor(problem: str) -> None:
    log: list[str] = []
    container = ContainerRuntime()
    container.register(_descriptor("first", _tracked("first", log)))
    target = "absent"
    if problem == "cycle":
        target = "root"
    elif problem == "scope":
        target = "short"
        container.register(_descriptor("short", scope=DIScope.TRANSIENT))
    container.register(
        _descriptor(
            "root",
            PairConsumer,
            dependencies=(("first", ServiceId("first")), ("second", ServiceId(target))),
        )
    )
    error_type = {
        "missing": ServiceResolutionError,
        "cycle": CircularDependencyError,
        "scope": ScopeViolationError,
    }[problem]
    with pytest.raises(error_type):
        await container.resolve(ServiceId("root"))
    assert log == []
    await container.shutdown()


async def test_eager_dependency_order_once_and_atomic_failure_retry() -> None:
    log: list[str] = []
    fail = True

    async def initialize() -> None:
        if fail:
            raise ValueError("initialize")

    class EagerConsumer(Consumer):
        async def initialize(self) -> None:
            log.append("initialize:root")
            await initialize()
            await super().initialize()

        async def shutdown(self) -> None:
            log.append("shutdown:root")
            await super().shutdown()

    container = ContainerRuntime()
    container.register(
        _descriptor(
            "root", EagerConsumer, dependencies=(("dependency", ServiceId("leaf")),), eager=True
        )
    )
    container.register(_descriptor("leaf", _tracked("leaf", log)))
    with pytest.raises(ServiceResolutionError) as caught:
        await container.initialize()
    assert isinstance(caught.value.__cause__, ValueError)
    assert log == [
        "construct:leaf",
        "initialize:leaf",
        "initialize:root",
        "shutdown:root",
        "shutdown:leaf",
    ]
    fail = False
    await container.initialize()
    count = len(log)
    await container.initialize()
    assert len(log) == count
    root = cast(Consumer, await container.resolve(ServiceId("root")))
    assert root.ready and cast(ExampleService, root.dependency).initializations == 1
    await container.shutdown()


async def test_eager_graph_checks_unresolved_non_eager_registration() -> None:
    log: list[str] = []
    container = ContainerRuntime()
    container.register(_descriptor("eager", _tracked("eager", log), eager=True))
    container.register(
        _descriptor("bad", Consumer, dependencies=(("dependency", ServiceId("missing")),))
    )
    with pytest.raises(ServiceResolutionError):
        await container.initialize()
    assert log == []
    await container.shutdown()


async def test_failed_acquisition_preserves_previously_ready_dependency() -> None:
    log: list[str] = []

    async def fail() -> None:
        raise ValueError("initialize")

    class Broken(Consumer):
        async def initialize(self) -> None:
            await fail()

        async def shutdown(self) -> None:
            log.append("shutdown:broken")

    container = ContainerRuntime()
    container.register(_descriptor("leaf", _tracked("leaf", log)))
    container.register(
        _descriptor("broken", Broken, dependencies=(("dependency", ServiceId("leaf")),))
    )
    leaf = await container.resolve(ServiceId("leaf"))
    with pytest.raises(ServiceResolutionError):
        await container.resolve(ServiceId("broken"))
    assert await container.resolve(ServiceId("leaf")) is leaf
    assert log == ["construct:leaf", "initialize:leaf", "shutdown:broken"]
    await container.shutdown()


async def test_constructor_error_is_chained_and_rolls_back_new_dependency() -> None:
    log: list[str] = []
    original = LookupError("construction")

    class Broken(Consumer):
        def __init__(self, *, dependency: ServiceContract) -> None:
            del dependency
            raise original

    container = ContainerRuntime()
    container.register(_descriptor("leaf", _tracked("leaf", log)))
    container.register(
        _descriptor("broken", Broken, dependencies=(("dependency", ServiceId("leaf")),))
    )
    with pytest.raises(ServiceResolutionError) as caught:
        await container.resolve(ServiceId("broken"))
    assert caught.value.__cause__ is original
    assert log == ["construct:leaf", "initialize:leaf", "shutdown:leaf"]
    await container.shutdown()


async def test_transient_descendants_release_not_independent_instances() -> None:
    container = ContainerRuntime()
    container.register(_descriptor("leaf", scope=DIScope.TRANSIENT))
    container.register(
        _descriptor(
            "pair",
            PairConsumer,
            DIScope.TRANSIENT,
            dependencies=(("first", ServiceId("leaf")), ("second", ServiceId("leaf"))),
        )
    )
    independent = cast(ExampleService, await container.resolve(ServiceId("leaf")))
    root = cast(PairConsumer, await container.resolve(ServiceId("pair")))
    first, second = cast(ExampleService, root.first), cast(ExampleService, root.second)
    assert first is not second and first is not independent
    await container.release(first)
    await container.release(root)
    await container.release(root)
    assert first.shutdowns == second.shutdowns == root.shutdowns == 1
    assert independent.shutdowns == 0
    await container.release(independent)
    await container.shutdown()


async def test_release_rejects_unknown_and_cached_without_retaining_released() -> None:
    container = ContainerRuntime()
    container.register(_descriptor("cached"))
    container.register(_descriptor("transient", scope=DIScope.TRANSIENT))
    with pytest.raises(ScopeViolationError):
        await container.release(ExampleService())
    with pytest.raises(ScopeViolationError):
        await container.release(await container.resolve(ServiceId("cached")))
    service = await container.resolve(ServiceId("transient"))
    reference = weakref.ref(service)
    await container.release(service)
    del service
    gc.collect()
    assert reference() is None
    await container.shutdown()


async def test_scoped_clear_disposes_transients_and_dependent_scopes_only() -> None:
    container = ContainerRuntime()
    for scope in DIScope:
        container.register(_descriptor(scope.value, scope=scope))
    one, other = _context(), _context()
    first = {
        scope: cast(ExampleService, await container.resolve(ServiceId(scope.value), context=one))
        for scope in DIScope
    }
    second = {
        scope: cast(ExampleService, await container.resolve(ServiceId(scope.value), context=other))
        for scope in DIScope
    }
    await container.clear_pipeline(one.pipeline_id)
    assert first[DIScope.PIPELINE].shutdowns == first[DIScope.TRANSIENT].shutdowns == 1
    assert first[DIScope.SESSION].shutdowns == first[DIScope.APPLICATION].shutdowns == 0
    assert second[DIScope.PIPELINE].shutdowns == 0
    replacement = cast(ExampleService, await container.resolve(ServiceId("pipeline"), context=one))
    assert replacement is not first[DIScope.PIPELINE]
    await container.clear_session(one.session_id)
    await container.clear_session(one.session_id)
    assert replacement.shutdowns == first[DIScope.SESSION].shutdowns == 1
    assert second[DIScope.SESSION].shutdowns == 0
    await container.shutdown()
    assert all(service.shutdowns == 1 for service in (*first.values(), *second.values()))


async def test_remove_consumer_guard_missing_and_replacement_after_disposal_error() -> None:
    failure = ValueError("shutdown")

    async def broken_shutdown() -> None:
        raise failure

    container = ContainerRuntime()
    descriptor = _descriptor("leaf", _tracked("leaf", [], shutdown=broken_shutdown))
    container.register(descriptor)
    container.register(
        _descriptor("consumer", Consumer, dependencies=(("dependency", ServiceId("leaf")),))
    )
    with pytest.raises(ServiceRegistrationError):
        await container.remove(ServiceId("leaf"))
    assert container.contains(ServiceId("leaf"))
    await container.remove(ServiceId("consumer"))
    old = await container.resolve(ServiceId("leaf"))
    with pytest.raises(RuntimeShutdownError) as caught:
        await container.remove(ServiceId("leaf"))
    cause = caught.value.__cause__
    assert isinstance(cause, ExceptionGroup)
    assert cast(ExceptionGroup[Exception], cause).exceptions == (failure,)
    assert not container.contains(ServiceId("leaf"))
    container.register(_descriptor("leaf"))
    assert await container.resolve(ServiceId("leaf")) is not old
    with pytest.raises(ServiceResolutionError):
        await container.remove(ServiceId("missing"))
    await container.shutdown()


async def test_remove_all_scoped_instances_reverse_order_before_callbacks() -> None:
    log: list[str] = []
    container = ContainerRuntime()

    async def check_evicted() -> None:
        assert not container.contains(ServiceId("service"))
        with pytest.raises(RuntimeStateError):
            await container.resolve(ServiceId("service"))

    implementation = _tracked("service", log, shutdown=check_evicted)
    container.register(_descriptor("service", implementation, DIScope.SESSION))
    for _ in range(3):
        await container.resolve(ServiceId("service"), context=_context())
    await container.remove(ServiceId("service"))
    assert log.count("shutdown:service") == 3
    container.register(_descriptor("service", scope=DIScope.SESSION))
    await container.resolve(ServiceId("service"), context=_context())
    await container.shutdown()


async def test_multiple_cleanup_errors_preserve_reverse_order_and_do_not_repeat() -> None:
    log: list[str] = []
    first_error, second_error = ValueError("first"), LookupError("second")

    async def fail_first() -> None:
        raise first_error

    async def fail_second() -> None:
        raise second_error

    container = ContainerRuntime()
    container.register(_descriptor("first", _tracked("first", log, shutdown=fail_first)))
    container.register(_descriptor("second", _tracked("second", log, shutdown=fail_second)))
    await container.resolve(ServiceId("first"))
    await container.resolve(ServiceId("second"))
    with pytest.raises(RuntimeShutdownError) as caught:
        await container.shutdown()
    group = cast(ExceptionGroup[Exception], caught.value.__cause__)
    assert group.exceptions == (second_error, first_error)
    assert log[-2:] == ["shutdown:second", "shutdown:first"]
    await container.shutdown()
    assert log.count("shutdown:first") == log.count("shutdown:second") == 1
    assert container.contains(ServiceId("first"))
    for operation in (container.resolve(ServiceId("first")), container.remove(ServiceId("first"))):
        with pytest.raises(RuntimeStateError):
            await operation
    with pytest.raises(RuntimeStateError):
        container.register(_descriptor("third"))


async def test_original_operation_error_precedes_rollback_failures() -> None:
    original, cleanup = ValueError("initialize"), LookupError("shutdown")

    async def fail_initialize() -> None:
        raise original

    async def fail_shutdown() -> None:
        raise cleanup

    container = ContainerRuntime()
    container.register(
        _descriptor("bad", _tracked("bad", [], initialize=fail_initialize, shutdown=fail_shutdown))
    )
    with pytest.raises(ServiceResolutionError) as caught:
        await container.resolve(ServiceId("bad"))
    assert cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions == (original, cleanup)
    await container.shutdown()


async def test_acquisition_cancellation_rolls_back_before_propagation() -> None:
    log: list[str] = []
    entered = asyncio.Event()

    async def wait_initialize() -> None:
        entered.set()
        await asyncio.Event().wait()

    container = ContainerRuntime()
    container.register(_descriptor("wait", _tracked("wait", log, initialize=wait_initialize)))
    task = asyncio.create_task(container.resolve(ServiceId("wait")))
    await entered.wait()
    with pytest.raises(RuntimeStateError):
        await container.resolve(ServiceId("wait"))
    with pytest.raises(RuntimeStateError):
        container.register(_descriptor("new"))
    with pytest.raises(RuntimeStateError):
        await container.shutdown()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert log == ["construct:wait", "initialize:wait", "shutdown:wait"]
    await container.shutdown()


async def test_second_cancellation_keeps_partial_acquisition_owned_for_shutdown() -> None:
    log: list[str] = []
    initialized, disposing = asyncio.Event(), asyncio.Event()
    resume = asyncio.Event()

    async def wait_initialize() -> None:
        initialized.set()
        await asyncio.Event().wait()

    async def wait_shutdown() -> None:
        disposing.set()
        await resume.wait()

    container = ContainerRuntime()
    container.register(
        _descriptor(
            "wait", _tracked("wait", log, initialize=wait_initialize, shutdown=wait_shutdown)
        )
    )
    task = asyncio.create_task(container.resolve(ServiceId("wait")))
    await initialized.wait()
    task.cancel()
    await disposing.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert log.count("shutdown:wait") == 1
    resume.set()
    await container.shutdown()
    await container.shutdown()
    assert log.count("shutdown:wait") == 2


async def test_interrupted_shutdown_retries_only_pending_instances() -> None:
    log: list[str] = []
    disposing, resume = asyncio.Event(), asyncio.Event()

    async def wait_shutdown() -> None:
        disposing.set()
        await resume.wait()

    container = ContainerRuntime()
    container.register(_descriptor("wait", _tracked("wait", log, shutdown=wait_shutdown)))
    container.register(_descriptor("ready", _tracked("ready", log)))
    await container.resolve(ServiceId("wait"))
    await container.resolve(ServiceId("ready"))
    task = asyncio.create_task(container.shutdown())
    await disposing.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert log.count("shutdown:ready") == 1
    resume.set()
    await container.shutdown()
    assert log.count("shutdown:ready") == 1
    assert log.count("shutdown:wait") == 2


async def test_reentrant_initialization_rejected_and_rolled_back() -> None:
    log: list[str] = []
    container = ContainerRuntime()

    async def reenter() -> None:
        await container.resolve(ServiceId("reentrant"))

    container.register(_descriptor("reentrant", _tracked("reentrant", log, initialize=reenter)))
    with pytest.raises(ServiceResolutionError) as caught:
        await container.resolve(ServiceId("reentrant"))
    assert isinstance(caught.value.__cause__, RuntimeStateError)
    assert log[-1] == "shutdown:reentrant"
    await container.shutdown()


async def test_default_parameters_and_annotations_are_not_evaluated() -> None:
    class Defaults(ExampleService):
        def __init__(self, *, text: str = "default") -> None:
            super().__init__()
            self.text = text

    Defaults.__init__.__annotations__["text"] = "1 / 0"
    container = ContainerRuntime()
    container.register(_descriptor("defaults", Defaults))
    value = cast(Defaults, await container.resolve(ServiceId("defaults")))
    assert value.text == "default"
    await container.shutdown()


@pytest.mark.parametrize(
    "bindings",
    (
        (),
        (("unknown", ServiceId("target")),),
        (("dependency", ServiceId("target")), ("dependency", ServiceId("target"))),
        (("", ServiceId("target")),),
        (("dependency", ServiceId("")),),
        (("class", ServiceId("target")),),
    ),
)
def test_invalid_constructor_bindings_rejected_at_registration(
    bindings: tuple[tuple[str, ServiceId], ...],
) -> None:
    container = ContainerRuntime()
    with pytest.raises(ServiceRegistrationError):
        container.register(_descriptor("invalid", Consumer, dependencies=bindings))
    assert container.descriptors() == ()


def test_duplicate_invalid_identity_and_non_application_eager_rejected() -> None:
    container = ContainerRuntime()
    descriptor = _descriptor("one")
    container.register(descriptor)
    with pytest.raises(ServiceRegistrationError):
        container.register(descriptor)
    with pytest.raises(ServiceRegistrationError):
        container.register(_descriptor(""))
    with pytest.raises(ServiceRegistrationError):
        container.register(_descriptor("eager", scope=DIScope.SESSION, eager=True))
    assert container.descriptors() == (descriptor,)


def test_required_positional_only_and_variadic_binding_rejected() -> None:
    class Positional(ExampleService):
        def __init__(self, dependency: ServiceContract, /) -> None:
            super().__init__()
            self.dependency = dependency

    class Variadic(ExampleService):
        def __init__(self, **dependencies: ServiceContract) -> None:
            super().__init__()
            self.dependencies = dependencies

    container = ContainerRuntime()
    with pytest.raises(ServiceRegistrationError):
        container.register(_descriptor("positional", Positional))
    with pytest.raises(ServiceRegistrationError):
        container.register(
            _descriptor("variadic", Variadic, dependencies=(("dependencies", ServiceId("target")),))
        )


async def test_deep_dependency_graph_does_not_use_recursive_python_calls() -> None:
    container = ContainerRuntime()
    container.register(_descriptor("0"))
    for index in range(1, 1100):
        container.register(
            _descriptor(
                str(index), Consumer, dependencies=(("dependency", ServiceId(str(index - 1))),)
            )
        )
    assert cast(ExampleService, await container.resolve(ServiceId("1099"))).ready
    await container.shutdown()


async def test_generic_scope_foundation_keys_disposal_and_eviction() -> None:
    disposed: list[int] = []

    async def dispose(value: int) -> None:
        disposed.append(value)
        if value == 2:
            raise ValueError("dispose")

    scopes = ScopeRuntime[int](dispose=dispose)
    session, pipeline = SessionId(uuid4()), PipelineId(uuid4())
    scopes.put(ServiceId("application"), 1, scope=DIScope.APPLICATION)
    scopes.put(ServiceId("session"), 2, scope=DIScope.SESSION, session_id=session)
    scopes.put(
        ServiceId("pipeline"), 3, scope=DIScope.PIPELINE, session_id=session, pipeline_id=pipeline
    )
    with pytest.raises(ScopeViolationError):
        scopes.put(ServiceId("application"), 4, scope=DIScope.APPLICATION)
    with pytest.raises(ScopeViolationError):
        scopes.get(ServiceId("transient"), scope=DIScope.TRANSIENT)
    with pytest.raises(ScopeViolationError):
        scopes.put(ServiceId("transient"), 4, scope=DIScope.TRANSIENT)
    with pytest.raises(RuntimeShutdownError):
        await scopes.clear_session(session)
    assert disposed == [3, 2]
    assert scopes.get(ServiceId("session"), scope=DIScope.SESSION, session_id=session) is None
    assert (
        scopes.get(
            ServiceId("pipeline"), scope=DIScope.PIPELINE, session_id=session, pipeline_id=pipeline
        )
        is None
    )
    await scopes.clear_session(session)
    await scopes.remove(ServiceId("application"), scope=DIScope.APPLICATION)
    await scopes.clear_application()
    await scopes.remove_all(ServiceId("absent"))
    await scopes.shutdown()
    assert disposed == [3, 2, 1]


async def test_transient_remove_releases_its_dependencies_and_preserves_independent() -> None:
    container = ContainerRuntime()
    container.register(_descriptor("leaf", scope=DIScope.TRANSIENT))
    container.register(
        _descriptor(
            "root", Consumer, DIScope.TRANSIENT, dependencies=(("dependency", ServiceId("leaf")),)
        )
    )
    independent = cast(ExampleService, await container.resolve(ServiceId("leaf")))
    root = cast(Consumer, await container.resolve(ServiceId("root")))
    child = cast(ExampleService, root.dependency)
    await container.remove(ServiceId("root"))
    assert root.shutdowns == child.shutdowns == 1
    assert independent.shutdowns == 0
    await container.release(root)
    await container.shutdown()
    assert independent.shutdowns == 1


async def test_container_identity_health_lifecycle_and_invalid_clear_ids() -> None:
    from src.core.types import HealthStatus

    container = ContainerRuntime()
    assert container.runtime_name == "container"
    assert container.runtime_layer is RuntimeLayer.L0_KERNEL
    assert container.health() is HealthStatus.OK
    await container.initialize()
    await container.start()
    await container.stop()
    with pytest.raises(ScopeViolationError):
        await container.clear_session(cast(SessionId, "not-uuid"))
    with pytest.raises(ScopeViolationError):
        await container.clear_pipeline(cast(PipelineId, "not-uuid"))
    await container.shutdown()


@pytest.mark.parametrize(
    "candidate",
    (
        None,
        _descriptor("abstract", ServiceContract),
        _descriptor("wrong-type", cast(type[ServiceContract], object)),
        _descriptor(
            "bindings-list", Consumer, dependencies=cast(tuple[tuple[str, ServiceId], ...], [])
        ),
        _descriptor(
            "binding-string",
            Consumer,
            dependencies=cast(tuple[tuple[str, ServiceId], ...], ("dependency",)),
        ),
        _descriptor(
            "binding-triple",
            Consumer,
            dependencies=cast(
                tuple[tuple[str, ServiceId], ...], (("dependency", "target", "extra"),)
            ),
        ),
    ),
)
def test_malformed_descriptor_construction_is_defended(candidate: object) -> None:
    container = ContainerRuntime()
    with pytest.raises(ServiceRegistrationError):
        container.register(cast(ServiceDescriptor, candidate))
    assert container.descriptors() == ()


def test_internal_registry_invalid_registration_and_missing_unregister() -> None:
    from src.kernel.runtime.registry import RegistryRuntime

    registry = RegistryRuntime()
    with pytest.raises(ServiceRegistrationError):
        registry.register(_descriptor(""))
    with pytest.raises(ServiceResolutionError):
        registry.unregister(ServiceId("missing"))


async def test_non_service_constructor_result_rejected() -> None:
    from typing import Self

    class Wrong(ExampleService):
        def __new__(cls) -> Self:
            return cast(Self, object())

    container = ContainerRuntime()
    container.register(_descriptor("wrong", Wrong))
    with pytest.raises(ServiceResolutionError):
        await container.resolve(ServiceId("wrong"))
    await container.shutdown()


async def test_generic_scope_validation_and_shutdown_error_phases() -> None:
    disposed: list[int] = []

    async def dispose(value: int) -> None:
        disposed.append(value)
        raise ValueError(str(value))

    scopes = ScopeRuntime[int](dispose=dispose)
    session, pipeline = SessionId(uuid4()), PipelineId(uuid4())
    with pytest.raises(ScopeViolationError):
        scopes.get(ServiceId("missing"), scope=DIScope.SESSION)
    with pytest.raises(ScopeViolationError):
        scopes.get(ServiceId("missing"), scope=DIScope.PIPELINE, session_id=session)
    with pytest.raises(ScopeViolationError):
        scopes.get(
            ServiceId("missing"),
            scope=DIScope.PIPELINE,
            session_id=session,
            pipeline_id=cast(PipelineId, "invalid"),
        )
    with pytest.raises(ScopeViolationError):
        await scopes.clear_pipeline(cast(PipelineId, "invalid"))
    scopes.put(ServiceId("a"), 1, scope=DIScope.APPLICATION)
    scopes.put(ServiceId("s"), 2, scope=DIScope.SESSION, session_id=session)
    scopes.put(ServiceId("p"), 3, scope=DIScope.PIPELINE, session_id=session, pipeline_id=pipeline)
    with pytest.raises(ScopeViolationError):
        scopes.get(
            ServiceId("p"),
            scope=DIScope.PIPELINE,
            session_id=SessionId(uuid4()),
            pipeline_id=pipeline,
        )
    await scopes.clear_pipeline(PipelineId(uuid4()))
    with pytest.raises(RuntimeShutdownError) as caught:
        await scopes.shutdown()
    assert disposed == [3, 2, 1]
    assert [
        str(error) for error in cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions
    ] == ["3", "2", "1"]
    await scopes.shutdown()
    assert disposed == [3, 2, 1]


async def test_generic_scope_interrupted_cleanup_preserves_remaining_ownership() -> None:
    disposed: list[int] = []
    entered, resume = asyncio.Event(), asyncio.Event()

    async def dispose(value: int) -> None:
        disposed.append(value)
        if value == 2:
            raise ValueError("second")
        if value == 1:
            entered.set()
            await resume.wait()

    scopes = ScopeRuntime[int](dispose=dispose)
    session = SessionId(uuid4())
    scopes.put(ServiceId("one"), 1, scope=DIScope.SESSION, session_id=session)
    scopes.put(ServiceId("two"), 2, scope=DIScope.SESSION, session_id=session)
    task = asyncio.create_task(scopes.clear_session(session))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError) as caught:
        await task
    assert isinstance(caught.value.__cause__, ExceptionGroup)
    resume.set()
    await scopes.shutdown()
    assert disposed == [2, 1, 1]


@pytest.mark.parametrize("owner", ("container", "scope"))
async def test_shutdown_cancellation_keeps_prior_and_current_phase_errors(owner: str) -> None:
    log: list[str] = []
    entered, resume = asyncio.Event(), asyncio.Event()
    pipeline_error, application_error = ValueError("pipeline"), LookupError("application")

    async def fail_pipeline() -> None:
        raise pipeline_error

    async def fail_application() -> None:
        raise application_error

    async def wait_shutdown() -> None:
        entered.set()
        await resume.wait()

    wait_type = _tracked("wait", log, shutdown=wait_shutdown)
    application_type = _tracked("application", log, shutdown=fail_application)
    pipeline_type = _tracked("pipeline", log, shutdown=fail_pipeline)
    context = _context()
    if owner == "container":
        container = ContainerRuntime()
        container.register(_descriptor("wait", wait_type))
        container.register(_descriptor("application", application_type))
        container.register(_descriptor("pipeline", pipeline_type, DIScope.PIPELINE))
        await container.resolve(ServiceId("wait"))
        await container.resolve(ServiceId("application"))
        await container.resolve(ServiceId("pipeline"), context=context)
        shutdown = container.shutdown
    else:

        async def dispose(service: ServiceContract) -> None:
            await service.shutdown()

        scopes = ScopeRuntime[ServiceContract](dispose=dispose)
        scopes.put(ServiceId("wait"), wait_type(), scope=DIScope.APPLICATION)
        scopes.put(ServiceId("application"), application_type(), scope=DIScope.APPLICATION)
        scopes.put(
            ServiceId("pipeline"),
            pipeline_type(),
            scope=DIScope.PIPELINE,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
        )
        shutdown = scopes.shutdown
    task = asyncio.create_task(shutdown())
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError) as caught:
        await task
    assert cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions == (
        pipeline_error,
        application_error,
    )
    resume.set()
    await shutdown()
    await shutdown()
    assert log.count("shutdown:pipeline") == log.count("shutdown:application") == 1
    assert log.count("shutdown:wait") == 2


@pytest.mark.parametrize("cancel_initialize", (False, True))
async def test_interrupted_rollback_keeps_original_and_completed_cleanup_failures(
    cancel_initialize: bool,
) -> None:
    log: list[str] = []
    initialized, disposing, resume = asyncio.Event(), asyncio.Event(), asyncio.Event()
    original, cleanup = ValueError("initialize"), LookupError("root cleanup")

    async def initialize() -> None:
        if cancel_initialize:
            initialized.set()
            await asyncio.Event().wait()
        raise original

    async def leaf_shutdown() -> None:
        disposing.set()
        await resume.wait()

    class Root(Consumer):
        async def initialize(self) -> None:
            await initialize()

        async def shutdown(self) -> None:
            log.append("shutdown:root")
            raise cleanup

    container = ContainerRuntime()
    container.register(_descriptor("leaf", _tracked("leaf", log, shutdown=leaf_shutdown)))
    container.register(_descriptor("root", Root, dependencies=(("dependency", ServiceId("leaf")),)))
    task = asyncio.create_task(container.resolve(ServiceId("root")))
    if cancel_initialize:
        await initialized.wait()
        task.cancel()
    await disposing.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError) as caught:
        await task
    errors = cast(ExceptionGroup[Exception], caught.value.__cause__).exceptions
    assert errors == ((cleanup,) if cancel_initialize else (original, cleanup))
    resume.set()
    await container.shutdown()
    assert log.count("shutdown:root") == 1
    assert log.count("shutdown:leaf") == 2


async def test_cancelled_remove_stays_evicted_and_re_registration_is_fresh() -> None:
    log: list[str] = []
    entered, resume = asyncio.Event(), asyncio.Event()

    async def wait_shutdown() -> None:
        entered.set()
        await resume.wait()

    container = ContainerRuntime()
    container.register(_descriptor("service", _tracked("old", log, shutdown=wait_shutdown)))
    old = await container.resolve(ServiceId("service"))
    task = asyncio.create_task(container.remove(ServiceId("service")))
    await entered.wait()
    assert not container.contains(ServiceId("service"))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    container.register(_descriptor("service", _tracked("new", log)))
    new = await container.resolve(ServiceId("service"))
    assert new is not old
    resume.set()
    await container.shutdown()
    assert log[-2:] == ["shutdown:new", "shutdown:old"]
