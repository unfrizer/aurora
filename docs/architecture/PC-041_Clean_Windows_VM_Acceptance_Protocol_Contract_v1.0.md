# AURORA — Clean Windows VM Acceptance Protocol Contract v1.0

- Document ID: PC-041
- Status: APPROVED — explicit authority in ADR-046
- Module: QA-011 — Clean Windows VM Acceptance Protocol
- Date: 2026-10-20

## Exact ownership

QA-011 may create or change only:

```text
docs/architecture/ADR-046_Clean_Windows_VM_Acceptance_Decision_v1.0.md
docs/architecture/PC-041_Clean_Windows_VM_Acceptance_Protocol_Contract_v1.0.md
docs/acceptance/WINDOWS_MVP_ACCEPTANCE.md  # target eligibility and evidence only
README.md                                   # matching acceptance-status wording only
```

No `src/`, `frontend/`, `tests/`, workflow, build tool, dependency, project
format, credential, generated artifact or repository-security change is in
scope. ADR-038 and PC-033 remain historical approved records; ADR-046 has
narrow precedence only over their physical-target restriction.

## Acceptance

The checklist must permit either a separate clean Windows x64 physical PC or
a fresh isolated Windows x64 VM that satisfies ADR-046. It must distinguish
guest OS isolation from a second host profile, require absent developer tools
and user AURORA data, preserve the exact-commit/portable-artifact trace, and
record whether evidence came from a physical PC or VM. It must retain every
M01–M10 and O01–O02 action, result state, real-service consent and secret
boundary. Overall PASS on a VM must be labelled clean-VM acceptance and must
not claim physical-hardware testing. Neither this contract nor a green CI
run marks any checklist item PASS.

Review the exact documentation diff. Run repository Ruff, strict Pyright and
all discovered Pytest. Require latest-head hosted CI and no blocking conflict
or review before routine merge under ADR-003. Produce one QA-011 report and
stop; provisioning a VM, handling credentials and executing paid calls are
not authorized by this documentation-only module.
