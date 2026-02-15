# uDOS Wiki

Version: v1.3.16
Last Updated: February 15, 2026

Welcome to the uDOS wiki.

## Quick Start

1. [Home](Home.md)
2. [Installation](Installation.md)
3. [Core](Core.md)
4. [Wizard](Wizard.md)

## Core/Wizard split (v1.3.16)

- Core owns offline/local command surfaces.
- Wizard owns provider/integration/full-system network-aware checks.
- No command shims for removed core commands.
- Canonical command surfaces include `PLACE`, `SEND`, `RUN --ts|--py`, `READ --ts`, and `REBOOT`.

Core checks:

```bash
HEALTH
VERIFY
```

Wizard checks:

```bash
WIZARD CHECK
WIZARD PROV STATUS
WIZARD INTEG status
```

## Documentation

- [Core](Core.md)
- [Wizard](Wizard.md)
- [TUI Z-Layer, TOYBOX, and Theme Switching](TUI-Z-Layer-and-TOYBOX.md)
- [TypeScript Runtime](TypeScript-Runtime.md)
- [uCODE Command Reference](../docs/howto/UCODE-COMMAND-REFERENCE.md)

## Notes

For canonical command allowlist and policy, see:

- `/Users/fredbook/Code/uDOS/core/config/ucli_command_contract_v1_3_16.json`
- `/Users/fredbook/Code/uDOS/docs/specs/UCLI-COMMAND-CONTRACT-v1.3.md`
