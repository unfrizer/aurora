from __future__ import annotations

from src.core.types import DIScope, ServiceId
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.container import ContainerRuntime


class ExampleService(ServiceContract):
    async def initialize(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None


def test_application_service_is_cached_and_removable() -> None:
    container = ContainerRuntime()
    service_id = ServiceId("example")
    container.register(
        ServiceDescriptor(
            service_id=service_id,
            scope=DIScope.APPLICATION,
            implementation=ExampleService,
        )
    )
    assert container.resolve(service_id) is container.resolve(service_id)
    container.remove(service_id)
    assert not container.contains(service_id)
