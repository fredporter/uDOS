# uDOS Command Reference

Version: Core v1.3.16
Updated: 2026-02-15

uDOS command ownership is split between offline Core and network-capable Wizard.

## Core (offline/local)

Core owns local command surfaces, including:

- system checks: `HEALTH`, `VERIFY`, `REPAIR`
- runtime/data: `DRAW PAT ...`, `RUN DATA ...`
- local TUI/file/workspace operations

See:

- `docs/howto/UCODE-COMMAND-REFERENCE.md`
- `docs/howto/commands/system.md`

## Wizard (integration/provider/full checks)

Wizard owns integration/provider/full-system network-aware checks.

Use:

- `WIZARD PROV ...`
- `WIZARD INTEG ...`
- `WIZARD CHECK`

See:

- `docs/howto/commands/wizard.md`
- `wiki/Wizard.md`

## No-shims policy (v1.3.16)

Removed top-level core commands hard-fail and are not remapped:

- `SHAKEDOWN`
- `PATTERN`
- `DATASET`
- `INTEGRATION`
- `PROVIDER`

Use migration targets documented in `docs/howto/UCODE-COMMAND-REFERENCE.md`.
