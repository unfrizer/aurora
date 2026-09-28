"""KR-009 immutable pipeline definitions."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.types import ModuleId, PipelineId


@dataclass(frozen=True, kw_only=True, slots=True)
class PipelineStage:
    """One module stage in an immutable pipeline DAG."""

    stage_id: str
    module_id: ModuleId
    depends_on: tuple[str, ...]

    @property
    def dependency_count(self) -> int:
        return len(self.depends_on)

    @property
    def has_dependencies(self) -> bool:
        return bool(self.depends_on)


@dataclass(frozen=True, kw_only=True, slots=True)
class PipelineDefinition:
    """Ordered, immutable pipeline execution graph."""

    pipeline_id: PipelineId
    stages: tuple[PipelineStage, ...]

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    @property
    def is_empty(self) -> bool:
        return not self.stages


__all__ = ["PipelineDefinition", "PipelineStage"]
