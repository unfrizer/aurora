from __future__ import annotations

import ast
import json
from enum import Enum, IntEnum, StrEnum
from pathlib import Path
from typing import NewType, TypeAliasType, assert_type, get_args
from uuid import UUID, uuid4

import pytest

from src import core
from src.core import constants, exceptions, types, version
from src.core.types import DIScope, EventPriority, RuntimeLayer, RuntimeStatus


def test_canonical_runtime_vocabulary() -> None:
    assert tuple(RuntimeLayer) == (
        RuntimeLayer.L0_KERNEL,
        RuntimeLayer.L1_STATE,
        RuntimeLayer.L2_LAYOUT,
        RuntimeLayer.L3_THEME,
        RuntimeLayer.L4_MOTION,
        RuntimeLayer.L5_INTERACTION,
        RuntimeLayer.L6_ACCESSIBILITY,
        RuntimeLayer.L7_PLATFORM,
        RuntimeLayer.L8_RENDER,
    )
    assert len(DIScope) == 4
    assert len(RuntimeStatus) == 10
    assert tuple(status.value for status in RuntimeStatus) == (
        "CREATED",
        "INITIALIZING",
        "READY",
        "STARTING",
        "RUNNING",
        "STOPPING",
        "STOPPED",
        "SHUTTING_DOWN",
        "TERMINATED",
        "FAILED",
    )


def test_event_priority_is_descending_numeric_vocabulary() -> None:
    assert EventPriority.CRITICAL > EventPriority.HIGH > EventPriority.NORMAL
    assert EventPriority.NORMAL > EventPriority.LOW > EventPriority.BACKGROUND


@pytest.mark.parametrize(
    ("enum", "expected"),
    [
        (
            RuntimeLayer,
            tuple(
                (name, name)
                for name in (
                    "L0_KERNEL",
                    "L1_STATE",
                    "L2_LAYOUT",
                    "L3_THEME",
                    "L4_MOTION",
                    "L5_INTERACTION",
                    "L6_ACCESSIBILITY",
                    "L7_PLATFORM",
                    "L8_RENDER",
                )
            ),
        ),
        (
            DIScope,
            (
                ("APPLICATION", "application"),
                ("SESSION", "session"),
                ("PIPELINE", "pipeline"),
                ("TRANSIENT", "transient"),
            ),
        ),
        (
            RuntimeStatus,
            tuple(
                (name, name)
                for name in (
                    "CREATED",
                    "INITIALIZING",
                    "READY",
                    "STARTING",
                    "RUNNING",
                    "STOPPING",
                    "STOPPED",
                    "SHUTTING_DOWN",
                    "TERMINATED",
                    "FAILED",
                )
            ),
        ),
        (types.HealthStatus, (("OK", "ok"), ("WARNING", "warning"), ("ERROR", "error"))),
        (
            types.EventPhase,
            (
                ("CREATED", "created"),
                ("PUBLISHED", "published"),
                ("HANDLED", "handled"),
                ("FAILED", "failed"),
            ),
        ),
        (
            EventPriority,
            (("BACKGROUND", 0), ("LOW", 25), ("NORMAL", 50), ("HIGH", 75), ("CRITICAL", 100)),
        ),
    ],
)
def test_exact_enum_members_without_aliases(
    enum: type[Enum], expected: tuple[tuple[str, str | int], ...]
) -> None:
    assert tuple((name, item.value) for name, item in enum.__members__.items()) == expected
    assert issubclass(enum, IntEnum if enum is EventPriority else StrEnum)
    for name, value in expected:
        assert enum(value) is enum[name]
    with pytest.raises(ValueError):
        enum("not-an-approved-value")
    with pytest.raises(KeyError):
        enum["NOT_AN_APPROVED_MEMBER"]


def test_derived_enum_value_constants() -> None:
    assert types.RUNTIME_LAYER_VALUES == constants.RUNTIME_LAYERS
    assert types.DI_SCOPE_VALUES == ("application", "session", "pipeline", "transient")
    assert tuple(item.value for item in RuntimeStatus) == types.RUNTIME_STATUS_VALUES
    assert types.HEALTH_STATUS_VALUES == ("ok", "warning", "error")
    assert types.EVENT_PRIORITY_VALUES == (0, 25, 50, 75, 100)
    assert types.EVENT_PHASE_VALUES == ("created", "published", "handled", "failed")


