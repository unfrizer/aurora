"""Tests for immutable terminal generation snapshots."""

from __future__ import annotations

import pytest

from src.generation.models import (
    GenerationFailure,
    GenerationJob,
    GenerationRequest,
    GenerationResult,
)


def test_completed_job_requires_result_without_failure() -> None:
    request = GenerationRequest(model="model", prompt="prompt")
    result = GenerationResult(response_id="resp_1", model="model", output_text="text")

    job = GenerationJob(job_id="job_1", request=request, status="completed", result=result)

    assert job.result == result


def test_job_rejects_mismatched_terminal_outcome() -> None:
    request = GenerationRequest(model="model", prompt="prompt")
    failure = GenerationFailure(category="network", message="failed", retryable=True)

    with pytest.raises(ValueError, match="exactly one"):
        GenerationJob(job_id="job_1", request=request, status="completed", failure=failure)
