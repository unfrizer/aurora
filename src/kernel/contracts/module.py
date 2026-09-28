"""
AURORA Runtime Engine — KR-004 Kernel Contracts
Module: KR-004
File: src/kernel/contracts/module.py

Canonical Runtime Module Manifest contract.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.types import ModuleId, RuntimeLayer


@dataclass(frozen=True, kw_only=True, slots=True)
class RuntimeModuleManifest:
    """
    Immutable runtime module metadata.

    Every runtime module must expose exactly one manifest describing its
    identity, ownership layer, and static dependencies.
    """

    module_id: ModuleId
    runtime_layer: RuntimeLayer
    depends_on: tuple[ModuleId, ...]
    provides: tuple[str, ...]
    version: str


__all__ = ["RuntimeModuleManifest"]
