"""Public HTTP composition of P6, P7 and P1 across application reopen."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app
from src.projects import ProjectRepository

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class EmptyStore(WindowsCredentialStore):
    def __init__(self) -> None:
        pass

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("Unexpected credential write")

    def get_secret(self, name: SecretName) -> str | None:
        raise AssertionError("Unexpected credential read")

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("Unexpected credential delete")


def _editor(reference: str | None) -> dict[str, object]:
    return {
        "schema_version": 1,
        "language": "ru",
        "brand": {
            "name": "Студия",
            "tagline": "Идеи",
            "primary_color": "#4F46E5",
            "secondary_color": "#0F172A",
            "font_family": "system",
            "logo_path": reference,
        },
        "pages": [
            {
                "id": "37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                "slug": "index",
                "title": "Главная",
                "meta_description": "Студия",
                "heading": "Добро пожаловать",
                "sections": [
                    {
                        "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        "heading": "Работы",
                        "body": "Наши работы",
                        "image_path": reference,
                        "image_alt": "Пример" if reference else "",
                    }
                ],
            }
        ],
    }


def test_create_upload_editor_save_reopen_dereference_and_delete(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    store = EmptyStore()
    image = b"\x89PNG\r\n\x1a\nsynthetic-integration"
    first = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(first, base_url=_ORIGIN)) as client:
        created = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Студия"})
        assert created.status_code == 201
        project = created.json()
        project_id = project["metadata"]["project_id"]
        uploaded = client.post(
            f"/api/v1/projects/{project_id}/assets",
            headers={**_HEADERS, "Content-Type": "image/png"},
            content=image,
        )
        assert uploaded.status_code == 201
        reference = uploaded.json()["path"]
        saved = client.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={
                "editor": _editor(reference),
                "expected_updated_at": project["metadata"]["updated_at"],
            },
        )
        assert saved.status_code == 200
        assert saved.json()["state"]["editor"] == _editor(reference)

    second = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(second, base_url=_ORIGIN)) as client:
        reopened = client.get(f"/api/v1/projects/{project_id}")
        assert reopened.status_code == 200
        assert reopened.json()["state"]["editor"] == _editor(reference)
        asset_url = f"/api/v1/projects/{project_id}/{reference}"
        assert client.get(asset_url).content == image
        assert client.delete(asset_url, headers=_HEADERS).status_code == 400
        detached = client.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={
                "editor": _editor(None),
                "expected_updated_at": reopened.json()["metadata"]["updated_at"],
            },
        )
        assert detached.status_code == 200
        assert client.delete(asset_url, headers=_HEADERS).status_code == 204
        assert client.get(asset_url).status_code == 404
        assert client.get(f"/api/v1/projects/{project_id}").json()["state"]["editor"] == _editor(
            None
        )
    assert ProjectRepository(root).load(project_id).state["editor"] == _editor(None)
