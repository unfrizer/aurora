"""Behavior tests for the Interaction Runtime."""

from __future__ import annotations

import pytest

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.interaction import InteractionRequest, InteractionRuntime, InteractionSnapshot


def _request() -> InteractionRequest:
    return InteractionRequest(interaction_id="select-1", action="select", target_id="hero")


@pytest.mark.asyncio
async def test_identity_lifecycle_and_health_are_deterministic() -> None:
    runtime = InteractionRuntime()

    assert runtime.runtime_name == "interaction"
    assert runtime.runtime_layer is RuntimeLayer.L5_INTERACTION
    assert runtime.health() is HealthStatus.OK
    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    assert runtime.snapshot() == InteractionSnapshot(revision=0, latest=None)


def test_submit_and_clear_follow_revision_semantics() -> None:
    runtime = InteractionRuntime()
    request = _request()

    assert runtime.current() is None
    assert runtime.submit(request) == InteractionSnapshot(revision=1, latest=request)
    assert runtime.submit(request).revision == 2
    assert runtime.clear() == InteractionSnapshot(revision=3, latest=None)
    assert runtime.clear().revision == 3


@pytest.mark.parametrize(
    "interaction",
    [
        InteractionRequest(interaction_id=" ", action="select", target_id="hero"),
        InteractionRequest(interaction_id="id", action=" ", target_id="hero"),
        InteractionRequest(interaction_id="id", action="select", target_id=" "),
    ],
)
def test_invalid_requests_are_rejected(interaction: InteractionRequest) -> None:
    with pytest.raises(ValidationError):
        InteractionRuntime().submit(interaction)


@pytest.mark.asyncio
async def test_shutdown_releases_request_and_initialize_starts_fresh() -> None:
    runtime = InteractionRuntime()
    runtime.submit(_request())
    await runtime.shutdown()

    with pytest.raises(RuntimeError):
        runtime.snapshot()

    await runtime.initialize()
    assert runtime.snapshot() == InteractionSnapshot(revision=0, latest=None)
