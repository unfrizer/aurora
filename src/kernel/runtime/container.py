"""KR-005 public Dependency Injection container."""

from __future__ import annotations

from src.core.types import HealthStatus, RuntimeLayer, ServiceId
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.registry import RegistryRuntime
from src.kernel.runtime.resolver import ResolverRuntime
from src.kernel.runtime.scope import ScopeRuntime


class ContainerRuntime(RuntimeContract):
    """Own explicit service registration, resolution and scope lifetime."""

    @property
    def runtime_name(self) -> str:
        return "container"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    def __init__(self) -> None:
        self._registry = RegistryRuntime()
        self._provider = ProviderRuntime()
        self._scopes = ScopeRuntime(self._provider)
        self._resolver = ResolverRuntime(self._provider, self._scopes)
        self._initialized: set[ServiceId] = set()

    def register(self, descriptor: ServiceDescriptor) -> None:
        self._resolver.validate(descriptor)
        self._registry.register(descriptor)

    def remove(self, service_id: ServiceId) -> None:
        self._registry.unregister(service_id)

    def resolve(
        self, service_id: ServiceId, *, context: RuntimeContext | None = None
    ) -> ServiceContract:
        return self._resolver.resolve(self._registry.get(service_id), context=context)

    def contains(self, service_id: ServiceId) -> bool:
        return self._registry.contains(service_id)

    def descriptors(self) -> tuple[ServiceDescriptor, ...]:
        return self._registry.list()

    async def initialize(self) -> None:
        for descriptor in self.descriptors():
            if descriptor.eager:
                service = self.resolve(descriptor.service_id)
                await service.initialize()
                self._initialized.add(descriptor.service_id)

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        await self._scopes.shutdown()
        self._initialized.clear()

    def health(self) -> HealthStatus:
        return HealthStatus.OK


__all__ = ["ContainerRuntime"]
