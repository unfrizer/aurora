"""Deterministic in-memory implementation of the Wave 8 Platform Runtime."""

# pyright: reportUnnecessaryIsInstance=false
from __future__ import annotations

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.platform.contracts import PlatformContract, PlatformDescriptor, PlatformSnapshot


class PlatformRuntime(PlatformContract):
    """Own a target-platform descriptor without querying the host OS."""

    def __init__(self) -> None:
        self._platform: PlatformDescriptor | None = None
        self._revision = 0
        self._is_shutdown = False

    @property
    def runtime_name(self) -> str:
        return "platform"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L7_PLATFORM

    async def initialize(self) -> None:
        if self._is_shutdown:
            self._platform = None
            self._revision = 0
            self._is_shutdown = False

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self._platform = None
        self._is_shutdown = True

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def current(self) -> PlatformDescriptor | None:
        self._require_active()
        return self._platform

    def snapshot(self) -> PlatformSnapshot:
        self._require_active()
        return PlatformSnapshot(revision=self._revision, platform=self._platform)

    def configure(self, platform: PlatformDescriptor) -> PlatformSnapshot:
        self._require_active()
        self._validate(platform)
        self._platform = platform
        self._revision += 1
        return self.snapshot()

    def clear(self) -> PlatformSnapshot:
        self._require_active()
        if self._platform is not None:
            self._platform = None
            self._revision += 1
        return self.snapshot()

    def _require_active(self) -> None:
        if self._is_shutdown:
            raise RuntimeError("Platform Runtime is shut down")

    @staticmethod
    def _validate(platform: PlatformDescriptor) -> None:
        if not isinstance(platform, PlatformDescriptor):
            raise ValidationError("Platform must be a PlatformDescriptor")
        if not platform.platform_id.strip() or not platform.display_name.strip():
            raise ValidationError("Platform fields must be non-empty")


__all__ = ["PlatformRuntime"]
