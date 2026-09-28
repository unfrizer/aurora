"""KR-007 public Event Bus runtime facade."""

from __future__ import annotations

from src.core.types import EventPriority, HealthStatus, Payload, RuntimeLayer
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.dispatcher import DispatcherRuntime
from src.kernel.runtime.publisher import PublisherRuntime
from src.kernel.runtime.subscriber import SubscriberRuntime


class EventBusRuntime(RuntimeContract):
    """Own the public Event Bus composition root."""

    def __init__(self) -> None:
        self._subscribers = SubscriberRuntime()
        self._dispatcher = DispatcherRuntime(self._subscribers)
        self._publisher = PublisherRuntime(self._dispatcher)

    @property
    def runtime_name(self) -> str:
        return "event_bus"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    def subscribe(self, event_type: str, handler: EventHandlerContract) -> None:
        self._subscribers.subscribe(event_type, handler)

    def unsubscribe(self, event_type: str, handler: EventHandlerContract) -> None:
        self._subscribers.unsubscribe(event_type, handler)

    async def publish(self, event: RuntimeEvent) -> None:
        await self._publisher.publish(event)

    async def publish_many(self, events: tuple[RuntimeEvent, ...]) -> None:
        await self._publisher.publish_many(events)

    def create_for_runtime(
        self,
        *,
        event_type: str,
        payload: Payload,
        context: RuntimeContext,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> RuntimeEvent:
        return self._publisher.create(
            event_type=event_type,
            payload=payload,
            context=context,
            priority=priority,
        )

    def handlers(self, event_type: str) -> tuple[EventHandlerContract, ...]:
        return self._subscribers.handlers(event_type)

    def contains(self, event_type: str) -> bool:
        return self._subscribers.contains(event_type)

    def clear(self) -> None:
        self._subscribers.clear()

    async def initialize(self) -> None:
        return None

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self.clear()

    def health(self) -> HealthStatus:
        return HealthStatus.OK


__all__ = ["EventBusRuntime"]
