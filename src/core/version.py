"""
AURORA Runtime Engine — KR-001 Foundation Core
File: src/core/version.py

Canonical runtime version metadata.

Architecture Freeze v1.0
Python 3.13
"""

from __future__ import annotations

from typing import Final

# ============================================================================
# Project Identity
# ============================================================================

PROJECT_NAME: Final[str] = "AURORA"
PROJECT_DISPLAY_NAME: Final[str] = "AURORA Runtime Engine"


# ============================================================================
# Architecture Freeze
# ============================================================================

ARCHITECTURE_VERSION: Final[str] = "1.0"
ARCHITECTURE_FREEZE: Final[str] = "Architecture Freeze v1.0"


# ============================================================================
# Runtime / Engine Version
# ============================================================================

ENGINE_VERSION: Final[str] = "0.1.0"
ENGINE_STAGE: Final[str] = "Wave 1 — Kernel Runtime"

KERNEL_RUNTIME_VERSION: Final[str] = "1.0.0"


# ============================================================================
# Public API Version
# ============================================================================

API_VERSION: Final[str] = "v1"


# ============================================================================
# Python Runtime Requirement
# ============================================================================

PYTHON_VERSION: Final[str] = "3.13"


# ============================================================================
# Version Tuple
# ============================================================================

VERSION: Final[tuple[int, int, int]] = (0, 1, 0)

__version__: Final[str] = ENGINE_VERSION
