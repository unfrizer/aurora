"""
AURORA Runtime Engine — KR-001 Foundation Core
File: src/core/types.py

Canonical shared runtime types for Architecture Freeze v1.0.

This module contains immutable type aliases and enums shared across the
Foundation Core. Runtime models are implemented in later runtime modules.

Python 3.13
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Final, NewType
from uuid import UUID

# ============================================================================
# Strong Runtime Identifiers
# ============================================================================

ModuleId = NewType("ModuleId", str)
SessionId = NewType("SessionId", UUID)
PipelineId = NewType("PipelineId", UUID)
ServiceId = NewType("ServiceId", str)

EventId = NewType("EventId", UUID)
TraceId = NewType("TraceId", UUID)


# ============================================================================
# Generic Runtime Aliases (Python 3.13)
# ============================================================================

type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]
type JSONDict = dict[str, JSONValue]

type Payload = JSONDict
type Metadata = JSONDict
type Headers = dict[str, str]


# ============================================================================
# Runtime Layers
# ============================================================================


class RuntimeLayer(StrEnum):
    """Canonical runtime layers defined by Architecture Freeze v1.0."""

    L0_KERNEL = "L0_KERNEL"
    L1_STATE = "L1_STATE"
    L2_LAYOUT = "L2_LAYOUT"
    L3_THEME = "L3_THEME"
    L4_MOTION = "L4_MOTION"
    L5_INTERACTION = "L5_INTERACTION"
    L6_ACCESSIBILITY = "L6_ACCESSIBILITY"
    L7_PLATFORM = "L7_PLATFORM"
    L8_RENDER = "L8_RENDER"


RUNTIME_LAYER_VALUES: Final[tuple[str, ...]] = tuple(layer.value for layer in RuntimeLayer)


# ============================================================================
# Dependency Injection Scopes
# ============================================================================


class DIScope(StrEnum):
    """Canonical Dependency Injection scopes."""

    APPLICATION = "application"
    SESSION = "session"
    PIPELINE = "pipeline"
    TRANSIENT = "transient"


DI_SCOPE_VALUES: Final[tuple[str, ...]] = tuple(scope.value for scope in DIScope)


# ============================================================================
# Runtime Lifecycle
# ============================================================================


class RuntimeStatus(StrEnum):
    """Lifecycle state of a runtime module."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED = "terminated"
    FAILED = "failed"


RUNTIME_STATUS_VALUES: Final[tuple[str, ...]] = tuple(status.value for status in RuntimeStatus)


# ============================================================================
# Health Status
# ============================================================================


class HealthStatus(StrEnum):
    """Health status returned by Diagnostics Runtime."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


HEALTH_STATUS_VALUES: Final[tuple[str, ...]] = tuple(status.value for status in HealthStatus)


# ============================================================================
# Event Bus Types
# ============================================================================


class EventPriority(IntEnum):
    """Typed Event Bus priority levels."""

    BACKGROUND = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    CRITICAL = 100


EVENT_PRIORITY_VALUES: Final[tuple[int, ...]] = tuple(priority.value for priority in EventPriority)


class EventPhase(StrEnum):
    """Event processing lifecycle."""

    CREATED = "created"
    PUBLISHED = "published"
    HANDLED = "handled"
    FAILED = "failed"


EVENT_PHASE_VALUES: Final[tuple[str, ...]] = tuple(phase.value for phase in EventPhase)
