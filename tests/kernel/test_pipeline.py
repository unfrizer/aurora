from __future__ import annotations

from uuid import uuid4

import pytest

from src.core.exceptions import RuntimeDependencyError
from src.core.types import ModuleId, PipelineId
from src.kernel.runtime.manifest import ManifestRuntime
from src.kernel.runtime.pipeline import PipelineDefinition, PipelineStage


def test_manifest_validates_topological_pipeline() -> None:
    pipeline = PipelineDefinition(
        pipeline_id=PipelineId(uuid4()),
        stages=(
            PipelineStage(stage_id="first", module_id=ModuleId("first"), depends_on=()),
            PipelineStage(stage_id="second", module_id=ModuleId("second"), depends_on=("first",)),
        ),
    )
    assert ManifestRuntime().validate(pipeline) is pipeline


def test_manifest_rejects_cycles() -> None:
    pipeline = PipelineDefinition(
        pipeline_id=PipelineId(uuid4()),
        stages=(
            PipelineStage(stage_id="one", module_id=ModuleId("one"), depends_on=("two",)),
            PipelineStage(stage_id="two", module_id=ModuleId("two"), depends_on=("one",)),
        ),
    )
    with pytest.raises(RuntimeDependencyError):
        ManifestRuntime().validate(pipeline)
