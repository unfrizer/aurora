"""KR-005 service construction and disposal."""

from __future__ import annotations

from src.core.exceptions import ServiceResolutionError
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor


class ProviderRuntime:
    """Create and dispose concrete service instances only."""

    def provide(
        self,
        descriptor: ServiceDescriptor,
        *,
        context: RuntimeContext | None,
    ) -> ServiceContract:
        del context
        try:
            service = descriptor.implementation()
        except TypeError as exc:
            raise ServiceResolutionError(
                "Service implementation cannot be constructed without arguments",
                service_id=descriptor.service_id,
            ) from exc
        return service

    async def dispose(self, service: ServiceContract) -> None:
        await service.shutdown()


__all__ = ["ProviderRuntime"]
