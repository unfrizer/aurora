"""P1 → P7 → P4 → P6 preview composition across an app reopen."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.editor import load_editor_state, to_static_site_document
from src.local_api import create_app
from src.projects import ProjectRepository
from src.site_export import StaticSiteAsset, StaticSiteBuilder

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_IMAGE = b"\x89PNG\r\n\x1a\nsynthetic-preview"


class EmptyStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        self.calls += 1
        raise AssertionError("Unexpected credential write")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls += 1
        raise AssertionError("Unexpected credential read")

    def delete_secret(self, name: SecretName) -> bool:
        self.calls += 1
        raise AssertionError("Unexpected credential delete")


def _editor(reference: str, heading: str) -> dict[str, object]:
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
                "meta_description": "Предпросмотр",
                "heading": heading,
                "sections": [
                    {
                        "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        "heading": "Работы",
                        "body": "Наши проекты",
                        "image_path": reference,
                        "image_alt": "Проект",
                    }
                ],
            }
        ],
    }


def test_create_save_preview_reopen_and_rebuild_from_latest_editor(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    store = EmptyStore()
    first = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(first, base_url=_ORIGIN)) as client:
        created = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Студия"})
        assert created.status_code == 201
        project_id = created.json()["metadata"]["project_id"]
        uploaded = client.post(
            f"/api/v1/projects/{project_id}/assets",
            headers={**_HEADERS, "Content-Type": "image/png"},
            content=_IMAGE,
        )
        assert uploaded.status_code == 201
        reference = uploaded.json()["path"]
        saved = client.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={
                "editor": _editor(reference, "Первый заголовок"),
                "expected_updated_at": created.json()["metadata"]["updated_at"],
            },
        )
        assert saved.status_code == 200
        prefix = f"/api/v1/projects/{project_id}/preview/"
        first_html = client.get(prefix + "index.html")
        assert first_html.status_code == 200
        assert "Первый заголовок" in first_html.text
        first_css = client.get(prefix + "assets/site.css")
        first_image = client.get(prefix + reference)
        assert first_css.status_code == first_image.status_code == 200
        assert first_image.content == _IMAGE
        before_preview = ProjectRepository(root).load(project_id)

    second = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(second, base_url=_ORIGIN)) as client:
        reopened = client.get(f"/api/v1/projects/{project_id}")
        assert reopened.status_code == 200
        assert reopened.json()["state"]["editor"] == _editor(reference, "Первый заголовок")
        assert client.get(prefix + "index.html").content == first_html.content
        assert client.get(prefix + "assets/site.css").content == first_css.content
        assert client.get(prefix + reference).content == _IMAGE
        assert ProjectRepository(root).load(project_id) == before_preview
        updated = client.put(
            f"/api/v1/projects/{project_id}/editor",
            headers=_HEADERS,
            json={
                "editor": _editor(reference, "Новый заголовок"),
                "expected_updated_at": reopened.json()["metadata"]["updated_at"],
            },
        )
        assert updated.status_code == 200
        rebuilt = client.get(prefix + "index.html")
        assert rebuilt.status_code == 200
        assert "Новый заголовок" in rebuilt.text
        assert rebuilt.content != first_html.content
        assert client.get(prefix + "assets/site.css").content == first_css.content
        assert client.get(prefix + reference).content == _IMAGE

    repository = ProjectRepository(root)
    document = repository.load(project_id)
    editor = load_editor_state(document.state)
    assert editor is not None
    asset = StaticSiteAsset(path=reference, data=repository.read_asset(project_id, reference))
    build = StaticSiteBuilder().build(to_static_site_document(editor, (asset,)))
    expected = {item.path: item.data for item in build.files}
    assert rebuilt.content == expected["index.html"]
    assert first_css.content == expected["assets/site.css"]
    assert expected[reference] == _IMAGE
    project_directory = next(root.iterdir())
    assert list((project_directory / "site").iterdir()) == []
    assert list((project_directory / "exports").iterdir()) == []
    assert store.calls == 0
