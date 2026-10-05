"""KR-005 public asynchronous Dependency Injection facade."""

# Only the DI composition root/collaborators use these private module internals.
# pyright: reportPrivateUsage=false
# Runtime validation deliberately defends against malformed contract construction.
# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from typing import cast
from uuid import UUID

from src.core.exceptions import (
    RuntimeShutdownError,
    RuntimeStateError,
    ScopeViolationError,
    ServiceRegistrationError,
)
from src.core.types import DIScope, HealthStatus, PipelineId, RuntimeLayer, ServiceId, SessionId
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.registry import RegistryRuntime
from src.kernel.runtime.resolver import ResolverRuntime
from src.kernel.runtime.scope import ScopeRuntime


class ContainerRuntime(RuntimeContract):
    """Compose DI owners; reject concurrent or re-entrant mutation."""

    @property
    def runtime_name(self) -> str:
        return "container"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    def __init__(self) -> None:
        self._registry = RegistryRuntime()
        self._provider = ProviderRuntime(_constructed=self._constructed)
        self._scopes: ScopeRuntime[ServiceContract] = ScopeRuntime(dispose=self._provider.dispose)
        self._resolver = ResolverRuntime(self._registry, self._provider, self._scopes)
        self._busy = False
        self._closed = False
        self._initialized = False
        self._shutdown_complete = False

    def _constructed(self, service: ServiceContract) -> None:
        self._resolver._constructed(service)

    def _enter(self, *, cleanup: bool = False) -> None:
        if self._busy or (self._closed and not cleanup):
            raise RuntimeStateError("Container mutation is unavailable")
        self._busy = True

    def register(self, descriptor: ServiceDescriptor) -> None:
        self._enter()
        try:
            self._resolver.validate(descriptor)
            self._registry.register(descriptor)
        finally:
            self._busy = False

    async def resolve(
        self, service_id: ServiceId, *, context: RuntimeContext | None = None
    ) -> ServiceContract:
        self._enter()
        try:
            return await self._resolver.resolve(self._registry.get(service_id), context=context)
        finally:
            self._busy = False

    async def remove(self, service_id: ServiceId) -> None:
        self._enter()
        try:
            self._registry.get(service_id)
            if any(
                target == service_id
                for descriptor in self.descriptors()
                if descriptor.service_id != service_id
                for _, target in descriptor.dependencies
            ):
                raise ServiceRegistrationError("Registered consumers still require this service")
            self._registry.unregister(service_id)
            values = self._scopes._detach(lambda key: key[3] == service_id)
            values.extend(
                self._resolver._detach(lambda record: record.descriptor.service_id == service_id)
            )
            for record in tuple(self._resolver._pending):
                if (
                    record.descriptor.service_id == service_id
                    and record.descriptor.scope is DIScope.TRANSIENT
                ):
                    values.extend(self._resolver._detach_release(record.service))
            await self._cleanup(values)
        finally:
            self._busy = False

    async def release(self, service: ServiceContract) -> None:
        self._enter()
        try:
            await self._cleanup(self._resolver._detach_release(service))
        finally:
            self._busy = False

    async def clear_session(self, session_id: SessionId) -> None:
        self._enter()
        try:
            if not isinstance(session_id, UUID):
                raise ScopeViolationError("A canonical session ID is required")
            values = self._scopes._detach(lambda key: key[1] == session_id)
            values.extend(self._resolver._detach(lambda record: record.session_id == session_id))
            await self._cleanup(values)
        finally:
            self._busy = False

    async def clear_pipeline(self, pipeline_id: PipelineId) -> None:
        self._enter()
        try:
            if not isinstance(pipeline_id, UUID):
                raise ScopeViolationError("A canonical pipeline ID is required")
            values = self._scopes._detach(lambda key: key[2] == pipeline_id)
            values.extend(self._resolver._detach(lambda record: record.pipeline_id == pipeline_id))
            await self._cleanup(values)
        finally:
            self._busy = False

    async def _cleanup(self, values: list[ServiceContract]) -> None:
        errors: list[Exception] = []
        ordered = sorted(
            {id(value): value for value in values}.values(),
            key=lambda value: self._resolver._orders[id(value)],
            reverse=True,
        )
        for service in ordered:
            try:
                await self._provider.dispose(service)
            except Exception as error:
                errors.append(error)
            except BaseException as interruption:
                if errors:
                    cause = interruption.__cause__
                    if isinstance(cause, ExceptionGroup):
                        errors.extend(cast(ExceptionGroup[Exception], cause).exceptions)
                    raise interruption from ExceptionGroup("Earlier disposal failures", errors)
                raise
            self._scopes._complete(service)
            self._resolver._complete(service)
        if errors:
            raise RuntimeShutdownError("DI disposal failed") from ExceptionGroup(
                "DI disposal failures", errors
            )

    def contains(self, service_id: ServiceId) -> bool:
        return self._registry.contains(service_id)

    def descriptors(self) -> tuple[ServiceDescriptor, ...]:
        return self._registry.list()

    async def initialize(self) -> None:
        self._enter()
        try:
            if not self._initialized:
                await self._resolver._initialize_eager()
                self._initialized = True
        finally:
            self._busy = False

    async def start(self) -> None:
        self._enter()
        self._busy = False

    async def stop(self) -> None:
        self._enter()
        self._busy = False

    async def shutdown(self) -> None:
        self._enter(cleanup=True)
        try:
            if self._shutdown_complete:
                return
            self._closed = True
            self._scopes._detach(lambda _key: True)
            self._resolver._detach(lambda _record: True)
            # Transients may capture any cache; dispose them before cached scopes.
            phases: dict[DIScope, list[ServiceContract]] = {scope: [] for scope in DIScope}
            for key, service in self._scopes._pending:
                phases[key[0]].append(service)
            for record in self._resolver._pending:
                phases[record.descriptor.scope].append(record.service)
            errors: list[Exception] = []
            for scope in (
                DIScope.TRANSIENT,
                DIScope.PIPELINE,
                DIScope.SESSION,
                DIScope.APPLICATION,
            ):
                try:
                    await self._cleanup(phases[scope])
                except RuntimeShutdownError as error:
                    cause = error.__cause__
                    if isinstance(cause, ExceptionGroup):
                        errors.extend(cast(ExceptionGroup[Exception], cause).exceptions)
                    else:
                        errors.append(error)
                except BaseException as interruption:
                    if errors:
                        cause = interruption.__cause__
                        if isinstance(cause, ExceptionGroup):
                            errors.extend(cast(ExceptionGroup[Exception], cause).exceptions)
                        raise interruption from ExceptionGroup("Earlier disposal failures", errors)
                    raise
            self._shutdown_complete = True
            if errors:
                raise RuntimeShutdownError("DI shutdown failed") from ExceptionGroup(
                    "DI shutdown failures", errors
                )
        finally:
            self._busy = False

    def health(self) -> HealthStatus:
        return HealthStatus.OK


__all__ = ["ContainerRuntime"]
