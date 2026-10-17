# AURORA — Offline MVP Journey Verification Decision v1.0

- Document ID: ADR-035
- Status: APPROVED — delegated verification decision under ADR-001
- Date: 2026-10-17
- Module: QA-001 — Offline Local MVP Journey

## Decision and boundary

The separately approved P1/P2/P3/P4/P6/P7/P8, launcher and React contracts now
provide the local components of the ADR-002 workflow. One additional
integration test may verify their existing public composition as a continuous
journey. The test is evidence of API and launcher behavior with fakes, not an
implementation of new product behavior or an end-user acceptance certificate.

The journey uses a temporary project root, temporary settings file, synthetic
UI bundle, fake credential store, and monkeypatched provider/deployment
boundaries. It must not contact OpenAI or Netlify, use real credentials,
launch a browser, touch a real user profile, or package/install anything.
It exercises explicit confirmed actions only. No Runtime owner, API schema,
source file, dependency, workflow, or Architecture Freeze fact changes.

PC-030 fixes exact test and README scope. README may correct the now-stale
global-settings statement while continuing to disclose the missing prebuilt
Windows distribution and live-provider/end-user acceptance. A green journey
test cannot replace those separate decisions and manual acceptance steps.
