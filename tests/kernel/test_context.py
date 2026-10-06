"""KR-008 canonical acceptance for ADR-004 P-04 and ADR-006 C-01-C-04."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

import pytest

from src.core.exceptions import ContractValidationError, RuntimeStateError
from src.core.types import (
    HealthStatus,
    JSONValue,
    Metadata,
    PipelineId,
    RuntimeLayer,
    SessionId,
    TraceId,
)
from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.runtime import context as context_module
from src.kernel.runtime import metadata as metadata_module
from src.kernel.runtime import session as session_module
from src.kernel.runtime.context import ContextRuntime
from src.kernel.runtime.metadata import MetadataRuntime
from src.kernel.runtime.session import SessionRuntime


class InvalidOffset(tzinfo):
    def utcoffset(self, dt: datetime | None) -> timedelta:
        return timedelta(hours=25)


class RaisingOffset(tzinfo):
    def __init__(self, error: Exception) -> None:
        self.error = error

    def utcoffset(self, dt: datetime | None) -> timedelta:
        raise self.error


def _context(metadata: Metadata | None = None) -> RuntimeContext:
    return RuntimeContext(
        session_id=SessionId(uuid4()),
        pipeline_id=PipelineId(uuid4()),
        runtime_layer=RuntimeLayer.L0_KERNEL,
        trace=TraceContext(
            trace_id=TraceId(uuid4()),
            parent_trace_id=TraceId(uuid4()),
            correlation_id=uuid4(),
        ),
        metadata={} if metadata is None else metadata,
    )


def _create(runtime: ContextRuntime, context: RuntimeContext) -> RuntimeContext:
    return runtime.create(
        session_id=context.session_id,
        pipeline_id=context.pipeline_id,
        runtime_layer=context.runtime_layer,
        metadata=context.metadata,
        trace=context.trace,
    )


def _items(metadata: Metadata, key: str = "nested") -> list[JSONValue]:
    nested = metadata[key]
    assert isinstance(nested, dict)
    result = nested["items"]
    assert isinstance(result, list)
    return result


def _nested(levels: int, kind: str = "dict") -> Metadata:
    value: JSONValue = "leaf"
    for index in range(levels - 1):
        value = {"child": value} if kind == "dict" or (kind == "mixed" and index % 2) else [value]
    return {"root": value}


def _leaf(metadata: Metadata) -> JSONValue:
    value = metadata["root"]
    while isinstance(value, dict | list):
        value = value["child"] if isinstance(value, dict) else value[0]
    return value


def test_public_exports_and_frozen_contract_schema_are_unchanged() -> None:
    assert context_module.__all__ == ["ContextRuntime"]
    assert metadata_module.__all__ == ["MetadataRuntime"]
    assert session_module.__all__ == ["SessionRuntime"]
    assert [field.name for field in fields(RuntimeContext)] == [
        "session_id",
        "pipeline_id",
        "runtime_layer",
        "trace",
        "metadata",
        "created_at",
        "expires_at",
    ]
    assert [field.name for field in fields(TraceContext)] == [
        "trace_id",
        "parent_trace_id",
        "correlation_id",
    ]
    assert not hasattr(ContextRuntime, "set")
    assert not hasattr(ContextRuntime, "get")
    assert not hasattr(ContextRuntime, "clear_session")
    assert not hasattr(SessionRuntime, "clear")
    snapshot = _context()
    writes: tuple[tuple[object, str, object], ...] = (
        (snapshot, "metadata", {}),
        (snapshot.trace, "trace_id", TraceId(uuid4())),
    )
    for target, attribute, value in writes:
        with pytest.raises(FrozenInstanceError):
            setattr(target, attribute, value)


def test_context_create_and_current_detach_both_directions() -> None:
    runtime = ContextRuntime()
    source = _context({"nested": {"items": [1, {"label": "first"}]}})
    result = _create(runtime, source)
    before = runtime.current()
    assert result == before and result is not before
    assert result.session_id == source.session_id
    assert result.pipeline_id == source.pipeline_id
    assert result.runtime_layer == source.runtime_layer
    assert result.trace == source.trace
    assert result.created_at.utcoffset() == timedelta(0)
    assert result.expires_at is None
    _items(source.metadata).append("caller")
    _items(result.metadata).append("result")
    _items(before.metadata).append("read")
    assert _items(runtime.current().metadata) == [1, {"label": "first"}]
    assert _items(runtime.current().metadata) is not _items(runtime.current().metadata)


def test_replace_preserves_values_trace_time_and_detaches_every_snapshot() -> None:
    runtime = ContextRuntime()
    timestamp = datetime(2020, 1, 1, tzinfo=UTC)
    source = replace(
        _context({"nested": {"items": ["original"]}}),
        created_at=timestamp,
        expires_at=timestamp - timedelta(days=1),
    )
    result = runtime.replace(source)
    first = runtime.current()
    second = runtime.current()
    assert source == result == first == second
    assert source is not result and first is not second and first is not result
    assert first.is_expired
    assert first.created_at == timestamp
    assert first.trace_id == source.trace.trace_id
    assert first.root_trace_id == source.trace.parent_trace_id
    assert first.depth == 1
    _items(source.metadata).append("caller")
    _items(result.metadata).append("returned")
    _items(first.metadata).append("read")
    assert _items(runtime.current().metadata) == ["original"]


@pytest.mark.parametrize("layer", tuple(RuntimeLayer))
def test_context_accepts_each_existing_runtime_layer(layer: RuntimeLayer) -> None:
    runtime = ContextRuntime()
    result = _create(runtime, replace(_context(), runtime_layer=layer))
    assert result.runtime_layer is layer
    assert runtime.runtime_layer is RuntimeLayer.L0_KERNEL


def test_optional_trace_ids_and_zero_offset_timezone_are_valid() -> None:
    context = replace(
        _context(),
        trace=TraceContext(trace_id=TraceId(uuid4())),
        created_at=datetime(2020, 1, 1, tzinfo=timezone(timedelta(0), "zero")),
    )
    runtime = ContextRuntime()
    result = runtime.replace(context)
    assert result == context
    assert result.root_trace_id == result.trace.trace_id and result.depth == 0
    assert result.trace.parent_trace_id is None and result.trace.correlation_id is None


@pytest.mark.parametrize("method", ("create", "replace"))
@pytest.mark.parametrize(
    ("field_name", "invalid"),
    [
        ("session_id", "secret-session"),
        ("session_id", None),
        ("pipeline_id", "secret-pipeline"),
        ("pipeline_id", 5),
        ("runtime_layer", "L0_KERNEL"),
        ("runtime_layer", 0),
        ("trace", None),
        ("trace", {"trace_id": "secret"}),
    ],
)
def test_invalid_creation_fields_are_safe_and_atomic(
    method: str, field_name: str, invalid: object
) -> None:
    runtime = ContextRuntime()
    original = runtime.replace(_context({"ok": [1]}))
    invalid_context = replace(_context(), **{field_name: invalid})
    with pytest.raises(ContractValidationError) as error:
        if method == "create":
            _create(runtime, invalid_context)
        else:
            runtime.replace(invalid_context)
    assert "secret" not in str(error.value)
    assert runtime.current() == original


@pytest.mark.parametrize("field_name", ("trace_id", "parent_trace_id", "correlation_id"))
@pytest.mark.parametrize("method", ("create", "replace", "session"))
def test_invalid_trace_ids_fail_before_either_owner_changes(field_name: str, method: str) -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    session_id = SessionId(uuid4())
    original = sessions.create(session_id=session_id, trace=_context().trace, metadata={"ok": [1]})
    bad_trace = replace(original.trace, **{field_name: "private-secret"})
    with pytest.raises(ContractValidationError) as error:
        if method == "create":
            _create(runtime, replace(original, trace=bad_trace))
        elif method == "replace":
            runtime.replace(replace(original, trace=bad_trace))
        else:
            sessions.create(session_id=session_id, trace=bad_trace)
    assert "private-secret" not in str(error.value)
    assert sessions.get(session_id) == original == runtime.current()


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        "private-secret",
        datetime(2020, 1, 1),
        datetime(2020, 1, 1, tzinfo=timezone(timedelta(hours=1))),
        datetime(2020, 1, 1, tzinfo=InvalidOffset()),
        datetime(2020, 1, 1, tzinfo=RaisingOffset(OverflowError("private-secret"))),
        datetime(2020, 1, 1, tzinfo=RaisingOffset(TypeError("private-secret"))),
        datetime(2020, 1, 1, tzinfo=RaisingOffset(ValueError("private-secret"))),
    ],
)
@pytest.mark.parametrize("field_name", ("created_at", "expires_at"))
def test_invalid_timestamps_reject_safely_without_mutating_active_context(
    field_name: str, invalid: object
) -> None:
    if field_name == "expires_at" and invalid is None:
        assert ContextRuntime().replace(replace(_context(), expires_at=None)).expires_at is None
        return
    runtime = ContextRuntime()
    original = runtime.replace(_context())
    with pytest.raises(ContractValidationError) as error:
        runtime.replace(replace(original, **{field_name: invalid}))
    assert "private-secret" not in str(error.value)
    assert runtime.current() == original


@pytest.mark.parametrize("value", (None, {}, "secret", 123))
def test_non_context_replace_rejects_without_attribute_error(value: object) -> None:
    runtime = ContextRuntime()
    with pytest.raises(ContractValidationError):
        runtime.replace(cast(RuntimeContext, value))
    assert not runtime.has_context()


@pytest.mark.parametrize("value", (None, [], 42, "secret", ()))
@pytest.mark.parametrize(
    "operation", ("merge_base", "merge_update", "put", "remove", "contains", "get")
)
def test_metadata_roots_are_objects(value: object, operation: str) -> None:
    _reject_metadata(operation, value)


def _reject_metadata(operation: str, invalid: object) -> None:
    runtime = MetadataRuntime()
    metadata = cast(Metadata, invalid)
    with pytest.raises(ContractValidationError) as error:
        if operation == "merge_base":
            runtime.merge(metadata, {"key": "replacement"})
        elif operation == "merge_update":
            runtime.merge({"key": "base"}, metadata)
        elif operation == "put":
            runtime.put(metadata, key="key", value="replacement")
        elif operation == "remove":
            runtime.remove(metadata, key="key")
        elif operation == "contains":
            runtime.contains(metadata, key="key")
        else:
            runtime.get(metadata, key="key")
    assert "private-secret" not in str(error.value)


@pytest.mark.parametrize(
    "invalid",
    [
        {1: "private-secret"},
        {None: 1},
        {("key",): 1},
        {"key": float("nan")},
        {"key": float("inf")},
        {"key": -float("inf")},
        {"key": object()},
        {"key": uuid4()},
        {"key": datetime.now(UTC)},
        {"key": Path("private-secret")},
        {"key": (1, 2)},
        {"key": {1}},
        {"key": b"private-secret"},
        {"key": bytearray(b"private-secret")},
        {"key": "\ud800"},
        {"\udfff": "private-secret"},
        {"key": [{"nested": float("nan")}]},
        {"key": {1: "private-secret"}},
    ],
)
@pytest.mark.parametrize(
    "operation", ("merge_base", "merge_update", "put", "remove", "contains", "get")
)
def test_every_metadata_boundary_rejects_invalid_json(invalid: object, operation: str) -> None:
    _reject_metadata(operation, invalid)


@pytest.mark.parametrize(
    "operation", ("merge_base", "merge_update", "put", "remove", "contains", "get")
)
@pytest.mark.parametrize("kind", ("dict", "list", "indirect"))
def test_metadata_cycles_are_rejected_without_recursion_or_mutation(
    operation: str, kind: str
) -> None:
    root: Metadata = {"private-secret": []}
    if kind == "dict":
        root["key"] = root
    elif kind == "list":
        items: list[JSONValue] = []
        items.append(items)
        root["key"] = items
    else:
        items = [root]
        root["key"] = items
    _reject_metadata(operation, root)
    assert "private-secret" in root


@pytest.mark.parametrize("key", (None, 4, "\ud800"))
@pytest.mark.parametrize("operation", ("put", "remove", "contains", "get"))
def test_invalid_operation_keys_reject_even_when_missing(key: object, operation: str) -> None:
    runtime = MetadataRuntime()
    invalid_key = cast(str, key)
    original: Metadata = {"ok": [1]}
    with pytest.raises(ContractValidationError):
        if operation == "put":
            runtime.put(original, key=invalid_key, value=None)
        elif operation == "remove":
            runtime.remove(original, key=invalid_key)
        elif operation == "contains":
            runtime.contains(original, key=invalid_key)
        else:
            runtime.get(original, key=invalid_key)
    assert original == {"ok": [1]}


def test_metadata_shallow_order_and_outputs_are_independent() -> None:
    runtime = MetadataRuntime()
    base: Metadata = {"first": 1, "nested": {"items": ["old"]}, "last": 3}
    update: Metadata = {"nested": {"items": ["new"]}, "extra": [4]}
    merged = runtime.merge(base, update)
    assert tuple(merged) == ("first", "nested", "last", "extra")
    assert merged == {"first": 1, "nested": {"items": ["new"]}, "last": 3, "extra": [4]}
    _items(merged).append("output")
    _items(update).append("input")
    assert _items(base) == ["old"]
    assert _items(runtime.merge(base, {"nested": {"items": ["separate"]}})) == ["separate"]
    inserted = runtime.put(base, key="added", value={"items": [5]})
    assert tuple(inserted) == ("first", "nested", "last", "added")
    _items(inserted).append("local")
    assert _items(base) == ["old"]
    replaced = runtime.put(base, key="nested", value={"items": ["replacement"]})
    assert tuple(replaced) == tuple(base)
    removed = runtime.remove(base, key="first")
    assert tuple(removed) == ("nested", "last")
    _items(removed).append("local")
    missing = runtime.remove(base, key="absent")
    assert missing == base and missing is not base
    _items(missing).append("local")
    assert _items(base) == ["old"]
    assert runtime.contains(base, key="nested")
    assert not runtime.contains(base, key="absent")


def test_put_detaches_the_new_value_and_validates_overwritten_source() -> None:
    runtime = MetadataRuntime()
    value: JSONValue = {"items": [1]}
    result = runtime.put({}, key="new", value=value)
    assert isinstance(value, dict)
    items = value["items"]
    assert isinstance(items, list)
    items.append("caller")
    assert result == {"new": {"items": [1]}}
    with pytest.raises(ContractValidationError):
        runtime.put({"key": float("nan")}, key="key", value="valid")
    with pytest.raises(ContractValidationError):
        runtime.merge({"key": float("nan")}, {"key": "valid"})
    with pytest.raises(ContractValidationError):
        runtime.put({}, key="key", value=cast(JSONValue, object()))


def test_get_detaches_value_or_default_and_ignores_unused_default() -> None:
    runtime = MetadataRuntime()
    source: Metadata = {"key": {"items": [1]}, "null": None}
    result = runtime.get(source, key="key")
    assert isinstance(result, dict)
    items = result["items"]
    assert isinstance(items, list)
    items.append("local")
    assert source == {"key": {"items": [1]}, "null": None}
    default: JSONValue = {"items": [2]}
    fallback = runtime.get(source, key="missing", default=default)
    assert isinstance(fallback, dict)
    fallback_items = fallback["items"]
    assert isinstance(fallback_items, list)
    fallback_items.append("local")
    assert default == {"items": [2]}
    assert runtime.get(source, key="missing") is None
    assert runtime.get(source, key="null", default="unused") is None
    assert runtime.get(source, key="key", default=cast(JSONValue, object())) == {"items": [1]}
    with pytest.raises(ContractValidationError):
        runtime.get(source, key="missing", default=cast(JSONValue, object()))


def test_repeated_acyclic_references_are_detached_per_occurrence() -> None:
    shared: JSONValue = {"items": [1]}
    source: Metadata = {"a": shared, "b": shared}
    runtime = MetadataRuntime()
    result = runtime.merge(source, {})
    a, b = result["a"], result["b"]
    assert isinstance(a, dict) and isinstance(b, dict)
    assert a is not b and a is not shared
    a_items, b_items = a["items"], b["items"]
    assert isinstance(a_items, list) and isinstance(b_items, list)
    a_items.append("local")
    assert b_items == [1] and source["a"] == {"items": [1]}
    assert runtime.contains(source, key="a")


@pytest.mark.parametrize("levels", (1, 2, 128, 255, 256))
@pytest.mark.parametrize("kind", ("dict", "list", "mixed"))
def test_exact_supported_depth_is_valid_in_all_owners(levels: int, kind: str) -> None:
    data = _nested(levels, kind)
    metadata = MetadataRuntime()
    assert _leaf(metadata.merge(data, {})) == "leaf"
    assert metadata.contains(data, key="root")
    assert _leaf(metadata.remove(data, key="absent")) == "leaf"
    runtime = ContextRuntime()
    assert _leaf(_create(runtime, _context(data)).metadata) == "leaf"
    assert _leaf(runtime.current().metadata) == "leaf"
    sessions = SessionRuntime(runtime)
    result = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace, metadata=data)
    assert _leaf(sessions.get(result.session_id).metadata) == "leaf"
    assert _leaf(sessions.update_metadata(result.session_id, {}).metadata) == "leaf"


@pytest.mark.parametrize("levels", (257, 258, 1100))
@pytest.mark.parametrize("kind", ("dict", "list", "mixed"))
def test_excessive_depth_is_a_validation_error_and_keeps_state(levels: int, kind: str) -> None:
    data = _nested(levels, kind)
    _reject_metadata("merge_base", data)
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    original = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace)
    with pytest.raises(ContractValidationError):
        _create(runtime, _context(data))
    with pytest.raises(ContractValidationError):
        runtime.replace(replace(original, metadata=data))
    with pytest.raises(ContractValidationError):
        sessions.create(session_id=original.session_id, trace=original.trace, metadata=data)
    with pytest.raises(ContractValidationError):
        sessions.update_metadata(original.session_id, data)
    assert runtime.current() == original == sessions.get(original.session_id)


def test_put_counts_the_metadata_root_and_default_counts_its_own_root() -> None:
    runtime = MetadataRuntime()
    accepted = runtime.put({}, key="nested", value=_nested(255))
    assert _leaf(cast(Metadata, accepted["nested"])) == "leaf"
    with pytest.raises(ContractValidationError):
        runtime.put({}, key="nested", value=_nested(256))
    default = runtime.get({}, key="absent", default=_nested(256))
    assert isinstance(default, dict) and _leaf(default) == "leaf"
    with pytest.raises(ContractValidationError):
        runtime.get({}, key="absent", default=_nested(257))


def test_json_primitive_values_are_preserved_without_coercion() -> None:
    data: Metadata = {
        "null": None,
        "bool": True,
        "int": 2**4096,
        "negative": -100,
        "float": 1.25,
        "zero": -0.0,
        "unicode": "Бренд 😀",
        "": [],
    }
    assert MetadataRuntime().merge(data, {}) == data
    context = _create(ContextRuntime(), _context(data))
    assert context.metadata == data
    assert type(context.metadata["bool"]) is bool
    assert type(context.metadata["int"]) is int
    assert repr(context.metadata["zero"]) == "-0.0"


def test_sessions_create_get_active_and_returned_data_are_independent() -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    source: Metadata = {"nested": {"items": [1]}}
    created = sessions.create(
        session_id=SessionId(uuid4()), trace=_context().trace, metadata=source
    )
    session_read, active_read = sessions.get(created.session_id), runtime.current()
    assert created == session_read == active_read
    assert created is not session_read and session_read is not active_read
    assert isinstance(created.pipeline_id, UUID) and created.pipeline_id.version == 4
    assert created.runtime_layer is RuntimeLayer.L0_KERNEL
    _items(source).append("source")
    _items(created.metadata).append("created")
    _items(session_read.metadata).append("session")
    _items(active_read.metadata).append("active")
    assert _items(sessions.get(created.session_id).metadata) == [1]
    assert _items(runtime.current().metadata) == [1]


def test_session_update_is_shallow_and_preserves_identity_fields() -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    source = sessions.create(
        session_id=SessionId(uuid4()),
        trace=_context().trace,
        metadata={"nested": {"items": ["old"]}, "retained": [1]},
    )
    update: Metadata = {"nested": {"items": ["new"]}, "extra": [2]}
    result = sessions.update_metadata(source.session_id, update)
    assert result == runtime.current() == sessions.get(source.session_id)
    assert replace(result, metadata=source.metadata) == source
    assert tuple(result.metadata) == ("nested", "retained", "extra")
    _items(update).append("input")
    _items(result.metadata).append("output")
    assert _items(sessions.get(source.session_id).metadata) == ["new"]
    assert _items(runtime.current().metadata) == ["new"]
    assert _items(source.metadata) == ["old"]


def test_non_active_update_and_remove_do_not_clear_other_session() -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    first = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace)
    second = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace)
    updated = sessions.update_metadata(first.session_id, {"key": [1]})
    assert sessions.get(first.session_id) == updated
    assert runtime.current() == second
    sessions.remove(first.session_id)
    assert sessions.list() == (second.session_id,)
    assert runtime.current() == second
    sessions.remove(second.session_id)
    assert not runtime.has_context() and sessions.list() == ()
    assert not sessions.contains(first.session_id)


def test_same_id_creation_replaces_without_reordering_or_stale_aliases() -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    first = sessions.create(
        session_id=SessionId(uuid4()), trace=_context().trace, metadata={"old": [1]}
    )
    second = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace)
    original_ids = sessions.list()
    replacement = sessions.create(
        session_id=first.session_id, trace=_context().trace, metadata={"new": [2]}
    )
    assert sessions.list() == original_ids == (first.session_id, second.session_id)
    assert first.pipeline_id != replacement.pipeline_id
    assert first.created_at <= replacement.created_at
    assert first.metadata == {"old": [1]} and replacement.metadata == {"new": [2]}
    assert sessions.get(first.session_id) == runtime.current() == replacement
    sessions.remove(first.session_id)
    recreated = sessions.create(session_id=first.session_id, trace=first.trace)
    assert sessions.list() == (second.session_id, first.session_id)
    assert recreated.pipeline_id != replacement.pipeline_id


@pytest.mark.parametrize("operation", ("create", "replace", "session_create", "session_update"))
@pytest.mark.parametrize(
    "invalid",
    [
        {"private-secret": object()},
        {"private-secret": float("inf")},
        {1: "private-secret"},
        {"private-secret": "\ud800"},
    ],
)
def test_all_storage_ingress_failures_are_atomic(operation: str, invalid: object) -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    original = sessions.create(
        session_id=SessionId(uuid4()), trace=_context().trace, metadata={"ok": [1]}
    )
    data = cast(Metadata, invalid)
    with pytest.raises(ContractValidationError) as error:
        if operation == "create":
            _create(runtime, _context(data))
        elif operation == "replace":
            runtime.replace(replace(original, metadata=data))
        elif operation == "session_create":
            sessions.create(session_id=original.session_id, trace=original.trace, metadata=data)
        else:
            sessions.update_metadata(original.session_id, data)
    assert "private-secret" not in str(error.value)
    assert sessions.list() == (original.session_id,)
    assert runtime.current() == original == sessions.get(original.session_id)


def test_failed_new_session_does_not_overwrite_another_active_session() -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    original = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace)
    missing = SessionId(uuid4())
    with pytest.raises(ContractValidationError):
        sessions.create(session_id=missing, trace=original.trace, metadata={"bad": float("nan")})
    with pytest.raises(ContractValidationError):
        sessions.create(session_id=cast(SessionId, "secret"), trace=original.trace)
    assert not sessions.contains(missing)
    assert sessions.list() == (original.session_id,) and runtime.current() == original


def test_missing_states_raise_existing_state_error_without_side_effects() -> None:
    runtime = ContextRuntime()
    sessions = SessionRuntime(runtime)
    missing = SessionId(uuid4())
    with pytest.raises(RuntimeStateError):
        runtime.current()
    with pytest.raises(RuntimeStateError):
        sessions.get(missing)
    with pytest.raises(RuntimeStateError):
        sessions.update_metadata(missing, {})
    with pytest.raises(RuntimeStateError):
        sessions.remove(missing)
    assert sessions.list() == () and not runtime.has_context()


async def test_context_lifecycle_health_and_independent_session_lifetimes() -> None:
    runtime = ContextRuntime()
    assert isinstance(runtime, RuntimeContract)
    assert runtime.runtime_name == "context" and runtime.runtime_layer is RuntimeLayer.L0_KERNEL
    assert runtime.health() is HealthStatus.OK and not runtime.has_context()
    sessions = SessionRuntime(runtime)
    stored = sessions.create(session_id=SessionId(uuid4()), trace=_context().trace)
    await runtime.initialize()
    await runtime.start()
    await runtime.stop()
    assert runtime.current() == stored
    runtime.clear()
    runtime.clear()
    assert not runtime.has_context() and sessions.get(stored.session_id) == stored
    updated = sessions.update_metadata(stored.session_id, {"without_active": [1]})
    assert updated.metadata == {"without_active": [1]} and not runtime.has_context()
    runtime.replace(updated)
    await runtime.shutdown()
    await runtime.shutdown()
    assert runtime.health() is HealthStatus.OK and not runtime.has_context()
    assert sessions.get(stored.session_id) == updated
    sessions.remove(stored.session_id)
    assert sessions.list() == ()
    recreated = sessions.create(session_id=stored.session_id, trace=stored.trace)
    assert runtime.current() == recreated


def test_separate_instances_and_session_owners_share_no_mutable_storage() -> None:
    first, second = ContextRuntime(), ContextRuntime()
    first_sessions, second_sessions = SessionRuntime(first), SessionRuntime(second)
    source = _context({"nested": {"items": [1]}})
    a = first_sessions.create(
        session_id=source.session_id, trace=source.trace, metadata=source.metadata
    )
    b = second_sessions.create(
        session_id=source.session_id, trace=source.trace, metadata=source.metadata
    )
    first_sessions.update_metadata(a.session_id, {"nested": {"items": ["first"]}})
    assert _items(second_sessions.get(b.session_id).metadata) == [1]
    assert _items(second.current().metadata) == [1]
    first_sessions.remove(a.session_id)
    assert not first.has_context() and second.current() == b


def test_trace_is_never_regenerated_by_context_or_session_updates() -> None:
    trace = _context().trace
    runtime = ContextRuntime()
    created = _create(runtime, replace(_context(), trace=trace))
    replaced = runtime.replace(created)
    sessions = SessionRuntime(runtime)
    session = sessions.create(session_id=SessionId(uuid4()), trace=trace)
    updated = sessions.update_metadata(session.session_id, {"changed": True})
    assert created.trace == replaced.trace == session.trace == updated.trace == trace
    assert runtime.current().trace == trace
