# uCODE Command Reference

Version: Core v1.3.20+
Updated: 2026-02-20

This guide is split into:
- TypeScript-backed command paths (Node runtime required)
- Python ucode command surface (core dispatcher + TUI command routing)

## Hotkey + Keymap Quick Reference

Wizard/uCLI hotkey behavior is controlled by the keymap profile and fallback parser.

- Dashboard page: `Wizard -> Hotkeys`
- API:
  - `GET /api/ucode/hotkeys`
  - `GET /api/ucode/keymap`
  - `POST /api/ucode/keymap`
- Profiles:
  - `mac-obsidian` (mac-first default)
  - `mac-terminal`
  - `linux-default`
  - `windows-default`
- Env controls:
  - `UDOS_KEYMAP_PROFILE`
  - `UDOS_KEYMAP_OS` (`mac|linux|windows`)
  - `UDOS_KEYMAP_SELF_HEAL` (`1|0|true|false`)

Example:

```bash
export UDOS_KEYMAP_PROFILE=mac-obsidian
export UDOS_KEYMAP_SELF_HEAL=1
```

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
- `DRAW --py PAT <...>` (Python-backed pattern renderer)
- `DRAW MD <mode>` or `DRAW --md <mode>` (markdown fenced diagram output)
- `DRAW --save <file.md> <mode>` (persist diagram output)
- `GRID <calendar|table|schedule|map|dashboard|workflow> [options]`
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

Current dispatcher/TUI command surface (55 commands, Core v1.3.20+).
Global strict stdlib-only enforcement is not required; this is the active Python command surface in Core.

| Command | Description |
| --- | --- |
| ANCHOR | Manage gameplay anchors, bindings, and instances |
| BACKUP | Create backup snapshots in `.compost` |
| BAG | Inventory management |
| BINDER | Binder selection and compilation |
| CLEAN | Move non-default files into `.compost` trash |
| COMPOST | Archive `.archive/.backup/.tmp/.temp` into `.compost` |
| CONFIG | Configuration menu and Wizard config access |
| DESTROY | Destructive cleanup/reset operations |
| DEV | Wizard-controlled dev mode |
| DRAW | Viewport-aware ASCII panels and patterns |
| EMPIRE | Empire extension control |
| FILE | Workspace-aware file browser (use `FILE NEW` / `FILE EDIT`) |
| FIND | Search locations by query |
| GHOST | Ghost Mode status and policy |
| GOTO | Navigate to a location |
| GRAB | Pick up objects |
| GRID | Render grid views (calendar/table/schedule/map/dashboard/workflow) |
| HEALTH | Offline core health checks |
| HELP | Command reference and search |
| LIBRARY | Library integrations: status/sync/info/list |
| LOAD | Load file or state slot |
| LOGS | Unified log viewer |
| MAP | Spatial map view |
| MIGRATE | Location data migration |
| MUSIC | Songscribe/Groovebox workflows |
| NPC | NPC list and management |
| PANEL | Location info panel |
| PLACE | Workspace/tag/location operations |
| PLAY | Gameplay command surface (stats/map/gates/toybox) |
| READ | Read file content or TS runtime documents |
| REBOOT | Hot reload handlers + restart TUI |
| REPAIR | Self-healing and maintenance checks |
| RESTORE | Restore from backups |
| RULE | IF/THEN gameplay automation rules |
| RUN | Script execution (TS/Python) |
| SAVE | Save file or state slot |
| SCHEDULER | Wizard task scheduler |
| SCRIPT | System script runner |
| SEED | Framework seed installer |
| SEND | NPC dialogue/response routing |
| SETUP | Setup profiles and providers |
| SONIC | Sonic status/sync/plan/run |
| SPAWN | Spawn objects/sprites |
| STORY | Story runtime commands |
| TELL | Rich location description |
| TIDY | Move junk files into `.compost` trash |
| TOKEN | Token generation utilities |
| UID | User identity tools |
| UNDO | Restore latest backup (undo wrapper) |
| USER | User profiles and permissions |
| VERIFY | TS runtime verification |
| VIEWPORT | Measure/cache viewport size |
| WIZARD | Wizard server management |

Notes:
- Legacy `NEW` and `EDIT` are consolidated into `FILE NEW` and `FILE EDIT`.
- `OK` is a TUI helper command routed by uCLI (not part of dispatcher contract).

### Maintenance Storage Policy (v1.3.13+)

- `BACKUP` writes to `/.compost/<date>/backups/<scope>/`
- `RESTORE` and `UNDO` read latest from `/.compost/<date>/backups/<scope>/`
- `TIDY` and `CLEAN` move files to `/.compost/<date>/trash/<timestamp>/<scope>/`
- `COMPOST` migrates older local dirs (`.archive`, `.backup`, `.tmp`, `.temp`) into `/.compost/<date>/archive/...`

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
PLAY
PLAY OPTIONS
PLAY CLAIM
RULE LIST
DRAW PAT LIST
RUN DATA LIST
WIZARD CHECK
```

## GRID Workflow Quick Example

Use the tracked sample payload under `memory/system/`:

```bash
GRID WORKFLOW --input memory/system/grid-workflow-sample.json
```

Other canonical GRID samples:

```bash
GRID CALENDAR --input memory/system/grid-calendar-sample.json
GRID TABLE --input memory/system/grid-table-sample.json
GRID SCHEDULE --input memory/system/grid-schedule-sample.json
GRID MAP --input memory/system/grid-overlays-sample.json
```

## TUI Message Themes (Non-GUI)

uCODE message wording can be lightly themed for map-level consistency.

- Scope: terminal message IO only (not GUI/CSS/webview styling)
- Base env: `UDOS_THEME=<theme>`
- TUI override: `UDOS_TUI_MESSAGE_THEME=fantasy|role-play|explorer|scientist|pilot|captain-sailor|pirate|adventure|scavenge-hunt|traveller|dungeon|foundation|galaxy|stranger-things|lonely-planet|doomsday|hitchhikers`
- Optional map-level hint: `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy|...`
- Legacy broad replacements (temporary): `UDOS_TUI_LEGACY_REPLACEMENTS=1`

## TUI Z-Layer + TOYBOX Theme Routing

Use this simple operator pattern when changing gameplay lens:

```bash
# TOYBOX dungeon profile + dungeon-style message vocabulary
PLAY TOYBOX SET hethack
export UDOS_TUI_MAP_LEVEL=dungeon
export UDOS_TUI_MESSAGE_THEME=dungeon

# TOYBOX galaxy profile + galaxy-style message vocabulary
PLAY TOYBOX SET elite
export UDOS_TUI_MAP_LEVEL=galaxy
export UDOS_TUI_MESSAGE_THEME=pilot
```

Notes:
- `PLAY TOYBOX SET ...` changes gameplay profile state.
- `UDOS_TUI_MAP_LEVEL` and `UDOS_TUI_MESSAGE_THEME` control TUI message wording.
- z/elevation (`-Zz`, `z_min`, `z_max`, stairs/ramps/portals) is spatial/map data, and should not be conflated with GUI styling.
