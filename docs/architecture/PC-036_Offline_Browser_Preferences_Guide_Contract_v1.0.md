# AURORA — Offline Browser Preferences and Guide Contract v1.0

- Document ID: PC-036
- Status: APPROVED — compiled from ADR-041 under ADR-001
- Module: QA-006 — Offline Browser Preferences and Guide Journey
- Date: 2026-10-20

## Exact ownership

QA-006 may create or change only:

```text
docs/architecture/ADR-041_Offline_Browser_Preferences_Guide_Decision_v1.0.md
docs/architecture/PC-036_Offline_Browser_Preferences_Guide_Contract_v1.0.md
frontend/e2e/local-journey.spec.ts   # language/guide assertions only
README.md                            # verified scope and limits only
```

No production source, other test, fake server, dependency, lockfile, workflow,
build artifact, credential, production settings, user project or release file
may change. Preserve the existing QA-002/004/005 browser assertions and
isolated loopback server.

## Browser assertions

At the end of the existing one-project journey, use the Settings screen to
change the confirmed interface language from Russian to English. Before Save,
the active UI remains Russian; after Save, it becomes English. Confirm the
isolated `settings.json` has `language = "en"`, `onboarding_completed = true`
and no fake key. Reload the page and observe English Projects without an
automatic guide. Open the guide explicitly from the toolbar, observe the
English guide, close it and reload once more; it must stay closed and retain
English. No browser storage or real user-profile file is involved.

This verifies browser-to-P6-to-P8 persistence across page reloads, not a
clean-PC installation, process restart, real provider or publication.

## Validation and delivery

Run frozen frontend install, TypeScript typecheck, Vitest, Vite build and
Windows Chrome browser spec, plus repository Ruff, strict Pyright and all
discovered Pytest. Inspect exact diff and latest-head hosted CI. Routine merge
under ADR-003 requires all checks to pass and no blocking conflict/review.
Report one QA-006 module and stop.
