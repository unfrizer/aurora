# AURORA — Offline Browser Preferences and Guide Decision v1.0

- Document ID: ADR-041
- Status: APPROVED — delegated test decision under ADR-001
- Date: 2026-10-20
- Module: QA-006 — Offline Browser Preferences and Guide Journey
- Baseline: Architecture Freeze v1.0, ADR-003/031/034/037/040, PC-029/032/035

## Decision and boundary

QA-002 confirms first-use Russian selection and that onboarding stays closed
after a page reload. The browser gate does not yet exercise the Settings
language switch or the explicit reopening of the guide. QA-006 extends that
same isolated fake-service Chrome journey to verify the existing P8/P6/UI-006
preferences flow end to end. It changes no application source, API, settings
schema, Runtime, dependency, workflow, provider or user data.

After the project journey, the test switches from Russian to English through
Settings Save, reads only the isolated test settings file to confirm language
and completed-guide persistence, reloads the page, reopens the guide from the
toolbar, closes it, and reloads again. It must observe English UI throughout
and ensure the fake API key does not enter settings. A page reload is not an
application-process restart or clean-PC acceptance.

PC-036 fixes exact ownership and validation. QA-003 manual acceptance remains
outstanding; no real credential, OpenAI request, Netlify request or release
claim is authorized by this test decision.
