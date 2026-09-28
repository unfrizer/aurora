"""KR-007 subscriber registry."""

from __future__ import annotations

from src.core.exceptions import EventHandlerError
from src.kernel.contracts.events import EventHandlerContract


class SubscriberRuntime:
    """Own event-handler registration with stable insertion ordering."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandlerContract]] = {}

    def subscribe(self, event_type: str, handler: EventHandlerContract) -> None:
        handlers = self._handlers.setdefault(event_type, [])
        if handler in handlers:
            raise EventHandlerError("Event handler is already registered", event_type=event_type)
        handlers.append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandlerContract) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler not in handlers:
            raise EventHandlerError("Event handler is not registered", event_type=event_type)
        handlers.remove(handler)
        if not handlers:
            del self._handlers[event_type]

    def handlers(self, event_type: str) -> tuple[EventHandlerContract, ...]:
        return tuple(self._handlers.get(event_type, ()))

    def contains(self, event_type: str) -> bool:
        return event_type in self._handlers

    def clear(self) -> None:
        self._handlers.clear()


__all__ = ["SubscriberRuntime"]
