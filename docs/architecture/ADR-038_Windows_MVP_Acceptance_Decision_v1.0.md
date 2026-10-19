# AURORA — Windows MVP Acceptance Decision v1.0

- Document ID: ADR-038
- Status: APPROVED — delegated acceptance decision under ADR-001
- Date: 2026-10-19
- Module: QA-003 — Windows MVP Acceptance Protocol
- Baseline: Architecture Freeze v1.0, ADR-002/003/035/036/037, PC-030/031/032

## Decision

The offline API journey, actual-browser journey and portable-executable smoke
test cover different seams, but none certifies the ADR-002 first-usable Windows
journey on a clean target computer with live services. QA-003 records a
reproducible **manual acceptance protocol** and an evidence template for that
remaining work. It adds no product feature, test automation, runtime behavior,
provider call, dependency, release, or deployment.

The protocol distinguishes mandatory local usability checks from optional
Netlify publication and from live OpenAI requests that may incur charges.
The operator must supply their own credentials directly in the application
and consciously confirm each paid or publishing action. Codex must not use
real credentials or perform those actions merely because this document is
approved. A failed, skipped or blocked step is not a pass; an uncertain paid
request or deployment must be investigated before any retry.

## Evidence boundary

The portable ZIP must be traceable to a successful Windows CI run for an exact
commit. A different commit, an expired artifact, a security warning that blocks
launch, or a machine with preinstalled developer tooling must be recorded
honestly. Acceptance is not granted by a green CI badge alone. A clean-PC
result may be recorded only after an operator performs and documents the
steps on a separate Windows x64 machine without Python, uv, Node or pnpm.

Do not put tokens, full project contents, private prompts, personal paths or
unredacted screenshots in the evidence record. The protocol is a checklist,
not an instruction to weaken Windows security controls or delete user data.

PC-033 fixes QA-003's exact documentation ownership and validation. Completion
of QA-003 means the protocol is ready to execute; it does **not** mean the MVP
acceptance path has passed or authorize a public GitHub Release.
