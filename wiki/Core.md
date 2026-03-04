# Core

Updated: 2026-03-04
Status: v1.5 short overview

Core is the deterministic local runtime for uDOS.

## Core Owns

- `ucode` command handling
- local filesystem/state operations
- offline diagnostics and repair surfaces
- workflow, knowledge, and command routing that can run without Wizard
- the Python side of the v1.5 TUI protocol bridge

## Core Does Not Own

- provider or cloud integrations
- web APIs or dashboards
- GitHub/network orchestration
- contributor `@dev` policy and Goblin lifecycle

Those belong to Wizard.

## Useful Operator Paths

```bash
HEALTH
VERIFY
REPAIR
WORKFLOW LIST TEMPLATES
UCODE TEMPLATE LIST
```

## Canonical Docs

- Core/runtime architecture:
  [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- Command reference:
  [../docs/howto/UCODE-COMMAND-REFERENCE.md](../docs/howto/UCODE-COMMAND-REFERENCE.md)
- Python runtime contract:
  [../docs/decisions/v1-5-python-runtime-contract.md](../docs/decisions/v1-5-python-runtime-contract.md)
- Runtime operations spec:
  [../docs/specs/PYTHON-RUNTIME-OPERATIONS-v1.5.md](../docs/specs/PYTHON-RUNTIME-OPERATIONS-v1.5.md)
