# AURORA — Local Photo Drop Staging Decision v1.0

- Document ID: ADR-057
- Status: APPROVED — delegated UI decision under ADR-001
- Date: 2026-10-22
- Module: UI-011 — Local Photo Drop Staging
- Baseline: Architecture Freeze v1.0; ADR-001/003/047/048; PC-042/043

## Decision

The existing UI-008 photo tray gains a drag-and-drop selection surface. Dropping
local files has exactly the same staging semantics as its file picker: the
existing 20-item limit, four raster MIME types, nonempty and 16-MiB-per-file
limit, atomic rejection of invalid additions, transient previews and URL
cleanup all apply. The file picker remains available for keyboard use. The
drop surface visibly indicates an active drag and explains in RU/EN that a
drop does not upload or attach anything.

Only an explicit destination selection and **Attach** action may call the
existing P6 upload and P7 versioned save. A drop does not inspect photo
content, infer a target, transform bytes, access the filesystem outside the
browser's supplied `File` objects, persist a tray, invoke AI, or contact a
provider. While an attachment is pending, the surface cannot accept a new
selection. No new backend, dependency, Runtime, or public data contract is
created.

## Boundary

This is one browser-client module. PC-052 grants exact file scope. This
decision changes only how files enter the existing in-memory tray; it does
not revise ADR-048/PC-043's manual attachment or byte-preserving rules.

Validate picker/drop equivalence, invalid-selection atomicity, pending lock,
localized text and explicit attachment by deterministic frontend tests. Run
frontend typecheck, Vitest, build and browser regressions; repository Ruff,
Pyright and discovered Pytest; and latest-head hosted CI before routine merge.
