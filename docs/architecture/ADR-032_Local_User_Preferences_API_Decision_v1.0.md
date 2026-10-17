# AURORA — Local User Preferences API Decision v1.0

- Document ID: ADR-032
- Status: APPROVED — Architecture Authority approved decisions PA-01–PA-04
- Date: 2026-10-17
- Module: P6-009 — Local User Preferences API

## Authority and decision

ADR-031 and PC-026 establish the application-owned, credential-free settings
store. The Architecture Authority answered «полностью утверждаю, дальше» to
the following four explicit decisions for exposing that store:

- PA-01: `create_app` gains an optional, explicitly injected
  `PreferencesStore`, preserving existing callers and inert construction.
- PA-02: protected `GET` and `PUT /api/v1/preferences` use the existing
  loopback/Host and same-origin mutation gates. A confirmed change with a
  stale version returns 409; a damaged settings document fails safely
  without overwrite.
- PA-03: successful GET may disclose the server-owned project directory as a
  read-only local path. The client cannot send or change that path.
- PA-04: launcher injection and React persistence are later, separate
  modules. This API task neither touches real user settings nor changes those
  owners.

This is a narrow extension of PC-006's P6 application boundary and its
no-local-path response rule. It does not alter L0–L8, P1 ownership, P2
credential storage, KR-002 configuration, or the public `src.local_api`
gateway. The preference store remains owned by P8 and is accessed only
through `src.preferences`. No secret, provider call, directory migration,
frontend change, or new dependency is authorized.

PC-027 fixes the request/response, revision, failure and test details for
P6-009. A disagreement with a higher authoritative frozen fact requires
reconciliation rather than an override by this decision.
