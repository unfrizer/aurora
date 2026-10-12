"""Tests for public in-memory image generation snapshots."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Literal, cast

import pytest

from src.generation import (
    GenerationFailure,
    ImageGenerationJob,
    ImageGenerationRequest,
    ImageGenerationResult,
)

_ID = "a0000000-0000-4000-8000-000000000001"
_PNG = b"\x89PNG\r\n\x1a\nsynthetic"
_MAX_IMAGE_BYTES = 16 * 1024 * 1024


def test_public_snapshots_are_frozen_slotted_and_redact_private_data() -> None:
    request = ImageGenerationRequest("selected-model", "private prompt")
    result = ImageGenerationResult(_PNG)
    job = ImageGenerationJob(_ID, request, "completed", result=result)

    assert job.result == result
    assert result.media_type == "image/png"
    assert "private prompt" not in repr(job)
    assert "synthetic" not in repr(job)
    assert not hasattr(request, "__dict__")
    assert not hasattr(result, "__dict__")
    assert not hasattr(job, "__dict__")
    with pytest.raises(FrozenInstanceError):
        request.prompt = "changed"  # pyright: ignore[reportAttributeAccessIssue]


@pytest.mark.parametrize("data", [b"", b"not a PNG", bytearray(_PNG)])
def test_result_rejects_non_png_or_mutable_bytes(data: object) -> None:
    with pytest.raises(ValueError, match="bounded PNG"):
        ImageGenerationResult(cast(bytes, data))


def test_result_limit_matches_p1_and_does_not_truncate() -> None:
    assert _MAX_IMAGE_BYTES == 16 * 1024 * 1024
    assert len(ImageGenerationResult(_PNG + b"x" * (_MAX_IMAGE_BYTES - len(_PNG))).data) == (
        _MAX_IMAGE_BYTES
    )
    with pytest.raises(ValueError, match="bounded PNG"):
        ImageGenerationResult(_PNG + b"x" * (_MAX_IMAGE_BYTES - len(_PNG) + 1))
    with pytest.raises(ValueError, match="bounded PNG"):
        ImageGenerationResult(_PNG, cast(Literal["image/png"], "image/jpeg"))


def test_terminal_job_invariants_and_canonical_uuid() -> None:
    request = ImageGenerationRequest("model", "private prompt")
    result = ImageGenerationResult(_PNG)
    failure = GenerationFailure("network", "Safe failure", True)
    assert ImageGenerationJob(_ID, request, "failed", failure=failure).failure == failure
    for arguments in [
        {"status": "completed"},
        {"status": "failed"},
        {"status": "completed", "result": result, "failure": failure},
        {"status": "failed", "result": result, "failure": failure},
    ]:
        with pytest.raises(ValueError, match="terminal outcome"):
            ImageGenerationJob(_ID, request, **arguments)  # type: ignore[arg-type]
    for invalid_id in ["not-a-uuid", _ID.upper(), "{a0000000-0000-4000-8000-000000000001}"]:
        with pytest.raises(ValueError, match="canonical UUID"):
            ImageGenerationJob(invalid_id, request, "completed", result=result)
    with pytest.raises(ValueError, match="terminal outcome"):
        ImageGenerationJob(_ID, request, "completed", result=cast(ImageGenerationResult, object()))
