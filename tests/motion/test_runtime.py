"""Behavior tests for the Motion Runtime."""

from __future__ import annotations

import math

import pytest

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.motion import MotionDefinition, MotionRuntime


@pytest.mark.asyncio
async def test_identity_lifecycle_and_health_are_deterministic() -> None:
    runtime = MotionRuntime()

    assert runtime.runtime_name == "motion"
    assert runtime.runtime_layer is RuntimeLayer.L4_MOTION
    assert runtime.health() is HealthStatus.OK
    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    await runtime.shutdown()


def test_sample_returns_linear_clamped_progress() -> None:
    runtime = MotionRuntime()
    definition = MotionDefinition(motion_id="enter", duration_ms=100.0)

    assert runtime.sample(definition, 0.0).progress == 0.0
    assert runtime.sample(definition, 50.0).progress == 0.5
    assert runtime.sample(definition, 100.0).is_complete is True
    assert runtime.sample(definition, 400.0).progress == 1.0


def test_zero_duration_is_immediately_complete() -> None:
    sample = MotionRuntime().sample(MotionDefinition(motion_id="instant", duration_ms=0.0), 0.0)

    assert sample.progress == 1.0
    assert sample.is_complete is True


@pytest.mark.parametrize(
    "definition, elapsed_ms",
    [
        (MotionDefinition(motion_id=" ", duration_ms=1.0), 0.0),
        (MotionDefinition(motion_id="enter", duration_ms=-1.0), 0.0),
        (MotionDefinition(motion_id="enter", duration_ms=math.inf), 0.0),
        (MotionDefinition(motion_id="enter", duration_ms=1.0), -1.0),
        (MotionDefinition(motion_id="enter", duration_ms=1.0), math.nan),
    ],
)
def test_invalid_motion_values_are_rejected(
    definition: MotionDefinition, elapsed_ms: float
) -> None:
    with pytest.raises(ValidationError):
        MotionRuntime().sample(definition, elapsed_ms)
