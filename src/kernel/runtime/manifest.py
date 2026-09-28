"""KR-009 pipeline manifest validation."""

from __future__ import annotations

from src.core.exceptions import InvalidManifestError, RuntimeDependencyError
from src.kernel.runtime.pipeline import PipelineDefinition


class ManifestRuntime:
    """Validate immutable pipeline definitions without executing them."""

    def validate(self, definition: PipelineDefinition) -> PipelineDefinition:
        if definition.is_empty:
            raise InvalidManifestError("Pipeline must contain at least one stage")
        self.validate_stage_ids(definition)
        self.validate_dependencies(definition)
        self.validate_dag(definition)
        return definition

    def validate_stage_ids(self, definition: PipelineDefinition) -> None:
        stage_ids = tuple(stage.stage_id for stage in definition.stages)
        if len(stage_ids) != len(set(stage_ids)) or any(not stage_id for stage_id in stage_ids):
            raise InvalidManifestError("Pipeline stage identifiers must be unique and non-empty")

    def validate_dependencies(self, definition: PipelineDefinition) -> None:
        stage_ids = {stage.stage_id for stage in definition.stages}
        for stage in definition.stages:
            for dependency in stage.depends_on:
                if dependency == stage.stage_id or dependency not in stage_ids:
                    raise InvalidManifestError(
                        "Pipeline stage dependency is invalid",
                        stage_id=stage.stage_id,
                        dependency=dependency,
                    )

    def validate_dag(self, definition: PipelineDefinition) -> None:
        dependencies = {stage.stage_id: stage.depends_on for stage in definition.stages}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(stage_id: str) -> None:
            if stage_id in visiting:
                raise RuntimeDependencyError(
                    "Pipeline dependency cycle detected", stage_id=stage_id
                )
            if stage_id in visited:
                return
            visiting.add(stage_id)
            for dependency in dependencies[stage_id]:
                visit(dependency)
            visiting.remove(stage_id)
            visited.add(stage_id)

        for stage_id in dependencies:
            visit(stage_id)


__all__ = ["ManifestRuntime"]
