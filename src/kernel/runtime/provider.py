"""KR-005 stateless service construction and asynchronous hooks."""

# Construction can violate annotations via a custom __new__; validate its result.
# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from collections.abc import Callable, Mapping

from src.core.exceptions import ServiceResolutionError
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor


class ProviderRuntime:
    """Construct only explicitly bound arguments; never own service instances."""

    def __init__(self, *, _constructed: Callable[[ServiceContract], None] | None = None) -> None:
        self._constructed = _constructed

    async def provide(
        self,
        descriptor: ServiceDescriptor,
        *,
        context: RuntimeContext | None,
        dependencies: Mapping[str, ServiceContract],
    ) -> ServiceContract:
        del context  # Context selects lifetime; it is not implicitly injected.
        try:
            service = descriptor.implementation(**dependencies)
        except Exception as error:
            raise ServiceResolutionError("Service construction failed") from error
        if not isinstance(service, ServiceContract):
            raise ServiceResolutionError("Constructor returned a non-service object")
        if self._constructed is not None:
            self._constructed(service)
        try:
            await service.initialize()
        except Exception as error:
            raise ServiceResolutionError("Service initialization failed") from error
        return service

    async def dispose(self, service: ServiceContract) -> None:
        await service.shutdown()


__all__ = ["ProviderRuntime"]
