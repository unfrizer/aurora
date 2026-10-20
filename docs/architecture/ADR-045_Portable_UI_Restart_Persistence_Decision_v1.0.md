# AURORA — Portable UI Restart Persistence Decision v1.0

- Document ID: ADR-045
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-20
- Module: QA-010 — Portable UI Restart Persistence
- Baseline: Architecture Freeze v1.0, ADR-002/003/043/044, PC-027/028/038/039

## Decision and boundary

QA-009 checks that the packaged UI's saved editor survives a browser reload,
but stops the executable before checking those browser-created changes across
another process start. QA-010 extends only the existing Windows portable smoke:
after the QA-009 browser journey, read the edited project and RU/onboarding
preferences through the running packaged app's local API, stop that test
process, restart the same executable against its isolated temporary profile,
and assert the same project content and preferences through the new origin.

This is a test-only extension. QA-008's initial API save/restart and QA-009's
browser journey remain intact. No production source, public API, Runtime,
project or settings format, dependency, build artifact, or distribution
behavior changes. It does not test a clean Windows PC, live AI/image quality,
Credential Manager, Netlify, or the complete ADR-002 acceptance path. PC-040
fixes exact scope and acceptance.
