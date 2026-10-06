"""KR-009 sequential execution of explicitly supplied application operations."""

from __future__ import annotations

from asyncio import CancelledError
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from time import monotonic
from typing import cast
from uuid import UUID

from src.core.exceptions import ContractValidationError, InvalidManifestError, RuntimeStateError
from src.core.logger import get_logger
from src.core.types import EventPriority, ModuleId, Payload, RuntimeLayer
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.metadata import MetadataRuntime
from src.kernel.runtime.pipeline import PipelineDefinition, PipelineStage


class ExecutorRuntime:
    """Execute one pipeline at a time; own no bindings, context store or DI scope."""

    def __init__(self, event_bus: EventBusRuntime) -> None:
        self._event_bus = event_bus
        self._metadata = MetadataRuntime()
        self._validator = ManifestRuntime()
        self._busy = False
        self._logger = get_logger("aurora.kernel.pipeline")

    async def execute(
        self,
        pipeline: PipelineDefinition,
        *,
        context: RuntimeContext,
        operations: Mapping[ModuleId, Callable[[RuntimeContext], Awaitable[None]]],
    ) -> None:
        self._acquire()
        try:
            ordered = self.execution_order(pipeline)
            captured = self._capture_context(context)
            if pipeline.pipeline_id != captured.pipeline_id:
                raise InvalidManifestError("Pipeline and context identifiers must agree")
            if not isinstance(cast(object, operations), Mapping):
                raise InvalidManifestError("Operation bindings must be a mapping")
            bindings = dict(operations)
            for stage in ordered:
                if stage.module_id not in bindings or not callable(bindings[stage.module_id]):
                    raise InvalidManifestError("Every pipeline stage requires an operation")
            captured = replace(
                captured,
                metadata=self._metadata.merge(
                    captured.metadata,
                    {
                        "execution_started_at": datetime.now(UTC).isoformat(),
                        "stage_count": len(ordered),
                    },
                ),
            )
            started = monotonic()
            failed_stage = ""
            try:
                await self._publish(
                    "pipeline.started",
                    captured,
                    {
                        "pipeline_id": str(captured.pipeline_id),
                        "session_id": str(captured.session_id),
                    },
                )
                for index, stage in enumerate(ordered):
                    failed_stage = stage.stage_id
                    await self._execute_stage(
                        stage, context=captured, operation=bindings[stage.module_id], index=index
                    )
            except CancelledError as primary:
                await self._notify(
                    primary,
                    "pipeline.cancelled",
                    captured,
                    {
                        "pipeline_id": str(captured.pipeline_id),
                        "reason": "Pipeline execution cancelled",
                    },
                )
                raise
            except Exception as primary:
                await self._notify(
                    primary,
                    "pipeline.failed",
                    captured,
                    {
                        "pipeline_id": str(captured.pipeline_id),
                        "failed_stage": failed_stage,
                        "reason": "Pipeline execution failed",
                        "exception_type": type(primary).__name__,
                    },
                )
                raise
            # Outside the failure handlers: a terminal delivery error is not a second outcome.
            await self._publish(
                "pipeline.completed",
                captured,
                {
                    "pipeline_id": str(captured.pipeline_id),
                    "duration_ms": self._elapsed(started),
                    "stage_count": len(ordered),
                },
            )
        finally:
            self._busy = False

    async def execute_stage(
        self,
        stage: PipelineStage,
        *,
        context: RuntimeContext,
        operation: Callable[[RuntimeContext], Awaitable[None]],
    ) -> None:
        self._acquire()
        try:
            captured = self._capture_context(context)
            self._validator.validate_stage_ids(
                PipelineDefinition(pipeline_id=captured.pipeline_id, stages=(stage,))
            )
            if not callable(operation):
                raise InvalidManifestError("Pipeline stage requires an operation")
            await self._execute_stage(stage, context=captured, operation=operation, index=0)
        finally:
            self._busy = False

    def execution_order(self, pipeline: PipelineDefinition) -> tuple[PipelineStage, ...]:
        self._validator.validate(pipeline)
        completed: set[str] = set()
        ordered: list[PipelineStage] = []
        while len(ordered) < len(pipeline.stages):
            # Capture a whole ready wave before advancing dependencies.
            ready = tuple(
                stage
                for stage in pipeline.stages
                if stage.stage_id not in completed and set(stage.depends_on).issubset(completed)
            )
            for stage in ready:
                ordered.append(stage)
                completed.add(stage.stage_id)
        return tuple(ordered)

    def _acquire(self) -> None:
        if self._busy:
            raise RuntimeStateError("Pipeline executor is busy")
        self._busy = True

    def _capture_context(self, context: RuntimeContext) -> RuntimeContext:
        if not isinstance(cast(object, context), RuntimeContext) or not isinstance(
            cast(object, context.trace), TraceContext
        ):
            raise ContractValidationError("Runtime context and trace contracts are required")
        trace = context.trace
        if (
            not isinstance(cast(object, context.session_id), UUID)
            or not isinstance(cast(object, context.pipeline_id), UUID)
            or not isinstance(cast(object, context.runtime_layer), RuntimeLayer)
            or not isinstance(cast(object, trace.trace_id), UUID)
            or (
                trace.parent_trace_id is not None
                and not isinstance(cast(object, trace.parent_trace_id), UUID)
            )
            or (
                trace.correlation_id is not None
                and not isinstance(cast(object, trace.correlation_id), UUID)
            )
        ):
            raise ContractValidationError("Runtime context identity fields are invalid")
        for timestamp in (context.created_at, context.expires_at):
            if timestamp is not None and (
                not isinstance(cast(object, timestamp), datetime)
                or timestamp.utcoffset() != timedelta(0)
            ):
                raise ContractValidationError("Runtime context timestamps must be aware UTC")
        if not isinstance(cast(object, context.created_at), datetime):
            raise ContractValidationError("Runtime context creation timestamp is required")
        return replace(context, metadata=self._metadata.merge({}, context.metadata))

    async def _execute_stage(
        self,
        stage: PipelineStage,
        *,
        context: RuntimeContext,
        operation: Callable[[RuntimeContext], Awaitable[None]],
        index: int,
    ) -> None:
        captured = replace(
            context,
            metadata=self._metadata.merge(
                context.metadata,
                {
                    "stage_id": stage.stage_id,
                    "module_id": str(stage.module_id),
                    "stage_index": index,
                },
            ),
        )
        started = monotonic()
        try:
            await self._publish(
                "pipeline.stage.started",
                captured,
                self._stage_payload(stage, captured, duration=None, reason=None),
            )
            await operation(captured)
            completed = self._event_bus.create_for_runtime(
                event_type="pipeline.stage.completed",
                context=context,
                payload=self._stage_payload(
                    stage, context, duration=self._elapsed(started), reason=None
                ),
            )
        except CancelledError:
            raise
        except Exception as primary:
            await self._notify(
                primary,
                "pipeline.stage.failed",
                context,
                self._stage_payload(
                    stage, context, duration=self._elapsed(started), reason="Pipeline stage failed"
                ),
            )
            raise
        # The logical terminal stage event exists; never produce a second stage outcome.
        await self._event_bus.publish(completed)

    @staticmethod
    def _elapsed(started: float) -> float:
        return max(0.0, (monotonic() - started) * 1000.0)

    @staticmethod
    def _stage_payload(
        stage: PipelineStage, context: RuntimeContext, *, duration: float | None, reason: str | None
    ) -> Payload:
        return {
            "pipeline_id": str(context.pipeline_id),
            "stage_id": stage.stage_id,
            "module_id": str(stage.module_id),
            "duration_ms": duration,
            "reason": reason,
        }

    async def _publish(self, event_type: str, context: RuntimeContext, payload: Payload) -> None:
        priority = (
            EventPriority.HIGH
            if event_type in ("pipeline.failed", "pipeline.cancelled", "pipeline.stage.failed")
            else EventPriority.NORMAL
        )
        event = self._event_bus.create_for_runtime(
            event_type=event_type, payload=payload, context=context, priority=priority
        )
        await self._event_bus.publish(event)

    async def _notify(
        self, primary: BaseException, event_type: str, context: RuntimeContext, payload: Payload
    ) -> None:
        try:
            await self._publish(event_type, context, payload)
        except (Exception, CancelledError) as secondary:
            self._logger.warning("Pipeline notification failed (%s)", type(secondary).__name__)
            if secondary is primary:
                return
            earlier = primary.__cause__
            errors: list[BaseException] = (
                [earlier] if earlier is not None and earlier is not primary else []
            ) + [secondary]
            primary.__cause__ = BaseExceptionGroup("Pipeline notification failures", errors)
            primary.__suppress_context__ = True


__all__ = ["ExecutorRuntime"]