@pytest.mark.parametrize("alias", [types.SessionId, types.PipelineId, types.EventId, types.TraceId])
def test_uuid_identifiers_preserve_underlying_identity(alias: NewType) -> None:
    identity = uuid4()
    assert alias.__supertype__ is UUID
    assert alias(identity) is identity


@pytest.mark.parametrize("alias", [types.ModuleId, types.ServiceId])
def test_string_identifiers_preserve_underlying_identity(alias: NewType) -> None:
    assert alias.__supertype__ is str
    assert alias("synthetic") == "synthetic"
    assert not hasattr(types, "RuntimeId")


def test_recursive_json_alias_contracts() -> None:
    assert isinstance(types.JSONValue, TypeAliasType)
    assert get_args(types.JSONPrimitive.__value__) == (str, int, float, bool, type(None))
    assert get_args(types.JSONValue.__value__) == (
        types.JSONPrimitive,
        list[types.JSONValue],
        dict[str, types.JSONValue],
    )
    assert types.JSONDict.__value__ == dict[str, types.JSONValue]
    assert types.Metadata.__value__ is types.JSONDict
    assert types.Payload.__value__ is types.JSONDict
    assert types.Headers.__value__ == dict[str, str]
    metadata: types.Metadata = {"nested": ["Русский", 3, 1.5, True, None, {"child": []}]}
    payload: types.Payload = metadata
    headers: types.Headers = {"Content-Type": "application/json"}
    assert_type(metadata, types.Metadata)
    assert_type(payload, types.Payload)
    assert_type(headers, types.Headers)
    assert json.loads(json.dumps(payload, ensure_ascii=False)) == metadata
    assert headers == {"Content-Type": "application/json"}


