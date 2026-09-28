# AURORA — Public API Registry v1.0

A public symbol must have an owner, purpose, exact signature/type contract, consumers, and tests before implementation.

## KR-001 Canonical Concepts
Identifiers:
```text
ModuleId
SessionId
PipelineId
ServiceId
EventId
TraceId
```

Typed structured values:
```text
JSONPrimitive
JSONValue
JSONDict
Payload
Metadata
Headers
```

`RuntimeId` is not authorized.

## Runtime Layer
Exactly:
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

## DI Scopes
Exactly:
```text
Application
Session
Pipeline
Transient
```

## KR-004
RuntimeEvent mandatory fields:
```text
event_id
event_type
session_id
timestamp
payload
trace
```

RuntimeModuleManifest mandatory fields:
```text
module_id
runtime_layer
depends_on
provides
version
```

ServiceContract required lifecycle behavior:
```text
initialize()
shutdown()
```

Service implementation descriptors must express compatibility with ServiceContract; bare `type` is insufficient.

Later-wave exact classes/functions/signatures are pending compilation from the authoritative Engineering Bible and must not be invented.
