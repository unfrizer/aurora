# AURORA — Manual Site Draft Guard Decision v1.0

- Document ID: ADR-074
- Status: APPROVED — delegated browser UI correction under ADR-001
- Date: 2026-10-26
- Module: UI-026 — Manual Site Draft Guard
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/060/069/072/073; PC-014/055/064/067/068

## Finding and decision

The UI-025 manual-site fields live only on the Projects screen until the user
activates **Create site from my text**. Using another project-start action,
opening an existing project or leaving Projects can unmount the form and lose
the typed copy. UI-026 adds an explicit loss warning for each action that can
discard a nonempty manual-site draft. A draft is present when any of the five
manual fields contains a character, including whitespace or invalid Unicode.
The shared project name alone does not count as a manual-site draft.

The warning is localized, does not echo the draft and appears before any
create/import/open/provider request. Declining leaves the form and all other
inputs untouched and makes no request. Accepting continues the chosen action
once. When the chosen action already requires a confirmation, the combined
message retains its existing public-content or paid-request warning; it does
not require two dialogs. The UI-024 brief-only warning and all no-draft flows
retain their existing behavior. When both brief and manual-site draft are
present before blank creation, one message names both omitted drafts.

The manual form gains an explicit **Clear site text** action, shown for any
nonempty manual field and disabled while busy. It clears only the five manual
fields. It does not clear the shared name, offline brief, AI prompt, JSON
import, clipboard state or persisted project. It makes no API request.

Navigation away from Projects warns while a manual-site draft exists.
Browser close/reload uses the existing native unsaved-change warning. A
successful transition clears the transient dirty indicator; a cancelled or
failed operation keeps it. No form data is persisted in browser storage or
project files until the explicit UI-025 creation action succeeds.

No P1/P6/P7 behavior, route, schema, dependency, Runtime, provider, credential,
asset, export or deployment behavior changes.

## Acceptance

PC-069 defines exact scope. Cover RU/EN cancellation, accepted actions, the
brief-only and combined warning, clear action, failed-operation retention,
navigation and unload, and absence of requests on cancellation/clear. Preserve
UI-023–UI-025 regressions. Run frozen frontend install, TypeScript, Vitest,
Vite build, browser tests, Ruff, Pyright and full Pytest. Review exact diff and
latest-head CI before ADR-003 merge.
