"""KR-008 session context lifecycle."""

from __future__ import annotations

from uuid import uuid4

from src.core.exceptions import RuntimeStateError
from src.core.types import Metadata, PipelineId, RuntimeLayer, SessionId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.metadata import MetadataRuntime


class SessionRuntime:
    """Own immutable context snapshots for active sessions."""

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
        self._sessions[session_id] = context
        return context

    def get(self, session_id: SessionId) -> RuntimeContext:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise RuntimeStateError(
                "Session context does not exist", session_id=session_id
            ) from exc

    def update_metadata(self, session_id: SessionId, metadata: Metadata) -> RuntimeContext:
        context = self.get(session_id)
        replacement = RuntimeContext(
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            runtime_layer=context.runtime_layer,
            trace=context.trace,
            metadata=self._metadata.merge(context.metadata, metadata),
            created_at=context.created_at,
            expires_at=context.expires_at,
        )
        self._sessions[session_id] = replacement
        if (
            self._context_runtime.has_context()
            and self._context_runtime.current().session_id == session_id
        ):
            self._context_runtime.replace(replacement)
        return replacement

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


__all__ = ["SessionRuntime"]
