"""Deterministic provider-boundary tests; no live OpenAI requests."""

from __future__ import annotations

import base64
import json
from email.message import Message
from http.client import HTTPResponse, IncompleteRead
from io import BytesIO
from typing import NoReturn, cast
from urllib.error import HTTPError, URLError
from urllib.request import OpenerDirector, Request
from uuid import UUID

import pytest

import src.generation.openai_image_client as image_client_module
from src.generation import (
    GenerationConfigurationError,
    ImageGenerationRequest,
    OpenAIImageClient,
)

_PNG = b"\x89PNG\r\n\x1a\nsynthetic image bytes"


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.body = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        self.read_limit: int | None = None
        self.closed = False

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.closed = True

    def read(self, limit: int = -1) -> bytes:
        self.read_limit = limit
        return self.body if limit < 0 else self.body[:limit]


def _image_response(image: bytes = _PNG) -> dict[str, object]:
    return {"created": 1, "data": [{"b64_json": base64.b64encode(image).decode("ascii")}]}


def test_exact_one_call_and_detached_png_result(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Request, float]] = []
    response = FakeResponse(_image_response())

    def open_response(request: Request, *, timeout: float) -> FakeResponse:
        calls.append((request, timeout))
        return response

    monkeypatch.setattr(image_client_module, "_open_response", open_response)
    request = ImageGenerationRequest("configured-image-model", "  Private café prompt  ")
    job = OpenAIImageClient("test-key", timeout_seconds=12.5).generate(request)

    assert job.status == "completed" and job.result is not None
    assert job.result.data == _PNG
    assert job.result.media_type == "image/png"
    assert str(UUID(job.job_id)) == job.job_id
    assert response.closed
    assert response.read_limit == 24 * 1024 * 1024 + 1
    assert len(calls) == 1
    sent, timeout = calls[0]
    assert timeout == 12.5
    assert sent.full_url == "https://api.openai.com/v1/images/generations"
    assert sent.get_method() == "POST"
    assert sent.get_header("Authorization") == "Bearer test-key"
    assert sent.get_header("Content-type") == "application/json"
    assert json.loads(cast(bytes, sent.data)) == {
        "model": "configured-image-model",
        "prompt": "  Private café prompt  ",
        "n": 1,
        "size": "1024x1024",
        "output_format": "png",
    }
    assert "test-key" not in repr(job)
    assert "Private café prompt" not in repr(job)
    assert "synthetic image bytes" not in repr(job)


@pytest.mark.parametrize(
    ("status", "category", "retryable"),
    [
        (401, "authentication", False),
        (403, "authentication", False),
        (429, "rate_limited", True),
        (500, "remote", True),
        (503, "remote", True),
        (400, "remote", False),
        (302, "remote", False),
    ],
)
def test_http_error_is_closed_sanitized_and_never_retried(
    monkeypatch: pytest.MonkeyPatch, status: int, category: str, retryable: bool
) -> None:
    body = BytesIO(b"private provider body and key")
    calls = 0

    def open_response(request: Request, *, timeout: float) -> NoReturn:
        nonlocal calls
        calls += 1
        raise HTTPError(request.full_url, status, "private provider body", Message(), body)

    monkeypatch.setattr(image_client_module, "_open_response", open_response)
    job = OpenAIImageClient("secret-key").generate(ImageGenerationRequest("model", "private"))
    assert calls == 1
    assert body.closed
    assert job.status == "failed" and job.failure is not None and job.result is None
    assert job.failure.category == category
    assert job.failure.retryable is retryable
    assert "private" not in repr(job)
    assert "secret-key" not in repr(job)


