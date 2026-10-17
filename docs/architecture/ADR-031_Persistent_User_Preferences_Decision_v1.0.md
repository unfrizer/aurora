# AURORA — Persistent User Preferences Decision v1.0

- Document ID: ADR-031
- Status: APPROVED — Architecture Authority approved the stated settings boundary
- Date: 2026-10-17
- First module: P8-001 — Application User Preferences Store

## Decision and authority

ADR-002 requires global settings at `%LOCALAPPDATA%\AURORA\settings.json`.
ADR-020 deliberately left language and model choices session-only. On
2026-10-17 the Architecture Authority answered «полностью утверждаю, дальше»
to the explicit proposal for a separate application-level preferences owner,
atomic persistence of language, selected models and onboarding completion,
no credentials in the file, a read-only project-directory display, and
failure without silent reset when settings are corrupt.

The preferences owner is an application service outside L0–L8. It is not a
Runtime, configuration cache, replacement for immutable KR-002 `Settings`,
P1 project state, P2 credential storage, or a new DI scope. It must not import
P6, the launcher, browser code or a higher Runtime. Lower-layer ownership and
dependency direction remain unchanged. The canonical Architecture Freeze is
not present in this checkout; an incompatible frozen fact requires
reconciliation, not an override by this ADR.

## Persisted product state

The first persisted settings snapshot contains only:

```text
schema_version = 1
language = null | "ru" | "en"
general_model = configurable text model ID (default "gpt-5.6-terra")
image_model = configurable image model ID (default "gpt-image-2")
onboarding_completed = boolean (default false)
```

`language = null` means the user has not chosen an interface language yet.
The existing UI has general and image model choices; this decision does not
invent a new complex-model control. No API key, token, credential identifier,
project state, prompt, generated content, path override or provider response
may enter the settings snapshot. P2 remains the sole credential owner.

The project root remains ADR-002's fixed default under the user's Documents
directory. Settings may show that location read-only, but cannot select a new
root or migrate projects in this phase. Custom directory selection and
migration require a later explicit decision.

## Failure and task sequencing

Missing `settings.json` means defaults and does not itself create a file.
Malformed, unsupported or unsafe existing settings fail closed: neither a
silent reset nor an overwrite is permitted. A user-visible, sanitized error
must be provided by a later application/UI composition task. The settings
write is atomic by same-directory temporary file replacement. A successful
write contains no secret fields.

P8-001 implements only the store and deterministic temporary-directory tests
under PC-026. A separate later P6/API or launcher composition contract must
expose the store; a separate UI contract must persist confirmed choices and
show the read-only project location. Neither later module is authorized by
this first-module contract. No real user settings file, browser, credential,
provider, or deployment may be touched in P8-001 acceptance tests.
