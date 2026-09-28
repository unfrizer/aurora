"""
AURORA Runtime Engine — KR-001 Foundation Core
File: src/core/exceptions.py

Canonical exception hierarchy for the Kernel Runtime.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from typing import Any


class AuroraError(Exception):
    """
    Base exception for the entire AURORA Runtime Engine.

    Every runtime-specific exception must inherit from this class.
    """

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self) -> str:
        if not self.context:
            return self.message

        details = ", ".join(f"{key}={value!r}" for key, value in sorted(self.context.items()))
        return f"{self.message} ({details})"


# ============================================================================
# Configuration Runtime
# ============================================================================


class ConfigurationError(AuroraError):
    """Raised when runtime configuration is invalid."""


class MissingConfigurationError(ConfigurationError):
    """Raised when a required configuration value is missing."""


class InvalidConfigurationError(ConfigurationError):
    """Raised when a configuration value fails validation."""


# ============================================================================
# Dependency Injection Runtime
# ============================================================================


class ContainerError(AuroraError):
    """Base exception for the Dependency Injection container."""


class ServiceRegistrationError(ContainerError):
    """Raised when service registration is invalid."""


class ServiceResolutionError(ContainerError):
    """Raised when dependency resolution fails."""


class CircularDependencyError(ContainerError):
    """Raised when the container detects a circular dependency."""


class ScopeViolationError(ContainerError):
    """Raised when a service is requested from an invalid scope."""


# ============================================================================
# Runtime Module Manifest
# ============================================================================


class ManifestError(AuroraError):
    """Base exception for runtime manifest validation."""


class InvalidManifestError(ManifestError):
    """Raised when a runtime manifest is malformed."""


class RuntimeLayerError(ManifestError):
    """Raised when a runtime layer violates Architecture Freeze rules."""


class RuntimeDependencyError(ManifestError):
    """Raised when runtime module dependencies are invalid."""


# ============================================================================
# Event Bus Runtime
# ============================================================================


class EventBusError(AuroraError):
    """Base exception for the Typed Event Bus."""


class InvalidEventError(EventBusError):
    """Raised when an event payload does not satisfy the contract."""


class EventValidationError(EventBusError):
    """Raised when required event fields are missing or invalid."""


class EventPublishError(EventBusError):
    """Raised when an event cannot be published."""


class EventHandlerError(EventBusError):
    """Raised when an event handler fails during execution."""


# ============================================================================
# Diagnostics Runtime
# ============================================================================


class DiagnosticsError(AuroraError):
    """Base exception for Diagnostics Runtime."""


class ReadOnlyViolationError(DiagnosticsError):
    """Raised when Diagnostics Runtime attempts a write operation."""


# ============================================================================
# Validation Runtime
# ============================================================================


class ValidationError(AuroraError):
    """Base validation exception for runtime models and contracts."""


class ContractValidationError(ValidationError):
    """Raised when a runtime contract fails validation."""


class StateValidationError(ValidationError):
    """Raised when runtime state becomes invalid."""


# ============================================================================
# Lifecycle Runtime
# ============================================================================


class RuntimeError(AuroraError):
    """Base runtime lifecycle exception."""


class RuntimeInitializationError(RuntimeError):
    """Raised when runtime initialization fails."""


class RuntimeShutdownError(RuntimeError):
    """Raised when runtime shutdown fails."""


class RuntimeStateError(RuntimeError):
    """Raised when runtime lifecycle state is invalid."""
