# uCLI Command Contract (v1.3)

## Policy

- No shims.
- No backward compatibility aliases.
- Contract-driven command exposure and dispatch.

## Source of truth

- `core/config/ucli_command_contract_v1_3.json`

## Launcher subcommands

Allowed:

- `help`
- `tui`
- `wizard`
- `prompt`
- `cmd`

Removed aliases:

- `core` -> use `tui`
- `server` -> use `wizard`
- `command` -> use `cmd`
- `run` -> use `cmd`

## uCODE dispatch commands

- Allowlist is loaded from contract in `wizard/routes/ucode_contract_utils.py`.
- `wizard/routes/ucode_routes.py` treats contract entries as authoritative.
- Commands not in contract are not exposed through uCLI command metadata.

Removed aliases (hard fail):

- `GOBLIN` -> use `DEV`
- `WIZ` -> use `WIZARD`

## Behavior

- Deprecated aliases return explicit error (not remapped).
- Capability-gated commands remain hidden/blocked unless required modules/services are available.
