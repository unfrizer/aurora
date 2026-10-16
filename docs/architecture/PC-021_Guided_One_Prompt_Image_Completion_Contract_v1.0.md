# AURORA — Guided One-Prompt Image Completion Contract v1.0

- Document ID: PC-021
- Status: APPROVED — compiled from explicitly approved ADR-027 GI-01–GI-05
- Module: UI-004 — Guided Image Completion After Draft Acceptance
- Date: 2026-10-16

## Authority and exact ownership

[ADR-027](ADR-027_Guided_One_Prompt_Image_Completion_Proposal_v1.0.md)
GI-01–GI-05 are incorporated in full. The Architecture Authority explicitly
approved them on 2026-10-16. AGENTS.md, ADR-001/002/003/023–026,
PC-014/017/019/020 and unaffected approved contracts remain in force.
UI-004 is a browser application module, not a new L0–L8 Runtime, backend
route, editor schema, asset store, or provider owner.

Only the implementation files enumerated in ADR-027 GI-01 may change,
plus ADR-027's approval record and this contract. No Python production or
test, other frontend file, dependency, lockfile, workflow, launcher, user
project, or lower-owner file may change. UI-004 consumes existing same-origin
P6 calls only through the unchanged `frontend/src/api.ts`.

## Required client behavior

After a successful saved UI-002 draft acceptance, show GI-02's explicit
choice before any image call. A saved valid P7 v1 editor can also open the
guide from the workspace. Construct a bounded, ordered, ID-frozen plan of
currently empty slots. Reconcile remaining frozen IDs against each latest
saved editor after attachment or explicit reload; do not replenish targets
from other pages/sections or overwrite a populated slot. Skips are
session-only. Expose the count and retry-charge warning before generation.

Use GI-02's exact visible prompt templates without a hidden instruction or
silent truncation. Never transmit the original business prompt or section
body through this flow. The user may edit the suggestion. Require a
user-entered nonblank alt string for a section before any paid attempt.

Reuse UI-003's saved-snapshot, per-attempt consent, single PC-019 call,
strict response parsing, stored-but-unattached review, explicit versioned
editor attachment, retained discarded asset, safe terminal/uncertain
failure, and 409 reload/reselection rules. In guided mode, reselected
targets must be current, empty, and among the frozen plan IDs; no silent
overwrite or automatic paid retry is allowed. UI-003's modal lock remains
in force while its form is open; a closed modal at an idle guide boundary
may be left freely. Pending/candidate unload protection remains in force.
Partial projects remain saved and exportable. No build or deploy is
triggered by UI-004.

## Acceptance and deferrals

Implement GI-05's complete deterministic fake-fetch/jsdom matrix and
preserve UI-001/002/003 regression tests. Run frozen pnpm install, strict
TypeScript, Vitest, Vite build and PC-013-compatible bundle check; Ruff,
strict Pyright and all discovered Pytest; exact diff/import review; and
latest-head hosted CI before routine merge. Use no real credential, paid
provider request, user project, skipped/xfail acceptance, or fabricated
live-provider certification. Produce one UI-004 module report and stop for
Tech Lead review.

This contract does not authorize a background multi-image batch, new P6
route, silent image attachment, populated-slot replacement, persistent
settings, folder export, Windows packaging, live OpenAI acceptance, or a
second AI provider. UI-004 does not alone certify ADR-002's entire usable
Windows acceptance path.
