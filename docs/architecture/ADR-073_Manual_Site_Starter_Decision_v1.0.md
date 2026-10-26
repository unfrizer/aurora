# AURORA — Manual Site Starter Decision v1.0

- Document ID: ADR-073
- Status: APPROVED — delegated browser UI decision under ADR-001
- Date: 2026-10-26
- Module: UI-025 — Manual Site Starter
- Baseline: Architecture Freeze v1.0; ADR-001/002/003/020/047/069/072; PC-006/007/014/064/067

## Decision

Add an explicit no-key path for a one-page site whose public copy is supplied by
the user. The user enters project name, page headline, section heading and body;
tagline and SEO description are optional. AURORA places these values in the
existing P7 v1 blank editor and saves the new project through the existing P6
create and versioned editor-save routes. It does not infer content from a brief,
rewrite text, generate images, send provider requests, or claim AI generation.
The entered site copy is visible in preview, export and deployment. The UI
requires a separate public-content confirmation before creating anything.

The shared project name becomes the brand name and initial SEO page title. The
name is trimmed for project identity and these two fields; all other entered
text is preserved exactly. The starter keeps the blank editor's language,
IDs, slug, palette, typography and null image fields. No schema or lower-layer
owner changes. User review and editing before publishing remain explicit.

Validate every field as Unicode without unpaired surrogates. Project name,
headline and section heading must be nonblank after trimming; body must also be
nonblank. Limits are 256 UTF-8 bytes for name, tagline, headline and section
heading, 8 KiB for body and 320 bytes for optional SEO description. No implicit
creation occurs while typing. Existing blank, offline-brief, import and paid
generation actions retain their behavior. If a transient offline brief is also
present, the manual-start confirmation says that it will not be included.

One activation performs at most one create and one save. Verify saved identity
and every editor field before opening the workspace. On uncertain create/save,
leave the user on Projects, refresh the list when possible, retain form input
and never delete or retry automatically. A failed list refresh after verified
save does not invalidate the saved editor. No new route, dependency, runtime,
browser storage, credential, file format or provider behavior is introduced.

## Acceptance

PC-068 defines exact ownership. Test Unicode/bounds, RU/EN labels and public
confirmation, cancellation, verbatim mapping, one versioned save, verification,
duplicate guard, recovery and absence of provider calls. Run frozen frontend
install, TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright and full
Pytest. Review exact diff and latest-head CI before ADR-003 merge.
