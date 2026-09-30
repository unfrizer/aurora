"""Tests for the Windows Credential Manager application adapter."""

from __future__ import annotations

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
