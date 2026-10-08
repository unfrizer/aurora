"""Immutable, structurally typed version-one editor snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorBrand:
    name: str
    tagline: str
    primary_color: str
    secondary_color: str
    font_family: Literal["system", "serif", "monospace"]
    logo_path: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorSection:
    id: str
    heading: str
    body: str
    image_path: str | None
    image_alt: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorPage:
    id: str
    slug: str
    title: str
    meta_description: str
    heading: str
    sections: tuple[EditorSection, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorDocument:
    schema_version: Literal[1]
    language: Literal["ru", "en"]
    brand: EditorBrand
    pages: tuple[EditorPage, ...]


class EditorStateError(ValueError):
    """Malformed or unsupported editor-state boundary value."""


__all__ = [
    "EditorBrand",
    "EditorDocument",
    "EditorPage",
    "EditorSection",
    "EditorStateError",
]
