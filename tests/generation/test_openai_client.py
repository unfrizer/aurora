"""Tests for OpenAI Responses API payload and failure handling."""

from __future__ import annotations

import json
from email.message import Message
from http.client import HTTPResponse, IncompleteRead
from io import BytesIO
from typing import NoReturn, cast
from urllib.error import HTTPError, URLError
from urllib.request import OpenerDirector, Request

import pytest

import src.generation.openai_client as openai_client_module
from src.generation import GenerationConfigurationError, GenerationRequest, OpenAIResponsesClient


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        return None

    def read(self, limit: int = -1) -> bytes:
        return self._body if limit < 0 else self._body[:limit]


def test_successful_generation_sends_stateless_response_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request: Request, *, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "id": "resp_123",
                "status": "completed",
                "model": "gpt-5.6-terra",
                "output": [
                    {"type": "reasoning"},
                    {
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {"type": "output_text", "text": "First paragraph.\n"},
                            {"type": "output_text", "text": "Second paragraph."},
                        ],
                    },
                ],
            }
        )

    monkeypatch.setattr(openai_client_module, "_open_response", fake_urlopen)
    client = OpenAIResponsesClient("test-key", timeout_seconds=12.5)

    job = client.generate(
        GenerationRequest(
            model="gpt-5.6-terra",
            prompt="Create a business outline.",
            instructions="Return concise text.",
        )
    )

    request = captured["request"]
    assert isinstance(request, Request)
    assert job.status == "completed"
    assert job.result is not None
    assert job.result.output_text == "First paragraph.\nSecond paragraph."
    assert json.loads(cast(bytes, request.data)) == {
        "model": "gpt-5.6-terra",
        "input": "Create a business outline.",
        "instructions": "Return concise text.",
        "store": False,
    }
    assert request.get_header("Authorization") == "Bearer test-key"
    assert captured["timeout"] == 12.5


@pytest.mark.parametrize(
    ("status_code", "category", "retryable"),
    [
        (401, "authentication", False),
        (429, "rate_limited", True),
        (503, "remote", True),
        (400, "remote", False),
    ],
)
def test_http_failures_are_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    category: str,
    retryable: bool,
) -> None:
    def fake_urlopen(request: Request, *, timeout: float) -> NoReturn:
        headers: Message[str, str] = Message()
        raise HTTPError(
            request.full_url,
            status_code,
            "remote body must not escape",
            headers,
            BytesIO(),
        )

    monkeypatch.setattr(openai_client_module, "_open_response", fake_urlopen)

    request = GenerationRequest(model="model", prompt="prompt")
    job = OpenAIResponsesClient("test-key").generate(request)

    assert job.status == "failed"
    assert job.failure is not None
    assert job.failure.category == category
    assert job.failure.retryable is retryable
    assert "remote body" not in job.failure.message


def test_network_failure_is_retryable(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, *, timeout: float) -> NoReturn:
        raise URLError("offline")

    monkeypatch.setattr(openai_client_module, "_open_response", fake_urlopen)

    request = GenerationRequest(model="model", prompt="prompt")
    job = OpenAIResponsesClient("test-key").generate(request)

    assert job.failure is not None
    assert job.failure.category == "network"
    assert job.failure.retryable is True


def test_malformed_response_becomes_terminal_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse({"id": "r"})

    monkeypatch.setattr(openai_client_module, "_open_response", fake_urlopen)

    request = GenerationRequest(model="model", prompt="prompt")
    job = OpenAIResponsesClient("test-key").generate(request)

    assert job.failure is not None
    assert job.failure.category == "invalid_response"


@pytest.mark.parametrize(
    ("api_key", "timeout_seconds"),
    [
        ("", 1.0),
        ("key", 0.0),
        ("key\r\nX-Header: value", 1.0),
        ("key", float("nan")),
        ("key", float("inf")),
        ("key", -1.0),
    ],
)
def test_invalid_local_configuration_is_rejected(api_key: str, timeout_seconds: float) -> None:
    with pytest.raises(GenerationConfigurationError):
        OpenAIResponsesClient(api_key, timeout_seconds=timeout_seconds)


