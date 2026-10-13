"""P6-007 same-origin image command, paid-call gates and safe publication."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import cast
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.core.exceptions import ValidationError
from src.credentials import CredentialStoreError, SecretName, WindowsCredentialStore
from src.generation import (
    GenerationErrorCategory,
    GenerationFailure,
    ImageGenerationJob,
    ImageGenerationRequest,
    ImageGenerationResult,
    OpenAIImageClient,
)
from src.local_api import create_app
from src.projects import ProjectDocument, ProjectRepository

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_JOB_ID = "a0000000-0000-4000-8000-000000000001"
_PNG = b"\x89PNG\r\n\x1a\nsynthetic-image"


class _Store(WindowsCredentialStore):
    def __init__(self, key: str | None = "synthetic-key") -> None:
        self.key = key
        self.fail = False
        self.reads = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("No credential write")

    def get_secret(self, name: SecretName) -> str | None:
        assert name == "openai_api_key"
        self.reads += 1
        if self.fail:
            raise CredentialStoreError("native-private-error")
        return self.key

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("No credential delete")


@pytest.fixture
def api(tmp_path: Path) -> Iterator[tuple[Client, _Store, ProjectRepository, str, str]]:
    root = tmp_path / "Projects"
    store = _Store()
    repository = ProjectRepository(root)
    project = repository.create("Studio")
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        yield client, store, repository, project.metadata.project_id, project.metadata.updated_at


def _path(identifier: str) -> str:
    return f"/api/v1/projects/{identifier}/generation/image"


def _body(timestamp: str) -> dict[str, object]:
    return {
        "prompt": "  Draw a studio hero  ",
        "model": "configured-image-model",
        "expected_updated_at": timestamp,
        "confirm_generation": True,
    }


def _success(request: ImageGenerationRequest, data: bytes = _PNG) -> ImageGenerationJob:
    return ImageGenerationJob(
        job_id=_JOB_ID,
        request=request,
        status="completed",
        result=ImageGenerationResult(data),
    )


def test_completed_job_publishes_only_p1_asset_and_redacts_response(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, repository, identifier, timestamp = api
    requests: list[ImageGenerationRequest] = []

    def generate(_client: OpenAIImageClient, request: ImageGenerationRequest) -> ImageGenerationJob:
        requests.append(request)
        return _success(request)

    monkeypatch.setattr(OpenAIImageClient, "generate", generate)
    before = repository.load(identifier)
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"job_id", "status", "source_updated_at", "asset_path", "failure"}
    assert payload == {
        "job_id": _JOB_ID,
        "status": "completed",
        "source_updated_at": timestamp,
        "asset_path": payload["asset_path"],
        "failure": None,
    }
    assert isinstance(payload["asset_path"], str)
    assert payload["asset_path"].startswith("assets/")
    assert payload["asset_path"].endswith(".png")
    assert repository.read_asset(identifier, payload["asset_path"]) == _PNG
    assert repository.load(identifier) == before
    assert store.reads == 1
    assert len(requests) == 1
    assert requests[0].model == "configured-image-model"
    assert requests[0].prompt == "  Draw a studio hero  "
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert "Draw a studio hero" not in response.text
    assert "synthetic-key" not in response.text
    assert "synthetic-image" not in response.text
    assert "access-control-allow-origin" not in response.headers

    asset = client.get(f"/api/v1/projects/{identifier}/{payload['asset_path']}")
    assert asset.status_code == 200
    assert asset.content == _PNG
    assert asset.headers["content-type"] == "image/png"


@pytest.mark.parametrize(
    ("category", "retryable"),
    [
        ("authentication", False),
        ("rate_limited", True),
        ("remote", True),
        ("network", True),
        ("invalid_response", False),
    ],
)
def test_terminal_provider_failure_is_200_without_asset_or_retry(
    api: tuple[Client, _Store, ProjectRepository, str, str],
    monkeypatch: pytest.MonkeyPatch,
    category: str,
    retryable: bool,
) -> None:
    client, store, repository, identifier, timestamp = api
    calls = 0

    def fail(_client: OpenAIImageClient, request: ImageGenerationRequest) -> ImageGenerationJob:
        nonlocal calls
        calls += 1
        return ImageGenerationJob(
            _JOB_ID,
            request,
            "failed",
            failure=GenerationFailure(
                category=cast("GenerationErrorCategory", category),
                message="Safe provider failure.",
                retryable=retryable,
            ),
        )

    monkeypatch.setattr(OpenAIImageClient, "generate", fail)
    before = repository.load(identifier)
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 200
    assert response.json() == {
        "job_id": _JOB_ID,
        "status": "failed",
        "source_updated_at": timestamp,
        "asset_path": None,
        "failure": {
            "category": category,
            "message": "Safe provider failure.",
            "retryable": retryable,
        },
    }
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert repository.load(identifier) == before
    assert calls == store.reads == 1


@pytest.mark.parametrize(
    "change",
    [
        {},
        {"confirm_generation": False},
        {"confirm_generation": 1},
        {"confirm_generation": "true"},
        {"prompt": None},
        {"prompt": "  "},
        {"prompt": "é" * 4096 + "x"},
        {"prompt": 8},
        {"model": " "},
        {"model": 8},
        {"expected_updated_at": 8},
        {"api_key": "private-secret"},
    ],
)
def test_invalid_body_never_reads_secret_or_calls_provider(
    api: tuple[Client, _Store, ProjectRepository, str, str],
    monkeypatch: pytest.MonkeyPatch,
    change: dict[str, object],
) -> None:
    client, store, _repository, identifier, timestamp = api

    def forbidden(
        _client: OpenAIImageClient, _request: ImageGenerationRequest
    ) -> ImageGenerationJob:
        raise AssertionError("No provider call")

    monkeypatch.setattr(OpenAIImageClient, "generate", forbidden)
    body = _body(timestamp)
    if not change:
        del body["confirm_generation"]
    else:
        body.update(change)
    response = client.post(_path(identifier), headers=_HEADERS, json=body)
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert store.reads == 0
    assert "private-secret" not in response.text


def test_prompt_exact_utf8_limit_and_configured_model(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _store, _repository, identifier, timestamp = api
    seen: list[ImageGenerationRequest] = []

    def generate(_client: OpenAIImageClient, request: ImageGenerationRequest) -> ImageGenerationJob:
        seen.append(request)
        return _success(request)

    monkeypatch.setattr(OpenAIImageClient, "generate", generate)
    prompt = " é" * 2730 + "  "
    assert len(prompt.encode("utf-8")) == 8192
    body = _body(timestamp)
    body["prompt"] = prompt
    assert client.post(_path(identifier), headers=_HEADERS, json=body).status_code == 200
    assert len(seen) == 1
    assert seen[0].prompt == prompt
    assert seen[0].model == "configured-image-model"


def test_security_gate_precedes_secret_and_provider(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, _repository, identifier, timestamp = api
    path = _path(identifier)
    body = _body(timestamp)

    def forbidden(
        _client: OpenAIImageClient, _request: ImageGenerationRequest
    ) -> ImageGenerationJob:
        raise AssertionError("No provider call")

    monkeypatch.setattr(OpenAIImageClient, "generate", forbidden)
    attempts = [
        client.post(path, headers={**_HEADERS, "Host": "evil.example"}, json=body),
        client.post(path, headers={"X-Aurora-Request": "1"}, json=body),
        client.post(path, headers={"Origin": _ORIGIN}, json=body),
        client.post(path, headers={**_HEADERS, "Origin": "null"}, json=body),
        client.post(path, headers={**_HEADERS, "Content-Type": "text/plain"}, content="{}"),
        client.post(
            path,
            headers={**_HEADERS, "Content-Type": "application/json"},
            content="not-json",
        ),
        client.post(
            path,
            headers={**_HEADERS, "Content-Type": "application/json"},
            content=b" " * (2 * 1024 * 1024 + 1),
        ),
    ]
    assert all(item.status_code == 400 for item in attempts)
    assert all(item.json() == {"error": {"code": 400}} for item in attempts)
    assert store.reads == 0


def test_missing_stale_and_invalid_project_precede_secret(
    api: tuple[Client, _Store, ProjectRepository, str, str],
) -> None:
    client, store, repository, identifier, timestamp = api
    for invalid in ["not-a-uuid", identifier.upper()]:
        response = client.post(_path(invalid), headers=_HEADERS, json=_body(timestamp))
        assert response.status_code == 400
    missing = client.post(_path(str(uuid4())), headers=_HEADERS, json=_body(timestamp))
    assert missing.status_code == 404
    current = repository.load(identifier)
    updated = repository.save(ProjectDocument(metadata=current.metadata, state={"note": "new"}))
    assert updated.metadata.updated_at != timestamp
    stale = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert stale.status_code == 409
    assert stale.json() == {"error": {"code": 409}}
    assert store.reads == 0


def test_missing_native_failed_and_invalid_stored_credential(
    api: tuple[Client, _Store, ProjectRepository, str, str],
) -> None:
    client, store, _repository, identifier, timestamp = api
    store.key = None
    missing = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert missing.status_code == 409
    store.fail = True
    native = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert native.status_code == 503
    assert "native-private-error" not in native.text
    store.fail = False
    store.key = "invalid key with spaces"
    invalid = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert invalid.status_code == 503
    assert invalid.json() == {"error": {"code": 503}}
    assert "invalid key" not in invalid.text
    assert store.reads == 3


@pytest.mark.parametrize("failure", ["quota", "signature", "native"])
def test_p1_publication_failure_is_sanitized_and_never_retries_paid_call(
    api: tuple[Client, _Store, ProjectRepository, str, str],
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    client, _store, repository, identifier, timestamp = api
    calls = 0

    def generate(_client: OpenAIImageClient, request: ImageGenerationRequest) -> ImageGenerationJob:
        nonlocal calls
        calls += 1
        return _success(request)

    def broken_write(
        _repository: ProjectRepository, _identifier: str, _data: bytes, _media_type: str
    ) -> str:
        if failure == "quota":
            raise ValidationError("private-capacity-path")
        if failure == "signature":
            raise ValidationError("private-signature-path")
        raise OSError("C:\\private\\asset")

    monkeypatch.setattr(OpenAIImageClient, "generate", generate)
    monkeypatch.setattr(ProjectRepository, "write_asset", broken_write)
    before = repository.load(identifier)
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    expected_status = 500 if failure == "native" else 400
    assert response.status_code == expected_status
    assert response.json() == {"error": {"code": expected_status}}
    assert "private" not in response.text
    assert calls == 1
    assert repository.load(identifier) == before


def test_p1_read_failure_precedes_secret_and_old_routes_remain_available(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, _repository, identifier, timestamp = api

    def broken_load(_repository: ProjectRepository, _identifier: str) -> ProjectDocument:
        raise OSError("C:\\private\\project")

    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get(f"/api/v1/projects/{identifier}").status_code == 200
    monkeypatch.setattr(ProjectRepository, "load", broken_load)
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 500
    assert response.json() == {"error": {"code": 500}}
    assert "private" not in response.text
    assert store.reads == 0
