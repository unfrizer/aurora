"""Contract tests for the Motion Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.kernel.contracts.runtime import RuntimeContract
from src.motion.contracts import MotionContract, MotionDefinition, MotionSample


def test_motion_models_are_frozen_dataclasses() -> None:
    definition = MotionDefinition(motion_id="enter", duration_ms=100.0)
    sample = MotionSample(motion_id="enter", progress=0.5, is_complete=False)

    assert is_dataclass(definition)
    assert is_dataclass(sample)
    with pytest.raises(FrozenInstanceError):
        sample.progress = 1.0  # type: ignore[misc]


def test_motion_contract_is_abstract_runtime_contract() -> None:
    assert issubclass(MotionContract, RuntimeContract)
    assert MotionContract.__abstractmethods__ == {
        "health",
        "initialize",
        "runtime_layer",
        "runtime_name",
        "sample",
        "shutdown",
        "start",
        "stop",
        "validate",
    }
