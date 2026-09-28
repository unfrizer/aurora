# AURORA — Dependency Graph v1.0

## Runtime Layer DAG
```text
L0 Kernel
  ↓
L1 State
  ↓
L2 Layout
  ↓
L3 Theme
  ↓
L4 Motion
  ↓
L5 Interaction
  ↓
L6 Accessibility
  ↓
L7 Platform Bridge
  ↓
L8 Render
```

## Wave 1 Order
```text
W1.01 Foundation
  ↓
W1.02 Configuration
  ↓
W1.03 Logging
  ↓
W1.04 Kernel Contracts
  ↓
W1.05 DI
  ↓
W1.06 Lifecycle
  ↓
W1.07 Event Bus
  ↓
W1.08 Pipeline Context
  ↓
W1.09 Orchestrator
  ↓
W1.10 Bootstrap
  ↓
W1.11 Tests
```

The order is implementation authorization order; not every adjacent stage must be a direct Python import dependency.

## Known Allowed Dependencies
- Foundation: standard library and approved foundational dependencies.
- Configuration: Foundation.
- Logging: Foundation and Configuration where required.
- Kernel Contracts: Foundation and sibling contract modules.

## Forbidden
- Lower runtime layer importing higher runtime layer.
- Contracts importing concrete DI/EventBus/Pipeline/Renderer implementations.
- ORION modules.
- Unowned utility modules.
- Cycles.

Exact later-wave file-to-file edges are intentionally not fabricated.
