"""Preferences survive API reconstruction without affecting sibling projects."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app
from src.preferences import PreferencesStore

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class NoCredentials(WindowsCredentialStore):
    def __init__(self) -> None:
        pass

    def set_secret(self, name: SecretName, secret: str) -> None:
        raise AssertionError("No credential access")

    def get_secret(self, name: SecretName) -> str | None:
        raise AssertionError("No credential access")

    def delete_secret(self, name: SecretName) -> bool:
        raise AssertionError("No credential access")


def test_preferences_survive_new_api_instance_without_project_mutation(tmp_path: Path) -> None:
    project_root = tmp_path / "Projects"
    project_root.mkdir()
    sentinel = project_root / "existing-project.txt"
    sentinel.write_bytes(b"untouched project")
    settings_path = tmp_path / "Settings" / "settings.json"
    credentials = NoCredentials()
    first = create_app(
        project_root=project_root,
        credential_store=credentials,
        allowed_origin=_ORIGIN,
        preferences_store=PreferencesStore(settings_path),
    )
    with cast(Client, TestClient(first, base_url=_ORIGIN)) as client:
        current = client.get("/api/v1/preferences").json()
        proposed = {**current["preferences"], "language": "en", "onboarding_completed": True}
        response = client.put(
            "/api/v1/preferences",
            headers=_HEADERS,
            json={"preferences": proposed, "expected_revision": current["revision"]},
        )
        assert response.status_code == 200
        saved = response.json()
    second = create_app(
        project_root=project_root,
        credential_store=credentials,
        allowed_origin=_ORIGIN,
        preferences_store=PreferencesStore(settings_path),
    )
    with cast(Client, TestClient(second, base_url=_ORIGIN)) as client:
        reopened = client.get("/api/v1/preferences")
        assert reopened.status_code == 200
        assert reopened.json()["preferences"] == proposed
        assert reopened.json()["revision"] == saved["revision"]
        assert reopened.json()["projects_directory"] == str(project_root)
    assert sentinel.read_bytes() == b"untouched project"
