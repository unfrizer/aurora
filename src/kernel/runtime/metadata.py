"""KR-008 validated, detached JSON metadata transformations."""

from __future__ import annotations

from math import isfinite
from typing import cast

from src.core.exceptions import ContractValidationError
from src.core.types import JSONValue, Metadata


class MetadataRuntime:
    """Validate and detach JSON values without owning mutable runtime state."""

    def merge(self, base: Metadata, update: Metadata) -> Metadata:
        copied_base = self._copy_metadata(base)
        copied_update = self._copy_metadata(update)
        return {**copied_base, **copied_update}

    def put(self, metadata: Metadata, *, key: str, value: JSONValue) -> Metadata:
        self._validate_string(key)
        result = self._copy_metadata(metadata)
        result[key] = self._copy_json(value, ancestors=set(), depth=1)
        return result

    def remove(self, metadata: Metadata, *, key: str) -> Metadata:
        self._validate_string(key)
        result = self._copy_metadata(metadata)
        result.pop(key, None)
        return result

    def contains(self, metadata: Metadata, *, key: str) -> bool:
        self._validate_string(key)
        return key in self._copy_metadata(metadata)

    def get(
        self, metadata: Metadata, *, key: str, default: JSONValue | None = None
    ) -> JSONValue | None:
        self._validate_string(key)
        copied = self._copy_metadata(metadata)
        if key in copied:
            return copied[key]
        return self._copy_json(default, ancestors=set(), depth=0)

    def _copy_metadata(self, metadata: object) -> Metadata:
        if not isinstance(metadata, dict):
            raise ContractValidationError("Metadata must be a JSON object")
        return cast(Metadata, self._copy_json(cast(object, metadata), ancestors=set(), depth=0))

    @staticmethod
    def _validate_string(value: object) -> None:
        if not isinstance(value, str):
            raise ContractValidationError("Metadata strings must contain valid Unicode")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ContractValidationError("Metadata strings must contain valid Unicode") from None

    def _copy_json(self, value: object, *, ancestors: set[int], depth: int) -> JSONValue:
        """Copy each occurrence; only current-path references are cycles."""
        if value is None or isinstance(value, bool | int):
            return value
        if isinstance(value, str):
            self._validate_string(value)
            return value
        if isinstance(value, float):
            if not isfinite(value):
                raise ContractValidationError("Metadata JSON numbers must be finite")
            return value
        if not isinstance(value, dict | list):
            raise ContractValidationError("Metadata contains a non-JSON value")
        if depth >= 256:
            raise ContractValidationError("Metadata JSON exceeds 256 container levels")
        identity = id(cast(object, value))
        if identity in ancestors:
            raise ContractValidationError("Metadata JSON must not contain cycles")
        ancestors.add(identity)
        try:
            if isinstance(value, list):
                return [
                    self._copy_json(item, ancestors=ancestors, depth=depth + 1)
                    for item in cast(list[object], value)
                ]
            result: Metadata = {}
            for key, item in cast(dict[object, object], value).items():
                self._validate_string(key)
                result[cast(str, key)] = self._copy_json(item, ancestors=ancestors, depth=depth + 1)
            return result
        finally:
            ancestors.remove(identity)


__all__ = ["MetadataRuntime"]
