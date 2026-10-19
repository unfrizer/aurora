# AURORA — Offline Browser Image Journey Contract v1.0

- Document ID: PC-034
- Status: APPROVED — compiled from ADR-039 under ADR-001
- Module: QA-004 — Offline Browser Image Journey
- Date: 2026-10-19

## Exact ownership

QA-004 may create or change only:

```text
docs/architecture/ADR-039_Offline_Browser_Image_Journey_Decision_v1.0.md
docs/architecture/PC-034_Offline_Browser_Image_Journey_Contract_v1.0.md
tests/browser/server.py                    # valid synthetic PNG only
frontend/e2e/local-journey.spec.ts         # image journey assertions only
README.md                                  # test coverage and limit wording only
```

No application `src/`, frontend application source, other test, dependency,
lockfile, workflow, package, credential, project data or release file may
change. The existing QA-002 isolated root, fake credentials, fake provider,
loopback server and Windows CI gate must remain intact.

## Test requirements

Extend the existing one-prompt browser journey after explicit text-draft
acceptance. Review the guided image plan and visible derived prompt. Dismiss
one synthetic charge confirmation and assert zero image requests. For the logo,
accept a new confirmation, assert one image request, browser-decodable candidate,
stored-but-unattached project state, then explicitly attach and save. For a
section, require nonblank user-entered alt text, accept a separate confirmation,
review the candidate, then attach and save. Assert exactly two confirmed image
requests in total and no automatic retry.

Continue the existing editor, preview, folder/ZIP export and reopen checks.
Assert the saved editor retains both image references and section alt text,
the preview renders the synthetic image, and the folder export includes the
referenced PNG. Do not modify real user files, trigger a live service or
claim image-quality or clean-PC acceptance.

## Validation and delivery

Run frozen frontend install, TypeScript typecheck, Vitest, Vite build and the
Windows Chrome browser spec; run repository Ruff, strict Pyright and all
discovered Pytest. Review the exact diff and latest-head CI. Routine merge
under ADR-003 is permitted only after all required checks pass with no
blocking conflict/review. Report one QA-004 module and stop.
