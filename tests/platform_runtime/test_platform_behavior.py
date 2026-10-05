from __future__ import annotations

from typing import cast

import pytest

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.platform import PlatformDescriptor, PlatformRuntime


def test_configuration_revision_and_identity() -> None:
    runtime = PlatformRuntime()
    platform = PlatformDescriptor(platform_id="windows", display_name="Windows")
    assert runtime.runtime_name == "platform" and runtime.runtime_layer is RuntimeLayer.L7_PLATFORM
    assert runtime.health() is HealthStatus.OK and runtime.current() is None
    assert runtime.configure(platform).revision == 1
    assert runtime.configure(platform).revision == 2
    assert runtime.clear().revision == 3 and runtime.clear().revision == 3


@pytest.mark.parametrize(
    "platform",
    [
        PlatformDescriptor(platform_id=" ", display_name="Windows"),
        PlatformDescriptor(platform_id="windows", display_name=" "),
    ],
)
def test_invalid_platform_is_rejected(platform: PlatformDescriptor) -> None:
    with pytest.raises(ValidationError):
        PlatformRuntime().configure(platform)


@pytest.mark.parametrize(
    "invalid_platform",
    [
        PlatformDescriptor(platform_id=cast(str, None), display_name="Windows"),
        PlatformDescriptor(platform_id="windows", display_name=cast(str, 123)),
    ],
)
def test_invalid_platform_preserves_existing_configuration(
    invalid_platform: PlatformDescriptor,
) -> None:
    runtime = PlatformRuntime()
    before = runtime.configure(PlatformDescriptor(platform_id="windows", display_name="Windows"))

    with pytest.raises(ValidationError):
        runtime.configure(invalid_platform)

    assert runtime.snapshot() == before


@pytest.mark.asyncio
async def test_shutdown_resets_on_initialize() -> None:
    runtime = PlatformRuntime()
    runtime.configure(PlatformDescriptor(platform_id="windows", display_name="Windows"))
    await runtime.shutdown()
    with pytest.raises(RuntimeError):
        runtime.snapshot()
    await runtime.initialize()
    assert runtime.snapshot().revision == 0
