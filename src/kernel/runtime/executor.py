"""KR-009 sequential pipeline execution."""

from __future__ import annotations

from src.core.types import Payload
from src.kernel.contracts.context import RuntimeContext
from src.kernel.runtime.bus import EventBusRuntime
from src.kernel.runtime.pipeline import PipelineDefinition, PipelineStage


class ExecutorRuntime:
    """Own sequential execution flow for validated pipeline stages."""

    def __init__(self, event_bus: EventBusRuntime) -> None:
        self._event_bus = event_bus

    async def execute(self, pipeline: PipelineDefinition, *, context: RuntimeContext) -> None:
        await self._publish("pipeline.started", context, {"pipeline_id": str(pipeline.pipeline_id)})
        try:
            for stage in self.execution_order(pipeline):
                await self.execute_stage(stage, context=context)
        except Exception:
            await self._publish(
                "pipeline.failed", context, {"pipeline_id": str(pipeline.pipeline_id)}
            )
            raise
        await self._publish(
            "pipeline.completed", context, {"pipeline_id": str(pipeline.pipeline_id)}
        )

    async def execute_stage(self, stage: PipelineStage, *, context: RuntimeContext) -> None:
        await self._publish("pipeline.stage.started", context, {"stage_id": stage.stage_id})
        await self._publish("pipeline.stage.completed", context, {"stage_id": stage.stage_id})

    def execution_order(self, pipeline: PipelineDefinition) -> tuple[PipelineStage, ...]:
        stages = {stage.stage_id: stage for stage in pipeline.stages}
        completed: set[str] = set()
        ordered: list[PipelineStage] = []
        while len(ordered) < len(pipeline.stages):
            ready = [
                stage
                for stage in pipeline.stages
                if stage.stage_id not in completed and set(stage.depends_on).issubset(completed)
            ]
            if not ready:
                raise RuntimeError("Pipeline cannot be topologically ordered")
            for stage in ready:
                ordered.append(stages[stage.stage_id])
                completed.add(stage.stage_id)
        return tuple(ordered)

    async def _publish(self, event_type: str, context: RuntimeContext, payload: Payload) -> None:
        event = self._event_bus.create_for_runtime(
            event_type=event_type,
            payload=payload,
            context=context,
        )
        await self._event_bus.publish(event)


__all__ = ["ExecutorRuntime"]
