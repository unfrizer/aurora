from __future__ import annotations

from uuid import uuid4

from src.core.types import PipelineId, RuntimeLayer, SessionId, TraceId
from src.kernel.contracts.context import TraceContext
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.session import SessionRuntime


def test_context_and_session_replace_immutable_snapshots() -> None:
    context_runtime = ContextRuntime()
    session_runtime = SessionRuntime(context_runtime)
    session_id = SessionId(uuid4())
    context = context_runtime.create(
        session_id=session_id,
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        metadata={"source": "test"},
        trace=TraceContext(trace_id=TraceId(uuid4())),
    )
    assert context_runtime.current() is context
    session_runtime.create(session_id=session_id, trace=context.trace)
    updated = session_runtime.update_metadata(session_id, {"key": "value"})
    assert updated.metadata["key"] == "value"
