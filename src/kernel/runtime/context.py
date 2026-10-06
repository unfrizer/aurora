"""KR-008 active validated, detached RuntimeContext owner."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

from src.core.exceptions import ContractValidationError, RuntimeStateError
from src.core.types import HealthStatus, Metadata, PipelineId, RuntimeLayer, SessionId
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime.metadata import MetadataRuntime


class ContextRuntime(RuntimeContract):
    """Own only the active context; public snapshots never alias its metadata."""

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
            metadata=metadata,
            created_at=datetime.now(UTC),
            expires_at=None,
        )
        return self.replace(context)

    def current(self) -> RuntimeContext:
        if self._context is None:
            raise RuntimeStateError("No active runtime context")
        return self._snapshot(self._context)

    def replace(self, context: RuntimeContext) -> RuntimeContext:
        stored = self._snapshot(context)
        returned = self._snapshot(stored)
        self._context = stored
        return returned

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

    def _snapshot(self, context: object) -> RuntimeContext:
        """Internal KR-008 value capture; does not change the active reference."""
        if not isinstance(context, RuntimeContext):
            raise ContractValidationError("Context must be RuntimeContext")
        self._validate_uuid(context.session_id)
        self._validate_uuid(context.pipeline_id)
        if not isinstance(cast(object, context.runtime_layer), RuntimeLayer):
            raise ContractValidationError("Context layer must be RuntimeLayer")
        self._validate_trace(context.trace)
        self._validate_timestamp(context.created_at)
        if context.expires_at is not None:
            self._validate_timestamp(context.expires_at)
        return replace(context, metadata=self._metadata.merge({}, context.metadata))

    def _validate_trace(self, trace: object) -> None:
        if not isinstance(trace, TraceContext):
            raise ContractValidationError("Context trace must be TraceContext")
        self._validate_uuid(trace.trace_id)
        if trace.parent_trace_id is not None:
            self._validate_uuid(trace.parent_trace_id)
        if trace.correlation_id is not None:
            self._validate_uuid(trace.correlation_id)

    @staticmethod
    def _validate_uuid(value: object) -> None:
        if not isinstance(value, UUID):
            raise ContractValidationError("Context identifiers must be UUID values")

    @staticmethod
    def _validate_timestamp(value: object) -> None:
        if not isinstance(value, datetime):
            raise ContractValidationError("Context timestamps must be UTC datetimes")
        try:
            offset = value.utcoffset()
        except (OverflowError, TypeError, ValueError):
            raise ContractValidationError("Context timestamps must use UTC") from None
        if value.tzinfo is None or offset != timedelta(0):
            raise ContractValidationError("Context timestamps must use UTC")


__all__ = ["ContextRuntime"]
