# AURORA — Launcher Preferences Composition Contract v1.0

- Document ID: PC-028
- Status: APPROVED — delegated compilation of ADR-033 under ADR-001
- Module: APP-002 — Launcher Preferences Composition
- Date: 2026-10-17

## Exact ownership

APP-002 may change only `src/launcher/desktop.py`, `src/launcher/server.py`,
`tests/launcher/test_desktop.py`, `tests/launcher/test_server.py`, and
`tests/integration/test_windows_launcher.py`. It may add
`tests/integration/test_launcher_preferences.py`. ADR-033, PC-028 and a
narrow PC-013 extension note are the only architecture-document changes.
No P1/P2/P6/P8 source, other tests, frontend, dependency or workflow change.

`src.launcher` retains exactly `create_desktop_app` and `run`. The launcher
may additionally import only the public `src.preferences` gateway. Its
existing public-gateway AST guard is extended only for that gateway.

## Composition

`create_desktop_app` retains existing keyword arguments and adds
`preferences_store: PreferencesStore | None = None`, forwarding it to P6's
`create_app`. A missing injection preserves P6's sanitized 503 on preferences
routes and leaves all existing routes intact. The factory does no settings
path resolution or settings I/O, socket binding or browser launch.

The private `_serve` receives the optional injected store and forwards it
to the factory while retaining the existing prebound loopback/readiness
behavior. Production `run()` validates Windows, fixed USERPROFILE project
root and built UI before calling `default_preferences_path()` and constructing
the store, then invokes `_serve`. It does not read the settings file. Missing,
relative or unsafe LOCALAPPDATA fails with the existing sanitized startup
error before socket/browser; it does not fall back to another path. An
existing corrupt settings file does not change startup and is not reset.

## Acceptance

Tests use only synthetic UI, temporary LOCALAPPDATA/projects and fake P2
credentials. Cover explicit store injection through the composed same-origin
app; strict read/write/reopen via P6; inert factory; production fixed-path
selection without a real user-file read; missing/unsafe LOCALAPPDATA failure
before socket/browser; unchanged host/mutation gates, UI serving and socket
readiness. No uncontrolled browser, real credential, paid request or deploy.

Run Ruff, strict Pyright and full discovered Pytest. Inspect exact scope and
latest-head hosted CI. Produce one APP-002 report and stop for Tech Lead
review. React persistence remains a separate module.
