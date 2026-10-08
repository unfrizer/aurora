"""P6-002 editor and raster HTTP acceptance with only temporary projects."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Client

from src.credentials import SecretName, WindowsCredentialStore
from src.local_api import create_app
from src.projects import ProjectDocument, ProjectRepository

_ORIGIN = "http://127.0.0.1:8765"
_HEADERS = {"Origin": _ORIGIN, "X-Aurora-Request": "1"}
_SIGNATURES = {
    "image/png": (b"\x89PNG\r\n\x1a\n", "png"),
    "image/jpeg": (b"\xff\xd8\xff", "jpg"),
    "image/gif": (b"GIF89a", "gif"),
    "image/webp": (b"RIFF\x00\x00\x00\x00WEBP", "webp"),
}


class EmptyStore(WindowsCredentialStore):
    def __init__(self) -> None:
        self.calls = 0

    def set_secret(self, name: SecretName, secret: str) -> None:
        self.calls += 1
        raise AssertionError("Unexpected credential write")

    def get_secret(self, name: SecretName) -> str | None:
        self.calls += 1
        return None

    def delete_secret(self, name: SecretName) -> bool:
        self.calls += 1
        raise AssertionError("Unexpected credential delete")


@pytest.fixture
def api(tmp_path: Path) -> Iterator[tuple[Client, EmptyStore, Path]]:
    store = EmptyStore()
    root = tmp_path / "Projects"
    app = create_app(project_root=root, credential_store=store, allowed_origin=_ORIGIN)
    with cast(Client, TestClient(app, base_url=_ORIGIN, raise_server_exceptions=False)) as client:
        yield client, store, root


def _create(client: Client) -> dict[str, object]:
    response = client.post("/api/v1/projects", headers=_HEADERS, json={"name": "Studio"})
    assert response.status_code == 201
    return cast(dict[str, object], response.json())


def _metadata(document: dict[str, object]) -> dict[str, str]:
    return cast(dict[str, str], document["metadata"])


def _editor(reference: str | None = None) -> dict[str, object]:
    return {
        "schema_version": 1,
        "language": "en",
        "brand": {
            "name": "Studio",
            "tagline": "Ideas",
            "primary_color": "#4F46E5",
            "secondary_color": "#0F172A",
            "font_family": "system",
            "logo_path": reference,
        },
        "pages": [
            {
                "id": "37d407e8-9af8-4ca4-9e57-c0c28cce4266",
                "slug": "index",
                "title": "Home",
                "meta_description": "Studio",
                "heading": "Welcome",
                "sections": [
                    {
                        "id": "8bc80959-6e1d-4ad1-aa1e-9678e404c980",
                        "heading": "Work",
                        "body": "Our work",
                        "image_path": reference,
                        "image_alt": "Work image" if reference else "",
                    }
                ],
            }
        ],
    }


def _upload(client: Client, project_id: str, data: bytes, media_type: str = "image/png"):
    return client.post(
        f"/api/v1/projects/{project_id}/assets",
        headers={**_HEADERS, "Content-Type": media_type},
        content=data,
    )


def test_editor_save_validates_and_preserves_opaque_state(
    api: tuple[Client, EmptyStore, Path],
) -> None:
    client, store, root = api
    created = _create(client)
    metadata = _metadata(created)
    project_id = metadata["project_id"]
    repository = ProjectRepository(root)
    original = repository.load(project_id)
    with_notes = repository.save(
        ProjectDocument(metadata=original.metadata, state={"notes": {"source": "test"}})
    )
    payload = {"editor": _editor(), "expected_updated_at": with_notes.metadata.updated_at}
    saved = client.put(f"/api/v1/projects/{project_id}/editor", headers=_HEADERS, json=payload)
    assert saved.status_code == 200
    document = cast(dict[str, object], saved.json())
    assert _metadata(document)["name"] == "Studio"
    assert _metadata(document)["created_at"] == metadata["created_at"]
    state = cast(dict[str, object], document["state"])
    assert state["notes"] == {"source": "test"}
    assert state["editor"] == _editor()
    assert repository.load(project_id).state == state
    assert store.calls == 0

    stale = client.put(f"/api/v1/projects/{project_id}/editor", headers=_HEADERS, json=payload)
    assert stale.status_code == 409
    assert stale.json() == {"error": {"code": 409}}
    assert repository.load(project_id).state == state


@pytest.mark.parametrize(
    "editor",
    [
        {"schema_version": 2},
        {"schema_version": 1, "language": "en"},
        {"unexpected": "secret-value"},
    ],
)
def test_invalid_editor_does_not_replace_state(
    api: tuple[Client, EmptyStore, Path], editor: dict[str, object]
) -> None:
    client, _store, root = api
    created = _create(client)
    metadata = _metadata(created)
    project_id = metadata["project_id"]
    response = client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={"editor": editor, "expected_updated_at": metadata["updated_at"]},
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert "secret-value" not in response.text
    assert ProjectRepository(root).load(project_id).state == {}


def test_editor_rejects_unknown_keys_secrets_and_invalid_existing_state(
    api: tuple[Client, EmptyStore, Path],
) -> None:
    client, _store, root = api
    created = _create(client)
    metadata = _metadata(created)
    project_id = metadata["project_id"]
    base = f"/api/v1/projects/{project_id}/editor"
    for editor in (
        {**_editor(), "extra": True},
        {**_editor(), "openai_api_key": "synthetic"},
    ):
        response = client.put(
            base,
            headers=_HEADERS,
            json={"editor": editor, "expected_updated_at": metadata["updated_at"]},
        )
        assert response.status_code == 400
        assert response.json() == {"error": {"code": 400}}
    repository = ProjectRepository(root)
    document = repository.load(project_id)
    invalid = repository.save(
        ProjectDocument(metadata=document.metadata, state={"editor": {"schema_version": 2}})
    )
    response = client.put(
        base,
        headers=_HEADERS,
        json={"editor": _editor(), "expected_updated_at": invalid.metadata.updated_at},
    )
    assert response.status_code == 400
    assert repository.load(project_id).state == invalid.state


def test_editor_missing_project_and_invalid_schema_are_sanitized(
    api: tuple[Client, EmptyStore, Path],
) -> None:
    client, _store, _root = api
    created = _create(client)
    metadata = _metadata(created)
    body = {"editor": _editor(), "expected_updated_at": metadata["updated_at"]}
    absent = client.put(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000/editor",
        headers=_HEADERS,
        json=body,
    )
    assert absent.status_code == 404
    assert absent.json() == {"error": {"code": 404}}
    malformed = client.put(
        f"/api/v1/projects/{metadata['project_id']}/editor",
        headers=_HEADERS,
        json={**body, "extra": "private"},
    )
    assert malformed.status_code == 400
    assert "private" not in malformed.text


@pytest.mark.parametrize(("media_type", "sample"), tuple(_SIGNATURES.items()))
def test_upload_read_and_idempotent_reference_for_each_raster(
    api: tuple[Client, EmptyStore, Path], media_type: str, sample: tuple[bytes, str]
) -> None:
    client, store, root = api
    project_id = _metadata(_create(client))["project_id"]
    data = sample[0] + b"synthetic"
    expected = f"assets/{hashlib.sha256(data).hexdigest()}.{sample[1]}"
    uploaded = _upload(client, project_id, data, media_type)
    assert uploaded.status_code == 201
    assert uploaded.json() == {"path": expected}
    assert _upload(client, project_id, data, media_type).json() == {"path": expected}
    read = client.get(f"/api/v1/projects/{project_id}/{expected}")
    assert read.status_code == 200
    assert read.content == data
    assert read.headers["content-type"] == media_type
    assert read.headers["cache-control"] == "no-store"
    assert read.headers["x-content-type-options"] == "nosniff"
    assert read.headers["cross-origin-resource-policy"] == "same-origin"
    assert "access-control-allow-origin" not in read.headers
    assert ProjectRepository(root).read_asset(project_id, expected) == data
    assert store.calls == 0


def test_asset_upload_security_and_validation_are_non_mutating(
    api: tuple[Client, EmptyStore, Path],
) -> None:
    client, store, root = api
    project_id = _metadata(_create(client))["project_id"]
    path = f"/api/v1/projects/{project_id}/assets"
    data = _SIGNATURES["image/png"][0] + b"synthetic"
    attempts = [
        client.post(
            path, content=data, headers={**_HEADERS, "Host": "evil", "Content-Type": "image/png"}
        ),
        client.post(
            path, content=data, headers={"X-Aurora-Request": "1", "Content-Type": "image/png"}
        ),
        client.post(path, content=data, headers={"Origin": _ORIGIN, "Content-Type": "image/png"}),
        client.post(path, content=data, headers={**_HEADERS, "Content-Type": "application/json"}),
        client.post(
            path, content=data, headers={**_HEADERS, "Content-Type": "image/png; charset=utf-8"}
        ),
        client.post(
            path, content=b"bad-signature", headers={**_HEADERS, "Content-Type": "image/png"}
        ),
        client.post(
            path,
            content=data,
            headers={**_HEADERS, "Content-Type": "image/png", "Content-Length": "16777217"},
        ),
    ]
    assert all(
        item.status_code == 400 and item.json() == {"error": {"code": 400}} for item in attempts
    )
    assert not list((next(root.iterdir()) / "assets").iterdir())
    assert store.calls == 0


def test_asset_stream_limit_accepts_exact_16_mib_and_rejects_extra_byte(
    api: tuple[Client, EmptyStore, Path],
) -> None:
    client, _store, root = api
    project_id = _metadata(_create(client))["project_id"]
    data = _SIGNATURES["image/png"][0] + b"x" * (16 * 1024 * 1024 - 8)
    accepted = _upload(client, project_id, data)
    assert accepted.status_code == 201
    rejected = _upload(client, project_id, data + b"x")
    assert rejected.status_code == 400
    assert rejected.json() == {"error": {"code": 400}}
    assert len(list((next(root.iterdir()) / "assets").iterdir())) == 1


@pytest.mark.parametrize("declared_length", [None, "1"])
def test_streaming_upload_rejects_actual_oversize_without_publication(
    api: tuple[Client, EmptyStore, Path], declared_length: str | None
) -> None:
    client, _store, root = api
    project_id = _metadata(_create(client))["project_id"]

    def chunks() -> Iterator[bytes]:
        yield _SIGNATURES["image/png"][0] + b"x" * (8 * 1024 * 1024 - 8)
        yield b"y" * (8 * 1024 * 1024 + 1)

    headers = {**_HEADERS, "Content-Type": "image/png"}
    if declared_length is not None:
        headers["Content-Length"] = declared_length
    response = client.post(
        f"/api/v1/projects/{project_id}/assets", headers=headers, content=chunks()
    )
    assert response.status_code == 400
    assert response.json() == {"error": {"code": 400}}
    assert not list((next(root.iterdir()) / "assets").iterdir())


def test_asset_missing_malformed_corrupt_and_linked_cases(
    api: tuple[Client, EmptyStore, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _store, root = api
    project_id = _metadata(_create(client))["project_id"]
    invalid = f"/api/v1/projects/{project_id}/assets/not-canonical.png"
    assert client.get(invalid).json() == {"error": {"code": 400}}
    assert client.delete(invalid, headers=_HEADERS).json() == {"error": {"code": 400}}
    absent = f"/api/v1/projects/{project_id}/assets/{'a' * 64}.png"
    assert client.get(absent).status_code == 404
    assert client.delete(absent, headers=_HEADERS).status_code == 404
    data = _SIGNATURES["image/png"][0] + b"valid"
    reference = _upload(client, project_id, data).json()["path"]
    target = next(root.iterdir()) / reference
    url = f"/api/v1/projects/{project_id}/{reference}"
    target.write_bytes(_SIGNATURES["image/png"][0] + b"corrupt")
    assert client.get(url).json() == {"error": {"code": 400}}
    target.write_bytes(data)
    original = Path.is_junction

    def junction(path: Path) -> bool:
        return path == target or original(path)

    monkeypatch.setattr(Path, "is_junction", junction)
    assert client.get(url).json() == {"error": {"code": 400}}
    assert client.delete(url, headers=_HEADERS).json() == {"error": {"code": 400}}
    assert target.exists()


def test_asset_native_error_is_fixed_500(
    api: tuple[Client, EmptyStore, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _store, _root = api
    project_id = _metadata(_create(client))["project_id"]
    url = f"/api/v1/projects/{project_id}/assets/{'a' * 64}.png"

    def fail_read(_repository: ProjectRepository, _project_id: str, _path: str) -> bytes:
        raise OSError("C:\\private\\asset")

    monkeypatch.setattr(ProjectRepository, "read_asset", fail_read)
    response = client.get(url)
    assert response.status_code == 500
    assert response.json() == {"error": {"code": 500}}
    assert "private" not in response.text


def test_referenced_asset_delete_requires_saved_dereference(
    api: tuple[Client, EmptyStore, Path],
) -> None:
    client, _store, root = api
    created = _create(client)
    project_id = _metadata(created)["project_id"]
    data = _SIGNATURES["image/png"][0] + b"referenced"
    reference = _upload(client, project_id, data).json()["path"]
    url = f"/api/v1/projects/{project_id}/{reference}"
    saved = client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={
            "editor": _editor(reference),
            "expected_updated_at": _metadata(created)["updated_at"],
        },
    )
    assert saved.status_code == 200
    blocked = client.delete(url, headers=_HEADERS)
    assert blocked.status_code == 400
    assert blocked.json() == {"error": {"code": 400}}
    assert ProjectRepository(root).read_asset(project_id, reference) == data
    detached = client.put(
        f"/api/v1/projects/{project_id}/editor",
        headers=_HEADERS,
        json={
            "editor": _editor(),
            "expected_updated_at": _metadata(cast(dict[str, object], saved.json()))["updated_at"],
        },
    )
    assert detached.status_code == 200
    removed = client.delete(url, headers=_HEADERS)
    assert removed.status_code == 204
    assert removed.content == b""
    assert client.get(url).status_code == 404
