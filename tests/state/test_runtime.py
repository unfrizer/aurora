from __future__ import annotations

import asyncio

import pytest

from src.core.exceptions import StateValidationError
from src.core.types import HealthStatus, JSONValue, RuntimeLayer
from src.state import SharedStateRuntime


async def test_runtime_identity_and_lifecycle_do_not_create_background_tasks() -> None:
    runtime = SharedStateRuntime()
    tasks_before = asyncio.all_tasks()

    await runtime.initialize()
    await runtime.start()
    await runtime.stop()

    assert runtime.runtime_name == "shared_state"
    assert runtime.runtime_layer is RuntimeLayer.L1_STATE
    assert asyncio.all_tasks() == tasks_before


async def test_stop_preserves_state_and_shutdown_releases_the_store() -> None:
    runtime = SharedStateRuntime()
    await runtime.initialize()
    runtime.set("mode", "active")

    await runtime.stop()
    assert runtime.get("mode") == "active"

    await runtime.shutdown()
    assert runtime._store is None  # pyright: ignore[reportPrivateUsage]


def test_new_runtime_has_an_empty_zero_revision_snapshot() -> None:
    snapshot = SharedStateRuntime().snapshot()

    assert snapshot.revision == 0
    assert snapshot.values == {}


def test_missing_get_and_contains_distinguish_an_absent_key() -> None:
    runtime = SharedStateRuntime()

    assert runtime.get("missing") is None
    assert not runtime.contains("missing")
    runtime.set("present_none", None)
    assert runtime.get("present_none") is None
    assert runtime.contains("present_none")


def test_set_stores_scalars_and_nested_json_values() -> None:
    runtime = SharedStateRuntime()

    scalar_snapshot = runtime.set("count", 1)
    nested_snapshot = runtime.set("view", {"panels": ["left", "right"]})

    assert scalar_snapshot.revision == 1
    assert nested_snapshot.revision == 2
    assert runtime.get("count") == 1
    assert runtime.get("view") == {"panels": ["left", "right"]}


def test_successful_set_always_increments_revision() -> None:
    runtime = SharedStateRuntime()
    first = runtime.set("mode", "active")
    second = runtime.set("mode", "active")

    assert first.revision == 1
    assert second.revision == 2


def test_remove_and_clear_only_increment_revision_when_state_changes() -> None:
    runtime = SharedStateRuntime()
    runtime.set("one", 1)
    removed = runtime.remove("one")
    missing = runtime.remove("one")
    runtime.set("two", 2)
    cleared = runtime.clear()
    empty = runtime.clear()

    assert removed.revision == 2
    assert missing.revision == 2
    assert cleared.revision == 4
    assert empty.revision == 4


def test_input_result_and_snapshot_mutation_do_not_alias_runtime_truth() -> None:
    runtime = SharedStateRuntime()
    source: dict[str, JSONValue] = {"items": ["initial"]}
    runtime.set("data", source)
    source_items = source["items"]
    assert isinstance(source_items, list)
    source_items.append("source-change")

    returned = runtime.get("data")
    assert isinstance(returned, dict)
    items = returned["items"]
    assert isinstance(items, list)
    items.append("returned-change")

    snapshot = runtime.snapshot()
    snapshot_value = snapshot.values["data"]
    assert isinstance(snapshot_value, dict)
    snapshot_items = snapshot_value["items"]
    assert isinstance(snapshot_items, list)
    snapshot_items.append("snapshot-change")

    assert runtime.get("data") == {"items": ["initial"]}


@pytest.mark.parametrize("key", ["", "   "])
def test_empty_or_whitespace_keys_are_rejected(key: str) -> None:
    with pytest.raises(StateValidationError):
        SharedStateRuntime().set(key, "value")


def test_non_json_compatible_values_are_rejected() -> None:
    with pytest.raises(StateValidationError):
        SharedStateRuntime().set("invalid", {"values": {1, 2}})  # type: ignore[arg-type]


def test_health_is_read_only_and_uses_canonical_vocabulary() -> None:
    runtime = SharedStateRuntime()
    runtime.set("mode", "active")
    before = runtime.snapshot()

    assert runtime.health() is HealthStatus.OK
    assert runtime.snapshot() == before
