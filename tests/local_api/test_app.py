"""Behavioral acceptance for the approved local API routes."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import CredentialStoreError, SecretName, WindowsCredentialStore
from src.generation import (
    GenerationConfigurationError,
    GenerationFailure,
    GenerationJob,
    GenerationRequest,
    GenerationResult,
    OpenAIResponsesClient,
)
from src.local_api import create_app
from src.projects import ProjectMetadata, ProjectRepository

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class FakeStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.fail = False

    def set_secret(self, name: SecretName, secret: str) -> None:
        if self.fail:
            raise CredentialStoreError("sensitive-native-error")
        self.values[name] = secret

    def get_secret(self, name: SecretName) -> str | None:
        if self.fail:
            raise CredentialStoreError("sensitive-native-error")
        return self.values.get(name)

    def delete_secret(self, name: SecretName) -> bool:
        if self.fail:
            raise CredentialStoreError("sensitive-native-error")
        return self.values.pop(name, None) is not None


@pytest.fixture
def api(tmp_path: Path) -> Iterator[tuple[Client, FakeStore, Path]]:
    store = FakeStore()
    app = create_app(
        project_root=tmp_path / "Projects", credential_store=store, allowed_origin=_ORIGIN
    )
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        yield client, store, tmp_path / "Projects"


def test_health_and_exact_route_surface(api: tuple[Client, FakeStore, Path]) -> None:
    client, _store, _root = api
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get("/health").status_code == 404
    assert client.get("/health").json() == {"error": {"code": 404}}
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/api/v1/projects").json() == []


def test_project_create_save_reopen_list_delete(api: tuple[Client, FakeStore, Path]) -> None:
    client, _store, root = api
    created = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "  Studio  "})
    assert created.status_code == 201
    document = created.json()
    project_id = document["metadata"]["project_id"]
    assert document["metadata"]["name"] == "Studio"
    assert document["state"] == {}
    assert len(client.get("/api/v1/projects").json()) == 1
    assert client.get(f"/api/v1/projects/{project_id}").json() == document

    saved = client.put(
        f"/api/v1/projects/{project_id}",
        headers=_HEADERS,
        json={
            "name": "New Studio",
            "state": {"brand": {"name": "AURORA"}, "pages": ["index"]},
            "expected_updated_at": document["metadata"]["updated_at"],
        },
    )
    assert saved.status_code == 200
    updated = saved.json()
    assert updated["metadata"]["name"] == "New Studio"
    assert updated["metadata"]["created_at"] == document["metadata"]["created_at"]
    assert updated["state"]["brand"]["name"] == "AURORA"
    assert ProjectRepository(root).load(project_id).state["pages"] == ["index"]
    assert client.get(f"/api/v1/projects/{project_id}").json() == updated

    stale = client.put(
        f"/api/v1/projects/{project_id}",
        headers=_HEADERS,
        json={
            "name": "Stale",
            "state": {},
            "expected_updated_at": "2000-01-01T00:00:00+00:00",
        },
    )
    assert stale.status_code == 409
    assert stale.json() == {"error": {"code": 409}}
    assert ProjectRepository(root).load(project_id).metadata.name == "New Studio"

    removed = client.delete(f"/api/v1/projects/{project_id}", headers=_HEADERS)
    assert removed.status_code == 204
    assert removed.content == b""
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
    assert client.get("/api/v1/projects").json() == []


def test_invalid_projects_are_sanitized_and_non_mutating(
    api: tuple[Client, FakeStore, Path],
) -> None:
    client, _store, root = api
    assert client.post("/api/v1/projects", headers=_HEADERS, json={"name": " "}).status_code == 400
    assert client.get("/api/v1/projects/not-a-uuid").json() == {"error": {"code": 400}}
    assert client.delete("/api/v1/projects/not-a-uuid", headers=_HEADERS).status_code == 400
    assert client.get("/api/v1/projects").json() == []
    assert not root.exists()

    created = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Clean"}).json()
    project_id = created["metadata"]["project_id"]
    bad_state = {
        "name": "Clean",
        "state": {"nested": [{"OpenAI_API_Key": "never-persist"}]},
        "expected_updated_at": created["metadata"]["updated_at"],
    }
    rejected = client.put(f"/api/v1/projects/{project_id}", headers=_HEADERS, json=bad_state)
    assert rejected.status_code == 400
    assert "never-persist" not in rejected.text
    assert ProjectRepository(root).load(project_id).state == {}


def test_credentials_have_presence_and_write_only_http_surface(
    api: tuple[Client, FakeStore, Path],
) -> None:
    client, store, _root = api
    path = "/api/v1/credentials/openai_api_key"
    assert client.get(path + "/status").json() == {"configured": False}
    stored = client.put(path, headers=_HEADERS, json={"secret": "synthetic-key"})
    assert stored.status_code == 204
    assert stored.content == b""
    assert store.values["openai_api_key"] == "synthetic-key"
    assert client.get(path + "/status").json() == {"configured": True}
    assert client.get(path).status_code == 405
    assert client.get(path + "/status").text.find("synthetic-key") == -1
    assert client.delete(path, headers=_HEADERS).status_code == 204
    assert client.delete(path, headers=_HEADERS).status_code == 204
    assert client.get(path + "/status").json() == {"configured": False}
    assert (
        client.put("/api/v1/credentials/other", headers=_HEADERS, json={"secret": "x"}).status_code
        == 400
    )


def test_native_errors_and_framework_validation_never_echo_input(
    api: tuple[Client, FakeStore, Path],
) -> None:
    client, store, _root = api
    store.fail = True
    response = client.put(
        "/api/v1/credentials/openai_api_key", headers=_HEADERS, json={"secret": "synthetic-secret"}
    )
    assert response.status_code == 503
    assert response.json() == {"error": {"code": 503}}
    assert "synthetic-secret" not in response.text
    assert "sensitive-native-error" not in response.text
    invalid = client.put(
        "/api/v1/credentials/openai_api_key",
        headers=_HEADERS,
        json={"secret": "synthetic-secret", "unexpected": "sensitive-prompt"},
    )
    assert invalid.status_code == 400
    assert invalid.json() == {"error": {"code": 400}}
    assert "sensitive" not in invalid.text


def test_text_generation_projects_only_terminal_result(
    api: tuple[Client, FakeStore, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, _root = api
    request_path = "/api/v1/generation/text"
    payload = {"model": "sample-model", "prompt": "private prompt", "instructions": "private rule"}
    assert client.post(request_path, headers=_HEADERS, json=payload).status_code == 409
    store.values["openai_api_key"] = "synthetic-key"

    def succeed(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        assert request.prompt == "private prompt"
        return GenerationJob(
            job_id="synthetic-job",
            request=request,
            status="completed",
            result=GenerationResult(
                response_id="synthetic-response", model=request.model, output_text="safe output"
            ),
        )

    monkeypatch.setattr(OpenAIResponsesClient, "generate", succeed)
    result = client.post(request_path, headers=_HEADERS, json=payload)
    assert result.status_code == 200
    assert result.json() == {
        "job_id": "synthetic-job",
        "status": "completed",
        "result": {
            "response_id": "synthetic-response",
            "model": "sample-model",
            "output_text": "safe output",
        },
        "failure": None,
    }
    assert "private prompt" not in result.text
    assert "synthetic-key" not in result.text

    def fail(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        return GenerationJob(
            job_id="failed-job",
            request=request,
            status="failed",
            failure=GenerationFailure(
                category="rate_limited", message="Try again later.", retryable=True
            ),
        )

    monkeypatch.setattr(OpenAIResponsesClient, "generate", fail)
    failure = client.post(request_path, headers=_HEADERS, json=payload)
    assert failure.status_code == 200
    assert failure.json()["status"] == "failed"
    assert failure.json()["result"] is None
    assert failure.json()["failure"]["category"] == "rate_limited"
    assert "private prompt" not in failure.text


def test_local_generation_validation_and_project_io_errors_are_safe(
    api: tuple[Client, FakeStore, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, _root = api
    store.values["openai_api_key"] = "synthetic-key"
    invalid = client.post(
        "/api/v1/generation/text", headers=_HEADERS, json={"model": "", "prompt": "secret"}
    )
    assert invalid.status_code == 400
    assert "secret" not in invalid.text

    def configuration_error(
        _client: OpenAIResponsesClient, _request: GenerationRequest
    ) -> GenerationJob:
        raise GenerationConfigurationError("private-configuration")

    monkeypatch.setattr(OpenAIResponsesClient, "generate", configuration_error)
    response = client.post(
        "/api/v1/generation/text",
        headers=_HEADERS,
        json={"model": "sample-model", "prompt": "secret"},
    )
    assert response.json() == {"error": {"code": 400}}
    assert "private-configuration" not in response.text

    def broken_list(_repository: ProjectRepository) -> tuple[ProjectMetadata, ...]:
        raise OSError("C:\\private\\project")

    monkeypatch.setattr(ProjectRepository, "list", broken_list)
    listing = client.get("/api/v1/projects")
    assert listing.json() == {"error": {"code": 500}}
    assert "private" not in listing.text
