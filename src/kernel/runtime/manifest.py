"""KR-009 stateless validation of immutable pipeline DAGs."""

from __future__ import annotations

from collections import deque
from typing import cast
from uuid import UUID

from src.core.exceptions import InvalidManifestError, RuntimeDependencyError
from src.kernel.runtime.pipeline import PipelineDefinition, PipelineStage


class ManifestRuntime:
    """Validate existing contracts without changing their fields or identity."""

    def validate(self, definition: PipelineDefinition) -> PipelineDefinition:
        self.validate_dag(definition)
        return definition

    def validate_stage_ids(self, definition: PipelineDefinition) -> None:
        self._validate_shape(definition)
        stage_ids = tuple(stage.stage_id for stage in definition.stages)
        if len(stage_ids) != len(set(stage_ids)):
            raise InvalidManifestError("Pipeline stage identifiers must be unique")

    def validate_dependencies(self, definition: PipelineDefinition) -> None:
        self.validate_stage_ids(definition)
        stage_ids = {stage.stage_id for stage in definition.stages}
        for stage in definition.stages:
            for dependency in stage.depends_on:
                if dependency == stage.stage_id or dependency not in stage_ids:
                    raise InvalidManifestError("Pipeline stage dependency is invalid")

    def validate_dag(self, definition: PipelineDefinition) -> None:
        self.validate_dependencies(definition)
        remaining = {stage.stage_id: len(set(stage.depends_on)) for stage in definition.stages}
        dependents: dict[str, list[str]] = {stage.stage_id: [] for stage in definition.stages}
        for stage in definition.stages:
            for dependency in set(stage.depends_on):
                dependents[dependency].append(stage.stage_id)
        ready = deque(stage_id for stage_id, count in remaining.items() if count == 0)
        visited = 0
        while ready:
            stage_id = ready.popleft()
            visited += 1
            for dependent in dependents[stage_id]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)
        if visited != len(definition.stages):
            raise RuntimeDependencyError("Pipeline dependency cycle detected")

    @staticmethod
    def _identifier(value: object) -> None:
        if not isinstance(value, str) or not value:
            raise InvalidManifestError("Pipeline identifiers must be non-empty strings")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise InvalidManifestError("Pipeline identifiers must contain valid Unicode") from None

    def _validate_shape(self, definition: PipelineDefinition) -> None:
        if not isinstance(cast(object, definition), PipelineDefinition):
            raise InvalidManifestError("Pipeline definition contract is required")
        if not isinstance(cast(object, definition.pipeline_id), UUID):
            raise InvalidManifestError("Pipeline identifier must be a UUID")
        if not isinstance(cast(object, definition.stages), tuple) or not definition.stages:
            raise InvalidManifestError("Pipeline must contain a non-empty stage tuple")
        for stage in definition.stages:
            if not isinstance(cast(object, stage), PipelineStage):
                raise InvalidManifestError("Pipeline stage contract is required")
            self._identifier(stage.stage_id)
            self._identifier(stage.module_id)
            if not isinstance(cast(object, stage.depends_on), tuple):
                raise InvalidManifestError("Stage dependencies must be a tuple")
            for dependency in stage.depends_on:
                self._identifier(dependency)


__all__ = ["ManifestRuntime"]
