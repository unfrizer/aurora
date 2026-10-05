"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/context.py

Canonical Runtime Context contract.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from src.core.types import Metadata, PipelineId, RuntimeLayer, SessionId, TraceId

# ============================================================================
# Typed Default Factories
# ============================================================================


def _metadata_factory() -> Metadata:
    """Return an empty metadata mapping with the canonical Metadata type."""
    return {}


# ============================================================================
# Trace Context Contract
# ============================================================================


@dataclass(frozen=True, kw_only=True, slots=True)
class TraceContext:
    """
    Immutable trace metadata propagated across runtime boundaries.
    """

    trace_id: TraceId
    parent_trace_id: TraceId | None = None
    correlation_id: UUID | None = None


# ============================================================================
# Runtime Context Contract
# ============================================================================


@dataclass(frozen=True, kw_only=True, slots=True)
class RuntimeContext:
    """
    Frozen execution-context shell with JSON-compatible metadata.

    Frozen fields do not make nested JSON immutable. KR-008 owns detached JSON
    copies at public context boundaries (ADR-004 P-04); snapshot object identity
    is not guaranteed. Direct construction does not copy or validate metadata.
    """

    session_id: SessionId
    pipeline_id: PipelineId
    runtime_layer: RuntimeLayer
    trace: TraceContext
    metadata: Metadata = field(default_factory=_metadata_factory)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.now(UTC) >= self.expires_at

    @property
    def trace_id(self) -> TraceId:
        return self.trace.trace_id

    @property
    def root_trace_id(self) -> TraceId:
        return self.trace.parent_trace_id or self.trace.trace_id

    @property
    def depth(self) -> int:
        return 0 if self.trace.parent_trace_id is None else 1


__all__ = ["RuntimeContext", "TraceContext"]
