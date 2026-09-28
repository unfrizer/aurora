"""KR-008 immutable metadata transformations."""

from __future__ import annotations

from src.core.types import JSONValue, Metadata


class MetadataRuntime:
    """Create JSON-compatible metadata snapshots without mutating inputs."""

    def merge(self, base: Metadata, update: Metadata) -> Metadata:
        return {**base, **update}

    def put(self, metadata: Metadata, *, key: str, value: JSONValue) -> Metadata:
        return {**metadata, key: value}

    def remove(self, metadata: Metadata, *, key: str) -> Metadata:
        return {item_key: value for item_key, value in metadata.items() if item_key != key}

    def contains(self, metadata: Metadata, *, key: str) -> bool:
        return key in metadata

    def get(
        self, metadata: Metadata, *, key: str, default: JSONValue | None = None
    ) -> JSONValue | None:
        return metadata.get(key, default)


__all__ = ["MetadataRuntime"]
