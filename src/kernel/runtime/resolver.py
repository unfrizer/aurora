"""KR-005 deterministic service resolution."""

from __future__ import annotations

from src.core.exceptions import CircularDependencyError
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.provider import ProviderRuntime
from src.kernel.runtime.scope import ScopeRuntime


class ResolverRuntime:
    """Resolve descriptors through their explicit owning scope."""

    def __init__(self, provider: ProviderRuntime, scopes: ScopeRuntime) -> None:
        self._provider = provider
        self._scopes = scopes
        self._resolving: set[str] = set()

    def resolve(
        self,
        descriptor: ServiceDescriptor,
        *,
        context: RuntimeContext | None,
    ) -> ServiceContract:
        cached = self._scopes.get(descriptor, context=context)
        if cached is not None:
            return cached
        service_key = str(descriptor.service_id)
        if service_key in self._resolving:
            raise CircularDependencyError(
                "Circular service construction detected", service_id=service_key
            )
        self._resolving.add(service_key)
        try:
            service = self._provider.provide(descriptor, context=context)
            self._scopes.put(descriptor, service, context=context)
            return service
        finally:
            self._resolving.remove(service_key)

    def validate(self, descriptor: ServiceDescriptor) -> None:
        del descriptor


__all__ = ["ResolverRuntime"]
