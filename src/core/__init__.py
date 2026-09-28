"""
AURORA Runtime Engine — KR-001 Foundation Core
File: src/core/__init__.py

Public exports for the Foundation Core package.

Architecture Freeze v1.0
Python 3.13
"""

from src.core.types import (
    DIScope,
    EventPhase,
    EventPriority,
    HealthStatus,
    RuntimeLayer,
    RuntimeStatus,
)
from src.core.version import (
    ARCHITECTURE_FREEZE,
    ARCHITECTURE_VERSION,
    ENGINE_STAGE,
    ENGINE_VERSION,
    KERNEL_RUNTIME_VERSION,
    PROJECT_DISPLAY_NAME,
    PROJECT_NAME,
    PYTHON_VERSION,
)

__all__ = [
    "ARCHITECTURE_FREEZE",
    "ARCHITECTURE_VERSION",
    "ENGINE_STAGE",
    "ENGINE_VERSION",
    "KERNEL_RUNTIME_VERSION",
    "PROJECT_DISPLAY_NAME",
    "PROJECT_NAME",
    "PYTHON_VERSION",
    "DIScope",
    "EventPhase",
    "EventPriority",
    "HealthStatus",
    "RuntimeLayer",
    "RuntimeStatus",
]
