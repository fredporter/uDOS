# uDOS Command Reference

Version: Core v1.3.16
Updated: 2026-02-15

uDOS command ownership is split between offline Core and network-capable Wizard.

## Core (offline/local)

Core owns local command surfaces, including:

- system checks: `HEALTH`, `VERIFY`, `REPAIR`
- runtime/data: `DRAW PAT ...`, `RUN --ts DATA ...`, `READ --ts ...`
- local TUI/file/workspace operations (`PLACE`, `SEND`, `SAVE/LOAD --state`, `TOKEN`, `GHOST`)

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

Removed top-level core commands are not remapped:

- `SHAKEDOWN`
- `PATTERN`
- `DATASET`
- `INTEGRATION`
- `PROVIDER`

Use migration targets documented in `docs/howto/UCODE-COMMAND-REFERENCE.md`.

## Legacy Pages (Archived)

The following v1.1-era pages were archived to:

- `/.compost/<date>/archive/docs/.archive/2026-02-17-archived-docs/howto/commands/`

Redirect stubs remain at the original paths:

- `docs/howto/commands/navigation.md`
- `docs/howto/commands/content.md`
- `docs/howto/commands/interface.md`
- `docs/howto/commands/maintenance.md`
- `docs/howto/commands/transport.md`
- `docs/howto/commands/user.md`
- `docs/howto/commands/wellbeing.md`
