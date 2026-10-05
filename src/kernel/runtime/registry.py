"""KR-005 service descriptor registry."""

# Descriptors intentionally do not validate their own runtime construction.
# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from src.core.exceptions import ServiceRegistrationError, ServiceResolutionError
from src.core.types import ServiceId
from src.kernel.contracts.service import ServiceDescriptor


class RegistryRuntime:
    """Own immutable descriptors; registration itself remains explicitly mutable."""

    def __init__(self) -> None:
        self._descriptors: dict[ServiceId, ServiceDescriptor] = {}

    def register(self, descriptor: ServiceDescriptor) -> None:
        if (
            not isinstance(descriptor, ServiceDescriptor)
            or not isinstance(descriptor.service_id, str)
            or not descriptor.service_id.strip()
        ):
            raise ServiceRegistrationError("Invalid service descriptor identity")
        if descriptor.service_id in self._descriptors:
            raise ServiceRegistrationError(
                "Service is already registered", service_id=descriptor.service_id
            )
        self._descriptors[descriptor.service_id] = descriptor

    def unregister(self, service_id: ServiceId) -> None:
        if service_id not in self._descriptors:
            raise ServiceResolutionError("Service is not registered", service_id=service_id)
        del self._descriptors[service_id]

    def get(self, service_id: ServiceId) -> ServiceDescriptor:
        try:
            return self._descriptors[service_id]
        except KeyError as exc:
            raise ServiceResolutionError(
                "Service is not registered", service_id=service_id
            ) from exc

    def contains(self, service_id: ServiceId) -> bool:
        return service_id in self._descriptors

    def list(self) -> tuple[ServiceDescriptor, ...]:
        return tuple(self._descriptors.values())


__all__ = ["RegistryRuntime"]
