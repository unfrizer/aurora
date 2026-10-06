"""KR-007 canonical RuntimeEvent construction and publication."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from math import isfinite
from typing import cast
from uuid import UUID, uuid4

from src.core.exceptions import EventValidationError
from src.core.types import EventId, EventPriority, JSONValue, Payload
from src.kernel.contracts.context import RuntimeContext, TraceContext
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
        if not isinstance(cast(object, context), RuntimeContext):
            raise EventValidationError("Event creation requires RuntimeContext")
        event = RuntimeEvent(
            event_id=EventId(uuid4()),
            event_type=event_type,
            session_id=context.session_id,
            trace=context.trace,
            priority=priority,
            payload=self._copy_payload(payload),
        )
        self._validate_fields(event)
        return event

    def validate(self, event: RuntimeEvent) -> None:
        """Validate without mutating or normalizing the supplied event."""
        self._validate_fields(event)
        self._copy_payload(event.payload)

    async def publish(self, event: RuntimeEvent) -> None:
        """Capture validated data before the first handler can run."""
        await self._dispatcher.dispatch(self._snapshot(event))

    async def publish_many(self, events: tuple[RuntimeEvent, ...]) -> None:
        """Validate and capture the entire batch before any handler effect."""
        captured = tuple(self._snapshot(event) for event in events)
        await self._dispatcher.dispatch_many(captured)

    def _snapshot(self, event: RuntimeEvent) -> RuntimeEvent:
        self._validate_fields(event)
        return replace(event, payload=self._copy_payload(event.payload))

    def _validate_fields(self, event: object) -> None:
        if not isinstance(event, RuntimeEvent):
            raise EventValidationError("Publication requires RuntimeEvent")
        self._validate_string(event.event_type)
        if not event.event_type:
            raise EventValidationError("event_type must not be empty")
        self._validate_uuid(event.event_id)
        self._validate_uuid(event.session_id)
        self._validate_trace(event.trace)
        if not isinstance(cast(object, event.priority), EventPriority):
            raise EventValidationError("Event priority must be EventPriority")
        self._validate_timestamp(event.timestamp)

    def _validate_trace(self, trace: object) -> None:
        if not isinstance(trace, TraceContext):
            raise EventValidationError("Event trace must be TraceContext")
        self._validate_uuid(trace.trace_id)
        if trace.parent_trace_id is not None:
            self._validate_uuid(trace.parent_trace_id)
        if trace.correlation_id is not None:
            self._validate_uuid(trace.correlation_id)

    @staticmethod
    def _validate_uuid(value: object) -> None:
        if not isinstance(value, UUID):
            raise EventValidationError("Event identifiers must be UUID values")

    @staticmethod
    def _validate_timestamp(value: object) -> None:
        if not isinstance(value, datetime):
            raise EventValidationError("Event timestamp must be a UTC datetime")
        try:
            offset = value.utcoffset()
        except (OverflowError, TypeError, ValueError):
            raise EventValidationError("Event timestamp must use UTC") from None
        if value.tzinfo is None or offset != timedelta(0):
            raise EventValidationError("Event timestamp must use UTC")

    @staticmethod
    def _validate_string(value: object) -> None:
        if not isinstance(value, str):
            raise EventValidationError("Event strings must contain valid Unicode")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise EventValidationError("Event strings must contain valid Unicode") from None

    def _copy_payload(self, payload: object) -> Payload:
        if not isinstance(payload, dict):
            raise EventValidationError("Event payload must be a JSON object")
        return cast(Payload, self._copy_json(cast(object, payload), ancestors=set(), depth=0))

    def _copy_json(self, value: object, *, ancestors: set[int], depth: int) -> JSONValue:
        """Detach every occurrence; track only the current path to reject cycles."""
        if value is None or isinstance(value, bool | int):
            return value
        if isinstance(value, str):
            self._validate_string(value)
            return value
        if isinstance(value, float):
            if not isfinite(value):
                raise EventValidationError("Event JSON numbers must be finite")
            return value
        if not isinstance(value, dict | list):
            raise EventValidationError("Event payload contains a non-JSON value")
        if depth >= 256:
            raise EventValidationError("Event JSON exceeds 256 container levels")
        identity = id(cast(object, value))
        if identity in ancestors:
            raise EventValidationError("Event JSON must not contain cycles")
        ancestors.add(identity)
        try:
            if isinstance(value, list):
                return [
                    self._copy_json(item, ancestors=ancestors, depth=depth + 1)
                    for item in cast(list[object], value)
                ]
            result: Payload = {}
            for key, item in cast(dict[object, object], value).items():
                if not isinstance(key, str):
                    raise EventValidationError("Event JSON object keys must be strings")
                self._validate_string(key)
                result[key] = self._copy_json(item, ancestors=ancestors, depth=depth + 1)
            return result
        finally:
            ancestors.remove(identity)


__all__ = ["PublisherRuntime"]
