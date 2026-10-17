# AURORA — Application User Preferences Store Contract v1.0

- Document ID: PC-026
- Status: APPROVED — delegated compilation of ADR-031 under ADR-001
- Module: P8-001 — Application User Preferences Store
- Date: 2026-10-17

## Exact ownership

P8-001 is a pure application filesystem service. It may create only:

```text
src/preferences/__init__.py
src/preferences/models.py
src/preferences/store.py
tests/preferences/test_user_preferences.py
tests/integration/test_preferences_store.py
```

ADR-031 and this contract are the only architecture documents in this task.
No KR-002 configuration, P1 project, P2 credential, P6 API, launcher,
frontend, dependency, workflow, README or existing test file may change.
The package has no production imports from another AURORA module. It adds no
Runtime, global mutable cache, worker, provider call or network access.

## Public gateway and snapshot

`src.preferences` exports exactly `UserPreferences`, `PreferencesError`,
`PreferencesStore` and `default_preferences_path`. `UserPreferences` is a
frozen, slotted dataclass with the five ADR-031 fields and their exact
defaults. `PreferencesError` is a sanitized failure type: its text and
representation never include a filesystem path, document contents or secret.

`default_preferences_path() -> Path` returns the absolute fixed
`%LOCALAPPDATA%\AURORA\settings.json` location from an existing absolute
`LOCALAPPDATA` directory; a missing/relative/unsafe base fails without
creating anything. It does not read or write the settings file.

`PreferencesStore(path: Path)` accepts an explicit absolute `settings.json`
path for dependency injection and tests, without I/O during construction.
`load() -> UserPreferences` returns fresh defaults if the file is absent and
does not create directories. `save(preferences: UserPreferences) -> None`
validates the exact snapshot and writes it atomically. It may create only the
immediate settings parent directory; its parent must already exist. An
existing malformed/unsupported file is never replaced. The store neither
loads nor saves credentials, project data, arbitrary JSON fields or a project
root override.

## Validation and filesystem boundary

The on-disk UTF-8 JSON object has exactly the five named fields; no extras,
missing fields, duplicate keys, wrong types or unsupported schema version.
Model IDs must be nonempty valid UTF-8 strings without control characters;
they are not normalized or replaced with provider policy guesses. The file is
bounded to 64 KiB. A valid snapshot round-trips without model-name changes.
Validation errors are `PreferencesError` with fixed safe messages; native I/O
failures are wrapped without exposing paths or content.

Existing directory/file symlinks, junctions, reparse points, nonregular files
and hard-linked settings files are rejected before access. Writing uses a
same-directory temporary file, flush and replace only after successful
serialization. On failure, the old settings file remains unchanged and this
invocation's temporary file is removed best-effort. The store does not claim
cross-process transactions, protection from concurrent filesystem replacement
after validation, or durability across sudden power loss.

## Acceptance

Tests use only `tmp_path` and patched environment, never actual LOCALAPPDATA.
Cover defaults/no I/O, exact schema and immutable snapshot, Russian/English
roundtrip, custom model IDs, byte limit, invalid fields/unknown/duplicate
keys, malformed UTF-8/JSON, unsupported version, nonlinked path boundary,
atomic replace failure and preservation of old bytes, and no secret fields.
Integration reopens a store with the same temporary path and verifies state
survives while a sibling project directory remains untouched. No real user
file, credential, provider, browser, or network call.

Run repository Ruff, strict Pyright and all discovered Pytest. Inspect the
exact diff and require latest-head hosted CI before routine merge. Produce
one P8-001 report and stop for Tech Lead review. P6/API and UI persistence
remain separate future approved-contract tasks.
