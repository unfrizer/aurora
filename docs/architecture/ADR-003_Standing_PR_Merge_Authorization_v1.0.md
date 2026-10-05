# AURORA — Standing PR and Merge Authorization v1.0

**Document ID:** ADR-003  
**Status:** APPROVED — GOVERNANCE ONLY  
**Authority:** Explicit project-owner authorization, 2026-10-05  
**Scope:** Routine pull-request creation and merge for authorized AURORA tasks

## Authorization Record

The Architecture Authority confirmed merge of PR #14 and added:

> подтверждаю, так же разрешаю подтверждать за меня в дальнейшем

This is standing user authorization for the ordinary project-workflow
confirmations previously requested for AURORA PR creation and merge. It is not
a claim that the user personally reviewed future changes, nor permission to
submit a fabricated human review.

## Decision

For tasks already authorized by the user and their applicable approved contracts,
Codex may create, update and merge pull requests in `unfrizer/aurora` without
asking again for a separate routine PR/merge acknowledgement, subject to all
conditions below:

1. The exact task scope and canonical ownership are established. The change
   complies with Architecture Freeze v1.0, Master Pack v1.1 and applicable
   approved resolutions/contracts.
2. Codex inspects the final diff, reports the result, and preserves unrelated
   user changes. The module-task boundary and Build Protocol remain in force.
3. Required Ruff, strict Pyright and discovered Pytest tests pass. Required
   hosted CI for the latest head commit passes. Missing, pending, failed or
   cancelled required checks are not treated as success.
4. The pull request has no unresolved conflict or blocking review. Normal
   repository protections apply; this authorization is not an admin bypass.
5. The merge target and head are verified before merge. Every created PR is
   attached to the task, and the actual merge result is verified afterward.
6. PR descriptions/reports identify Codex's checks and this delegation honestly.
   Codex must not submit an approval purporting to be an independent human code
   review or certify user acceptance tests that were not performed.

Codex may make the documentation-only PR for this authorization and merge it
under the same conditions. It does not require another conversational approval
to record the permission already supplied by the user.

## Explicit Limits

- This standing authorization does not approve K-01–K-05 in RCN-001. The request
  remains DRAFT, and the unresolved Kernel contracts remain unresolved.
- It does not grant implementation authority to DRAFT contracts or expand the
  architecture-document approval powers defined in ADR-001.
- Architecture Conflict, Contract Conflict, missing authority, public-behavior
  ambiguity or a conflicting authoritative document still requires STOP and
  an explicit decision. Merge permission cannot supply that decision.
- Runtime ownership, L0–L8, public event/lifecycle/DI vocabularies, module file
  ownership and all unaffected approved decisions remain unchanged.
- No force push, destructive reset, branch-protection change, bypass, security
  weakening, unrelated repository change or permanent deletion is authorized.
- No new credentials/permissions, secret disclosure, paid API request, production
  deploy, release publication or user-data migration is authorized merely by
  this PR/merge delegation.
- Mandatory action-time confirmations, user handoffs and safety restrictions
  imposed by the execution environment still apply. Codex cannot confirm those
  on the user's behalf.

## Limited Precedence

ADR-003 supersedes only ADR-001's requirement for a new, separate user
confirmation for each routine PR creation and merge within this defined scope.
All other ADR-001 rules and the Build Protocol remain unchanged.

AGENTS.md records this narrow exception. ADR-001 remains the architecture
delegation record; it is not replaced or silently rewritten.

## Revocation

The user may withdraw or narrow this standing authorization at any time.
Later explicit user restrictions take precedence for the affected task.

## Validation and Acceptance

This governance task modifies no production source, tests, dependency versions,
CI workflows or repository security settings. Completion requires a documentation
diff review, passing repository validation, passing latest-commit hosted CI, and
a verified merge through the normal protected workflow.
