"""Tests for OpenAI Responses API payload and failure handling."""

from __future__ import annotations

import json
from email.message import Message
from io import BytesIO
from typing import NoReturn, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request

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

    def read(self) -> bytes:
        return self._body


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
                "model": "gpt-5.6-terra",
                "output": [
                    {"type": "reasoning"},
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "First paragraph."},
                            {"type": "output_text", "text": "Second paragraph."},
                        ],
                    },
                ],
            }
        )

    monkeypatch.setattr(openai_client_module, "urlopen", fake_urlopen)
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

    monkeypatch.setattr(openai_client_module, "urlopen", fake_urlopen)

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

    monkeypatch.setattr(openai_client_module, "urlopen", fake_urlopen)

    request = GenerationRequest(model="model", prompt="prompt")
    job = OpenAIResponsesClient("test-key").generate(request)

    assert job.failure is not None
    assert job.failure.category == "network"
    assert job.failure.retryable is True


def test_malformed_response_becomes_terminal_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, *, timeout: float) -> FakeResponse:
        return FakeResponse({"id": "r"})

    monkeypatch.setattr(openai_client_module, "urlopen", fake_urlopen)

    request = GenerationRequest(model="model", prompt="prompt")
    job = OpenAIResponsesClient("test-key").generate(request)

    assert job.failure is not None
    assert job.failure.category == "invalid_response"


@pytest.mark.parametrize(
    ("api_key", "timeout_seconds"),
    [("", 1.0), ("key", 0.0)],
)
def test_invalid_local_configuration_is_rejected(api_key: str, timeout_seconds: float) -> None:
    with pytest.raises(GenerationConfigurationError):
        OpenAIResponsesClient(api_key, timeout_seconds=timeout_seconds)


def test_invalid_request_is_rejected_before_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, *, timeout: float) -> NoReturn:
        pytest.fail("network called")

    monkeypatch.setattr(openai_client_module, "urlopen", fake_urlopen)

    with pytest.raises(GenerationConfigurationError, match="prompt"):
        OpenAIResponsesClient("test-key").generate(GenerationRequest(model="model", prompt=" "))
