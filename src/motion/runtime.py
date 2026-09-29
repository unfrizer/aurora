"""Deterministic implementation of the Wave 5 Motion Runtime."""

# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

import math

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.motion.contracts import MotionContract, MotionDefinition, MotionSample


class MotionRuntime(MotionContract):
    """Validate and sample motion progress without owning time or work."""

    @property
    def runtime_name(self) -> str:
        return "motion"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L4_MOTION

    async def initialize(self) -> None:
        return None

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def validate(self, definition: MotionDefinition) -> None:
        if not isinstance(definition, MotionDefinition):
            raise ValidationError("Motion definition must be a MotionDefinition")
        if not definition.motion_id.strip():
            raise ValidationError("Motion ID must be non-empty")
        self._validate_time(definition.duration_ms, field="duration_ms")

    def sample(self, definition: MotionDefinition, elapsed_ms: float) -> MotionSample:
        self.validate(definition)
        self._validate_time(elapsed_ms, field="elapsed_ms")

        if definition.duration_ms == 0.0:
            progress = 1.0
        else:
            progress = min(elapsed_ms / definition.duration_ms, 1.0)
        return MotionSample(
            motion_id=definition.motion_id,
            progress=progress,
            is_complete=progress == 1.0,
        )

    @staticmethod
    def _validate_time(value: object, *, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValidationError("Motion time must be numeric", field=field)
        if not math.isfinite(value):
            raise ValidationError("Motion time must be finite", field=field)
        if value < 0.0:
            raise ValidationError("Motion time must be non-negative", field=field)


__all__ = ["MotionRuntime"]
