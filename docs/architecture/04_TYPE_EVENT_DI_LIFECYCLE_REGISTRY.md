# AURORA — Type / Event / DI / Lifecycle Registry v1.0

## Python
Python 3.13.

Public contracts:
- parameterized collections;
- no implicit `Any`;
- no `Unknown`;
- no bare `dict`, `list`, `set`, or `type`;
- mutable dataclass values use `default_factory`;
- required fields precede defaulted fields;
- one canonical type for each architectural concept.

## JSON Types
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

## Runtime Event
Mandatory:
```text
event_id
event_type
session_id
timestamp
payload
trace
```

## Module Manifest
Mandatory:
```text
module_id
runtime_layer
depends_on
provides
version
```

## DI
Exactly:
```text
Application
Session
Pipeline
Transient
```

## Lifecycle
Current Foundation RuntimeStatus vocabulary is preserved during reconciliation:
```text
created
initialized
running
stopping
stopped
failed
```

Do not invent new lifecycle states or transitions while the authoritative lifecycle contract is unavailable.

## EventPhase / EventPriority
Preserve existing vocabulary until authoritative contract compilation. Do not rename, add, remove, or redefine.
