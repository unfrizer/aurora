"""KR-007 deterministic RuntimeEvent dispatch."""

from __future__ import annotations

from src.kernel.contracts.events import RuntimeEvent
from src.kernel.runtime.subscriber import SubscriberRuntime


class DispatcherRuntime:
    """Dispatch events sequentially after stable priority ordering."""

    def __init__(self, subscribers: SubscriberRuntime) -> None:
        self._subscribers = subscribers

    async def dispatch(self, event: RuntimeEvent) -> None:
        for handler in self._subscribers.handlers(event.event_type):
            await handler.handle(event)

    async def dispatch_many(self, events: tuple[RuntimeEvent, ...]) -> None:
        for event in self._ordered_events(events):
            await self.dispatch(event)

    def _ordered_events(self, events: tuple[RuntimeEvent, ...]) -> tuple[RuntimeEvent, ...]:
        return tuple(sorted(events, key=lambda event: event.priority, reverse=True))


__all__ = ["DispatcherRuntime"]
