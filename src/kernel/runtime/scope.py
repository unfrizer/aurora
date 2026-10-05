"""KR-005 cached lifetime ownership; independent of runtime implementations."""

# Explicit IDs are checked at runtime even when a caller violates annotations.
# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast
from uuid import UUID

from src.core.exceptions import RuntimeShutdownError, ScopeViolationError
from src.core.types import DIScope, PipelineId, ServiceId, SessionId

type _Key = tuple[DIScope, SessionId | None, PipelineId | None, ServiceId]


class ScopeRuntime[T]:
    """Own cached instances and interrupted disposal, never construct services."""

    def __init__(self, *, dispose: Callable[[T], Awaitable[None]]) -> None:
        self._dispose = dispose
        self._entries: dict[_Key, T] = {}
        self._pending: list[tuple[_Key, T]] = []
        self._pipeline_sessions: dict[PipelineId, SessionId] = {}

    def _bind_pipeline(self, session_id: SessionId, pipeline_id: PipelineId) -> None:
        self._validate_ids(session_id, pipeline_id)
        existing = self._pipeline_sessions.get(pipeline_id)
        if existing is not None and existing != session_id:
            raise ScopeViolationError("Pipeline already belongs to another session")
        self._pipeline_sessions[pipeline_id] = session_id

    @staticmethod
    def _validate_ids(session_id: object, pipeline_id: object = None) -> None:
        if not isinstance(session_id, UUID):
            raise ScopeViolationError("A canonical session ID is required")
        if pipeline_id is not None and not isinstance(pipeline_id, UUID):
            raise ScopeViolationError("A canonical pipeline ID is required")

    def _key(
        self,
        service_id: ServiceId,
        scope: DIScope,
        session_id: SessionId | None,
        pipeline_id: PipelineId | None,
    ) -> _Key:
        if scope is DIScope.APPLICATION:
            return scope, None, None, service_id
        if scope is DIScope.SESSION:
            self._validate_ids(session_id)
            return scope, session_id, None, service_id
        if scope is DIScope.PIPELINE:
            self._validate_ids(session_id, pipeline_id)
            if session_id is None or pipeline_id is None:
                raise ScopeViolationError("Pipeline requires session and pipeline IDs")
            existing = self._pipeline_sessions.get(pipeline_id)
            if existing is not None and existing != session_id:
                raise ScopeViolationError("Pipeline already belongs to another session")
            return scope, session_id, pipeline_id, service_id
        raise ScopeViolationError("Only cached DI scopes are supported")

    def get(
        self,
        service_id: ServiceId,
        *,
        scope: DIScope,
        session_id: SessionId | None = None,
        pipeline_id: PipelineId | None = None,
    ) -> T | None:
        return self._entries.get(self._key(service_id, scope, session_id, pipeline_id))

    def put(
        self,
        service_id: ServiceId,
        service: T,
        *,
        scope: DIScope,
        session_id: SessionId | None = None,
        pipeline_id: PipelineId | None = None,
    ) -> None:
        key = self._key(service_id, scope, session_id, pipeline_id)
        if key in self._entries:
            raise ScopeViolationError("Cannot overwrite an owned cached instance")
        if scope is DIScope.PIPELINE and session_id is not None and pipeline_id is not None:
            self._bind_pipeline(session_id, pipeline_id)
        self._entries[key] = service

    def _detach(self, select: Callable[[_Key], bool]) -> list[T]:
        for key in tuple(self._entries):
            if select(key):
                self._pending.append((key, self._entries.pop(key)))
        return [value for key, value in self._pending if select(key)]

    def _complete(self, value: T) -> None:
        self._pending = [(key, item) for key, item in self._pending if item is not value]

    async def _cleanup(self, values: list[T]) -> None:
        errors: list[Exception] = []
        for value in reversed(values):
            try:
                await self._dispose(value)
            except Exception as error:
                errors.append(error)
            except BaseException as interruption:
                if errors:
                    cause = interruption.__cause__
                    if isinstance(cause, ExceptionGroup):
                        errors.extend(cast(ExceptionGroup[Exception], cause).exceptions)
                    raise interruption from ExceptionGroup("Earlier disposal failures", errors)
                raise
            self._complete(value)
        if errors:
            raise RuntimeShutdownError("Scope disposal failed") from ExceptionGroup(
                "Scope disposal failures", errors
            )

    async def remove(
        self,
        service_id: ServiceId,
        *,
        scope: DIScope,
        session_id: SessionId | None = None,
        pipeline_id: PipelineId | None = None,
    ) -> None:
        key = self._key(service_id, scope, session_id, pipeline_id)
        await self._cleanup(self._detach(lambda candidate: candidate == key))

    async def remove_all(self, service_id: ServiceId) -> None:
        await self._cleanup(self._detach(lambda key: key[3] == service_id))

    async def clear_session(self, session_id: SessionId) -> None:
        self._validate_ids(session_id)
        await self._cleanup(self._detach(lambda key: key[1] == session_id))

    async def clear_pipeline(self, pipeline_id: PipelineId) -> None:
        if not isinstance(pipeline_id, UUID):
            raise ScopeViolationError("A canonical pipeline ID is required")
        await self._cleanup(self._detach(lambda key: key[2] == pipeline_id))

    async def clear_application(self) -> None:
        await self._cleanup(self._detach(lambda key: key[0] is DIScope.APPLICATION))

    async def shutdown(self) -> None:
        self._detach(lambda _key: True)
        errors: list[Exception] = []
        for scope in (DIScope.PIPELINE, DIScope.SESSION, DIScope.APPLICATION):
            try:
                await self._cleanup([value for key, value in self._pending if key[0] is scope])
            except RuntimeShutdownError as error:
                cause = error.__cause__
                if isinstance(cause, ExceptionGroup):
                    errors.extend(cast(ExceptionGroup[Exception], cause).exceptions)
                else:
                    errors.append(error)
            except BaseException as interruption:
                if errors:
                    cause = interruption.__cause__
                    if isinstance(cause, ExceptionGroup):
                        errors.extend(cast(ExceptionGroup[Exception], cause).exceptions)
                    raise interruption from ExceptionGroup("Earlier disposal failures", errors)
                raise
        if errors:
            raise RuntimeShutdownError("Scope shutdown failed") from ExceptionGroup(
                "Scope shutdown failures", errors
            )


__all__ = ["ScopeRuntime"]
