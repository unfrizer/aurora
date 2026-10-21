# AURORA — Local Customer Photo Tray Contract v1.0

- Document ID: PC-043
- Status: APPROVED — compiled from ADR-048 PH-01–PH-05 and the explicit
  byte-preserving choice of 2026-10-21
- Date: 2026-10-21
- Module: UI-008 — Local Customer Photo Tray
- Authority: ADR-048; ADR-001/002/003/014/015/020/026/047; PC-008/009/014/020/042

## Boundary and exact scope

ADR-048 PH-01–PH-05 are normative in full. UI-008 is a browser-client
extension of the existing manual image upload flow. It is not a new Runtime,
P1 asset store, P6 route, P7 schema, provider, or persistent asset library.

The active module may modify only:

```text
frontend/src/components/Workspace.tsx
frontend/src/i18n.ts
frontend/src/styles.css
frontend/tests/App.test.tsx
README.md
docs/architecture/ADR-048_Local_Customer_Photo_Tray_Proposal_v1.0.md
docs/architecture/PC-043_Local_Customer_Photo_Tray_Contract_v1.0.md
```

It may create only:

```text
frontend/src/components/PhotoTray.tsx
frontend/tests/photo_tray.test.tsx
```

No other production, test, documentation, dependency, lockfile, workflow,
launcher or user-data file may change. `frontend/src/api.ts` and `types.ts`
remain unchanged; the tray consumes the already-approved P6 client calls.

## Required behavior

The workspace exposes an explicit batch file picker and an in-memory tray of
at most 20 files. Each selected file must have an approved raster MIME type,
nonzero size and size at most 16 MiB. Invalid additions do not discard prior
tray selections or call P6. Local previews, if shown, use revocable browser
object URLs. The tray never persists filenames, URLs or bytes and explains
that selections disappear on reload or close.

For each item, the user chooses the current logo or a current section using
stable page/section IDs and presses Attach. Only then, once per action, use
the existing raw raster POST followed by the existing versioned editor PUT.
Preserve every unrelated editor field and user-authored `image_alt`. Replacing
an existing image keeps the existing manual-upload reference-aware old-asset
deletion order. Do not infer destinations, transform image bytes, create a
provider request or automatically build/export/deploy.

One attachment may be pending at a time. Lock workspace navigation during
the attempt, and never mark the tray item complete before the editor save
returns success. On upload failure retain the item. On uncertain or failed
save, retain the item and disclose that an unattached stored asset may remain;
do not automatically retry or delete it. On a changed/missing target, fail
without upload and ask the user to choose a current target. P1/P6 remain final
authorities for signature, capacity and persistence.

## Acceptance

Use deterministic local files/fake P6 responses and cover the PH-05 matrix,
including the 20/16-MiB boundaries, four MIME types, invalid additions, URL
cleanup, stable target resolution, exact upload→save order, old-image cleanup,
pending lock, rejected save, no provider/deploy calls and RU/EN guidance.
Preserve all existing frontend regressions. Run frozen pnpm install,
TypeScript, Vitest, Vite build, repository Ruff, Pyright and all discovered
Pytest; inspect exact scope/imports and require latest-head hosted CI before
routine merge. Produce one UI-008 module report and stop for Tech Lead review.

No photo analysis, automatic placement, resizing, recompression, metadata
stripping, GIF-frame conversion, persistent tray, bulk backend route or
clean-Windows acceptance is authorized by UI-008.
