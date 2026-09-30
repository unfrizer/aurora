"""A narrow, file-free adapter for Windows Credential Manager."""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Sequence
from ctypes import wintypes
from typing import Final, Literal, NoReturn, cast

SecretName = Literal["openai_api_key", "netlify_token"]

_ALLOWED_NAMES: Final[frozenset[str]] = frozenset({"openai_api_key", "netlify_token"})
_TARGET_PREFIX: Final[str] = "AURORA:"
_CRED_TYPE_GENERIC: Final[int] = 1
_CRED_PERSIST_LOCAL_MACHINE: Final[int] = 2
_ERROR_NOT_FOUND: Final[int] = 1168


class CredentialStoreError(RuntimeError):
    """Raised when Windows Credential Manager cannot complete an operation."""


class _Credential(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


_CredentialPointer = ctypes.POINTER(_Credential)


class _WindowsCredentialApi:
    """The private, typed wrapper around Advapi32 credential functions."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise CredentialStoreError("Windows Credential Manager is available only on Windows.")

        library = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
        self._cred_write = cast(_NativeFunction, library.CredWriteW)
        self._cred_read = cast(_NativeFunction, library.CredReadW)
        self._cred_delete = cast(_NativeFunction, library.CredDeleteW)
        self._cred_free = cast(_NativeFunction, library.CredFree)

        for function, argument_types, result_type in (
            (self._cred_write, [ctypes.POINTER(_Credential), wintypes.DWORD], wintypes.BOOL),
            (
                self._cred_read,
                [
                    wintypes.LPCWSTR,
                    wintypes.DWORD,
                    wintypes.DWORD,
                    ctypes.POINTER(_CredentialPointer),
                ],
                wintypes.BOOL,
            ),
            (self._cred_delete, [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD], wintypes.BOOL),
            (self._cred_free, [ctypes.c_void_p], None),
        ):
            function.argtypes = argument_types
            function.restype = result_type

    def write(self, target: str, username: str, secret: str) -> None:
        encoded_secret = secret.encode("utf-16-le")
        secret_buffer = (ctypes.c_ubyte * len(encoded_secret)).from_buffer_copy(encoded_secret)
        credential = _Credential(
            Flags=0,
            Type=_CRED_TYPE_GENERIC,
            TargetName=target,
            Comment=None,
            LastWritten=wintypes.FILETIME(),
            CredentialBlobSize=len(encoded_secret),
            CredentialBlob=ctypes.cast(secret_buffer, ctypes.POINTER(ctypes.c_ubyte)),
            Persist=_CRED_PERSIST_LOCAL_MACHINE,
            AttributeCount=0,
            Attributes=None,
            TargetAlias=None,
            UserName=username,
        )
        if not self._cred_write(ctypes.byref(credential), 0):
            self._raise_native_error("write")

    def read(self, target: str) -> str | None:
        credential_pointer = _CredentialPointer()
        if not self._cred_read(target, _CRED_TYPE_GENERIC, 0, ctypes.byref(credential_pointer)):
            if ctypes.get_last_error() == _ERROR_NOT_FOUND:
                return None
            self._raise_native_error("read")

        try:
            credential = credential_pointer.contents
            if credential.CredentialBlobSize == 0:
                return ""
            raw_secret = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
            return raw_secret.decode("utf-16-le")
        finally:
            self._cred_free(credential_pointer)

    def delete(self, target: str) -> bool:
        if self._cred_delete(target, _CRED_TYPE_GENERIC, 0):
            return True
        if ctypes.get_last_error() == _ERROR_NOT_FOUND:
            return False
        self._raise_native_error("delete")

    @staticmethod
    def _raise_native_error(operation: str) -> NoReturn:
        error_code = ctypes.get_last_error()
        raise CredentialStoreError(
            "Windows Credential Manager could not "
            f"{operation} the requested credential (error {error_code})."
        )


class _NativeFunction:
    argtypes: Sequence[object]
    restype: object

    def __call__(self, *arguments: object) -> int: ...


class WindowsCredentialStore:
    """Stores AURORA's approved production secrets outside application files."""

    def __init__(self) -> None:
        self._api = _WindowsCredentialApi()

    def set_secret(self, name: SecretName, secret: str) -> None:
        """Persist a non-empty secret in Windows Credential Manager."""
        target = self._target_for(name)
        if not secret:
            raise CredentialStoreError("A credential secret must not be empty.")
        self._api.write(target, "AURORA", secret)

    def get_secret(self, name: SecretName) -> str | None:
        """Return an allowed secret, or ``None`` when it has not been stored."""
        return self._api.read(self._target_for(name))

    def delete_secret(self, name: SecretName) -> bool:
        """Delete an allowed secret and report whether it existed."""
        return self._api.delete(self._target_for(name))

    @staticmethod
    def _target_for(name: SecretName) -> str:
        if name not in _ALLOWED_NAMES:
            raise CredentialStoreError("This credential name is not approved for AURORA storage.")
        return f"{_TARGET_PREFIX}{name}"
