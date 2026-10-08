"""Real project reopening through two local API instances, with no live providers."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class EmptyStore(WindowsCredentialStore):
    def __init__(self) -> None:
        pass

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("No real credential write in integration test")

    def get_secret(self, name: SecretName) -> str | None:
        return None

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("No real credential delete in integration test")


def test_create_save_close_reopen_via_new_api_instance(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    store = EmptyStore()
    first = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(first, base_url=_ORIGIN)) as client:
        created = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Example"})
        assert created.status_code == 201
        document = created.json()
        project_id = document["metadata"]["project_id"]
        saved = client.put(
            f"/api/v1/projects/{project_id}",
            headers=_HEADERS,
            json={
                "name": "Example",
                "state": {"language": "ru", "site": {"pages": ["index"]}},
                "expected_updated_at": document["metadata"]["updated_at"],
            },
        )
        assert saved.status_code == 200
        final = saved.json()

    second = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(second, base_url=_ORIGIN)) as client:
        assert client.get(f"/api/v1/projects/{project_id}").json() == final
        assert client.get("/api/v1/projects").json()[0]["project_id"] == project_id
    assert (root / f"example-{project_id}" / "state.json").is_file()
