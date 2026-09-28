# AURORA — Module Interaction Matrix v1.0

**Status:** ACTIVE  
**Scope:** Wave 1

## Module Matrix

| Module | Produces | Consumes | Owns |
|---|---|---|---|
| W1.01 Foundation | canonical types/constants/version/exceptions | stdlib | foundation definitions |
| W1.02 Config | settings/config access | Foundation | configuration data |
| W1.03 Logging | logging API/config/context | Foundation + Config where approved | logging infrastructure |
| W1.04 Contracts | runtime/context/event/module/service/lifecycle contracts | Foundation | public runtime contracts |
| W1.05 DI | service resolution | W1.04 + Foundation | DI scopes/ownership |
| W1.06 Lifecycle | concrete lifecycle | W1.05 + W1.04 | lifecycle transitions |
| W1.07 Event Bus | event registration/dispatch | W1.04 + lifecycle/DI as approved | event delivery |
| W1.08 Pipeline Context | pipeline execution context | lower approved runtime services | pipeline context |
| W1.09 Orchestrator | pipeline orchestration | pipeline context + approved runtime services | orchestration |
| W1.10 Bootstrap | application composition | approved lower modules | composition/bootstrap |
| W1.11 Tests | verification | all approved Wave 1 modules | test evidence |

## Contract Flow

```text
Foundation
   ↓
Configuration / Logging
   ↓
Kernel Contracts
   ↓
DI
   ↓
Lifecycle
   ↓
Event Bus
   ↓
Pipeline Context
   ↓
Orchestrator
   ↓
Bootstrap
```

## Important

The arrows describe architecture and implementation order. They do not authorize every module to import every previous module.

Exact import edges must be listed per file.

## No Reverse Dependencies

Forbidden examples:

```text
Foundation → DI
Foundation → Event Bus
Contracts → Pipeline
Contracts → Renderer
DI → Theme
Lifecycle → Render
Render → mutable runtime owner
```

## Cross-File API Rule

Use exact public symbols.

Do not import private implementation details from another module.

Do not reach through a package using undocumented internals.