def test_invalid_request_is_rejected_before_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, *, timeout: float) -> NoReturn:
        pytest.fail("network called")

    monkeypatch.setattr(openai_client_module, "_open_response", fake_urlopen)

    with pytest.raises(GenerationConfigurationError, match="prompt"):
        OpenAIResponsesClient("test-key").generate(GenerationRequest(model="model", prompt=" "))


def _response_payload(text: str = "A complete answer.") -> dict[str, object]:
    return {
        "id": "resp_test",
        "model": "test-model",
        "status": "completed",
        "error": None,
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": text}],
            }
        ],
    }


@pytest.mark.parametrize("status", ["incomplete", "failed", "queued", "cancelled", None])
def test_partial_text_never_becomes_success(
    monkeypatch: pytest.MonkeyPatch,
    status: str | None,
) -> None:
    payload = _response_payload("truncated...")
    payload["status"] = status

    def response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(payload)

    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.status == "failed"
    assert job.result is None
    assert job.failure is not None and job.failure.category == "invalid_response"


@pytest.mark.parametrize("text", ["", "  \n"])
def test_empty_output_is_failure(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    def response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(_response_payload(text))

    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.status == "failed"


def test_text_fragments_preserve_exact_json(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _response_payload()
    payload["output"] = [
        {"type": "reasoning", "content": [{"type": "output_text", "text": "ignore"}]},
        {
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [
                {"type": "output_text", "text": '{"brand":"Au'},
                {"type": "output_text", "text": 'rora"}'},
            ],
        },
    ]

    def response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(payload)

    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.result is not None
    assert json.loads(job.result.output_text) == {"brand": "Aurora"}


@pytest.mark.parametrize(
    "output",
    [
        [
            {
                "type": "message",
                "role": "assistant",
                "status": "incomplete",
                "content": [{"type": "output_text", "text": "partial"}],
            }
        ],
        [
            {
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "refusal", "refusal": "private refusal"}],
            }
        ],
        [
            {
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": 42}],
            }
        ],
    ],
)
def test_invalid_messages_fail_safely(monkeypatch: pytest.MonkeyPatch, output: object) -> None:
    payload = _response_payload()
    payload["output"] = output

    def response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(payload)

    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.failure is not None
    assert "private refusal" not in repr(job.failure)


def test_http_error_body_closed_and_secret_not_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    body = BytesIO(b"secret-key and private prompt")

    def response(request: Request, *, timeout: float) -> NoReturn:
        raise HTTPError(request.full_url, 401, "secret-key", Message(), body)

    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("secret-key").generate(GenerationRequest("model", "private prompt"))
    assert body.closed
    assert "secret-key" not in repr(job)
    assert "private prompt" not in repr(job)


def test_truncated_http_body_is_network_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def response(request: Request, *, timeout: float) -> NoReturn:
        raise IncompleteRead(b"partial private output")

    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.failure is not None and job.failure.category == "network"


def test_bounded_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def response(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(_response_payload("x" * 1024))

    monkeypatch.setattr(openai_client_module, "_MAX_RESPONSE_BYTES", 512)
    monkeypatch.setattr(openai_client_module, "_open_response", response)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.failure is not None and job.failure.category == "invalid_response"


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
        # Exercise the actual opener/redirect handler without network traffic.
        return cast(
            HTTPResponse,
            self.error(
                "https",
                fullurl,
                BytesIO(),
                302,
                "Found",
                headers,
            ),
        )

    monkeypatch.setattr(OpenerDirector, "open", open_request)
    job = OpenAIResponsesClient("test-key").generate(GenerationRequest("model", "prompt"))
    assert job.status == "failed"
    assert calls == ["https://api.openai.com/v1/responses"]
