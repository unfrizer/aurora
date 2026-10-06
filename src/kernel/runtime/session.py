"""KR-008 detached session-context registry and active-owner coordination."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from src.core.exceptions import RuntimeStateError
from src.core.types import Metadata, PipelineId, RuntimeLayer, SessionId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.metadata import MetadataRuntime


class SessionRuntime:
    """Own session snapshots independently of caller and active context data."""

    def __init__(self, context_runtime: ContextRuntime) -> None:
        self._context_runtime = context_runtime
        self._metadata = MetadataRuntime()
        self._sessions: dict[SessionId, RuntimeContext] = {}

    def create(
        self,
        *,
        session_id: SessionId,
        trace: TraceContext,
        metadata: Metadata | None = None,
    ) -> RuntimeContext:
        context = self._context_runtime.create(
            session_id=session_id,
            pipeline_id=PipelineId(uuid4()),
            runtime_layer=RuntimeLayer.L0_KERNEL,
            metadata={} if metadata is None else metadata,
            trace=trace,
        )
        stored = self._snapshot(context)
        returned = self._snapshot(stored)
        self._sessions[session_id] = stored
        return returned

    def get(self, session_id: SessionId) -> RuntimeContext:
        try:
            stored = self._sessions[session_id]
        except KeyError as exc:
            raise RuntimeStateError(
                "Session context does not exist", session_id=session_id
            ) from exc
        return self._snapshot(stored)

    def update_metadata(self, session_id: SessionId, metadata: Metadata) -> RuntimeContext:
        context = self.get(session_id)
        replacement = replace(context, metadata=self._metadata.merge(context.metadata, metadata))
        stored = self._snapshot(replacement)
        returned = self._snapshot(stored)
        if (
            self._context_runtime.has_context()
            and self._context_runtime.current().session_id == session_id
        ):
            self._context_runtime.replace(stored)
        self._sessions[session_id] = stored
        return returned

    def remove(self, session_id: SessionId) -> None:
        self.get(session_id)
        del self._sessions[session_id]
        if (
            self._context_runtime.has_context()
            and self._context_runtime.current().session_id == session_id
        ):
            self._context_runtime.clear()

    def contains(self, session_id: SessionId) -> bool:
        return session_id in self._sessions

    def list(self) -> tuple[SessionId, ...]:
        return tuple(self._sessions)

    def _snapshot(self, context: RuntimeContext) -> RuntimeContext:
        """Detach a stored context whose fields were validated by ContextRuntime."""
        return replace(context, metadata=self._metadata.merge({}, context.metadata))


__all__ = ["SessionRuntime"]
