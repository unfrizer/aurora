"""KR-007 canonical RuntimeEvent construction and publication."""

from __future__ import annotations

from datetime import UTC
from uuid import uuid4

from src.core.exceptions import EventValidationError, InvalidEventError
from src.core.types import EventId, EventPriority, Payload
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.events import RuntimeEvent
from src.kernel.runtime.dispatcher import DispatcherRuntime


class PublisherRuntime:
    """Own construction, validation and dispatch entry for RuntimeEvent."""

    def __init__(self, dispatcher: DispatcherRuntime) -> None:
        self._dispatcher = dispatcher

    def create(
        self,
        *,
        event_type: str,
        payload: Payload,
        context: RuntimeContext,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> RuntimeEvent:
        event = RuntimeEvent(
            event_id=EventId(uuid4()),
            event_type=event_type,
            session_id=context.session_id,
            trace=context.trace,
            priority=priority,
            payload=payload.copy(),
        )
        self.validate(event)
        return event

    def validate(self, event: RuntimeEvent) -> None:
        if not event.event_type:
            raise InvalidEventError("event_type must not be empty")
        if event.timestamp.tzinfo is None or event.timestamp.utcoffset() != UTC.utcoffset(
            event.timestamp
        ):
            raise EventValidationError("RuntimeEvent timestamp must use UTC")

    async def publish(self, event: RuntimeEvent) -> None:
        self.validate(event)
        await self._dispatcher.dispatch(event)

    async def publish_many(self, events: tuple[RuntimeEvent, ...]) -> None:
        for event in events:
            self.validate(event)
        await self._dispatcher.dispatch_many(events)


__all__ = ["PublisherRuntime"]
