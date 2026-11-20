# AURORA — Manual Multipage Site Starter Decision v1.0

- Document ID: ADR-081
- Status: APPROVED — delegated application UI decision under ADR-001
- Date: 2026-11-20
- Scope: no-key manual site creation
- Baseline: Architecture Freeze v1.0; ADR-001/002/013/020/073; PC-004/007/014/068

## Decision

Extend the existing explicit **Build a site from my text** path with two
optional public-text fields: Services and Contact. A nonblank Services field
creates a `services` page and a nonblank Contact field creates a `contact`
page, after the existing `index` page and in that order. Each added page has
one section containing exactly the entered text. Its localized page/section
heading is `Услуги`/`Services` or `Контакты`/`Contact`; its SEO title uses
the project name and that heading. Its SEO description is initially empty for
manual review. Every page and section receives a unique browser UUID. Blank
optional fields create no page, preserving the original one-page path.

The public-content confirmation applies to all entered fields. The existing
one-create/one-save flow, saved-document verification, uncertainty recovery,
draft-loss warning and no-provider boundary remain in force. The action does
not infer or rewrite a business brief, create images, or call a provider. It
produces an editable P7 v1 document and leaves publishability to P4. Existing
blank, offline-brief, prepared-import and paid-generation paths are unchanged.

Each optional field allows at most 8 KiB UTF-8 and rejects malformed Unicode.
This refinement supersedes ADR-073's one-page-only statement only when one or
both optional fields are nonblank. It does not change P7/P4/P6 schemas,
ownership, routes, dependencies or the L0–L8 Runtime architecture.

## Acceptance

PC-076 fixes implementation scope. Verify one-, two- and three-page output,
localized headings, exact text, UUID/slug uniqueness, input bounds, consent,
save/reopen, preview and static folder/ZIP export without provider calls. Run
frontend and Python checks and browser journeys before publication.
