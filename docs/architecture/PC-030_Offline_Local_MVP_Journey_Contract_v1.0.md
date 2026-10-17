# AURORA — Offline Local MVP Journey Contract v1.0

- Document ID: PC-030
- Status: APPROVED — delegated compilation of ADR-035 under ADR-001
- Module: QA-001 — Offline Local MVP Journey
- Date: 2026-10-17

## Exact ownership

QA-001 may create only `tests/integration/test_local_mvp_journey.py` and
modify only `README.md` to reconcile the settings status and describe the
test's limits. ADR-035 and PC-030 are the only architecture documents in
scope. No production source, existing test, frontend, dependency, lockfile,
workflow, installer or other repository file may change.

## Acceptance scenario

Use only public AURORA gateways and the composed same-origin launcher app.
With temporary roots and synthetic UI bytes, verify first-use preferences,
confirmed language/model/onboarding save, project creation, one fake text
generation attempt, explicit candidate acceptance, one fake image generation
attempt, explicit image attachment through the editor, saved preview, ZIP and
project-local folder export, application reconstruction, project/settings
reopen, and deterministic site contents. Optionally verify the existing
Netlify route with a fake P5 deployer and explicit consent; no live deploy.

Assert the draft is not persisted before acceptance, generated image bytes
remain a separate stored asset until explicit attachment, project/settings
files remain separate, the ZIP contains only site members, and no real
credential, network, browser or user project is accessed. Preserve the
existing fixed Host/Origin/mutation boundary and module ownership; the test
must not weaken or replace the dedicated lower-module tests.

## Validation and limits

Run Ruff, strict Pyright and all discovered Pytest tests. Review the exact
file scope and latest-head hosted CI before a routine merge under ADR-003.
Produce one QA-001 report and stop for Tech Lead review.

This test uses a synthetic UI bundle and fake external services. It does not
prove React browser operation, live OpenAI account/model availability,
Netlify publication, Windows installer behavior, or the complete clean-PC
ADR-002 acceptance path. Those remain separate work.
