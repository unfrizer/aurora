"""KR-005 deterministic DI scope storage."""

from __future__ import annotations

from src.core.exceptions import ScopeViolationError
from src.core.types import DIScope, PipelineId, ServiceId, SessionId
from src.kernel.contracts.context import RuntimeContext
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor
from src.kernel.runtime.provider import ProviderRuntime


class ScopeRuntime:
    """Own cache lifetime for Application, Session and Pipeline scopes."""

    def __init__(self, provider: ProviderRuntime) -> None:
        self._provider = provider
        self._application: dict[ServiceId, ServiceContract] = {}
        self._sessions: dict[SessionId, dict[ServiceId, ServiceContract]] = {}
        self._pipelines: dict[PipelineId, dict[ServiceId, ServiceContract]] = {}

    def get(
        self,
        descriptor: ServiceDescriptor,
        *,
        context: RuntimeContext | None,
    ) -> ServiceContract | None:
        cache = self._cache_for(descriptor.scope, context)
        return None if cache is None else cache.get(descriptor.service_id)

    def put(
        self,
        descriptor: ServiceDescriptor,
        service: ServiceContract,
        *,
        context: RuntimeContext | None,
    ) -> None:
        cache = self._cache_for(descriptor.scope, context)
        if cache is not None:
            cache[descriptor.service_id] = service

    def remove(self, descriptor: ServiceDescriptor, *, context: RuntimeContext | None) -> None:
        cache = self._cache_for(descriptor.scope, context)
        if cache is not None:
            cache.pop(descriptor.service_id, None)

    async def clear_session(self, session_id: SessionId) -> None:
        await self._dispose_cache(self._sessions.pop(session_id, {}))

    async def clear_pipeline(self, pipeline_id: PipelineId) -> None:
        await self._dispose_cache(self._pipelines.pop(pipeline_id, {}))

    async def clear_application(self) -> None:
        await self._dispose_cache(self._application)
        self._application = {}

    async def shutdown(self) -> None:
        for session_id in tuple(self._sessions):
            await self.clear_session(session_id)
        for pipeline_id in tuple(self._pipelines):
            await self.clear_pipeline(pipeline_id)
        await self.clear_application()

    def _cache_for(
        self,
        scope: DIScope,
        context: RuntimeContext | None,
    ) -> dict[ServiceId, ServiceContract] | None:
        if scope is DIScope.APPLICATION:
            return self._application
        if scope is DIScope.TRANSIENT:
            return None
        if context is None:
            raise ScopeViolationError("A runtime context is required for scoped resolution")
        if scope is DIScope.SESSION:
            return self._sessions.setdefault(context.session_id, {})
        if scope is DIScope.PIPELINE:
            return self._pipelines.setdefault(context.pipeline_id, {})
        raise ScopeViolationError("Unsupported dependency-injection scope", scope=scope)

    async def _dispose_cache(self, cache: dict[ServiceId, ServiceContract]) -> None:
        for service in tuple(cache.values()):
            await self._provider.dispose(service)


__all__ = ["ScopeRuntime"]