def test_every_runtime_constant_has_its_confirmed_value() -> None:
    expected: dict[str, object] = {
        "RUNTIME_KERNEL_ID": "KR-001",
        "LAYER_KERNEL": "L0_KERNEL",
        "LAYER_STATE": "L1_STATE",
        "LAYER_LAYOUT": "L2_LAYOUT",
        "LAYER_THEME": "L3_THEME",
        "LAYER_MOTION": "L4_MOTION",
        "LAYER_INTERACTION": "L5_INTERACTION",
        "LAYER_ACCESSIBILITY": "L6_ACCESSIBILITY",
        "LAYER_PLATFORM_BRIDGE": "L7_PLATFORM",
        "LAYER_RENDER": "L8_RENDER",
        "RUNTIME_LAYERS": (
            "L0_KERNEL",
            "L1_STATE",
            "L2_LAYOUT",
            "L3_THEME",
            "L4_MOTION",
            "L5_INTERACTION",
            "L6_ACCESSIBILITY",
            "L7_PLATFORM",
            "L8_RENDER",
        ),
        "SCOPE_APPLICATION": "application",
        "SCOPE_SESSION": "session",
        "SCOPE_PIPELINE": "pipeline",
        "SCOPE_TRANSIENT": "transient",
        "DI_SCOPES": ("application", "session", "pipeline", "transient"),
        "EVENT_VERSION": "1.0",
        "EVENT_FIELD_EVENT_ID": "event_id",
        "EVENT_FIELD_EVENT_TYPE": "event_type",
        "EVENT_FIELD_SESSION_ID": "session_id",
        "EVENT_FIELD_TIMESTAMP": "timestamp",
        "EVENT_FIELD_PAYLOAD": "payload",
        "EVENT_FIELD_TRACE": "trace",
        "EVENT_REQUIRED_FIELDS": (
            "event_id",
            "event_type",
            "session_id",
            "timestamp",
            "payload",
            "trace",
        ),
        "MANIFEST_FIELD_MODULE_ID": "module_id",
        "MANIFEST_FIELD_RUNTIME_LAYER": "runtime_layer",
        "MANIFEST_FIELD_DEPENDS_ON": "depends_on",
        "MANIFEST_FIELD_PROVIDES": "provides",
        "MANIFEST_FIELD_VERSION": "version",
        "MANIFEST_REQUIRED_FIELDS": (
            "module_id",
            "runtime_layer",
            "depends_on",
            "provides",
            "version",
        ),
        "RUNTIME_CONTAINER": "container_runtime",
        "RUNTIME_EVENT_BUS": "event_bus_runtime",
        "RUNTIME_CONFIG": "config_runtime",
        "RUNTIME_LOGGER": "logger_runtime",
        "RUNTIME_DIAGNOSTICS": "diagnostics_runtime",
        "LOGGER_NAME": "aurora",
        "LOG_FORMAT": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        "LOG_DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
        "DEFAULT_LOG_LEVEL": "INFO",
        "DEFAULT_ENCODING": "utf-8",
        "DEFAULT_TIMEZONE": "UTC",
        "UUID_VERSION": 4,
        "TRACE_ROOT_ID": "root",
        "STATUS_OK": "ok",
        "STATUS_WARNING": "warning",
        "STATUS_ERROR": "error",
        "HEALTH_STATUSES": ("ok", "warning", "error"),
        "EXIT_SUCCESS": 0,
        "EXIT_FAILURE": 1,
        "EXIT_CONFIGURATION_ERROR": 10,
        "EXIT_RUNTIME_ERROR": 20,
        "EXIT_DEPENDENCY_ERROR": 30,
        "EXIT_VALIDATION_ERROR": 40,
        "ENV_FILENAME": ".env",
        "CONFIG_DIRECTORY": "config",
        "LOG_DIRECTORY": "logs",
        "CACHE_DIRECTORY": ".cache",
        "DATA_DIRECTORY": "data",
        "ENV_APP_ENV": "AURORA_ENV",
        "ENV_LOG_LEVEL": "AURORA_LOG_LEVEL",
        "ENV_CONFIG_PATH": "AURORA_CONFIG_PATH",
        "ENV_SESSION_ID": "AURORA_SESSION_ID",
        "RESERVED_ENV_VARS": (
            "AURORA_ENV",
            "AURORA_LOG_LEVEL",
            "AURORA_CONFIG_PATH",
            "AURORA_SESSION_ID",
        ),
    }
    for name, value in expected.items():
        assert getattr(constants, name) == value, name
    reexports = {
        "ARCHITECTURE_FREEZE",
        "ARCHITECTURE_VERSION",
        "ENGINE_STAGE",
        "ENGINE_VERSION",
        "PROJECT_DISPLAY_NAME",
        "PROJECT_NAME",
        "PYTHON_VERSION",
    }
    assert {name for name in vars(constants) if name.isupper()} == expected.keys() | reexports
    for name in reexports:
        assert getattr(constants, name) is getattr(version, name)


