# AURORA — Project Creation Path Clarity Decision v1.0

- Document ID: ADR-058
- Status: APPROVED — delegated browser-UI decision under ADR-001
- Date: 2026-10-22
- Module: UI-012 — Project Creation Path Clarity
- Baseline: Architecture Freeze v1.0; ADR-001/002/003/047/051/056;
  PC-042/046/051

## Decision

The Projects screen visibly separates its three existing creation paths:

1. Generate a text draft from one prompt with the configured OpenAI connection.
   This path requires the user's OpenAI API key and may incur provider charges.
2. Start an empty project without an OpenAI key, then edit it manually.
3. Import a reviewed, text-only P7 v1 JSON document without an AURORA OpenAI
   request. The document is prepared outside AURORA; that external tool may
   have its own account or cost requirements.

The project name remains shared. Each path keeps its current action and input
semantics. The file and paste import actions remain separate and use only their
own input. Switching attention among paths triggers no request, project
mutation, clipboard operation, storage write or paid call. This is disclosure
and presentation, not an alternative AI provider or a promise that an
external preparation service is free.

No existing validation, P7 format, provider policy, Runtime, API route,
credential handling, image workflow, or export behavior changes. The guide
remains read-only and the import remains raw strict JSON without repair.

## Boundary and acceptance

PC-053 defines exact browser-client file scope. Add RU/EN path headings,
clear key/cost notes and semantic grouping. Test that the three paths are
independently visible, their controls retain existing gating, and merely
viewing the screen invokes no create/generation/import/upload/deploy call.
Preserve existing action tests. Run frontend and repository quality gates,
review exact scope, and require latest-head hosted CI before routine merge.
