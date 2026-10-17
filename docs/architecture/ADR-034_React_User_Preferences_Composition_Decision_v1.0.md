# AURORA — React User Preferences Composition Decision v1.0

- Document ID: ADR-034
- Status: APPROVED — delegated compilation of ADR-002, ADR-031 and ADR-032 under ADR-001
- Date: 2026-10-17
- Module: UI-006 — Persistent User Preferences Client

## Boundary

ADR-020's session-only choice was explicit for UI-001 because no settings
route existed. ADR-031 approved persistent language, two model choices and
onboarding completion as application settings. ADR-032 and PC-027 now provide
the exact P6 HTTP contract, and APP-002 injects P8 in production. UI-006
uses that route only; it does not move P8/P6 ownership, touch credentials,
store browser state or add a new dependency.

The client loads settings before exposing the workspace. `language = null`
prompts first-use choice; completed onboarding stays closed across restarts
but can be reopened. A click on a language choice or onboarding completion
is a confirmed mutation. The Settings screen offers one explicit Save for
language and both model IDs; typing alone changes only a local draft. A
successful PUT updates the active UI and model choices. A rejected or
uncertain PUT leaves the prior confirmed values intact and the draft visible.
On 409 the client never retries/overwrites automatically; an explicit reload
may discard the draft after confirmation. Invalid/unsafe settings or missing
store show a localized error and Retry, never a silent default/reset.

The project directory returned by GET is rendered as read-only text; no
client-provided path, directory picker, migration or path edit exists. API
responses are validated as unknown data with exact fields and no secret.
PC-029 fixes exact owned files, request behavior and acceptance. This ADR
does not alter frozen L0–L8 ownership or authorize a paid call/deployment.
