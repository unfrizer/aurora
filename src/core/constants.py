"""
AURORA Runtime Engine — KR-001 Foundation Core
Module: KR-001
File: src/core/constants.py

Architecture Freeze: v1.0
Python: 3.13

This module is the single source of truth for immutable runtime constants used
across the Kernel Runtime. No runtime state or mutable configuration is allowed.
"""

from __future__ import annotations

from typing import Final

from src.core.version import ARCHITECTURE_FREEZE as ARCHITECTURE_FREEZE
from src.core.version import ARCHITECTURE_VERSION as ARCHITECTURE_VERSION
from src.core.version import ENGINE_STAGE as ENGINE_STAGE
from src.core.version import ENGINE_VERSION as ENGINE_VERSION
from src.core.version import PROJECT_DISPLAY_NAME as PROJECT_DISPLAY_NAME
from src.core.version import PROJECT_NAME as PROJECT_NAME
from src.core.version import PYTHON_VERSION as PYTHON_VERSION

# ============================================================================
# Project Metadata
# ============================================================================

# Project and architecture version facts are owned by src.core.version.


# ============================================================================
# Runtime Identity
# ============================================================================

RUNTIME_KERNEL_ID: Final[str] = "KR-001"


# ============================================================================
# Runtime Layers (Architecture Freeze)
# ============================================================================

LAYER_KERNEL: Final[str] = "L0_KERNEL"
LAYER_STATE: Final[str] = "L1_STATE"
LAYER_LAYOUT: Final[str] = "L2_LAYOUT"
LAYER_THEME: Final[str] = "L3_THEME"
LAYER_MOTION: Final[str] = "L4_MOTION"
LAYER_INTERACTION: Final[str] = "L5_INTERACTION"
LAYER_ACCESSIBILITY: Final[str] = "L6_ACCESSIBILITY"
LAYER_PLATFORM_BRIDGE: Final[str] = "L7_PLATFORM"
LAYER_RENDER: Final[str] = "L8_RENDER"


RUNTIME_LAYERS: Final[tuple[str, ...]] = (
    LAYER_KERNEL,
    LAYER_STATE,
    LAYER_LAYOUT,
    LAYER_THEME,
    LAYER_MOTION,
    LAYER_INTERACTION,
    LAYER_ACCESSIBILITY,
    LAYER_PLATFORM_BRIDGE,
    LAYER_RENDER,
)


# ============================================================================
# Dependency Injection Scopes
# ============================================================================

SCOPE_APPLICATION: Final[str] = "application"
SCOPE_SESSION: Final[str] = "session"
SCOPE_PIPELINE: Final[str] = "pipeline"
SCOPE_TRANSIENT: Final[str] = "transient"


DI_SCOPES: Final[tuple[str, ...]] = (
    SCOPE_APPLICATION,
    SCOPE_SESSION,
    SCOPE_PIPELINE,
    SCOPE_TRANSIENT,
)


# ============================================================================
# Event Bus Constants
# ============================================================================

EVENT_VERSION: Final[str] = "1.0"

EVENT_FIELD_EVENT_ID: Final[str] = "event_id"
EVENT_FIELD_EVENT_TYPE: Final[str] = "event_type"
EVENT_FIELD_SESSION_ID: Final[str] = "session_id"
EVENT_FIELD_TIMESTAMP: Final[str] = "timestamp"
EVENT_FIELD_PAYLOAD: Final[str] = "payload"
EVENT_FIELD_TRACE: Final[str] = "trace"

EVENT_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    EVENT_FIELD_EVENT_ID,
    EVENT_FIELD_EVENT_TYPE,
    EVENT_FIELD_SESSION_ID,
    EVENT_FIELD_TIMESTAMP,
    EVENT_FIELD_PAYLOAD,
    EVENT_FIELD_TRACE,
)


# ============================================================================
# Runtime Manifest Constants
# ============================================================================

MANIFEST_FIELD_MODULE_ID: Final[str] = "module_id"
MANIFEST_FIELD_RUNTIME_LAYER: Final[str] = "runtime_layer"
MANIFEST_FIELD_DEPENDS_ON: Final[str] = "depends_on"
MANIFEST_FIELD_PROVIDES: Final[str] = "provides"
MANIFEST_FIELD_VERSION: Final[str] = "version"

MANIFEST_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    MANIFEST_FIELD_MODULE_ID,
    MANIFEST_FIELD_RUNTIME_LAYER,
    MANIFEST_FIELD_DEPENDS_ON,
    MANIFEST_FIELD_PROVIDES,
    MANIFEST_FIELD_VERSION,
)


# ============================================================================
# Runtime Identifiers
# ============================================================================

RUNTIME_CONTAINER: Final[str] = "container_runtime"
RUNTIME_EVENT_BUS: Final[str] = "event_bus_runtime"
RUNTIME_CONFIG: Final[str] = "config_runtime"
RUNTIME_LOGGER: Final[str] = "logger_runtime"
RUNTIME_DIAGNOSTICS: Final[str] = "diagnostics_runtime"


# ============================================================================
# Logging
# ============================================================================

LOGGER_NAME: Final[str] = "aurora"

LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

DEFAULT_LOG_LEVEL: Final[str] = "INFO"


# ============================================================================
# Runtime Defaults
# ============================================================================

DEFAULT_ENCODING: Final[str] = "utf-8"

DEFAULT_TIMEZONE: Final[str] = "UTC"

UUID_VERSION: Final[int] = 4

TRACE_ROOT_ID: Final[str] = "root"


# ============================================================================
# Health & Diagnostics
# ============================================================================

STATUS_OK: Final[str] = "ok"
STATUS_WARNING: Final[str] = "warning"
STATUS_ERROR: Final[str] = "error"

HEALTH_STATUSES: Final[tuple[str, ...]] = (
    STATUS_OK,
    STATUS_WARNING,
    STATUS_ERROR,
)


# ============================================================================
# Exit Codes
# ============================================================================

EXIT_SUCCESS: Final[int] = 0
EXIT_FAILURE: Final[int] = 1
EXIT_CONFIGURATION_ERROR: Final[int] = 10
EXIT_RUNTIME_ERROR: Final[int] = 20
EXIT_DEPENDENCY_ERROR: Final[int] = 30
EXIT_VALIDATION_ERROR: Final[int] = 40


# ============================================================================
# Filesystem Defaults
# ============================================================================

ENV_FILENAME: Final[str] = ".env"

CONFIG_DIRECTORY: Final[str] = "config"
LOG_DIRECTORY: Final[str] = "logs"
CACHE_DIRECTORY: Final[str] = ".cache"
DATA_DIRECTORY: Final[str] = "data"


# ============================================================================
# Reserved Environment Variables
# ============================================================================

ENV_APP_ENV: Final[str] = "AURORA_ENV"
ENV_LOG_LEVEL: Final[str] = "AURORA_LOG_LEVEL"
ENV_CONFIG_PATH: Final[str] = "AURORA_CONFIG_PATH"
ENV_SESSION_ID: Final[str] = "AURORA_SESSION_ID"

RESERVED_ENV_VARS: Final[tuple[str, ...]] = (
    ENV_APP_ENV,
    ENV_LOG_LEVEL,
    ENV_CONFIG_PATH,
    ENV_SESSION_ID,
)
