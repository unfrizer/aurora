"""Immutable project-domain models for local portable persistence."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.types import JSONDict


@dataclass(slots=True, frozen=True, kw_only=True)
class ProjectMetadata:
    project_id: str
    name: str
    format_version: str
    created_at: str
    updated_at: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ProjectDocument:
    metadata: ProjectMetadata
    state: JSONDict


__all__ = ["ProjectDocument", "ProjectMetadata"]
