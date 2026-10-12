# AURORA — React Project Draft Generation UI Contract v1.0

- Document ID: PC-017
- Status: APPROVED — compiled from explicitly approved ADR-023 UD-01–UD-05
- Module: UI-002 — One-Prompt Draft Generation and Acceptance
- Date: 2026-10-12

## Authority and scope

[ADR-023](ADR-023_React_Project_Draft_Generation_UI_Proposal_v1.0.md)
UD-01–UD-05 are incorporated in full. The Architecture Authority explicitly
approved them on 2026-10-12. AGENTS.md, ADR-001/002/003, PC-014/015/016
and earlier approved application contracts remain in force. UI-002 is one
client application module, not a new L0–L8 Runtime or an expansion of PG/P6.

## Exact file and dependency boundary

Only the files enumerated in ADR-023 UD-01 may be created or modified in
this module task, plus this contract and the ADR-023 approval record. No
Python production/test, other frontend component, dependency or workflow
change is authorized. The client talks only to existing relative same-origin
P6 routes via `frontend/src/api.ts` and keeps all existing UI-001 controls.

## Required behavior

Implement UD-02's two separate project actions and explicit per-attempt
paid-call confirmation. Create-then-generate is an ordered two-request
flow; a successful create followed by generation failure leaves an empty
project. Existing projects may generate only when their editor key is absent.
The client mirrors name/prompt/model bounds without truncating or rewriting
the prompt, and sends the exact PC-016 body. It never retries automatically.

Interpret P6's five-field terminal response exactly as UD-03, treating
malformed data as an error. Show a completed candidate as unsaved structured
text; do not claim a preview or a saved project. Save only after separate
acceptance using the original source timestamp and the approved editor PUT.
A 409 keeps the candidate without rebasing; other save failures likewise
retain it for an explicit user action. A failed terminal result is not a
publishable editor. Discard affects browser memory only.

Follow UD-04's honest pending state, navigation/unload warnings, secret
boundary and same-origin request gates. No synthetic generation pipeline,
browser persistence, direct provider call or automatic write is permitted.

## Acceptance and deferrals

Cover the full UD-05 fake-fetch and jsdom matrix, preserving existing UI-001
tests. Run frozen pnpm install, TypeScript, Vitest, Vite build and compatible
bundle check, then repository Ruff, Pyright and all discovered Pytest.
Inspect exact diff and imports; latest-head hosted CI must pass before
routine merge under ADR-003. Produce one UI-002 module report and stop for
Tech Lead review.

This contract does not approve AI images, persistent settings, folder
export, Windows packaging, live OpenAI acceptance, automatic acceptance,
whole-project regeneration or a multistage pipeline. It does not by itself
meet the full ADR-002 usable-Windows acceptance path.
