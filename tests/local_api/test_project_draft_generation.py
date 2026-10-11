"""P6-006 local draft generation security, errors and candidate acceptance."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path
from typing import cast
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.core.types import JSONValue
from src.credentials import CredentialStoreError, SecretName, WindowsCredentialStore
from src.editor import load_editor_state
from src.generation import (
    GenerationFailure,
    GenerationJob,
    GenerationRequest,
    GenerationResult,
    OpenAIResponsesClient,
)
from src.local_api import create_app
from src.projects import ProjectDocument, ProjectRepository

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class _Store(WindowsCredentialStore):
    def __init__(self, key: str | None = "synthetic-key") -> None:
        self.key = key
        self.fail = False
        self.reads = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("No credential writes")

    def get_secret(self, name: SecretName) -> str | None:
        assert name == "openai_api_key"
        self.reads += 1
        if self.fail:
            raise CredentialStoreError("native-private-error")
        return self.key

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("No credential deletion")


@pytest.fixture
def api(tmp_path: Path) -> Iterator[tuple[Client, _Store, ProjectRepository, str, str]]:
    root = tmp_path / "Projects"
    store = _Store()
    repository = ProjectRepository(root)
    current = repository.create("Студия")
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        yield (
            client,
            store,
            repository,
            current.metadata.project_id,
            current.metadata.updated_at,
        )


def _path(identifier: str) -> str:
    return f"/api/v1/projects/{identifier}/generation/draft"


def _body(timestamp: str, *, language: str = "ru") -> dict[str, object]:
    return {
        "business_prompt": "Создай сайт студии",
        "language": language,
        "model": "configured-model",
        "expected_updated_at": timestamp,
        "confirm_generation": True,
    }


def _output(language: str) -> str:
    local = language == "ru"
    return json.dumps(
        {
            "brand": {
                "name": "Студия" if local else "Studio",
                "tagline": "Для вас" if local else "For you",
                "primary_color": "#123456",
                "secondary_color": "#abcdef",
                "font_family": "system",
            },
            "pages": [
                {
                    "slug": "index",
                    "title": "Главная" if local else "Home",
                    "meta_description": "Студия" if local else "Studio",
                    "heading": "Добро пожаловать" if local else "Welcome",
                    "sections": [
                        {"heading": "Услуги" if local else "Services", "body": "Our work"}
                    ],
                }
            ],
        },
        ensure_ascii=False,
    )


def _success(request: GenerationRequest, language: str) -> GenerationJob:
    return GenerationJob(
        job_id="synthetic-job",
        request=request,
        status="completed",
        result=GenerationResult(
            response_id="synthetic-response",
            model=request.model,
            output_text=_output(language),
        ),
    )


@pytest.mark.parametrize("language", ["ru", "en"])
def test_completed_candidate_has_exact_shape_headers_and_no_project_write(
    api: tuple[Client, _Store, ProjectRepository, str, str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    language: str,
) -> None:
    client, store, repository, identifier, timestamp = api
    calls: list[GenerationRequest] = []

    def generate(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        calls.append(request)
        assert request.model == "configured-model"
        assert request.instructions is not None
        assert json.loads(request.prompt) == {
            "project_name": "Студия",
            "business_prompt": "Создай сайт студии",
            "language": language,
        }
        return _success(request, language)

    monkeypatch.setattr(OpenAIResponsesClient, "generate", generate)
    original = repository.load(identifier)
    root = tmp_path / "Projects"
    project_files = sorted(root.rglob("*"))
    before = {path: path.read_bytes() for path in project_files if path.is_file()}
    response = client.post(
        _path(identifier), headers=_HEADERS, json=_body(timestamp, language=language)
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert "access-control-allow-origin" not in response.headers
    candidate = response.json()
    assert set(candidate) == {"job_id", "status", "source_updated_at", "editor", "failure"}
    assert candidate["job_id"] == "synthetic-job"
    assert candidate["status"] == "completed"
    assert candidate["source_updated_at"] == timestamp
    assert candidate["failure"] is None
    editor = load_editor_state({"editor": candidate["editor"]})
    assert editor is not None
    assert editor.language == language
    assert candidate["editor"]["schema_version"] == 1
    assert store.reads == 1
    assert len(calls) == 1
    assert repository.load(identifier) == original
    assert {path: path.read_bytes() for path in project_files if path.is_file()} == before
    assert set(root.rglob("*")) == set(project_files)
    assert "synthetic-key" not in response.text
    assert "Создай сайт студии" not in response.text
    assert "synthetic-response" not in response.text


def test_failed_outcome_is_safe_http_200_without_editor_or_write(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _store, repository, identifier, timestamp = api

    def fail(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        return GenerationJob(
            job_id="failure-job",
            request=request,
            status="failed",
            failure=GenerationFailure(
                category="rate_limited", message="OpenAI rate-limited the request.", retryable=True
            ),
        )

    monkeypatch.setattr(OpenAIResponsesClient, "generate", fail)
    before = repository.load(identifier)
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert response.json() == {
        "job_id": "failure-job",
        "status": "failed",
        "source_updated_at": timestamp,
        "editor": None,
        "failure": {
            "category": "rate_limited",
            "message": "OpenAI rate-limited the request.",
            "retryable": True,
        },
    }
    assert repository.load(identifier) == before


@pytest.mark.parametrize(
    "change",
    [
        {},
        {"confirm_generation": False},
        {"confirm_generation": 1},
        {"confirm_generation": "true"},
        {"business_prompt": None},
        {"business_prompt": " "},
        {"business_prompt": "é" * 4096 + "x"},
        {"business_prompt": 4},
        {"language": "fr"},
        {"model": "  "},
        {"model": 3},
        {"expected_updated_at": 3},
        {"key": "private-secret"},
    ],
)
def test_strict_body_rejected_before_secret_or_provider(
    api: tuple[Client, _Store, ProjectRepository, str, str],
    change: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, store, _repository, identifier, timestamp = api

    def forbidden(_client: OpenAIResponsesClient, _request: GenerationRequest) -> GenerationJob:
        raise AssertionError("Provider must not run")

    monkeypatch.setattr(OpenAIResponsesClient, "generate", forbidden)
    body = _body(timestamp)
    if not change:
        del body["confirm_generation"]
    else:
        body.update(change)
    response = client.post(_path(identifier), headers=_HEADERS, json=body)
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert "private-secret" not in response.text
    assert store.reads == 0


def test_utf8_prompt_boundary_and_unmodified_input(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, _repository, identifier, timestamp = api
    calls: list[str] = []

    def generate(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        calls.append(json.loads(request.prompt)["business_prompt"])
        return _success(request, "ru")

    monkeypatch.setattr(OpenAIResponsesClient, "generate", generate)
    prompt = " é" * 2730 + "  "  # Exactly 8192 UTF-8 bytes; spaces are preserved.
    assert len(prompt.encode()) == 8192
    body = _body(timestamp)
    body["business_prompt"] = prompt
    assert client.post(_path(identifier), headers=_HEADERS, json=body).status_code == 200
    assert calls == [prompt]
    assert store.reads == 1


@pytest.mark.parametrize("identifier", ["not-a-uuid", str(uuid4()).upper()])
def test_invalid_or_noncanonical_id_is_400_before_repository_or_secret(
    api: tuple[Client, _Store, ProjectRepository, str, str], identifier: str
) -> None:
    client, store, _repository, _real_id, timestamp = api
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert store.reads == 0


def test_missing_project_and_stale_timestamp_precedence(
    api: tuple[Client, _Store, ProjectRepository, str, str],
) -> None:
    client, store, repository, identifier, timestamp = api
    missing = client.post(_path(str(uuid4())), headers=_HEADERS, json=_body(timestamp))
    assert missing.status_code == 404
    current = repository.load(identifier)
    repository.save(ProjectDocument(metadata=current.metadata, state={"editor": None}))
    store.fail = True
    stale = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert stale.status_code == 409
    assert stale.json() == {"error": {"code": 409}}
    assert store.reads == 0


def test_missing_malformed_and_valid_editor_precede_credentials(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, repository, identifier, timestamp = api
    store.key = None
    absent = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert absent.status_code == 409
    assert store.reads == 1
    current = repository.load(identifier)
    malformed = repository.save(ProjectDocument(metadata=current.metadata, state={"editor": None}))
    store.fail = True
    rejected = client.post(
        _path(identifier), headers=_HEADERS, json=_body(malformed.metadata.updated_at)
    )
    assert rejected.status_code == 400
    assert store.reads == 1
    store.fail = False
    store.key = "synthetic-key"
    current = repository.load(identifier)
    clean = repository.save(ProjectDocument(metadata=current.metadata, state={}))

    def generate(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
        return _success(request, "ru")

    monkeypatch.setattr(OpenAIResponsesClient, "generate", generate)
    candidate = client.post(
        _path(identifier), headers=_HEADERS, json=_body(clean.metadata.updated_at)
    ).json()
    accepted = client.put(
        f"/api/v1/projects/{identifier}/editor",
        headers=_HEADERS,
        json={
            "editor": candidate["editor"],
            "expected_updated_at": clean.metadata.updated_at,
        },
    )
    assert accepted.status_code == 200
    before = store.reads
    store.fail = True
    again = client.post(
        _path(identifier),
        headers=_HEADERS,
        json=_body(accepted.json()["metadata"]["updated_at"]),
    )
    assert again.status_code == 409
    assert store.reads == before


def test_native_credential_failure_and_invalid_stored_key_are_503(
    api: tuple[Client, _Store, ProjectRepository, str, str],
) -> None:
    client, store, _repository, identifier, timestamp = api
    store.fail = True
    native = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert native.status_code == 503
    assert native.json() == {"error": {"code": 503}}
    assert "native-private-error" not in native.text
    store.fail = False
    store.key = "invalid key with spaces"
    invalid = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert invalid.status_code == 503
    assert invalid.json() == {"error": {"code": 503}}
    assert "invalid key" not in invalid.text


@pytest.mark.parametrize("editor", [None, {"schema_version": 2}])
def test_invalid_existing_editor_never_reads_secret(
    api: tuple[Client, _Store, ProjectRepository, str, str], editor: JSONValue
) -> None:
    client, store, repository, identifier, _timestamp = api
    current = repository.load(identifier)
    updated = repository.save(ProjectDocument(metadata=current.metadata, state={"editor": editor}))
    store.fail = True
    response = client.post(
        _path(identifier), headers=_HEADERS, json=_body(updated.metadata.updated_at)
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert store.reads == 0


def test_p1_native_read_failure_is_sanitized_500(
    api: tuple[Client, _Store, ProjectRepository, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, store, _repository, identifier, timestamp = api

    def broken_load(_repository: ProjectRepository, _identifier: str) -> ProjectDocument:
        raise OSError("C:\\private\\native-project")

    monkeypatch.setattr(ProjectRepository, "load", broken_load)
    response = client.post(_path(identifier), headers=_HEADERS, json=_body(timestamp))
    assert response.status_code == 500
    assert response.json() == {"error": {"code": 500}}
    assert "private" not in response.text
    assert store.reads == 0


def test_project_name_limit_comes_from_p1_before_credential(
    api: tuple[Client, _Store, ProjectRepository, str, str],
) -> None:
    client, store, repository, identifier, _timestamp = api
    current = repository.load(identifier)
    oversized = repository.save(
        ProjectDocument(metadata=replace(current.metadata, name="é" * 129), state={})
    )
    response = client.post(
        _path(identifier), headers=_HEADERS, json=_body(oversized.metadata.updated_at)
    )
    assert response.status_code == 400
    assert store.reads == 0


def test_existing_unrelated_routes_are_unchanged(
    api: tuple[Client, _Store, ProjectRepository, str, str],
) -> None:
    client, _store, _repository, identifier, _timestamp = api
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get(f"/api/v1/projects/{identifier}").status_code == 200
    assert client.post("/api/v1/generation/text", headers=_HEADERS, json={}).status_code == 400
