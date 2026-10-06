"""KR-007 deterministic RuntimeEvent dispatch."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from src.core.exceptions import EventHandlerError
from src.kernel.contracts.events import RuntimeEvent
from src.kernel.runtime.subscriber import SubscriberRuntime


class DispatcherRuntime:
    """Dispatch events sequentially after stable priority ordering."""

    def __init__(self, subscribers: SubscriberRuntime) -> None:
        self._subscribers = subscribers

    async def dispatch(self, event: RuntimeEvent) -> None:
        """Deliver already validated data using detached, insertion-ordered snapshots."""
        captured = self._snapshot(event)
        handlers = self._subscribers.handlers(captured.event_type)
        for handler in handlers:
            received = self._snapshot(captured)
            try:
                await handler.handle(received)
            except Exception as error:
                raise EventHandlerError(
                    "Event handler failed", handler=type(handler).__qualname__
                ) from error

    async def dispatch_many(self, events: tuple[RuntimeEvent, ...]) -> None:
        """Capture the full validated batch before the first handler executes."""
        captured = tuple(self._snapshot(event) for event in events)
        for event in self._ordered_events(captured):
            await self.dispatch(event)

    @staticmethod
    def _snapshot(event: RuntimeEvent) -> RuntimeEvent:
        return replace(event, payload=deepcopy(event.payload))

    def _ordered_events(self, events: tuple[RuntimeEvent, ...]) -> tuple[RuntimeEvent, ...]:
        return tuple(sorted(events, key=lambda event: event.priority, reverse=True))


__all__ = ["DispatcherRuntime"]
