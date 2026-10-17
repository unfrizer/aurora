"""Launcher composes the approved P8 store with P6 without profile side effects."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.launcher import create_desktop_app
from src.preferences import PreferencesStore

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class NoCredentials(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        self.calls += 1
        raise AssertionError("Unexpected credential use")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls += 1
        raise AssertionError("Unexpected credential use")

    def delete_secret(self, name: SecretName) -> bool:
        self.calls += 1
        raise AssertionError("Unexpected credential use")


def _ui(tmp_path: Path) -> Path:
    root = tmp_path / "frontend" / "dist"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<html>local</html>", encoding="utf-8")
    return root


def test_injected_preferences_roundtrip_across_desktop_instances(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    path = tmp_path / "LocalAppData" / "AURORA" / "settings.json"
    path.parent.parent.mkdir()
    ui_root = _ui(tmp_path)
    credentials = NoCredentials()

    def client() -> TestClient:
        app = create_desktop_app(
            project_root=root,
            credential_store=credentials,
            allowed_origin=_ORIGIN,
            ui_root=ui_root,
            preferences_store=PreferencesStore(path),
        )
        return TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)

    assert not path.exists()
    with cast(Client, client()) as first:
        assert first.get("/").text == "<html>local</html>"
        current = first.get("/api/v1/preferences")
        assert current.status_code == 200
        assert current.json()["projects_directory"] == str(root)
        assert not path.exists()
        proposed = {**current.json()["preferences"], "language": "ru"}
        bad = first.put(
            "/api/v1/preferences",
            json={"preferences": proposed, "expected_revision": current.json()["revision"]},
        )
        assert bad.status_code == 400
        saved = first.put(
            "/api/v1/preferences",
            headers=_HEADERS,
            json={"preferences": proposed, "expected_revision": current.json()["revision"]},
        )
        assert saved.status_code == 200
        assert "projects_directory" not in saved.json()

    with cast(Client, client()) as second:
        reopened = second.get("/api/v1/preferences")
        assert reopened.json()["preferences"] == proposed
        assert reopened.json()["revision"] == saved.json()["revision"]
        assert (
            second.get("/api/v1/preferences", headers={"Host": "other.invalid"}).status_code == 400
        )
    assert not root.exists()
    assert credentials.calls == 0
