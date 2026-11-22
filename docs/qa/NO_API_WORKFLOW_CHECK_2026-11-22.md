# No-API-charge workflow — 22 November 2026

The project owner requested usable website creation without additional API
payments. The main Projects flow now presents the existing manual ChatGPT
transfer as three visible steps: supply a brief, copy the structured prompt into
ChatGPT, then import the response as a new saved project. ChatGPT is used
separately within the user's existing access limits; AURORA does not automate
the subscription or claim unlimited generation. Photographs are attached locally.

Paid AI UI is off on each launch/reload, even when a credential already exists.
An explicitly labelled Settings checkbox enables it for the current tab only.
This is a frontend mode, not a server authorization change: existing local API
endpoints and per-request consent contracts remain in place. No project/settings
schema, Runtime ownership, dependencies or credential values were changed.

Import accepts raw JSON or one complete JSON code block. It still enforces the
one-MiB original byte limit, UTF-8 decoding, the exact P7 schema, valid unique
IDs and null image references. Prose surrounding a block, multiple blocks,
unsupported languages and malformed documents are rejected before creation.
Clipboard failure opens the complete prompt with the brief for manual copying.

## Validation

- TypeScript and Vite build passed; 208 frontend tests passed.
- Ruff and strict Pyright passed; 1952 Python tests passed. The installed
  Starlette/httpx deprecation warning remains unrelated to this frontend change.
- Nine built-Chrome journeys passed. The free workflow verifies brief copying,
  a fenced response, import, manual editing, photo attachment, folder and ZIP
  export, archive bytes, and reopening. It observed no external requests or
  local generation, credential or deployment calls.
- A separate fake-credential browser regression verifies that reload disables
  API mode even with a stored key, and that enabling it again preserves the
  stored credential. Existing fake-provider generation/error tests explicitly
  enable API mode; no live provider or paid generation was used.
- Visual inspection at 1400 and 390 pixels found and repaired compressed narrow
  navigation. A browser regression clicks Projects and Settings at 390 pixels.

Five portable-only tests were conditional skips in the source suite and then
all passed against the rebuilt EXE, including fenced JSON import, photo exports
and project/preferences persistence across process restarts. Test profiles are isolated under
ignored build directories. The real-user app was opened with the new default
mode; existing user projects and credentials were not edited for this check.

This validates local editing/export, not live ChatGPT response quality, paid API
availability, live Netlify deployment or a new clean-machine acceptance result.
