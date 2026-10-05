"""KR-005 deterministic dependency traversal and transient/acquisition ownership."""

# Only the DI composition root/collaborators use these private module internals.
# pyright: reportPrivateUsage=false
# Runtime validation deliberately defends against malformed contract construction.
# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

import inspect
import keyword
import weakref
from asyncio import CancelledError
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast
from uuid import UUID

from src.core.exceptions import (
    CircularDependencyError,
    ScopeViolationError,
    ServiceRegistrationError,
    ServiceResolutionError,
)
from src.core.types import DIScope, PipelineId, ServiceId, SessionId
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.registry import RegistryRuntime
from src.kernel.runtime.scope import ScopeRuntime


@dataclass(frozen=True, slots=True)
class _Owned:
    descriptor: ServiceDescriptor
    service: ServiceContract
    session_id: SessionId | None
    pipeline_id: PipelineId | None
    children: tuple[ServiceContract, ...]


@dataclass(slots=True)
class _Frame:
    descriptor: ServiceDescriptor
    arguments: dict[str, ServiceContract]


class ResolverRuntime:
    """Own traversal and transient lifetime, but no reusable instance cache."""

    def __init__(
        self,
        registry: RegistryRuntime,
        provider: ProviderRuntime,
        scopes: ScopeRuntime[ServiceContract],
    ) -> None:
        self._registry = registry
        self._provider = provider
        self._scopes = scopes
        self._transients: list[_Owned] = []
        self._pending: list[_Owned] = []
        self._acquisition: list[_Owned] | None = None
        self._constructing: (
            tuple[ServiceDescriptor, RuntimeContext | None, tuple[ServiceContract, ...]] | None
        ) = None
        # Non-owning ordinal metadata coordinates reverse teardown across owners.
        self._orders: dict[int, int] = {}
        self._next_order = 0
        self._released: dict[int, weakref.ReferenceType[ServiceContract]] = {}

    def validate(self, descriptor: ServiceDescriptor) -> None:
        candidate: object = descriptor
        if not isinstance(candidate, ServiceDescriptor):
            raise ServiceRegistrationError("A service descriptor is required")
        implementation: object = descriptor.implementation
        if (
            not isinstance(descriptor.service_id, str)
            or not descriptor.service_id.strip()
            or not isinstance(descriptor.scope, DIScope)
            or not isinstance(descriptor.eager, bool)
            or not isinstance(implementation, type)
            or not issubclass(implementation, ServiceContract)
            or inspect.isabstract(implementation)
        ):
            raise ServiceRegistrationError("Invalid service descriptor")
        if descriptor.eager and descriptor.scope is not DIScope.APPLICATION:
            raise ServiceRegistrationError("Only application services may be eager")
        implementation_type = implementation
        if not (
            inspect.iscoroutinefunction(implementation_type.initialize)
            and inspect.iscoroutinefunction(implementation_type.shutdown)
        ):
            raise ServiceRegistrationError("Service lifecycle hooks must be asynchronous")
        bindings: object = descriptor.dependencies
        if not isinstance(bindings, tuple):
            raise ServiceRegistrationError("Dependency bindings must be immutable")
        names: set[str] = set()
        for binding in cast(tuple[object, ...], bindings):
            if not isinstance(binding, tuple):
                raise ServiceRegistrationError("Invalid dependency binding")
            parts = cast(tuple[object, ...], binding)
            if len(parts) != 2:
                raise ServiceRegistrationError("Invalid dependency binding")
            name, target = parts
            if (
                not isinstance(name, str)
                or not name.isidentifier()
                or keyword.iskeyword(name)
                or name in names
                or not isinstance(target, str)
                or not target.strip()
            ):
                raise ServiceRegistrationError("Invalid dependency binding")
            names.add(name)
        try:
            parameters = inspect.signature(implementation_type, eval_str=False).parameters
        except (TypeError, ValueError) as error:
            raise ServiceRegistrationError("Constructor cannot be inspected") from error
        for name in names:
            parameter = parameters.get(name)
            if parameter is None or parameter.kind not in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                raise ServiceRegistrationError("Binding must name a declared keyword parameter")
        for name, parameter in parameters.items():
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if parameter.default is inspect.Parameter.empty and (
                parameter.kind is inspect.Parameter.POSITIONAL_ONLY or name not in names
            ):
                raise ServiceRegistrationError("Required constructor argument has no binding")

    @staticmethod
    def _compatible(owner: DIScope, dependency: DIScope) -> bool:
        if owner is DIScope.APPLICATION:
            return dependency is DIScope.APPLICATION
        if owner is DIScope.SESSION:
            return dependency in (DIScope.APPLICATION, DIScope.SESSION)
        if owner is DIScope.PIPELINE:
            return dependency is not DIScope.TRANSIENT
        return True

    def _preflight(
        self,
        roots: tuple[ServiceDescriptor, ...],
        context: RuntimeContext | None,
        *,
        require_context: bool = True,
    ) -> None:
        candidate: object = context
        if candidate is not None and (
            not isinstance(candidate, RuntimeContext)
            or not isinstance(candidate.session_id, UUID)
            or not isinstance(candidate.pipeline_id, UUID)
        ):
            raise ScopeViolationError("A canonical runtime context is required")
        colors: dict[ServiceId, int] = {}
        for root in roots:
            if colors.get(root.service_id) == 2:
                continue
            stack: list[tuple[ServiceDescriptor, int]] = [(root, 0)]
            while stack:
                descriptor, index = stack[-1]
                if index == 0:
                    self.validate(descriptor)
                    if (
                        require_context
                        and context is None
                        and descriptor.scope
                        in (
                            DIScope.SESSION,
                            DIScope.PIPELINE,
                        )
                    ):
                        raise ScopeViolationError("Scoped service requires a runtime context")
                    colors[descriptor.service_id] = 1
                if index == len(descriptor.dependencies):
                    colors[descriptor.service_id] = 2
                    stack.pop()
                    continue
                stack[-1] = descriptor, index + 1
                target = self._registry.get(descriptor.dependencies[index][1])
                if not self._compatible(descriptor.scope, target.scope):
                    raise ScopeViolationError("Dependency would capture a shorter lifetime")
                color = colors.get(target.service_id, 0)
                if color == 1:
                    raise CircularDependencyError("Circular service dependency")
                if color == 0:
                    stack.append((target, 0))

    def _cached(
        self, descriptor: ServiceDescriptor, context: RuntimeContext | None
    ) -> ServiceContract | None:
        if descriptor.scope is DIScope.TRANSIENT:
            return None
        return self._scopes.get(
            descriptor.service_id,
            scope=descriptor.scope,
            session_id=None if context is None else context.session_id,
            pipeline_id=None if context is None else context.pipeline_id,
        )

    def _constructed(self, service: ServiceContract) -> None:
        if self._acquisition is None or self._constructing is None:
            raise ServiceResolutionError("Construction outside an acquisition")
        if id(service) in self._orders:
            raise ServiceResolutionError("Constructor returned an already owned instance")
        descriptor, context, children = self._constructing
        self._acquisition.append(
            _Owned(
                descriptor,
                service,
                None if context is None else context.session_id,
                None if context is None else context.pipeline_id,
                children,
            )
        )
        self._orders[id(service)] = self._next_order
        self._next_order += 1

    async def _build(
        self,
        root: ServiceDescriptor,
        context: RuntimeContext | None,
        prepared: dict[ServiceId, ServiceContract],
    ) -> ServiceContract:
        stack = [_Frame(root, {})]
        while stack:
            frame = stack[-1]
            descriptor = frame.descriptor
            cached = self._cached(descriptor, context)
            service = cached if cached is not None else prepared.get(descriptor.service_id)
            if descriptor.scope is DIScope.TRANSIENT:
                service = None
            if service is None and len(frame.arguments) < len(descriptor.dependencies):
                name, service_id = descriptor.dependencies[len(frame.arguments)]
                target = self._registry.get(service_id)
                stack.append(_Frame(target, {}))
                continue
            if service is None:
                children = tuple(
                    frame.arguments[name]
                    for name, service_id in descriptor.dependencies
                    if self._registry.get(service_id).scope is DIScope.TRANSIENT
                )
                self._constructing = descriptor, context, children
                try:
                    service = await self._provider.provide(
                        descriptor, context=context, dependencies=frame.arguments
                    )
                finally:
                    self._constructing = None
                if descriptor.scope is not DIScope.TRANSIENT:
                    prepared[descriptor.service_id] = service
            stack.pop()
            if stack:
                parent = stack[-1]
                name = parent.descriptor.dependencies[len(parent.arguments)][0]
                parent.arguments[name] = service
            else:
                return service
        raise ServiceResolutionError("Service acquisition produced no instance")

    async def _acquire(
        self, roots: tuple[ServiceDescriptor, ...], context: RuntimeContext | None
    ) -> tuple[ServiceContract, ...]:
        if self._acquisition is not None:
            raise ServiceResolutionError("Nested resolver acquisition")
        if context is not None:
            self._scopes._bind_pipeline(context.session_id, context.pipeline_id)
        self._acquisition = []
        prepared: dict[ServiceId, ServiceContract] = {}
        try:
            results: list[ServiceContract] = []
            for descriptor in roots:
                results.append(await self._build(descriptor, context, prepared))
            for record in self._acquisition:
                if record.descriptor.scope is DIScope.TRANSIENT:
                    self._transients.append(record)
                else:
                    self._scopes.put(
                        record.descriptor.service_id,
                        record.service,
                        scope=record.descriptor.scope,
                        session_id=record.session_id,
                        pipeline_id=record.pipeline_id,
                    )
            return tuple(results)
        except (Exception, CancelledError) as original:
            self._pending.extend(self._acquisition)
            failures: list[Exception] = []
            try:
                for record in reversed(self._acquisition):
                    try:
                        await self._provider.dispose(record.service)
                    except Exception as error:
                        failures.append(error)
                    self._complete(record.service)
            except CancelledError as interruption:
                original_cause = original.__cause__ or original
                if isinstance(original_cause, Exception):
                    raise interruption from ExceptionGroup(
                        "Acquisition and interrupted rollback", [original_cause, *failures]
                    )
                if failures:
                    raise interruption from ExceptionGroup("Rollback failures", failures)
                raise
            if failures:
                original_cause = original.__cause__ or original
                if isinstance(original_cause, Exception):
                    raise original from ExceptionGroup(
                        "Acquisition and rollback failures", [original_cause, *failures]
                    )
                raise original from ExceptionGroup("Rollback failures", failures)
            raise
        finally:
            self._acquisition = None

    async def resolve(
        self, descriptor: ServiceDescriptor, *, context: RuntimeContext | None
    ) -> ServiceContract:
        self._preflight((descriptor,), context)
        return (await self._acquire((descriptor,), context))[0]

    async def _initialize_eager(self) -> None:
        descriptors = self._registry.list()
        self._preflight(descriptors, None, require_context=False)
        await self._acquire(tuple(item for item in descriptors if item.eager), None)

    def _detach(self, select: Callable[[_Owned], bool]) -> list[ServiceContract]:
        selected = [record for record in self._transients if select(record)]
        self._transients = [record for record in self._transients if not select(record)]
        self._pending.extend(selected)
        return [record.service for record in self._pending if select(record)]

    def _detach_release(self, service: ServiceContract) -> list[ServiceContract]:
        records = [*self._transients, *self._pending]
        root = next((record for record in records if record.service is service), None)
        if root is None or root.descriptor.scope is not DIScope.TRANSIENT:
            reference = self._released.get(id(service))
            if reference is not None and reference() is service:
                return []
            raise ScopeViolationError("Only owned transient instances may be released")
        selected: set[int] = set()
        stack = [root.service]
        lookup = {id(record.service): record for record in records}
        while stack:
            item = stack.pop()
            if id(item) in selected:
                continue
            selected.add(id(item))
            record = lookup.get(id(item))
            if record is not None:
                stack.extend(record.children)
        return self._detach(lambda record: id(record.service) in selected)

    def _complete(self, service: ServiceContract) -> None:
        records = [record for record in self._pending if record.service is service]
        if any(record.descriptor.scope is DIScope.TRANSIENT for record in records):
            self._released = {
                key: value for key, value in self._released.items() if value() is not None
            }
            self._released[id(service)] = weakref.ref(service)
        self._pending = [record for record in self._pending if record.service is not service]
        self._orders.pop(id(service), None)


__all__ = ["ResolverRuntime"]
