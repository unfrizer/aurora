# AURORA — Windows MVP Acceptance Protocol Contract v1.0

- Document ID: PC-033
- Status: APPROVED — compiled from ADR-038 under ADR-001
- Module: QA-003 — Windows MVP Acceptance Protocol
- Date: 2026-10-19

## Exact ownership

QA-003 may create or change only:

```text
docs/architecture/ADR-038_Windows_MVP_Acceptance_Decision_v1.0.md
docs/architecture/PC-033_Windows_MVP_Acceptance_Protocol_Contract_v1.0.md
docs/acceptance/WINDOWS_MVP_ACCEPTANCE.md
README.md  # link and acceptance-status clarification only
```

No `src/`, `frontend/`, `tests/`, workflow, build tool, dependency, project
file, credential or generated artifact is in scope.

## Protocol requirements

The acceptance document must identify the exact commit and successful portable
Windows workflow artifact used, require extraction before launch, and distinguish
the packaged executable from running a source checkout. It must exercise first
launch, RU/EN settings, a one-prompt text draft, explicit review and acceptance,
guided image completion, manual edits, panel collapse, preview, save/close/reopen,
folder and ZIP export, and optional Netlify deployment. It must make clear that
text generation and each image request are separate consented paid actions,
the image path is guided rather than unattended, and a ZIP is a static site,
not project state.

The record must have explicit PASS / FAIL / BLOCKED / NOT RUN outcomes and
separate mandatory versus optional steps. It must not infer a pass from tests
using fake providers, claim a signed installer, treat an unsigned-binary warning
as permission to bypass security, record secrets, automatically retry uncertain
external calls, or certify live services without using them.

## Validation and delivery

Review the exact documentation diff against the existing UI, ADR-002 and
PC-031/032. Run Ruff, strict Pyright and all discovered Pytest tests even
though QA-003 changes no executable code. Required latest-head hosted CI must
pass before routine merge under ADR-003. Report QA-003 as documentation ready,
with the actual clean-PC and live-provider acceptance still outstanding.
