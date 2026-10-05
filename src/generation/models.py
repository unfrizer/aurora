"""Immutable request, result, and terminal-job snapshots for text generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

GenerationErrorCategory = Literal[
    "authentication",
    "rate_limited",
    "remote",
    "network",
    "invalid_response",
]
GenerationJobStatus = Literal["completed", "failed"]


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """A single direct Responses API text-generation request."""

    model: str
    prompt: str = field(repr=False)
    instructions: str | None = field(default=None, repr=False)


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """The text extracted from one successful OpenAI response."""

    response_id: str
    model: str
    output_text: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class GenerationFailure:
    """A sanitized terminal failure that never contains a secret or response body."""

    category: GenerationErrorCategory
    message: str
    retryable: bool


@dataclass(frozen=True, slots=True)
class GenerationJob:
    """A terminal, in-memory record of a synchronous generation attempt."""

    job_id: str
    request: GenerationRequest
    status: GenerationJobStatus
    result: GenerationResult | None = None
    failure: GenerationFailure | None = None

    def __post_init__(self) -> None:
        if self.status == "completed" and self.result is not None and self.failure is None:
            return
        if self.status == "failed" and self.result is None and self.failure is not None:
            return
        raise ValueError("A generation job must contain exactly one matching terminal outcome.")
