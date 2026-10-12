"""Immutable terminal snapshots for one OpenAI image generation attempt."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, cast
from uuid import UUID

from src.generation.models import GenerationFailure, GenerationJobStatus

_MAX_IMAGE_BYTES = 16 * 1024 * 1024
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True, slots=True)
class ImageGenerationRequest:
    """Caller-selected model and unchanged private prompt for one image."""

    model: str
    prompt: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class ImageGenerationResult:
    """One detached PNG, not a persisted project asset."""

    data: bytes = field(repr=False)
    media_type: Literal["image/png"] = "image/png"

    def __post_init__(self) -> None:
        if (
            type(self.data) is not bytes
            or not self.data.startswith(_PNG_SIGNATURE)
            or len(self.data) > _MAX_IMAGE_BYTES
            or self.media_type != "image/png"
        ):
            raise ValueError("A generated image must be a bounded PNG byte string.")


@dataclass(frozen=True, slots=True)
class ImageGenerationJob:
    """Exactly one terminal, in-memory image generation outcome."""

    job_id: str
    request: ImageGenerationRequest
    status: GenerationJobStatus
    result: ImageGenerationResult | None = None
    failure: GenerationFailure | None = None

    def __post_init__(self) -> None:
        try:
            canonical_id = str(UUID(self.job_id))
        except (TypeError, ValueError, AttributeError):
            raise ValueError("An image generation job requires a canonical UUID.") from None
        if canonical_id != self.job_id:
            raise ValueError("An image generation job requires a canonical UUID.")
        if not isinstance(cast(object, self.request), ImageGenerationRequest):
            raise ValueError("An image generation job requires a request.")
        if (
            self.status == "completed"
            and isinstance(self.result, ImageGenerationResult)
            and self.failure is None
        ):
            return
        if (
            self.status == "failed"
            and self.result is None
            and isinstance(self.failure, GenerationFailure)
        ):
            return
        raise ValueError("An image generation job must contain one matching terminal outcome.")
