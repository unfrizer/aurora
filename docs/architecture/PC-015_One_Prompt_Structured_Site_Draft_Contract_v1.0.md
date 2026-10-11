# AURORA — One-Prompt Structured Site Draft Contract v1.0

**Document ID:** PC-015
**Status:** APPROVED — compiled from explicitly approved ADR-021 PG-01–PG-05
**Module:** PG-001 — One-Prompt Structured Site Draft
**Date:** 2026-10-11

## Authority and boundary

[ADR-021](ADR-021_One_Prompt_Site_Draft_Proposal_v1.0.md) is incorporated in
full. The Architecture Authority explicitly approved PG-01–PG-05 on
2026-10-11. This contract authorizes one application-composition module,
not a new L0–L8 Runtime or a change to Architecture Freeze v1.0. AGENTS.md,
ADR-001/002/003, PC-003, PC-004 and PC-007 remain in force.

## Exact ownership

The active PG-001 build may create or edit only:

```text
src/project_generation/__init__.py
src/project_generation/models.py
src/project_generation/service.py
tests/project_generation/__init__.py
tests/project_generation/test_models.py
tests/project_generation/test_service.py
tests/integration/test_project_generation.py
tests/editor/test_models.py
tests/site_export/test_models.py
docs/architecture/ADR-021_One_Prompt_Site_Draft_Proposal_v1.0.md
docs/architecture/PC-015_One_Prompt_Structured_Site_Draft_Contract_v1.0.md
```

The existing P7/P4 test edits admit only `src/project_generation/service.py`
as a consumer of each public gateway and preserve their private-import and
lower-owner prohibitions. No P1–P7 production file, frontend, lower Runtime,
dependency, configuration, or CI workflow may change.

## Public API and behavior

The `src.project_generation` gateway exports exactly `ProjectDraftRequest`,
`ProjectDraftOutcome`, and `ProjectDraftGenerator`, with the exact schema and
signatures in ADR-021 PG-02. The request and outcome are frozen, slotted,
keyword-only dataclasses. Input validation, JSON shape and bounds, UUID5 ID
derivation, P7 save/projection validation, P4 in-memory build validation,
terminal-failure mapping, and one-call/no-retry rule are precisely PG-02/03.
PG-001 never persists or accepts a candidate document on a user's behalf.

Production dependencies are standard library and the public `src.generation`,
`src.editor`, and `src.site_export` gateways only. No private imports, reverse
imports, provider registry, direct HTTP, credentials, or new dependency.

## Acceptance and deferred work

Implement deterministic fake-client tests covering the PG-04 matrix with no
network, secrets, skipped or xfailed cases. Run Ruff, strict Pyright, and all
discovered Pytest tests; inspect the exact diff/import boundary; then report
one module and stop. Required latest-head hosted checks must pass before a
routine merge under ADR-003. Green synthetic tests do not establish live
OpenAI generation or the full ADR-002 usable-Windows acceptance path.

P6 route, UI generation/acceptance, image generation, settings, folder export,
and Windows packaging each require a later separate APPROVED contract as
specified in PG-05. This contract authorizes none of them.
