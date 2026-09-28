"""KR-008 active RuntimeContext owner."""

from __future__ import annotations

from datetime import UTC, datetime

from src.core.exceptions import RuntimeStateError
from src.core.types import HealthStatus, Metadata, PipelineId, RuntimeLayer, SessionId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.metadata import MetadataRuntime


class ContextRuntime(RuntimeContract):
    """Own the current immutable execution-context snapshot."""

    def __init__(self) -> None:
        self._context: RuntimeContext | None = None
        self._metadata = MetadataRuntime()

    @property
    def runtime_name(self) -> str:
        return "context"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L0_KERNEL

    def create(
        self,
        *,
        session_id: SessionId,
        pipeline_id: PipelineId,
        runtime_layer: RuntimeLayer,
        metadata: Metadata,
        trace: TraceContext,
    ) -> RuntimeContext:
        context = RuntimeContext(
            session_id=session_id,
            pipeline_id=pipeline_id,
            runtime_layer=runtime_layer,
            trace=trace,
            metadata=self._metadata.merge({}, metadata),
            created_at=datetime.now(UTC),
            expires_at=None,
        )
        self._context = context
        return context

    def current(self) -> RuntimeContext:
        if self._context is None:
            raise RuntimeStateError("No active runtime context")
        return self._context

    def replace(self, context: RuntimeContext) -> RuntimeContext:
        self._context = context
        return context

    def clear(self) -> None:
        self._context = None

    def has_context(self) -> bool:
        return self._context is not None

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


__all__ = ["ContextRuntime"]
