# AURORA — Architecture Delegation Authorization v1.0

**Document ID:** ADR-001  
**Status:** APPROVED  
**Authority:** Architecture Authority delegation, 29 September 2026  
**Scope:** Governance and implementation authorization for Waves 1–9

## Decision

The Architecture Authority delegates to Codex the ability to maintain AURORA's
implementation-facing architecture documentation and to advance the project
through Waves 1–9, without changing the Architecture Freeze v1.0.

Codex may create and amend governance documents, ADRs, reconciliation records,
test matrices, and Wave contracts under `docs/architecture/`. Codex may mark a
prepared Wave contract **APPROVED** only when it is consistent with the
Architecture Freeze v1.0, canonical Master Pack v1.1, and all earlier approved
decisions.

For each approved module, Codex may create a branch, implement only that
module's authorized files, run Ruff, Pyright, and Pytest, commit, and push.
Creating a pull request and merging it require separate explicit confirmation
from the Architecture Authority.

## Defaults for Missing Detail

When the authoritative documents do not specify a detail, Codex may use only
these defaults:

- Python 3.13 and uv with strict typing;
- immutable dataclasses for public snapshots and contracts;
- deterministic in-memory behavior;
- no network, persistence, provider integration, background task, global
  mutable state, or new dependency;
- no change to lower-layer ownership;
- no extension of RuntimeLayer, RuntimeStatus, EventPhase, EventPriority, or
  dependency-injection scope vocabularies.

If these defaults cannot resolve the missing detail without changing public
behavior or the frozen architecture, Codex must stop and request a decision.

## Product Direction

The intended product is a Windows-focused visual workspace for creating and
managing a digital business from one prompt. It ultimately includes project and
brand generation, site/content/image/SEO generation, editable workspace and
preview, bilingual RU/EN experience, onboarding, project saving/reopening, and
export/deployment.

Persistence, network access, and external integrations are product goals, but
they require future approved contracts that preserve runtime ownership and
layer direction. They are not implicitly authorized for an otherwise
in-memory-only module.

## Constraints

The authorization does not permit mobile apps, multi-user enterprise features,
plugin ecosystems, autonomous operation of a real business, unrelated business
systems, implementation of a merely reserved runtime, or bypassing the
Architecture Freeze for MVP speed.

## Consequence

`AGENTS.md` is amended so that its current phase is no longer limited to Wave
1, while retaining the requirement for one approved contract per module.
