# AURORA — Local Customer Photo Tray Proposal v1.0

- Document ID: ADR-048
- Status: APPROVED — byte-preserving batch mode selected by Architecture Authority on 2026-10-21
- Date: 2026-10-21
- Proposed module: UI-008 — Local Customer Photo Tray
- Baseline: Architecture Freeze v1.0; ADR-001/002/014/015/020/026/047;
  PC-008/009/014/020/042

## Decision boundary

The owner chose ChatGPT-prepared text import first and asked development to
continue. ADR-047 explicitly defers customer photographs to the existing
approved raster controls. This proposal makes that separate workflow easier
without a new backend, AI call, asset owner, P7 schema, or L0–L8 Runtime.

The Architecture Authority explicitly chose the byte-preserving batch mode
described here. PC-043 compiles PH-01–PH-05 as the separate UI-008 module
authority. The complete Architecture Freeze and Master Pack are not present
in this checkout; this decision does not supersede either.

## PH-01 — Ownership and exact files

UI-008 is one browser-client module. It may modify only:

```text
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/App.test.tsx
README.md
docs/architecture/ADR-048_Local_Customer_Photo_Tray_Proposal_v1.0.md
```

It may create only:

```text
frontend/src/components/PhotoTray.tsx
frontend/tests/photo_tray.test.tsx
docs/architecture/PC-043_Local_Customer_Photo_Tray_Contract_v1.0.md
```

No Python source or test, `frontend/src/api.ts`, `types.ts`, project-import
code, dependency, lockfile, launcher, workflow, or user project changes. P1
keeps sole raster storage ownership; P6 keeps the same-origin HTTP boundary;
P7 keeps editor-state ownership. The component is private to the browser UI.

## PH-02 — Local selection and preview

The user may select up to 20 local raster files into a transient editor tray.
Only the four already-approved declared MIME types (PNG, JPEG, GIF, WebP) and
nonempty files of at most 16 MiB each are candidates. Selection alone does
not upload, mutate P7 state, call an AI provider, or create a background job.
The browser may show local thumbnail previews through revocable object URLs;
it must revoke them on removal, replacement, or tray teardown. No filename,
preview URL, or file bytes are persisted in browser storage or logged. P1/P6
remain authoritative for signature and capacity validation after upload.

Adding an invalid selection leaves existing tray entries intact and shows a
fixed localized error. The tray is session-only; closing or reloading the
workspace loses uncommitted selections, not previously attached project assets.
An accessible RU/EN note makes this limitation explicit.

## PH-03 — Manual destination and attachment

For each selected file, the user chooses the current brand logo or an existing
page/section by stable P7 IDs and presses **Attach**. One attachment runs at a
time. The client uses only the existing P6 raster POST, then the existing
versioned P7 editor PUT, exactly as the manual upload path does today. It
changes only the selected `logo_path` or `image_path`; a section's `image_alt`
remains unchanged and user-authored, as in existing manual upload. An
existing target image is replaced only on that explicit action. The current
manual-upload dereference-before-delete rule for an old unreferenced image is
preserved; no tray-wide garbage collection is introduced.

The tray removes an item only after confirmed editor save. It never imports
files directly into a project directory, infers destinations from filenames,
or places photos automatically. A failed P6 upload causes no editor mutation;
a failed or uncertain editor save may leave a stored but unattached asset.
The UI reports this possibility, retains the local selection while present,
and does not silently retry or delete an asset whose exclusive ownership is
unknown. Navigation is blocked only during the active upload/save attempt.

## PH-04 — Transformation choice

The approved initial mode is **byte-preserving**: no browser-side resizing,
cropping, recompression, EXIF stripping, color conversion, or format change.
This keeps customer originals intact and leaves P1's existing byte/signature
checks authoritative. Files over 16 MiB are rejected with guidance to prepare
a smaller copy outside AURORA. A future separate decision may authorize local
optimization, with an explicit quality/format policy and tests.

The alternative is browser-side conversion before upload. That would alter
customer-supplied content, potentially remove metadata or animation, change
quality and file identity, and require concrete output-format/size/failure
rules. It is **not** authorized by this decision. The Architecture Authority
selected the byte-preserving path on 2026-10-21; local optimization remains
deferred to a separate decision.

## PH-05 — Acceptance and deferrals

Deterministic frontend tests should cover RU/EN text, all four MIME types,
count/size/empty boundaries, invalid-selection no-mutation, local preview URL
revocation, stable target identity, explicit one-at-a-time action, exact
existing upload and versioned save call order, replacement/dereference
behavior, no provider/deployment call, confirmed-save-only removal, failed
upload/save visibility, no automatic retry, and cleanup on unmount. Preserve
UI-001–UI-007 regressions. Run frozen pnpm install, TypeScript, Vitest, Vite
build, Ruff, Pyright, discovered Pytest and latest-head hosted CI. Review the
exact file scope and imports, then produce one UI-008 module report.

This proposal does not authorize photo analysis, automatic image placement,
AI image generation, source-photo editing, a persistent asset library, arbitrary
archive import, local file-system paths in HTTP, new MIME formats, a new
backend endpoint, or a clean-Windows acceptance claim. Those need separate
owned decisions and tests.

## Approval record

On 2026-10-21, the Architecture Authority selected: up to 20 local
PNG/JPEG/GIF/WebP files, at most 16 MiB each, manually attached one at a time
to a logo or section, with upload only on attachment and no AI, automatic
placement, or recompression. This approval resolves PH-04 in favor of the
byte-preserving candidate. PC-043 is the UI-008 implementation contract.
