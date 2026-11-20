# AURORA — Manual Multipage Site Starter Contract v1.0

- Document ID: PC-076
- Status: APPROVED — compiled from ADR-081 under ADR-001
- Date: 2026-11-20
- Authority: ADR-001/002/013/020/073/081; PC-004/007/014/068

## Ownership

This application-client change may create these two documents and modify:

```text
frontend/src/manual_site.ts
frontend/src/components/Projects.tsx
frontend/src/i18n.ts
frontend/tests/App.test.tsx
frontend/e2e/manual-site-starter.spec.ts
README.md
```

No Python owner, API route, editor schema, dependency, deployment adapter,
secret store or generated-site builder changes.

## Behavior and gates

Implement ADR-081 as optional manual fields in the existing Projects form.
Preserve the exact text in new sections. Do not create optional pages from
blank or whitespace-only fields. Keep one project create and one versioned
editor save, with the existing public-content confirmation and failure
handling. Avoid new network calls. Validate the full editor through the
current save path and do not claim AI generation.

Test pure construction and bounds, RU/EN form behavior, no-provider flow and
the built browser's save, preview, folder export, ZIP export and reopen path.
Run frozen frontend install, TypeScript, Vitest, Vite build, browser tests,
Ruff, Pyright and discovered Pytest. Review the diff and latest-head CI before
merge.
