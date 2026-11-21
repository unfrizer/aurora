"""HTTP 429 billing distinctions for both adapters without provider calls."""

from __future__ import annotations

import json
from email.message import Message
from io import BytesIO
from typing import NoReturn
from urllib.error import HTTPError
from urllib.request import Request

import pytest

import src.generation.openai_client as text_module
import src.generation.openai_image_client as image_module
from src.generation import (
    GenerationRequest,
    ImageGenerationRequest,
    OpenAIImageClient,
    OpenAIResponsesClient,
)


def _body(code: object = None, error_type: object = None) -> bytes:
    return json.dumps({"error": {"code": code, "type": error_type,
        "message": "private-provider-message-secret-key"}}).encode()


@pytest.mark.parametrize("image", [False, True], ids=["text", "image"])
@pytest.mark.parametrize(
    ("body_bytes", "retryable"),
    [
        *[pytest.param(_body(code), False, id=code) for code in (
            "insufficient_quota", "credit_balance_exhausted",
            "organization_spend_limit_exceeded", "project_spend_limit_exceeded",
            "organization_usage_limit_exceeded", "usage_limit_exceeded",
            "billing_hard_limit_reached",
        )],
        pytest.param(_body(None, "insufficient_quota"), False, id="legacy-type"),
        pytest.param(_body("rate_limit_exceeded"), True, id="temporary"),
        pytest.param(_body("slow_down"), True, id="slow-down"),
        pytest.param(_body("future-code", "insufficient_quota"), True, id="unknown-specific-code"),
        pytest.param(_body(["insufficient_quota"]), True, id="malformed-code"),
        pytest.param(b'[]', True, id="wrong-shape"),
        pytest.param(b'{"error":[]}', True, id="wrong-error-shape"),
        pytest.param(b'{"error":', True, id="broken-json"),
        pytest.param(b'\xff', True, id="broken-encoding"),
        pytest.param(b'', True, id="missing-body"),
        pytest.param(_body("insufficient_quota") + b' ' * (64 * 1024), True, id="oversized"),
    ],
)
def test_bounded_sanitized_429_without_retries(
    monkeypatch: pytest.MonkeyPatch, image: bool, body_bytes: bytes, retryable: bool
) -> None:
    reads: list[int] = []
    calls = 0

    class TrackedBody(BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            reads.append(-1 if size is None else size)
            return super().read(size)

    body = TrackedBody(body_bytes)

    def fail(request: Request, *, timeout: float) -> NoReturn:
        nonlocal calls
        calls += 1
        raise HTTPError(request.full_url, 429, "private-reason", Message(), body)

    monkeypatch.setattr(image_module if image else text_module, "_open_response", fail)
    outcome = (
        OpenAIImageClient("secret-key").generate(ImageGenerationRequest("model", "private"))
        if image
        else OpenAIResponsesClient("secret-key").generate(GenerationRequest("model", "private"))
    )
    assert outcome.failure is not None
    assert outcome.failure.category == "rate_limited"
    assert outcome.failure.retryable is retryable
    assert reads == [64 * 1024 + 1]
    assert body.closed and calls == 1
    assert "private" not in repr(outcome.failure)
    assert "secret-key" not in repr(outcome.failure)
    if not retryable:
        assert "credits or billing and usage limits" in outcome.failure.message


@pytest.mark.parametrize("image", [False, True])
def test_error_body_read_failure_is_closed_and_does_not_escape(
    monkeypatch: pytest.MonkeyPatch, image: bool
) -> None:
    class BrokenBody(BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            raise OSError("private transport details")

    body = BrokenBody()

    def fail(request: Request, *, timeout: float) -> NoReturn:
        raise HTTPError(request.full_url, 429, "private-reason", Message(), body)

    monkeypatch.setattr(image_module if image else text_module, "_open_response", fail)
    outcome = (
        OpenAIImageClient("secret-key").generate(ImageGenerationRequest("model", "private"))
        if image
        else OpenAIResponsesClient("secret-key").generate(GenerationRequest("model", "private"))
    )
    assert body.closed and outcome.failure is not None
    assert outcome.failure.category == "rate_limited" and outcome.failure.retryable
    assert "private" not in repr(outcome.failure)
