# AURORA — Windows Credential Manager Contract v1.0

**Status:** APPROVED  
**Module:** P2-001 Windows Credential Manager Secret Adapter  
**Authority:** ADR-001 and ADR-002

P2-001 is a Windows-only application adapter, not an L0–L8 Runtime. It owns
the narrow boundary between AURORA and Windows Credential Manager. It may create:

```text
src/credentials/__init__.py
src/credentials/store.py
tests/credentials/test_store.py
```

Its public API is `SecretName`, `CredentialStoreError`, and
`WindowsCredentialStore`. `SecretName` permits exactly `openai_api_key` and
`netlify_token`. The store can set, get, and delete either secret. It uses
Generic Credentials with deterministic AURORA target names and local-machine
persistence. It returns `None` when an allowed secret has not been stored and
returns `False` when an allowed secret cannot be deleted because it does not
exist.

The adapter calls the Windows Credential Manager API through Python's standard
library `ctypes`; it adds no dependency. It must fail explicitly when used on a
non-Windows host. It never logs, serializes, exposes in a representation, or
writes a raw secret to a project, settings file, generated site, or source
control. Developer-mode environment-variable fallback remains application
bootstrap policy and is outside this adapter.

The adapter does not call AI or Netlify, provide HTTP, read project state,
manage configuration, or import a Runtime implementation. Tests replace the
private native API boundary with an in-memory fake and cover set/get, missing
credentials, deletion, invalid names, and native failures. Ruff, Pyright, and
Pytest are required.

## Audit Clarifications

Secrets are non-empty Unicode strings encoded as UTF-16LE blobs. Encoded size
cannot exceed the native limit of 2,560 bytes. Invalid native blob sizes, missing
buffers and invalid UTF-16 produce sanitized `CredentialStoreError` failures.
Successful native reads always release their allocated buffer with `CredFree`.
The temporary native write buffer is cleared after the call; this does not imply
that immutable Python strings can be reliably erased from memory.

Tests exercise the native wrapper with synthetic buffers and substituted native
functions, without accessing the user's Credential Manager entries. This is not
a real native credential roundtrip or production integration certification.

References: [CREDENTIALW](https://learn.microsoft.com/en-us/windows/win32/api/wincred/ns-wincred-credentialw)
and [CredReadW](https://learn.microsoft.com/en-us/windows/win32/api/wincred/nf-wincred-credreadw).
