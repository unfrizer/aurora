# AURORA — Explicit Project Creation Action Decision v1.0

- Document ID: ADR-060
- Status: APPROVED — delegated browser-UI correction under ADR-001
- Date: 2026-10-23
- Module: UI-014 — Explicit Project Creation Action
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/023/047/051/058/059;
  PC-014/017/042/046/053/054

## Finding and decision

The Projects screen shares one project-name input across three distinct
creation paths. Its current surrounding HTML form submits to blank project
creation. Pressing Enter in the shared name input can therefore create a
blank P1 project without choosing the blank path's visible button. This is
inconsistent with the approved separation of blank, generation and import
actions and can leave an unexpected empty project when preparing another path.

UI-014 removes implicit form submission for this shared control. Blank project
creation occurs only when the user activates its visible **Create project**
button, by pointer or keyboard while that button is focused. Enter in the
shared project-name input must not create a project or invoke generation or
import. The name remains shared and editable, and the existing blank button
disabled state and trimmed-name callback remain unchanged. The distinct
generation, file import and paste import buttons retain all current gating,
validation, confirmation, failure and request semantics.

This decision narrows only the unintended form-submit shortcut. It does not
change P1, P6, P7, provider policy, project format, editor initialization,
paid-call consent, data persistence or any L0–L8 ownership. No new dependency
or public API is introduced.

## Boundary and acceptance

PC-055 grants exact browser-client file scope. Test that pressing Enter in the
name input makes no project-create request, including with import data ready;
the explicit blank button still creates exactly one project and keyboard
activation on that button remains available. Preserve existing generation,
blank, import and browser journeys. Run the frontend and repository quality
gates and latest-head hosted CI before a routine ADR-003 merge.
