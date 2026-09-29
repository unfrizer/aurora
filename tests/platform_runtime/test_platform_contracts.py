from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.kernel.contracts.runtime import RuntimeContract
from src.platform import PlatformContract, PlatformDescriptor, PlatformSnapshot


def test_models_are_frozen() -> None:
    descriptor = PlatformDescriptor(platform_id="windows", display_name="Windows")
    assert is_dataclass(descriptor) and is_dataclass(
        PlatformSnapshot(revision=0, platform=descriptor)
    )
    with pytest.raises(FrozenInstanceError):
        descriptor.platform_id = "other"  # type: ignore[misc]


def test_contract_is_runtime_contract() -> None:
    assert issubclass(PlatformContract, RuntimeContract)
    assert {"configure", "current", "snapshot", "clear"} <= PlatformContract.__abstractmethods__
