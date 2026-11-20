# User actions check — 20 November 2026

## Observed defect and repair

The previously started source service ran as `CodexSandboxOffline`. It could
read default preferences but could not write the user's settings directory.
Chrome reproduced `GET /preferences = 200`, `PUT /preferences = 503`: choosing
a language left the dialog in place, with its error behind the overlay.
That process was stopped and AURORA was started as `raket`. The user-directory
preference writes, project creation and export then passed on the actual server.
No filesystem permissions or repository protections were weakened.

The initial dialog now has a close button and Escape handling. Closing before
language selection persists the existing English fallback and completed guide;
the language can be changed in Settings. Failed first-use saves appear inside
the dialog, leave actions enabled for an explicit retry, and do not claim
success. A completed guide can be closed without writing settings again.
Keyboard focus stays in the dialog and background controls are inert.

An empty credential field now disables Save key, instead of accepting a click
that does nothing. Submitted keys are still cleared from the field.
Launcher logs now show the ready URL for direct startup diagnosis.

## Executed checks

| User actions | Evidence and result |
| --- | --- |
| RU/EN selection, Start, close button, Escape, keyboard Tab, retry after 503 | Unit regressions and built-Chrome failure injection passed; real-user RU persistence and guide closing passed |
| Settings save, reload, language and configured model selection | Unit and built-Chrome tests passed; real-user settings write passed |
| Credential connect/remove and empty-field button | Built Chrome with isolated fake credential storage passed; no real key was read, changed or sent |
| Blank/manual/brief project creation; JSON file and paste import | Built-browser and portable EXE journeys passed |
| Project rename, search/clear, open, typed-name delete | Built-browser controls test passed; disposable real-user project created, reopened and deleted through UI |
| Page/section add, order, duplication and delete confirmation | Unit, manual-site browser and controls journeys passed |
| Brand, text, SEO, Save, disk reload, independent panel toggles | Unit and built-browser journeys passed |
| Photos select/drop, attach/replace/remove, logo/section references | Existing unit/browser journeys and portable import/photo/export journeys passed |
| Desktop/mobile preview and open preview tab | Built-browser journeys passed; actual-user saved preview passed |
| Folder and ZIP export, artifact contents and bytes, reopen | Built-browser and portable EXE journeys passed; actual-user ZIP exported successfully |
| AI draft/image generation, review, acceptance, locks and error paths | Unit tests and built-browser journeys passed using isolated fake providers; no paid live request was made |
| Deploy confirmation, cancellation and failure recovery | Unit tests and browser cancellation passed; no live deployment was made |

Final local results: TypeScript/Vite build passed; 190 frontend tests passed;
Ruff and Pyright passed; 1914 Python tests passed (one installed Starlette
deprecation warning). The standard browser suite passed eight journeys and
conditionally skipped five portable-only journeys. Those same five portable
journeys were then explicitly run against the rebuilt EXE and all passed,
including state/preferences verification after process restarts.

The real-user browser check recorded no JavaScript errors or HTTP errors.
Only its own clearly named disposable project was removed; existing user
projects were not modified. Temporary evidence is under ignored `build/`.

These checks cover the implemented controls and exercised failure paths. They
do not certify every possible input, a clean Windows installation, a paid
OpenAI account/model combination or a live Netlify deployment.
