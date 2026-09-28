# AURORA — KR-001 Reconciliation Decision v1.0

**Document ID:** KR-001-RD-001  
**Status:** APPROVED FOR IMPLEMENTATION  
**Scope:** W1.01 Foundation Core reconciliation  
**Authority:** Tech Lead reconciliation against AB-00A

---

# 1. DECISION SUMMARY

KR-001 may proceed with the following confirmed reconciliation:

1. Canonicalize `RuntimeLayer` to the frozen L0–L8 runtime hierarchy.
2. Remove `RuntimeId` from the public canonical type surface because no approved usage exists.
3. Replace public `Metadata = dict[str, Any]` with the canonical JSON-compatible typed mapping.
4. Add `provides` to the canonical manifest-required field set.
5. Make `version.py` the single owner of duplicated project/version/architecture version facts.
6. Preserve `EventPhase`, `EventPriority`, and `RuntimeStatus` exactly as currently declared until authoritative lifecycle/event vocabulary is available.
7. Do not modify KR-002, KR-003, or KR-004 during KR-001 implementation.

---

# 2. RUNTIME LAYER DECISION

`RuntimeLayer` MUST represent exactly:

```text
L0 Kernel
L1 State
L2 Layout
L3 Theme
L4 Motion
L5 Interaction
L6 Accessibility
L7 Platform Bridge
L8 Render
```

No additional runtime-layer values are authorized.

The following values are not valid members of the canonical runtime-layer vocabulary:

```text
core
runtime
infrastructure
application
diagnostics
```

All derived runtime-layer constants must agree with this vocabulary.

The exact enum/member naming style may follow the existing Python convention, provided the semantic values remain exactly the frozen L0–L8 layers.

---

# 3. RUNTIME ID DECISION

`RuntimeId` is not used by the current approved implementation surface.

It is therefore removed from the public canonical Foundation type surface.

Do not replace it with another identity abstraction.

No new runtime identifier is introduced.

---

# 4. METADATA DECISION

The public metadata contract is JSON-compatible and explicitly typed.

Canonical conceptual types:

```text
JSONPrimitive
JSONValue
JSONDict
Metadata
```

Canonical semantic definition:

```text
JSONPrimitive =
    str | int | float | bool | None

JSONValue =
    JSONPrimitive
    | list[JSONValue]
    | dict[str, JSONValue]

JSONDict =
    dict[str, JSONValue]

Metadata =
    JSONDict
```

The implementation may use Python 3.13 recursive type-alias syntax.

The key requirement is:

```text
Metadata MUST NOT be dict[str, Any].
```

There must be one canonical metadata representation.

KR-004 must consume this type rather than defining its own competing metadata type.

---

# 5. MANIFEST FIELD DECISION

The canonical required manifest fields are exactly:

```text
module_id
runtime_layer
depends_on
provides
version
```

`provides` is mandatory.

The Foundation Core manifest field declarations must contain these five fields only as the required-field set.

Do not create a second manifest schema.

---

# 6. VERSION OWNERSHIP DECISION

`src/core/version.py` is the canonical owner for project/version/architecture version facts that are duplicated between `constants.py` and `version.py`.

Therefore:

- `version.py` remains the canonical source;
- `constants.py` must not duplicate the same facts;
- package re-exports must resolve to the canonical source;
- no competing version constants are introduced.

This is an ownership consolidation, not a new runtime architecture.

---

# 7. EVENTPHASE DECISION

Current declaration is preserved.

Do not:

- rename;
- remove;
- expand;
- contract;
- redefine semantics.

Reason:

The current authoritative material available to the implementation layer does not establish the final EventPhase vocabulary.

The absence of authority is not permission to invent a replacement.

---

# 8. EVENTPRIORITY DECISION

Current declaration is preserved.

Do not:

- rename;
- remove;
- expand;
- contract;
- redefine semantics.

Reason:

The current authoritative material available to the implementation layer does not establish the final EventPriority vocabulary.

---

# 9. RUNTIME STATUS / LIFECYCLE DECISION

Current `RuntimeStatus` declaration is preserved during KR-001.

Do not modify lifecycle vocabulary or transitions during Foundation reconciliation.

Lifecycle resolution belongs to the authoritative lifecycle contract stage.

KR-004 must not use the absence of lifecycle authority as permission to invent additional lifecycle states.

---

# 10. SCOPE OF KR-001 CHANGES

Allowed changes are limited to:

```text
src/core/types.py
src/core/constants.py
src/core/version.py
src/core/__init__.py
```

`src/core/exceptions.py` must not be redesigned as part of this reconciliation unless a concrete import/export consequence of the confirmed KR-001 changes requires a mechanical adjustment.

No KR-002/KR-003/KR-004 files may be modified.

---

# 11. PUBLIC SURFACE RULE

After reconciliation:

The public Foundation surface must expose only concepts that have a defined owner in W1.01.

Future-stage exception names may remain only where their ownership and architectural purpose are already explicitly established by the approved project contract.

Do not expand the public surface during cleanup.

---

# 12. VALIDATION

After each changed file:

```powershell
uv run pyright
uv run ruff check .
```

After all KR-001 reconciliation changes:

```powershell
uv run pytest
```

At this point, existing zero-test status is a repository testing gap, not a reason to invent Foundation tests inside the reconciliation file pass.

W1.11 will provide the executable Wave 1 test suite.

---

# 13. KR-001 APPROVAL GATE

KR-001 becomes eligible for Tech Lead approval when:

- RuntimeLayer is canonical L0–L8;
- RuntimeId is removed from the public canonical type surface;
- Metadata no longer uses `dict[str, Any]`;
- manifest required fields include `provides`;
- duplicated version facts have one owner;
- EventPhase/EventPriority/RuntimeStatus have not been invented/redefined;
- no later-stage file was modified;
- Pyright passes;
- Ruff passes.

---

# 14. NEXT AUTHORIZED ACTION

The Build agent is authorized to perform:

```text
KR-001 reconciliation
→ one production file at a time
→ validate after each changed file
→ stop on failure
```

First file:

```text
src/core/types.py
```

No other file may be modified in the first KR-001 implementation step.