@pytest.mark.parametrize("error", [URLError("offline"), IncompleteRead(b"private bytes")])
def test_transport_failure_is_safe_without_retry(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    calls = 0

    def open_response(request: Request, *, timeout: float) -> NoReturn:
        nonlocal calls
        calls += 1
        raise error

    monkeypatch.setattr(image_client_module, "_open_response", open_response)
    job = OpenAIImageClient("test-key").generate(ImageGenerationRequest("model", "prompt"))
    assert calls == 1
    assert job.status == "failed" and job.failure is not None
    assert job.failure.category == "network" and job.failure.retryable
    assert "private" not in repr(job)


@pytest.mark.parametrize(
    "payload",
    [
        b"invalid JSON",
        {},
        {"data": []},
        {"data": [{"url": "https://example.invalid/image.png"}]},
        {"data": [{"b64_json": ""}]},
        {"data": [{"b64_json": "%%%"}]},
        {"data": [{"b64_json": base64.b64encode(b"not PNG").decode("ascii")}]},
        {"data": [{"b64_json": base64.b64encode(_PNG).decode("ascii")}, {"b64_json": "x"}]},
        {"data": [{"b64_json": base64.b64encode(_PNG).decode("ascii")}], "error": "failed"},
        {"data": [{"b64_json": base64.b64encode(_PNG).decode("ascii")}], "output_format": "jpeg"},
    ],
)
def test_invalid_response_never_becomes_image(
    monkeypatch: pytest.MonkeyPatch, payload: object
) -> None:
    def open_response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(payload)

    monkeypatch.setattr(image_client_module, "_open_response", open_response)
    job = OpenAIImageClient("test-key").generate(ImageGenerationRequest("model", "prompt"))
    assert job.status == "failed" and job.result is None and job.failure is not None
    assert job.failure.category == "invalid_response" and not job.failure.retryable


def test_response_envelope_limit_precedes_json_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(_image_response())

    def open_response(request: Request, *, timeout: float) -> FakeResponse:
        return response

    monkeypatch.setattr(image_client_module, "_MAX_RESPONSE_BYTES", 12)
    monkeypatch.setattr(image_client_module, "_open_response", open_response)
    job = OpenAIImageClient("test-key").generate(ImageGenerationRequest("model", "prompt"))
    assert response.read_limit == 13 and response.closed
    assert job.failure is not None and job.failure.category == "invalid_response"


def test_decoded_png_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    import src.generation.image_models as image_models_module

    def open_response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(_image_response(_PNG + b"x"))

    monkeypatch.setattr(image_models_module, "_MAX_IMAGE_BYTES", len(_PNG))
    monkeypatch.setattr(image_client_module, "_open_response", open_response)
    job = OpenAIImageClient("test-key").generate(ImageGenerationRequest("model", "prompt"))
    assert job.failure is not None and job.failure.category == "invalid_response"


@pytest.mark.parametrize(
    ("api_key", "timeout"),
    [
        ("", 1.0),
        ("test-key\r\nInjected: yes", 1.0),
        ("test-key", 0.0),
        ("test-key", -1.0),
        ("test-key", float("nan")),
        ("test-key", float("inf")),
        ("test-key", True),
    ],
)
def test_invalid_client_configuration_is_local(api_key: str, timeout: float) -> None:
    with pytest.raises(GenerationConfigurationError):
        OpenAIImageClient(api_key, timeout_seconds=timeout)


@pytest.mark.parametrize(
    "generation_request",
    [
        ImageGenerationRequest("", "prompt"),
        ImageGenerationRequest("model", "  "),
        ImageGenerationRequest("model", "x" * (8 * 1024 + 1)),
        ImageGenerationRequest("model", "é" * (4 * 1024 + 1)),
        ImageGenerationRequest("model", "\ud800"),
        ImageGenerationRequest("\ud800", "prompt"),
    ],
)
def test_invalid_request_never_opens_network(
    monkeypatch: pytest.MonkeyPatch, generation_request: ImageGenerationRequest
) -> None:
    def no_network(_request: Request, *, timeout: float) -> NoReturn:
        pytest.fail("network called before local validation")

    monkeypatch.setattr(image_client_module, "_open_response", no_network)
    with pytest.raises(GenerationConfigurationError):
        OpenAIImageClient("test-key").generate(generation_request)


def test_redirect_cannot_forward_authorization(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def open_request(
        self: OpenerDirector,
        fullurl: str | Request,
        data: bytes | None = None,
        timeout: object = None,
    ) -> HTTPResponse:
        assert isinstance(fullurl, Request)
        calls.append(fullurl.full_url)
        headers: Message[str, str] = Message()
        headers["Location"] = "https://example.invalid/steal"
        return cast(
            HTTPResponse,
            self.error("https", fullurl, BytesIO(), 302, "Found", headers),
        )

    monkeypatch.setattr(OpenerDirector, "open", open_request)
    job = OpenAIImageClient("test-key").generate(ImageGenerationRequest("model", "prompt"))
    assert job.status == "failed"
    assert calls == ["https://api.openai.com/v1/images/generations"]
