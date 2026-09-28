# KR-001 — Foundation Core Contract v1.0

## Files
```text
src/core/__init__.py
src/core/constants.py
src/core/exceptions.py
src/core/types.py
src/core/version.py
```

## Responsibilities
- foundational types;
- foundational constants;
- foundational exceptions;
- project/version metadata.

Must not implement configuration, logging, DI, Event Bus, pipeline, or bootstrap.

## Confirmed Decisions

### RuntimeLayer
Exactly L0–L8:
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

### RuntimeId
Remove from public canonical types.

### Metadata
`Metadata = JSONDict`, with recursively JSON-compatible values. Must not be `dict[str, Any]`.

### Manifest Fields
Exactly:
```text
module_id
runtime_layer
depends_on
provides
version
```

### Version Ownership
`src/core/version.py` is the canonical owner of duplicated project/version/architecture version facts. `constants.py` must not define competing copies.

### EventPhase / EventPriority / RuntimeStatus
Preserve current vocabulary. Do not redefine during KR-001.

## Acceptance
- canonical L0–L8;
- no RuntimeId;
- JSON-compatible public Metadata;
- manifest includes `provides`;
- one owner for version facts;
- no later-stage implementation;
- no changes outside KR-001.
