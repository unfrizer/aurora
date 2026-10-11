"""P1/P2/P3/PG/P7/P4 through P6 with a synthetic provider and no live effects."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Event, Thread
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.editor import load_editor_state, to_static_site_document
from src.generation import GenerationJob, GenerationRequest, GenerationResult, OpenAIResponsesClient
from src.local_api import create_app
from src.projects import ProjectRepository
from src.site_export import StaticSiteBuilder

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class _SyntheticStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.reads = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("No real credential write")

    def get_secret(self, name: SecretName) -> str | None:
        assert name == "openai_api_key"
        self.reads += 1
        return "synthetic-key"

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("No real credential delete")


def _body(timestamp: str) -> dict[str, object]:
    return {
        "business_prompt": "Make a design studio site",
        "language": "en",
        "model": "configured-model",
        "expected_updated_at": timestamp,
        "confirm_generation": True,
    }


def _success(request: GenerationRequest) -> GenerationJob:
    return GenerationJob(
        job_id="integration-job",
        request=request,
        status="completed",
        result=GenerationResult(
            response_id="integration-response",
            model=request.model,
            output_text=json.dumps(
                {
                    "brand": {
                        "name": "Studio",
                        "tagline": "Thoughtful design",
                        "primary_color": "#123456",
                        "secondary_color": "#abcdef",
                        "font_family": "system",
                    },
                    "pages": [
                        {
                            "slug": "index",
                            "title": "Studio Home",
                            "meta_description": "A design studio",
                            "heading": "Welcome",
                            "sections": [{"heading": "Services", "body": "Our design work"}],
                        }
                    ],
                }
            ),
        ),
    )


def test_origin_body_gates_precede_secret_and_paid_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "Projects"
    current = ProjectRepository(root).create("Studio")
    store = _SyntheticStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    path = f"/api/v1/projects/{current.metadata.project_id}/generation/draft"
    calls = 0

    def forbidden(_client: OpenAIResponsesClient, _request: GenerationRequest) -> GenerationJob:
        nonlocal calls
        calls += 1
        raise AssertionError("Provider must not run")

    monkeypatch.setattr(OpenAIResponsesClient, "generate", forbidden)
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        body = _body(current.metadata.updated_at)
        responses = [
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
    assert all(response.status_code == 400 for response in responses)
    assert all(response.json() == {"error": {"code": 400}} for response in responses)
    assert store.reads == 0
    assert calls == 0


def test_provider_work_releases_lock_and_stale_candidate_cannot_be_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "Projects"
    repository = ProjectRepository(root)
    initial = repository.create("Studio")
    identifier = initial.metadata.project_id
    source_timestamp = initial.metadata.updated_at
    store = _SyntheticStore()
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    path = f"/api/v1/projects/{identifier}/generation/draft"
    mutation_done = Event()
    mutation_status: list[int] = []
    provider_calls = 0

    with (
        cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client,
        cast(
            Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)
        ) as editor_client,
    ):

        def generate(_client: OpenAIResponsesClient, request: GenerationRequest) -> GenerationJob:
            nonlocal provider_calls
            provider_calls += 1

            def change_project() -> None:
                response = editor_client.put(
                    f"/api/v1/projects/{identifier}",
                    headers=_HEADERS,
                    json={
                        "name": "Studio",
                        "state": {"note": "changed while generating"},
                        "expected_updated_at": source_timestamp,
                    },
                )
                mutation_status.append(response.status_code)
                mutation_done.set()

            worker = Thread(target=change_project, daemon=True)
            worker.start()
            assert mutation_done.wait(timeout=5), "Project lock was held during provider work"
            worker.join(timeout=1)
            return _success(request)

        monkeypatch.setattr(OpenAIResponsesClient, "generate", generate)
        response = client.post(path, headers=_HEADERS, json=_body(source_timestamp))
        assert response.status_code == 200
        candidate = response.json()
        assert mutation_status == [200]
        assert provider_calls == 1
        assert store.reads == 1
        assert candidate["source_updated_at"] == source_timestamp
        assert candidate["status"] == "completed"
        editor = load_editor_state({"editor": candidate["editor"]})
        assert editor is not None
        build = StaticSiteBuilder().build(to_static_site_document(editor, ()))
        assert {site_file.path for site_file in build.files} == {"assets/site.css", "index.html"}
        stale_acceptance = client.put(
            f"/api/v1/projects/{identifier}/editor",
            headers=_HEADERS,
            json={"editor": candidate["editor"], "expected_updated_at": source_timestamp},
        )
        assert stale_acceptance.status_code == 409
        assert stale_acceptance.json() == {"error": {"code": 409}}
        assert repository.load(identifier).state == {"note": "changed while generating"}
        assert repository.load(identifier).metadata.updated_at != source_timestamp
