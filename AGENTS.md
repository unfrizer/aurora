# AURORA Project Instructions

## Architecture Authority

The Architecture Freeze v1.0 is the immutable architecture baseline.
The canonical Engineering Bible / Master Pack v1.1 describes that baseline.
Approved architecture resolutions, ADRs, and Wave contracts refine implementation
facts without changing the frozen layer ownership or dependency direction.

Architecture Delegation Authorization v1.0 permits Codex to create and approve
governance documents, ADRs, Wave contracts, reconciliation documents, and test
matrices when they comply with the Architecture Freeze v1.0, Master Pack v1.1,
and already approved decisions. Its canonical repository record is
`docs/architecture/ADR-001_Architecture_Delegation_Authorization_v1.0.md`.

Never redesign architecture.

## Current Phase

Waves 1–9 may be implemented in their canonical dependency order. A Wave is
implementable only when its module has a corresponding canonical **APPROVED**
contract. A reserved directory or DRAFT contract is not implementation authority.

Every Wave remains a separate module task and follows the Build Protocol below.

## Engineering Rules

* Python 3.13 only.
* Use uv.
* Use typing everywhere.
* Use dataclass or Pydantic where appropriate.
* Use logging instead of print().
* One Runtime = one owner.
* No circular dependencies.
* Output complete files only.
* Never output diffs unless explicitly requested.

## Build Contract

Every implementation response must contain:

1. Module ID.
2. Purpose.
3. Dependencies.
4. Files created.
5. Complete source code.
6. Tests.
7. Integration notes.

## Build Protocol

The canonical Build unit is:

* One module = one implementation task.

Within an active module, the Build agent may modify all explicitly owned and
authorized files. It must not modify files owned by another module.

For an active module, the Build agent must:

1. Read the applicable architecture, reconciliation, and module decisions.
2. Inspect and reconcile the current module implementation.
3. Implement all authorized files for that module.
4. Run Pyright, Ruff, and Pytest.
5. Self-repair mechanical or local implementation defects within the active
   module and rerun validation until the module is green.
6. Produce one module report and stop for Tech Lead review.

The Build agent may self-repair within the active module, including import
ordering, formatting, local typing errors, dataclass field ordering, default
factories, local imports, and contract-required local test adjustments.

The Build agent must stop and return control to Tech Lead when it encounters
an Architecture Conflict, Contract Conflict, missing authority, an ambiguity
that changes public behavior, a required RFC/ADR, or a conflict between
authoritative documents. It must not resolve those conditions by invention.

Repository-wide validation may expose failures outside the active module. Such
failures must be reported as pre-existing and must not be repaired outside the
active module.

The one-file rule applies only when a module-specific contract explicitly
requires it or Tech Lead imposes a temporary narrow scope.

## Quality Gates

Before finishing a module:

* Ruff passes.
* Pyright passes.
* Pytest passes.

## Forbidden

* Changing Runtime ownership.
* Changing architecture layers.
* Inventing new Runtime outside Engineering Bible.
* Breaking Architecture Freeze v1.0.
