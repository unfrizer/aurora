"""Contract tests for the Interaction Runtime."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.interaction.contracts import (
    InteractionContract,
    InteractionRequest,
    InteractionSnapshot,
)
from src.kernel.contracts.runtime import RuntimeContract


def test_interaction_models_are_frozen_dataclasses() -> None:
    request = InteractionRequest(interaction_id="select-1", action="select", target_id="hero")
    snapshot = InteractionSnapshot(revision=0, latest=request)

    assert is_dataclass(request)
    assert is_dataclass(snapshot)
    with pytest.raises(FrozenInstanceError):
        request.action = "activate"  # type: ignore[misc]


def test_interaction_contract_is_abstract_runtime_contract() -> None:
    assert issubclass(InteractionContract, RuntimeContract)
    assert InteractionContract.__abstractmethods__ == {
        "clear",
        "current",
        "health",
        "initialize",
        "runtime_layer",
        "runtime_name",
        "shutdown",
        "snapshot",
        "start",
        "stop",
        "submit",
    }
