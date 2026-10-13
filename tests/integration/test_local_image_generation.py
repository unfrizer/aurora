"""P2/P3 image attempt through P6 into P1, without live provider calls."""

from __future__ import annotations

from pathlib import Path
from threading import Event, Thread
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.generation import (
    ImageGenerationJob,
    ImageGenerationRequest,
    ImageGenerationResult,
    OpenAIImageClient,
)
from src.local_api import create_app
from src.projects import ProjectRepository

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_PNG = b"\x89PNG\r\n\x1a\nsynthetic-integration-image"
_JOB_ID = "a0000000-0000-4000-8000-000000000002"


class _Store(WindowsCredentialStore):
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
        "prompt": "A calm studio scene",
        "model": "configured-image-model",
        "expected_updated_at": timestamp,
        "confirm_generation": True,
    }


def _success(request: ImageGenerationRequest) -> ImageGenerationJob:
    return ImageGenerationJob(_JOB_ID, request, "completed", result=ImageGenerationResult(_PNG))


def test_intervening_save_preserves_generated_asset_but_stale_attachment_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "Projects"
    repository = ProjectRepository(root)
    initial = repository.create("Studio")
    identifier = initial.metadata.project_id
    source_timestamp = initial.metadata.updated_at
    app = create_app(project_root=root, credential_store=_Store(), allowed_origin=_ORIGIN)
    mutated = Event()
    mutation_status: list[int] = []
    calls = 0

    with (
        cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client,
        cast(
            Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)
        ) as editor_client,
    ):

        def generate(
            _client: OpenAIImageClient, request: ImageGenerationRequest
        ) -> ImageGenerationJob:
            nonlocal calls
            calls += 1

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
                mutated.set()

            worker = Thread(target=change_project, daemon=True)
            worker.start()
            assert mutated.wait(timeout=5), "Project lock was held during provider work"
            worker.join(timeout=1)
            return _success(request)

        monkeypatch.setattr(OpenAIImageClient, "generate", generate)
        response = client.post(
            f"/api/v1/projects/{identifier}/generation/image",
            headers=_HEADERS,
            json=_body(source_timestamp),
        )
        assert response.status_code == 200
        assert mutation_status == [200]
        assert calls == 1
        payload = response.json()
        assert payload["source_updated_at"] == source_timestamp
        assert payload["status"] == "completed"
        assert isinstance(payload["asset_path"], str)
        assert repository.read_asset(identifier, payload["asset_path"]) == _PNG
        assert repository.load(identifier).state == {"note": "changed while generating"}
        stale = client.put(
            f"/api/v1/projects/{identifier}/editor",
            headers=_HEADERS,
            json={"editor": {}, "expected_updated_at": source_timestamp},
        )
        assert stale.status_code == 409
        assert stale.json() == {"error": {"code": 409}}


def test_project_deleted_during_paid_attempt_does_not_publish_asset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "Projects"
    repository = ProjectRepository(root)
    initial = repository.create("Studio")
    identifier = initial.metadata.project_id
    app = create_app(project_root=root, credential_store=_Store(), allowed_origin=_ORIGIN)
    deleted = Event()
    delete_status: list[int] = []
    calls = 0

    with (
        cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client,
        cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as deleter,
    ):

        def generate(
            _client: OpenAIImageClient, request: ImageGenerationRequest
        ) -> ImageGenerationJob:
            nonlocal calls
            calls += 1

            def delete_project() -> None:
                response = deleter.delete(f"/api/v1/projects/{identifier}", headers=_HEADERS)
                delete_status.append(response.status_code)
                deleted.set()

            worker = Thread(target=delete_project, daemon=True)
            worker.start()
            assert deleted.wait(timeout=5), "Project lock was held during provider work"
            worker.join(timeout=1)
            return _success(request)

        monkeypatch.setattr(OpenAIImageClient, "generate", generate)
        response = client.post(
            f"/api/v1/projects/{identifier}/generation/image",
            headers=_HEADERS,
            json=_body(initial.metadata.updated_at),
        )
        assert response.status_code == 404
        assert response.json() == {"error": {"code": 404}}
        assert calls == 1
        assert delete_status == [204]
        assert not repository.list()
