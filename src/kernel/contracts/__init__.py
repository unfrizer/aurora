"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/__init__.py

Public exports for Kernel Runtime contracts.

Architecture Freeze v1.0
Python 3.13
"""

from src.kernel.contracts.context import RuntimeContext, TraceContext
from src.kernel.contracts.events import EventHandlerContract, RuntimeEvent
from src.kernel.contracts.lifecycle import LifecycleContract, LifecycleState
from src.kernel.contracts.module import RuntimeModuleManifest
from src.kernel.contracts.runtime import RuntimeContract
from src.kernel.contracts.service import ServiceContract, ServiceDescriptor

__all__ = [
    "EventHandlerContract",
    "LifecycleContract",
    "LifecycleState",
    "RuntimeContext",
    "RuntimeContract",
    "RuntimeEvent",
    "RuntimeModuleManifest",
    "ServiceContract",
    "ServiceDescriptor",
    "TraceContext",
]
