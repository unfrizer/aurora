# AURORA — Publication Checklist Decision v1.0

- Document ID: ADR-076
- Status: APPROVED — delegated browser UI decision under ADR-001
- Date: 2026-11-01
- Module: UI-028 — Publication Checklist
- Baseline: Architecture Freeze v1.0; ADR-001/003/020/073/075; PC-007/010/011/012/014

## Decision

The Export/Deploy screen displays a read-only checklist derived from the
currently saved P7 editor snapshot. It helps the user review content before
export or deployment. It is advisory: it neither certifies build validity
nor changes P4 validation, P6 export/deploy gates, confirmation flows or
buttons. P4 remains the sole static-site publication validator.

The checklist reports only these deterministic gaps, counting whitespace-only
text as empty:

- empty brand name or no pages;
- for each page, empty SEO title, main heading or meta description, or no
  content sections;
- for each section, empty heading or body, or empty image description when an
  image path is present.

Brand tagline, logo and missing images are optional and are not flagged.
Entries identify pages and sections by one-based position, never by echoing
user content. At most 20 entries are shown; the total count and number omitted
are displayed. An empty checklist means only that these particular gaps were
not found. The UI explicitly asks for a manual preview/review and does not
claim publish readiness.

Navigation to Export/Deploy already flushes editor changes. UI-028 receives
that in-memory editor from App and performs no additional request, mutation,
cache, persistence or provider call. Export ZIP/folder and Netlify deployment
continue to use their existing saved timestamps, confirmations, errors and
P4/P6 validation. No editor schema, Runtime, API route, dependency, browser
storage, generated file, credential or deployment behavior changes.

## Acceptance

PC-071 fixes ownership. Test every listed gap, one-based positions, 20-entry
display limit, no input echo, RU/EN copy, no-request rendering and unchanged
publication actions. Preserve existing regressions. Run frozen frontend
install, TypeScript, Vitest, Vite build, browser tests, Ruff, Pyright and
discovered Pytest. Review exact diff and latest-head CI before ADR-003 merge.
