"""Deterministic in-memory implementation of the Wave 6 Interaction Runtime."""

# pyright: reportUnnecessaryIsInstance=false

from __future__ import annotations

from src.core.exceptions import ValidationError
from src.core.types import HealthStatus, RuntimeLayer
from src.interaction.contracts import (
    InteractionContract,
    InteractionRequest,
    InteractionSnapshot,
)


class InteractionRuntime(InteractionContract):
    """Own the latest validated interaction request during a runtime lifetime."""

    def __init__(self) -> None:
        self._latest: InteractionRequest | None = None
        self._revision = 0
        self._is_shutdown = False

    @property
    def runtime_name(self) -> str:
        return "interaction"

    @property
    def runtime_layer(self) -> RuntimeLayer:
        return RuntimeLayer.L5_INTERACTION

    async def initialize(self) -> None:
        if self._is_shutdown:
            self._latest = None
            self._revision = 0
            self._is_shutdown = False

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def shutdown(self) -> None:
        self._latest = None
        self._is_shutdown = True

    def health(self) -> HealthStatus:
        return HealthStatus.OK

    def current(self) -> InteractionRequest | None:
        self._require_active()
        return self._latest

    def snapshot(self) -> InteractionSnapshot:
        self._require_active()
        return InteractionSnapshot(revision=self._revision, latest=self._latest)

    def submit(self, request: InteractionRequest) -> InteractionSnapshot:
        self._require_active()
        self._validate_request(request)
        self._latest = request
        self._revision += 1
        return self.snapshot()

    def clear(self) -> InteractionSnapshot:
        self._require_active()
        if self._latest is not None:
            self._latest = None
            self._revision += 1
        return self.snapshot()

    def _require_active(self) -> None:
        if self._is_shutdown:
            raise RuntimeError("Interaction Runtime is shut down")

    @staticmethod
    def _validate_request(request: InteractionRequest) -> None:
        if not isinstance(request, InteractionRequest):
            raise ValidationError("Interaction request must be an InteractionRequest")
        for field, value in (
            ("interaction_id", request.interaction_id),
            ("action", request.action),
            ("target_id", request.target_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValidationError("Interaction field must be non-empty", field=field)


__all__ = ["InteractionRuntime"]
