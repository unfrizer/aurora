"""P6 preferences HTTP boundary with injected temporary storage."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app
from src.preferences import PreferencesStore, UserPreferences

_ORIGIN = "http://127.0.0.1:8765"
_PATH = "/api/v1/preferences"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}


class EmptyCredentials(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        self.calls += 1
        raise AssertionError("Credentials must not be used")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls += 1
        raise AssertionError("Credentials must not be used")

    def delete_secret(self, name: SecretName) -> bool:
        self.calls += 1
        raise AssertionError("Credentials must not be used")


@pytest.fixture
def preferences_api(tmp_path: Path) -> tuple[Client, Path, Path, EmptyCredentials]:
    project_root = tmp_path / "Projects"
    settings_path = tmp_path / "Settings" / "settings.json"
    credentials = EmptyCredentials()
    app = create_app(
        project_root=project_root,
        credential_store=credentials,
        allowed_origin=_ORIGIN,
        preferences_store=PreferencesStore(settings_path),
    )
    assert not settings_path.exists()
    assert not project_root.exists()
    return (
        cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)),
        settings_path,
        project_root,
        credentials,
    )


def test_defaults_get_is_read_only_and_path_is_server_owned(
    preferences_api: tuple[Client, Path, Path, EmptyCredentials],
) -> None:
    client, settings_path, project_root, credentials = preferences_api
    with client:
        response = client.get(_PATH)
    assert response.status_code == 200
    assert response.json() == {
        "preferences": asdict(UserPreferences()),
        "revision": response.json()["revision"],
        "projects_directory": str(project_root),
    }
    assert len(response.json()["revision"]) == 64
    for key, value in {
        "cache-control": "no-store",
        "x-content-type-options": "nosniff",
        "cross-origin-resource-policy": "same-origin",
        "referrer-policy": "no-referrer",
    }.items():
        assert response.headers[key] == value
    assert "access-control-allow-origin" not in response.headers
    assert not settings_path.exists()
    assert not project_root.exists()
    assert credentials.calls == 0


def test_confirmed_put_reopens_and_rejects_stale_revision(
    preferences_api: tuple[Client, Path, Path, EmptyCredentials],
) -> None:
    client, settings_path, project_root, credentials = preferences_api
    with client:
        original = client.get(_PATH).json()
        proposed = {
            "schema_version": 1,
            "language": "ru",
            "general_model": "custom-text",
            "image_model": "custom-image",
            "onboarding_completed": True,
        }
        body = {"preferences": proposed, "expected_revision": original["revision"]}
        saved = client.put(_PATH, headers=_HEADERS, json=body)
        assert saved.status_code == 200
        assert saved.json()["preferences"] == proposed
        assert "projects_directory" not in saved.json()
        assert saved.json()["revision"] != original["revision"]
        assert saved.headers["cache-control"] == "no-store"
        old_bytes = settings_path.read_bytes()
        stale = client.put(_PATH, headers=_HEADERS, json=body)
        assert stale.status_code == 409
        assert stale.json() == {"error": {"code": 409}}
        assert settings_path.read_bytes() == old_bytes
        assert client.get(_PATH).json()["revision"] == saved.json()["revision"]
    assert asdict(PreferencesStore(settings_path).load()) == proposed
    assert not project_root.exists()
    assert credentials.calls == 0


@pytest.mark.parametrize(
    "change",
    [
        {"projects_directory": "C:/stolen"},
        {"preferences": {**asdict(UserPreferences()), "api_key": "secret"}},
        {"preferences": {**asdict(UserPreferences()), "schema_version": True}},
        {"preferences": {**asdict(UserPreferences()), "language": "fr"}},
        {"preferences": {**asdict(UserPreferences()), "general_model": ""}},
        {"expected_revision": "not-a-revision"},
    ],
)
def test_invalid_put_does_not_write(
    preferences_api: tuple[Client, Path, Path, EmptyCredentials], change: dict[str, object]
) -> None:
    client, settings_path, _root, credentials = preferences_api
    with client:
        revision = client.get(_PATH).json()["revision"]
        body = {"preferences": asdict(UserPreferences()), "expected_revision": revision}
        body.update(change)
        response = client.put(_PATH, headers=_HEADERS, json=body)
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert "secret" not in response.text
    assert not settings_path.exists()
    assert credentials.calls == 0


def test_request_gates_precede_effect(
    preferences_api: tuple[Client, Path, Path, EmptyCredentials],
) -> None:
    client, settings_path, _root, credentials = preferences_api
    with client:
        revision = client.get(_PATH).json()["revision"]
        body = {"preferences": asdict(UserPreferences()), "expected_revision": revision}
        attempts = [
            client.put(_PATH, headers={"Host": "evil.example", **_HEADERS}, json=body),
            client.put(_PATH, headers={"X-Aurora-Request": "1"}, json=body),
            client.put(_PATH, headers={"Origin": _ORIGIN}, json=body),
            client.put(_PATH, headers={"Origin": "null", "X-Aurora-Request": "1"}, json=body),
            client.put(_PATH, headers={**_HEADERS, "Content-Type": "text/plain"}, content="x"),
            client.put(_PATH, headers=_HEADERS, content=b"x" * (2 * 1024 * 1024 + 1)),
        ]
        bad_get = client.get(_PATH, headers={"Host": "evil.example"})
    assert all(item.status_code == 400 for item in attempts)
    assert bad_get.status_code == 400
    assert not settings_path.exists()
    assert credentials.calls == 0


def test_corrupt_settings_fail_closed_without_overwrite(
    preferences_api: tuple[Client, Path, Path, EmptyCredentials],
) -> None:
    client, settings_path, _root, credentials = preferences_api
    settings_path.parent.mkdir()
    original = b'{"schema_version":1,"openai_api_key":"sensitive"}'
    settings_path.write_bytes(original)
    with client:
        read = client.get(_PATH)
        write = client.put(
            _PATH,
            headers=_HEADERS,
            json={"preferences": asdict(UserPreferences()), "expected_revision": "0" * 64},
        )
    for response in (read, write):
        assert response.status_code == 503
        assert response.json() == {"error": {"code": 503}}
        assert "sensitive" not in response.text
        assert str(settings_path) not in response.text
    assert settings_path.read_bytes() == original
    assert credentials.calls == 0


def test_uninjected_preferences_route_is_unavailable(tmp_path: Path) -> None:
    root = tmp_path / "Projects"
    credentials = EmptyCredentials()
    app = create_app(project_root=root, credential_store=credentials, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(app, base_url=_ORIGIN)) as client:
        assert client.get(_PATH).json() == {"error": {"code": 503}}
        assert client.put(
            _PATH,
            headers=_HEADERS,
            json={"preferences": asdict(UserPreferences()), "expected_revision": "0" * 64},
        ).json() == {"error": {"code": 503}}
        assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert not root.exists()
    assert credentials.calls == 0
