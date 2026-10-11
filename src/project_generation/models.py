"""Immutable request data for one-prompt site drafts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectDraftRequest:
    """User-supplied data and configured model for one explicit generation."""

    project_name: str
    business_prompt: str = field(repr=False)
    language: Literal["ru", "en"]
    model: str
