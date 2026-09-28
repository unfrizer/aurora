# KR-004 — Kernel Contracts Contract v1.0

## Files
```text
src/kernel/contracts/__init__.py
src/kernel/contracts/context.py
src/kernel/contracts/events.py
src/kernel/contracts/lifecycle.py
src/kernel/contracts/module.py
src/kernel/contracts/runtime.py
src/kernel/contracts/service.py
```

## Boundary
Contract-only.

Forbidden:
- I/O;
- network;
- threads;
- subprocesses;
- event dispatch;
- service registration;
- bootstrap;
- provider execution;
- business logic;
- global runtime mutation.

## context.py
Defines kernel execution/context contracts.
Public metadata uses canonical `Metadata` typing.
Mutable defaults require factories.

## events.py
Defines Typed Event Runtime contract.
Mandatory:
```text
event_id
event_type
session_id
timestamp
payload
trace
```
No concrete dispatch.

## module.py
Defines `RuntimeModuleManifest`:
```text
module_id
runtime_layer
depends_on
provides
version
```

## lifecycle.py
Defines lifecycle contract boundary.
Do not invent lifecycle states/transitions.

## runtime.py
Defines runtime contract only.
No concrete bootstrap.

## service.py
Defines service contract with:
```text
initialize()
shutdown()
```
Implementation descriptors must be compatible with ServiceContract.

## DI
Only:
```text
Application
Session
Pipeline
Transient
```
No DI container implementation in KR-004.

## Tests
Required:
```text
tests/kernel/test_contracts.py
```
