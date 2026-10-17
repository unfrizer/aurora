# AURORA — Launcher Preferences Composition Decision v1.0

- Document ID: ADR-033
- Status: APPROVED — delegated compilation of ADR-002, ADR-031 and ADR-032 under ADR-001
- Date: 2026-10-17
- Module: APP-002 — Launcher Preferences Composition

## Decision boundary

ADR-002 owns the fixed Windows settings location. ADR-031 gives the
credential-free document to P8. ADR-032 PA-04 deliberately reserves launcher
injection as a separate task after P6-009. PC-027 makes an explicitly injected
`PreferencesStore` optional in P6. This decision composes those already
approved boundaries without changing L0–L8, P1, P2, P6, or P8 ownership.

APP-002 supplies the P8 store through the launcher to P6. The testable
`create_desktop_app` factory accepts an optional explicit store and preserves
existing callers. It never resolves a default profile location or reads
settings on construction. Production `run()` resolves only P8's public
`default_preferences_path()` after validating the Windows profile and built
UI, constructs `PreferencesStore`, then binds the loopback socket. No
preferences file is read or written during startup; a missing file remains
the P8 default. Invalid LOCALAPPDATA fails startup safely before socket or
browser. An existing damaged file is reported only through P6's sanitized
preferences API failure, never silently replaced.

The project root stays server-owned and read-only in P6's successful GET.
No custom directory, provider setting, secret storage, frontend change,
background service or new dependency is introduced. PC-028 fixes the exact
APP-002 file and acceptance boundary. A conflicting frozen architecture fact
requires reconciliation rather than an override by this document.
