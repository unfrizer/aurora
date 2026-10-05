"""A narrow, file-free adapter for Windows Credential Manager."""

from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable, Sequence
from ctypes import wintypes
from typing import Final, Literal, NoReturn, cast

SecretName = Literal["openai_api_key", "netlify_token"]

_ALLOWED_NAMES: Final[frozenset[str]] = frozenset({"openai_api_key", "netlify_token"})
_TARGET_PREFIX: Final[str] = "AURORA:"
_CRED_TYPE_GENERIC: Final[int] = 1
_CRED_PERSIST_LOCAL_MACHINE: Final[int] = 2
_ERROR_NOT_FOUND: Final[int] = 1168
_MAX_CREDENTIAL_BYTES: Final[int] = 5 * 512
_WINDLL_LOADER: Final[str] = "WinDLL"
_GET_LAST_ERROR: Final[str] = "get_last_error"
_CRED_WRITE: Final[str] = "CredWriteW"
_CRED_READ: Final[str] = "CredReadW"
_CRED_DELETE: Final[str] = "CredDeleteW"
_CRED_FREE: Final[str] = "CredFree"


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

    _cred_write: _NativeFunction
    _cred_read: _NativeFunction
    _cred_delete: _NativeFunction
    _cred_free: _NativeFunction

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise CredentialStoreError("Windows Credential Manager is available only on Windows.")

        native_loader = cast(Callable[..., object], getattr(ctypes, _WINDLL_LOADER))
        try:
            library = native_loader("Advapi32.dll", use_last_error=True)
        except OSError:
            raise CredentialStoreError("Windows Credential Manager could not be loaded.") from None
        self._cred_write = cast(_NativeFunction, getattr(library, _CRED_WRITE))
        self._cred_read = cast(_NativeFunction, getattr(library, _CRED_READ))
        self._cred_delete = cast(_NativeFunction, getattr(library, _CRED_DELETE))
        self._cred_free = cast(_NativeFunction, getattr(library, _CRED_FREE))

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
        encoded_secret = _encode_secret(secret)
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
        try:
            if not self._cred_write(ctypes.byref(credential), 0):
                self._raise_native_error("write")
        finally:
            ctypes.memset(secret_buffer, 0, len(encoded_secret))

    def read(self, target: str) -> str | None:
        credential_pointer = _CredentialPointer()
        if not self._cred_read(target, _CRED_TYPE_GENERIC, 0, ctypes.byref(credential_pointer)):
            if _last_error() == _ERROR_NOT_FOUND:
                return None
            self._raise_native_error("read")

        try:
            if not credential_pointer:
                raise CredentialStoreError("Windows returned an invalid credential buffer.")
            credential = credential_pointer.contents
            if credential.CredentialBlobSize == 0:
                return ""
            if (
                credential.CredentialBlobSize > _MAX_CREDENTIAL_BYTES
                or credential.CredentialBlobSize % 2 != 0
                or not credential.CredentialBlob
            ):
                raise CredentialStoreError("Windows returned an invalid credential buffer.")
            raw_secret = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
            try:
                return raw_secret.decode("utf-16-le")
            except UnicodeDecodeError:
                raise CredentialStoreError(
                    "Windows returned an invalid credential encoding."
                ) from None
        finally:
            if credential_pointer:
                self._cred_free(credential_pointer)

    def delete(self, target: str) -> bool:
        if self._cred_delete(target, _CRED_TYPE_GENERIC, 0):
            return True
        if _last_error() == _ERROR_NOT_FOUND:
            return False
        self._raise_native_error("delete")

    @staticmethod
    def _raise_native_error(operation: str) -> NoReturn:
        error_code = _last_error()
        raise CredentialStoreError(
            "Windows Credential Manager could not "
            f"{operation} the requested credential (error {error_code})."
        )


class _NativeFunction:
    argtypes: Sequence[object]
    restype: object

    def __call__(self, *arguments: object) -> int: ...


def _last_error() -> int:
    native_last_error = cast(Callable[[], int], getattr(ctypes, _GET_LAST_ERROR))
    return native_last_error()


def _encode_secret(secret: str) -> bytes:
    if not isinstance(cast(object, secret), str) or not secret:
        raise CredentialStoreError("A credential secret must not be empty and must be text.")
    try:
        encoded = secret.encode("utf-16-le")
    except UnicodeEncodeError:
        raise CredentialStoreError("A credential secret must be valid Unicode text.") from None
    if len(encoded) > _MAX_CREDENTIAL_BYTES:
        raise CredentialStoreError("The credential exceeds the Windows storage size limit.")
    return encoded


class WindowsCredentialStore:
    """Stores AURORA's approved production secrets outside application files."""

    def __init__(self) -> None:
        self._api = _WindowsCredentialApi()

    def set_secret(self, name: SecretName, secret: str) -> None:
        """Persist a non-empty secret in Windows Credential Manager."""
        target = self._target_for(name)
        _encode_secret(secret)
        self._api.write(target, "AURORA", secret)

    def get_secret(self, name: SecretName) -> str | None:
        """Return an allowed secret, or ``None`` when it has not been stored."""
        return self._api.read(self._target_for(name))

    def delete_secret(self, name: SecretName) -> bool:
        """Delete an allowed secret and report whether it existed."""
        return self._api.delete(self._target_for(name))

    @staticmethod
    def _target_for(name: SecretName) -> str:
        if not isinstance(cast(object, name), str) or name not in _ALLOWED_NAMES:
            raise CredentialStoreError("This credential name is not approved for AURORA storage.")
        return f"{_TARGET_PREFIX}{name}"
