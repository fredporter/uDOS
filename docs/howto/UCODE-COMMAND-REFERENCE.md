# uCODE Command Reference

Version: Core v1.3.16+
Updated: 2026-02-15

This guide is split into:
- TypeScript-backed command paths (Node runtime required)
- Python ucode command surface (core dispatcher + TUI command routing)

## TypeScript Command Set

These commands execute via TS/Node runtime components.

- `RUN --ts <file> [section_id]`
- `RUN --ts PARSE <file>`
- `RUN --ts DATA LIST`
- `RUN --ts DATA VALIDATE <id>`
- `RUN --ts DATA BUILD <id> [output_id]`
- `RUN --ts DATA REGEN <id> [output_id]`
- `READ --ts <file>`
- `STORY <file>`
- `STORY PARSE <file>`
- `STORY NEW <name>`
- `SCRIPT RUN <name>`
- `DRAW PAT LIST`
- `DRAW PAT CYCLE`
- `DRAW PAT TEXT "<text>"`
- `DRAW PAT <pattern-name>`
- `GRID <calendar|table|schedule|map|dashboard> [options]`
- `VERIFY`

## Script Policy (Mobile Default)

uDOS-flavored markdown scripts now run in mobile-safe mode by default.

- Default: script fences cannot execute stdlib ucode command lines.
- Explicit opt-in: add `allow_stdlib_commands: true` in markdown frontmatter.
- Applies to `RUN`, `SCRIPT RUN`, and system script execution paths.

Example frontmatter:

```yaml
---
title: Startup Script
allow_stdlib_commands: true
---
```

## Python ucode Commands (Core Surface)

Current dispatcher/TUI command surface:
Global strict stdlib-only enforcement is not required; this is the active Python command surface in Core.

- `ANCHOR`
- `BACKUP`
- `BAG`
- `BINDER`
- `CLEAN`
- `COMPOST`
- `CONFIG`
- `DESTROY`
- `DEV`
- `DRAW`
- `EDIT`
- `EMPIRE`
- `FILE`
- `FIND`
- `GHOST`
- `GAMEPLAY`
- `GOTO`
- `GRAB`
- `GRID`
- `HEALTH`
- `HELP`
- `LOAD`
- `LOGS`
- `MAP`
- `MIGRATE`
- `MUSIC`
- `NEW`
- `NPC`
- `OK` (TUI-routed AI/local helper command)
- `PANEL`
- `PLACE`
- `READ`
- `REBOOT`
- `REPAIR`
- `RESTORE`
- `RUN`
- `SAVE`
- `SCHEDULER`
- `SEND`
- `SCRIPT`
- `SEED`
- `SETUP`
- `SONIC`
- `SPAWN`
- `STORY`
- `TELL`
- `TIDY`
- `TOKEN`
- `UID`
- `UNDO`
- `USER`
- `VERIFY`
- `VIEWPORT`
- `WIZARD`

## Wizard-Owned Flows

Provider/integration/full network checks are Wizard-owned.

```bash
WIZARD PROV LIST
WIZARD PROV STATUS
WIZARD INTEG status
WIZARD CHECK
```

## SONIC Parity Quick Reference

Core command:
- `SONIC STATUS`
- `SONIC SYNC [--force]`
- `SONIC PLAN ...`
- `SONIC RUN ... --confirm`

Wizard API equivalents:
- `GET /api/platform/sonic/status`
- `POST /api/sonic/db/rebuild` (or `POST /api/sonic/sync`)
- `POST /api/platform/sonic/build`

## Removed Top-Level Commands

These are removed from the canonical command surface:

- `SHAKEDOWN`
- `PATTERN`
- `DATASET`
- `INTEGRATION`
- `PROVIDER`

Migration targets:

- `SHAKEDOWN` -> `HEALTH` or `VERIFY` (core), `WIZARD CHECK` (full checks)
- `PATTERN ...` -> `DRAW PAT ...`
- `DATASET ...` -> `RUN DATA ...`
- `INTEGRATION ...` -> `WIZARD INTEG ...`
- `PROVIDER ...` -> `WIZARD PROV ...`

## Quick Checks

```bash
HEALTH
VERIFY
GAMEPLAY
DRAW PAT LIST
RUN DATA LIST
WIZARD CHECK
```

## TUI Message Themes (Non-GUI)

uCODE message wording can be lightly themed for map-level consistency.

- Scope: terminal message IO only (not GUI/CSS/webview styling)
- Base env: `UDOS_THEME=<theme>`
- TUI override: `UDOS_TUI_MESSAGE_THEME=fantasy|role-play|explorer|scientist|dungeon|foundation|galaxy|stranger-things|lonely-planet|doomsday|hitchhikers`
- Optional map-level hint: `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy|...`
- Legacy broad replacements (temporary): `UDOS_TUI_LEGACY_REPLACEMENTS=1`
