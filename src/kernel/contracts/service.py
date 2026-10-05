"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/service.py

Canonical Service contract.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.types import DIScope, ServiceId

# ============================================================================
# Service Descriptor Contract
# ============================================================================


@dataclass(frozen=True, kw_only=True, slots=True)
class ServiceDescriptor:
    """
    Immutable Dependency Injection service descriptor.

    Each dependency pair binds a constructor keyword to a registered ServiceId.
    KR-005 owns constructor, graph and scope validation; this contract does not
    construct, initialize, resolve or cache services (ADR-004 P-01).
    """

    service_id: ServiceId
    scope: DIScope
    implementation: type[ServiceContract]
    eager: bool = False
    dependencies: tuple[tuple[str, ServiceId], ...] = ()


# ============================================================================
# Service Contract
# ============================================================================


class ServiceContract(ABC):
    """
    Base contract for every Dependency Injection service.

    Services expose a minimal lifecycle to allow the Container Runtime to
    initialize and gracefully shut them down.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the service.

        DI must await this once before returning or caching a ready instance.
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Gracefully shut down the service and release owned resources.

        Implementations must tolerate cleanup after partial initialization.
        """


__all__ = ["ServiceContract", "ServiceDescriptor"]
