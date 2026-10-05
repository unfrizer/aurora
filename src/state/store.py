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
        try:
            return deepcopy(value)
        except RecursionError:
            raise StateValidationError("Shared state nesting is too deep") from None

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(cast(object, key), str) or not key.strip():
            raise StateValidationError("Shared state key must be non-empty", key=key)

    @classmethod
    def _validate_json_value(cls, value: object, ancestors: set[int] | None = None) -> None:
        if ancestors is None:
            ancestors = set()
        if value is None or isinstance(value, str | int | bool):
            return
        if isinstance(value, float):
            if value != value or abs(value) == float("inf"):
                raise StateValidationError("Shared state numbers must be finite")
            return
        if isinstance(value, list | dict):
            identity = id(cast(object, value))
            if identity in ancestors:
                raise StateValidationError("Shared state must not contain circular references")
            ancestors.add(identity)
            try:
                if isinstance(value, list):
                    for item in cast(list[object], value):
                        cls._validate_json_value(item, ancestors)
                else:
                    for key, item in cast(dict[object, object], value).items():
                        if not isinstance(key, str):
                            raise StateValidationError("JSON object keys must be strings", key=key)
                        cls._validate_json_value(item, ancestors)
            except RecursionError:
                raise StateValidationError("Shared state nesting is too deep") from None
            finally:
                ancestors.remove(identity)
            return
        raise StateValidationError(
            "Shared state values must be JSON-compatible",
            value_type=type(value).__name__,
        )


__all__ = []
