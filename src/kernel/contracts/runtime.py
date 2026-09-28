"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/runtime.py

Canonical Runtime contract.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.types import HealthStatus, RuntimeLayer


class RuntimeContract(ABC):
    """
    Base contract for every runtime module.

    A runtime owns exactly one responsibility inside the Kernel Runtime and
    follows the immutable lifecycle defined by Architecture Freeze v1.0.
    """

    @property
    @abstractmethod
    def runtime_name(self) -> str:
        """Return the canonical runtime name."""

    @property
    @abstractmethod
    def runtime_layer(self) -> RuntimeLayer:
        """Return the runtime layer owned by this runtime."""

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize runtime resources.

        Called exactly once before the runtime starts.
        """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the runtime.

        Called after successful initialization.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Gracefully stop the runtime and release owned resources.
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """Release resources after the runtime has stopped."""

    @abstractmethod
    def health(self) -> HealthStatus:
        """Return a read-only health snapshot."""


__all__ = ["RuntimeContract"]
