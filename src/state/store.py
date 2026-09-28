"""Private copy-on-write storage for the Shared State Runtime."""

# pyright: reportUnusedClass=false

from __future__ import annotations

from copy import deepcopy
from typing import cast

from src.core.exceptions import StateValidationError
from src.core.types import JSONValue
from src.state.contracts import StateSnapshot


class _StateStore:
    """Own detached state values and their monotonically increasing revision."""

    def __init__(self) -> None:
        self._state: dict[str, JSONValue] = {}
        self._revision = 0

    def get(self, key: str) -> JSONValue | None:
        self._validate_key(key)
        value = self._state.get(key)
        return self._detach(value) if value is not None else None

    def contains(self, key: str) -> bool:
        self._validate_key(key)
        return key in self._state

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(revision=self._revision, values=deepcopy(self._state))

    def set(self, key: str, value: JSONValue) -> StateSnapshot:
        self._validate_key(key)
        self._validate_json_value(value)

        next_state = deepcopy(self._state)
        next_state[key] = self._detach(value)
        self._state = next_state
        self._revision += 1
        return self.snapshot()

    def remove(self, key: str) -> StateSnapshot:
        self._validate_key(key)
        if key in self._state:
            next_state = deepcopy(self._state)
            del next_state[key]
            self._state = next_state
            self._revision += 1
        return self.snapshot()

    def clear(self) -> StateSnapshot:
        if self._state:
            self._state = {}
            self._revision += 1
        return self.snapshot()

    @staticmethod
    def _detach(value: JSONValue) -> JSONValue:
        return deepcopy(value)

    @staticmethod
    def _validate_key(key: str) -> None:
        if not key.strip():
            raise StateValidationError("Shared state key must be non-empty", key=key)

    @classmethod
    def _validate_json_value(cls, value: object) -> None:
        if value is None or isinstance(value, str | int | float | bool):
            return
        if isinstance(value, list):
            for item in cast(list[object], value):
                cls._validate_json_value(item)
            return
        if isinstance(value, dict):
            for key, item in cast(dict[object, object], value).items():
                if not isinstance(key, str):
                    raise StateValidationError("JSON object keys must be strings", key=key)
                cls._validate_json_value(item)
            return
        raise StateValidationError(
            "Shared state values must be JSON-compatible",
            value_type=type(value).__name__,
        )


__all__ = []
