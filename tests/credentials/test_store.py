"""Tests for the Windows Credential Manager application adapter."""

from __future__ import annotations

import ctypes
from typing import cast

import pytest

import src.credentials.store as credential_store_module
from src.credentials.store import CredentialStoreError, SecretName, WindowsCredentialStore


class FakeWindowsCredentialApi:
    """An in-memory stand-in for the private native Windows boundary."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def write(self, target: str, username: str, secret: str) -> None:
        assert username == "AURORA"
        self.values[target] = secret

    def read(self, target: str) -> str | None:
        return self.values.get(target)

    def delete(self, target: str) -> bool:
        if target not in self.values:
            return False
        del self.values[target]
        return True


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> WindowsCredentialStore:
    fake_api = FakeWindowsCredentialApi()
    monkeypatch.setattr(credential_store_module, "_WindowsCredentialApi", lambda: fake_api)
    return WindowsCredentialStore()


def test_set_and_get_secret(store: WindowsCredentialStore) -> None:
    store.set_secret("openai_api_key", "secret-value")

    assert store.get_secret("openai_api_key") == "secret-value"


def test_missing_secret_returns_none_and_delete_reports_false(
    store: WindowsCredentialStore,
) -> None:
    assert store.get_secret("netlify_token") is None
    assert store.delete_secret("netlify_token") is False


def test_delete_existing_secret(store: WindowsCredentialStore) -> None:
    store.set_secret("netlify_token", "token")

    assert store.delete_secret("netlify_token") is True
    assert store.get_secret("netlify_token") is None


def test_empty_secret_is_rejected(store: WindowsCredentialStore) -> None:
    with pytest.raises(CredentialStoreError, match="must not be empty"):
        store.set_secret("openai_api_key", "")


def test_unapproved_name_is_rejected(store: WindowsCredentialStore) -> None:
    invalid_name = cast(SecretName, "unapproved")

    with pytest.raises(CredentialStoreError, match="not approved"):
        store.get_secret(invalid_name)


@pytest.mark.parametrize("value", [None, 1, b"secret", "\ud800", "a" * 1281])
def test_invalid_secrets_are_rejected_before_native_write(
    store: WindowsCredentialStore, value: object
) -> None:
    with pytest.raises(CredentialStoreError):
        store.set_secret("openai_api_key", cast(str, value))
    assert store.get_secret("openai_api_key") is None


def test_maximum_secret_size_counts_encoded_bytes(store: WindowsCredentialStore) -> None:
    store.set_secret("netlify_token", "a" * 1280)
    assert store.get_secret("netlify_token") == "a" * 1280
    with pytest.raises(CredentialStoreError, match="size"):
        store.set_secret("netlify_token", "😀" * 641)


def test_invalid_names_are_rejected_by_all_operations(store: WindowsCredentialStore) -> None:
    names: tuple[object, ...] = ("other", None, [], {})
    for value in names:
        name = cast(SecretName, value)
        with pytest.raises(CredentialStoreError, match="not approved"):
            store.set_secret(name, "dummy")
        with pytest.raises(CredentialStoreError, match="not approved"):
            store.get_secret(name)
        with pytest.raises(CredentialStoreError, match="not approved"):
            store.delete_secret(name)


def test_adapter_explicitly_rejects_non_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(credential_store_module.sys, "platform", "linux")
    with pytest.raises(CredentialStoreError, match="only on Windows"):
        WindowsCredentialStore()


def test_native_read_decodes_unicode_and_frees_buffer(monkeypatch: pytest.MonkeyPatch) -> None:
    credential_type = credential_store_module._Credential  # pyright: ignore[reportPrivateUsage]
    api_type = credential_store_module._WindowsCredentialApi  # pyright: ignore[reportPrivateUsage]
    api = api_type.__new__(api_type)
    encoded = "dummy-ключ-😀".encode("utf-16-le")
    buffer = (ctypes.c_ubyte * len(encoded)).from_buffer_copy(encoded)
    credential = credential_type(
        CredentialBlobSize=len(encoded),
        CredentialBlob=ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)),
    )
    freed: list[object] = []

    def read(target: str, kind: int, flags: int, output: object) -> int:
        assert (target, kind, flags) == ("AURORA:openai_api_key", 1, 0)
        destination = ctypes.cast(
            cast(ctypes.c_void_p, output), ctypes.POINTER(ctypes.POINTER(credential_type))
        )
        destination[0] = ctypes.pointer(credential)
        return 1

    monkeypatch.setattr(api, "_cred_read", read, raising=False)
    monkeypatch.setattr(api, "_cred_free", freed.append, raising=False)
    assert api.read("AURORA:openai_api_key") == "dummy-ключ-😀"
    assert len(freed) == 1


@pytest.mark.parametrize(
    "payload", [b"x", b"\x00\xd8", b"x" * 2562], ids=["odd", "invalid-utf16", "oversized"]
)
def test_invalid_native_blobs_raise_safe_errors_and_are_freed(
    monkeypatch: pytest.MonkeyPatch, payload: bytes
) -> None:
    credential_type = credential_store_module._Credential  # pyright: ignore[reportPrivateUsage]
    api_type = credential_store_module._WindowsCredentialApi  # pyright: ignore[reportPrivateUsage]
    api = api_type.__new__(api_type)
    buffer = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
    credential = credential_type(
        CredentialBlobSize=len(payload),
        CredentialBlob=ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)),
    )
    freed: list[object] = []

    def read(target: str, kind: int, flags: int, output: object) -> int:
        destination = ctypes.cast(
            cast(ctypes.c_void_p, output), ctypes.POINTER(ctypes.POINTER(credential_type))
        )
        destination[0] = ctypes.pointer(credential)
        return 1

    monkeypatch.setattr(api, "_cred_read", read, raising=False)
    monkeypatch.setattr(api, "_cred_free", freed.append, raising=False)
    with pytest.raises(CredentialStoreError, match="invalid credential"):
        api.read("AURORA:netlify_token")
    assert len(freed) == 1


def test_native_missing_and_error_paths_do_not_free_unallocated_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_type = credential_store_module._WindowsCredentialApi  # pyright: ignore[reportPrivateUsage]
    api = api_type.__new__(api_type)
    freed: list[object] = []

    def fail(*arguments: object) -> int:
        return 0

    monkeypatch.setattr(api, "_cred_read", fail, raising=False)
    monkeypatch.setattr(api, "_cred_delete", fail, raising=False)
    monkeypatch.setattr(api, "_cred_write", fail, raising=False)
    monkeypatch.setattr(api, "_cred_free", freed.append, raising=False)
    monkeypatch.setattr(credential_store_module, "_last_error", lambda: 1168)
    assert api.read("AURORA:openai_api_key") is None
    assert api.delete("AURORA:openai_api_key") is False

    monkeypatch.setattr(credential_store_module, "_last_error", lambda: 5)
    for operation in (api.read, api.delete):
        with pytest.raises(CredentialStoreError, match="error 5"):
            operation("AURORA:openai_api_key")
    with pytest.raises(CredentialStoreError, match="error 5") as failure:
        api.write("AURORA:openai_api_key", "AURORA", "dummy-sensitive")
    assert "dummy-sensitive" not in str(failure.value)
    assert freed == []


def test_native_write_uses_generic_local_machine_utf16_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credential_type = credential_store_module._Credential  # pyright: ignore[reportPrivateUsage]
    api_type = credential_store_module._WindowsCredentialApi  # pyright: ignore[reportPrivateUsage]
    api = api_type.__new__(api_type)
    captured: list[bytes] = []

    def write(pointer: object, flags: int) -> int:
        credential = ctypes.cast(
            cast(ctypes.c_void_p, pointer), ctypes.POINTER(credential_type)
        ).contents
        assert flags == 0
        assert credential.Type == 1
        assert credential.Persist == 2
        assert credential.TargetName == "AURORA:netlify_token"
        assert credential.UserName == "AURORA"
        captured.append(
            ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        )
        return 1

    monkeypatch.setattr(api, "_cred_write", write, raising=False)
    api.write("AURORA:netlify_token", "AURORA", "dummy-ключ")
    assert captured == ["dummy-ключ".encode("utf-16-le")]


def test_native_null_read_buffer_is_rejected_without_freeing_null(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_type = credential_store_module._WindowsCredentialApi  # pyright: ignore[reportPrivateUsage]
    api = api_type.__new__(api_type)
    freed: list[object] = []

    def read(*arguments: object) -> int:
        return 1

    monkeypatch.setattr(api, "_cred_read", read, raising=False)
    monkeypatch.setattr(api, "_cred_free", freed.append, raising=False)
    with pytest.raises(CredentialStoreError, match="invalid credential buffer"):
        api.read("AURORA:openai_api_key")
    assert freed == []
