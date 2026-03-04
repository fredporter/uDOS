# TypeScript Runtime

Updated: 2026-03-04
Status: short runtime note

The TypeScript runtime is a lightweight partner runtime in v1.5.

It does not replace the Python core.
It exists only where specific command surfaces still need a TS-backed helper path.

## Current Rule

- Python core remains authoritative for the standard runtime.
- TS helpers must not duplicate core ownership.
- Operator-facing behavior should still route through canonical `ucode` command surfaces.

## Canonical Docs

- TypeScript markdown/runtime contract:
  [../docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md](../docs/specs/TYPESCRIPT-MARKDOWN-RUNTIME-CONTRACT.md)
- Runtime operations:
  [../docs/specs/PYTHON-RUNTIME-OPERATIONS-v1.5.md](../docs/specs/PYTHON-RUNTIME-OPERATIONS-v1.5.md)