def test_version_facts_and_single_assignment_owner() -> None:
    expected: dict[str, object] = {
        "PROJECT_NAME": "AURORA",
        "PROJECT_DISPLAY_NAME": "AURORA Runtime Engine",
        "ARCHITECTURE_VERSION": "1.0",
        "ARCHITECTURE_FREEZE": "Architecture Freeze v1.0",
        "ENGINE_VERSION": "0.1.0",
        "ENGINE_STAGE": "Wave 1 — Kernel Runtime",
        "KERNEL_RUNTIME_VERSION": "1.0.0",
        "API_VERSION": "v1",
        "PYTHON_VERSION": "3.13",
        "VERSION": (0, 1, 0),
        "__version__": "0.1.0",
    }
    for name, value in expected.items():
        assert getattr(version, name) == value, name
    assert {name for name in vars(version) if name.isupper()} == expected.keys() - {"__version__"}
    tree = ast.parse(Path(constants.__file__).read_text(encoding="utf-8"))
    assignments = {
        node.target.id
        for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assert not assignments.intersection(expected)


def test_foundation_package_exports_are_canonical_and_identical() -> None:
    versions = {
        "ARCHITECTURE_FREEZE",
        "ARCHITECTURE_VERSION",
        "ENGINE_STAGE",
        "ENGINE_VERSION",
        "KERNEL_RUNTIME_VERSION",
        "PROJECT_DISPLAY_NAME",
        "PROJECT_NAME",
        "PYTHON_VERSION",
    }
    enums = {
        "DIScope",
        "EventPhase",
        "EventPriority",
        "HealthStatus",
        "RuntimeLayer",
        "RuntimeStatus",
    }
    assert set(core.__all__) == versions | enums
    assert len(core.__all__) == 14
    for name in versions:
        assert getattr(core, name) is getattr(version, name)
    for name in enums:
        assert getattr(core, name) is getattr(types, name)


def test_complete_exception_hierarchy_and_context_formatting() -> None:
    parents: dict[str, str] = {
        "AuroraError": "Exception",
        "ConfigurationError": "AuroraError",
        "MissingConfigurationError": "ConfigurationError",
        "InvalidConfigurationError": "ConfigurationError",
        "ContainerError": "AuroraError",
        "ServiceRegistrationError": "ContainerError",
        "ServiceResolutionError": "ContainerError",
        "CircularDependencyError": "ContainerError",
        "ScopeViolationError": "ContainerError",
        "ManifestError": "AuroraError",
        "InvalidManifestError": "ManifestError",
        "RuntimeLayerError": "ManifestError",
        "RuntimeDependencyError": "ManifestError",
        "EventBusError": "AuroraError",
        "InvalidEventError": "EventBusError",
        "EventValidationError": "EventBusError",
        "EventPublishError": "EventBusError",
        "EventHandlerError": "EventBusError",
        "DiagnosticsError": "AuroraError",
        "ReadOnlyViolationError": "DiagnosticsError",
        "ValidationError": "AuroraError",
        "ContractValidationError": "ValidationError",
        "StateValidationError": "ValidationError",
        "RuntimeError": "AuroraError",
        "RuntimeInitializationError": "RuntimeError",
        "RuntimeShutdownError": "RuntimeError",
        "RuntimeStateError": "RuntimeError",
    }
    tree = ast.parse(Path(exceptions.__file__).read_text(encoding="utf-8"))
    assert {node.name for node in tree.body if isinstance(node, ast.ClassDef)} == parents.keys()
    for name, parent in parents.items():
        exception = getattr(exceptions, name)
        assert exception.__bases__ == (
            (Exception,) if parent == "Exception" else (getattr(exceptions, parent),)
        )
        error = exception("synthetic")
        assert isinstance(error, exceptions.AuroraError)
        assert error.args == ("synthetic",) and error.context == {}
        assert str(error) == "synthetic"
    error = exceptions.AuroraError("synthetic", z=3, a="value")
    assert error.message == "synthetic"
    assert error.context == {"a": "value", "z": 3}
    assert str(error) == "synthetic (a='value', z=3)"


def test_owned_type_symbols_are_complete_without_runtime_implementation() -> None:
    expected = {
        "ModuleId",
        "SessionId",
        "PipelineId",
        "ServiceId",
        "EventId",
        "TraceId",
        "JSONPrimitive",
        "JSONValue",
        "JSONDict",
        "Payload",
        "Metadata",
        "Headers",
        "RuntimeLayer",
        "RUNTIME_LAYER_VALUES",
        "DIScope",
        "DI_SCOPE_VALUES",
        "RuntimeStatus",
        "RUNTIME_STATUS_VALUES",
        "HealthStatus",
        "HEALTH_STATUS_VALUES",
        "EventPriority",
        "EVENT_PRIORITY_VALUES",
        "EventPhase",
        "EVENT_PHASE_VALUES",
    }
    tree = ast.parse(Path(types.__file__).read_text(encoding="utf-8"))
    declared: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            declared.add(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            declared.add(node.target.id)
        elif isinstance(node, ast.TypeAlias):
            declared.add(node.name.id)
        elif isinstance(node, ast.Assign):
            declared.update(target.id for target in node.targets if isinstance(target, ast.Name))
        assert not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    assert declared == expected
    for name in ("ModuleId", "SessionId", "PipelineId", "ServiceId", "EventId", "TraceId"):
        assert getattr(types, name).__name__ == name


def test_all_foundation_files_keep_their_downward_import_boundary() -> None:
    for module in (core, constants, exceptions, types, version):
        assert module.__file__ is not None
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.level == 0
                assert node.module in {
                    "__future__",
                    "enum",
                    "typing",
                    "uuid",
                    "src.core.types",
                    "src.core.version",
                }
            elif isinstance(node, ast.Import):
                pytest.fail("Foundation keeps explicit approved imports, not later runtime owners")
