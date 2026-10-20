# AURORA — Clean Windows VM Acceptance Decision v1.0

- Document ID: ADR-046
- Status: APPROVED — explicit Architecture Authority decision
- Date: 2026-10-20
- Module: QA-011 — Clean Windows VM Acceptance Protocol
- Baseline: Architecture Freeze v1.0, ADR-002/003/038, PC-031/033

## Authority and narrow precedence

The Architecture Authority confirmed that a fresh isolated Windows VM may
replace the separate physical PC previously required for first-usable Windows
acceptance. This decision supersedes only ADR-038's physical-target evidence
requirement and the corresponding wording in PC-033. The mandatory M01–M10
journey, actual live-service requirement, safety boundaries and PASS criteria
remain unchanged.

## Eligible target

The guest must be a newly provisioned or restored-to-clean Windows x64 OS
instance distinct from the developer host, not merely another host profile or
browser context. It must have no Python, uv, Node or pnpm preinstalled and no
AURORA source checkout, existing AURORA project/settings data or inherited
host credentials. Only the traceable portable artifact is transferred into
the guest. Record the Windows version, x64 confirmation, VM technology and
how the clean guest state was established. Run the entire checklist in that
guest; normal project and settings persistence must survive an AURORA process
restart within the same guest session.

An eligible Windows Sandbox session may serve as such a guest if available;
its disposable storage does not substitute for checking persistence across
the app restart. A VM on the developer host is not evidence that the app was
tested on separate physical hardware. Report the outcome as **clean-VM
acceptance**, not physical-PC acceptance.

## Unchanged limits

The operator enters any OpenAI key only in the guest application and confirms
each potentially charged call at action time. A VM does not waive Windows
security warnings, allow secret capture, turn optional Netlify publication
into a mandatory step, or authorize a public release. Failed, blocked or
unrun mandatory steps still prevent an overall PASS. Do not silently alter
the checklist results. PC-041 fixes the exact documentation scope.
