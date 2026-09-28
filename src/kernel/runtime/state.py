"""KR-006 authoritative lifecycle state machine."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import ClassVar

from src.core.exceptions import RuntimeStateError
from src.core.types import RuntimeStatus
from src.kernel.contracts.lifecycle import LifecycleState


class StateRuntime:
    """Own the single mutable RuntimeStatus source."""

    _TRANSITIONS: ClassVar[dict[RuntimeStatus, frozenset[RuntimeStatus]]] = {
        RuntimeStatus.CREATED: frozenset({RuntimeStatus.INITIALIZING}),
        RuntimeStatus.INITIALIZING: frozenset({RuntimeStatus.READY, RuntimeStatus.FAILED}),
        RuntimeStatus.READY: frozenset({RuntimeStatus.STARTING, RuntimeStatus.FAILED}),
        RuntimeStatus.STARTING: frozenset({RuntimeStatus.RUNNING, RuntimeStatus.FAILED}),
        RuntimeStatus.RUNNING: frozenset({RuntimeStatus.STOPPING, RuntimeStatus.FAILED}),
        RuntimeStatus.STOPPING: frozenset({RuntimeStatus.STOPPED, RuntimeStatus.FAILED}),
        RuntimeStatus.STOPPED: frozenset({RuntimeStatus.SHUTTING_DOWN}),
        RuntimeStatus.SHUTTING_DOWN: frozenset({RuntimeStatus.TERMINATED, RuntimeStatus.FAILED}),
        RuntimeStatus.TERMINATED: frozenset(),
        RuntimeStatus.FAILED: frozenset(),
    }

    def __init__(self) -> None:
        self._current = RuntimeStatus.CREATED
        self._previous: RuntimeStatus | None = None
        self._entered_at = datetime.now(UTC)
        self._transition_count = 0

    def current(self) -> RuntimeStatus:
        return self._current

    def previous(self) -> RuntimeStatus | None:
        return self._previous

    def snapshot(self) -> LifecycleState:
        return LifecycleState(
            current=self._current,
            previous=self._previous,
            entered_at=self._entered_at,
            transition_count=self._transition_count,
        )

    def can_transition(self, target: RuntimeStatus) -> bool:
        return target in self._TRANSITIONS[self._current]

    def transition(self, target: RuntimeStatus) -> LifecycleState:
        if not self.can_transition(target):
            raise RuntimeStateError(
                "Illegal runtime lifecycle transition",
                current=self._current,
                target=target,
            )
        self._previous = self._current
        self._current = target
        self._entered_at = datetime.now(UTC)
        self._transition_count += 1
        return self.snapshot()


__all__ = ["StateRuntime"]
