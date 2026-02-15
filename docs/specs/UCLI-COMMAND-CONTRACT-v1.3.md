# uCLI Command Contract (v1.3.16)

## Policy

- No shims.
- No backward compatibility aliases for removed uCODE commands.
- Contract-driven command exposure and dispatch.

## Source of truth

- `/Users/fredbook/Code/uDOS/core/config/ucli_command_contract_v1_3_16.json`

## Launcher subcommands

Allowed:

- `help`
- `tui`
- `wizard`
- `prompt`
- `cmd`

Removed launcher aliases:

- `core` -> use `tui`
- `server` -> use `wizard`
- `command` -> use `cmd`
- `run` -> use `cmd`

## uCODE dispatch contract

- Allowlist is loaded from contract in `/Users/fredbook/Code/uDOS/wizard/routes/ucode_contract_utils.py`.
- `/Users/fredbook/Code/uDOS/wizard/routes/ucode_routes.py` treats contract entries as authoritative.
- Commands not in contract are not exposed through uCLI command metadata.

## Core vs Wizard ownership

Core-owned command checks:

- `HEALTH` (offline stdlib/local checks)
- `VERIFY` (TS runtime checks)

Wizard-owned command checks:

- provider flows via `WIZARD PROV ...`
- integration flows via `WIZARD INTEG ...`
- full Wizard-side shakedown via `WIZARD CHECK`

## Removed top-level core commands (hard fail)

- `SHAKEDOWN`
- `PATTERN`
- `DATASET`
- `INTEGRATION`
- `PROVIDER`
- `PROVIDOR` (typo, not accepted)

## Migration mapping

- `SHAKEDOWN` -> `HEALTH` or `VERIFY` (core), `WIZARD CHECK` for full network/provider checks
- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`
- `INTEGRATION ...` -> `WIZARD INTEG ...`
- `PROVIDER ...` -> `WIZARD PROV ...`

## Behavior

- Removed commands return explicit errors (not remapped).
- Capability-gated commands remain hidden/blocked unless required modules/services are available.
