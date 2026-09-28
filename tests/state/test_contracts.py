from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError

import pytest

from src.kernel.contracts.runtime import RuntimeContract
from src.state import SharedStateContract, SharedStateRuntime, StateSnapshot


def test_state_snapshot_is_a_frozen_dataclass_with_runtime_revision() -> None:
    runtime = SharedStateRuntime()
    snapshot = runtime.set("theme", {"palette": ["aurora"]})

    assert isinstance(snapshot, StateSnapshot)
    assert snapshot.revision == 1
    with pytest.raises(FrozenInstanceError):
        snapshot.revision = 2  # type: ignore[misc]


def test_snapshot_values_are_detached_from_runtime_truth() -> None:
    runtime = SharedStateRuntime()
    snapshot = runtime.set("preferences", {"panels": ["left"]})
    snapshot.values["preferences"] = {"panels": ["right"]}

    assert runtime.get("preferences") == {"panels": ["left"]}


def test_nested_snapshot_values_are_detached_from_runtime_truth() -> None:
    runtime = SharedStateRuntime()
    snapshot = runtime.set("preferences", {"panels": ["left"]})
    value = snapshot.values["preferences"]
    assert isinstance(value, dict)
    panels = value["panels"]
    assert isinstance(panels, list)
    panels.append("right")

    assert runtime.get("preferences") == {"panels": ["left"]}


def test_shared_state_contract_is_abstract_and_extends_runtime_contract() -> None:
    assert inspect.isabstract(SharedStateContract)
    assert issubclass(SharedStateContract, RuntimeContract)


def test_shared_state_contract_has_exact_domain_method_set() -> None:
    domain_methods = {
        name
        for name, member in SharedStateContract.__dict__.items()
        if inspect.isfunction(member) and not name.startswith("_")
    }

    assert domain_methods == {"clear", "contains", "get", "remove", "set", "snapshot"}
    assert not {"publish", "register_handler", "subscribe"} & set(SharedStateContract.__dict__)
