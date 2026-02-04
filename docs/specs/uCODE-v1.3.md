---
title: uCODE - Unified Terminal TUI (v1.3)
version: v1.3.0
status: Draft
date: 2026-02-04
---

# uCODE v1.3 — Unified Terminal TUI

uCODE is the single-entry Terminal TUI for uDOS. In v1.3 it stays **offline-first** and **component-aware**, while separating command ownership by **Core**, **Wizard**, and **Extensions**.

## Goals in v1.3

- Preserve the v1.2 setup story flow (same `SETUP` experience and fields).
- Keep Core commands local-only, deterministic, and usable without Wizard.
- Treat Wizard commands as network/integration only.
- Mark extension-bound commands explicitly (Groovebox/Songscribe, Sonic, Empire).
- Make TS runtime and shell workflows first-class in docs (rendering, indexing, scripts).

## Entry Points (Shell)

```bash
python uDOS.py                 # main entry
python -m core.tui.ucode        # direct module
./bin/Launch-uCODE.command      # macOS launcher
```

## Command Ownership Model

Use this split everywhere (docs + implementation):

| Component | Owns | Notes |
| --- | --- | --- |
| Core | Offline commands, vault operations, local state | No network; deterministic output |
| Wizard | Network, auth, integrations, plugin repo | Requires Wizard server running |
| Extensions | Feature modules (Sonic/Groovebox/Empire) | Only available if extension installed |

If a command depends on Wizard or an extension, the handler must fail gracefully in core-only mode.

## uCODE Meta Commands (Always Available)

- `STATUS` — component detection and health summary
- `HELP` — uCODE help
- `VIBE` — Vibe CLI integration commands (chat/context/history/config)
- `PROMPT` — prompt debugging and shortcuts
- `FKEYS`, `FKEY`, `F` — function key mapping view
- `EXIT`, `QUIT` — exit uCODE

Conditional uCODE commands (only when available):

- `WIZARD <cmd>` — Wizard control and status
- `PLUGIN <cmd>` — Plugin catalog management
- `EXT <cmd>` — Alias for `PLUGIN`

## Core Command Inventory (v1.2 Baseline, Python/TUI)

Navigation
- `MAP` — render grid map view
- `PANEL` — open panel UI
- `GOTO` — navigate to location
- `FIND` — search files or locations

Information
- `TELL` — system info
- `HELP` — core help

Game/State
- `BAG` — inventory
- `GRAB` — take item
- `SPAWN` — spawn entity
- `SAVE` — save state or file
- `LOAD` — load state or file

System
- `SHAKEDOWN` — run system diagnostics
- `REPAIR` — repair runtime
- `RESTART` / `REBOOT` — restart workflows
- `RELOAD` — hot reload watcher
- `SETUP` — setup story flow (preserved from v1.2)
- `UID` — user identity management
- `PATTERN` — ANSI/grid pattern generator
- `LOGS` — view logs
- `HOTKEYS`, `HOTKEY` — hotkey viewer
- `DEV`, `DEV MODE` — dev mode controls

User
- `USER` — profile/permissions

Cleanup
- `DESTROY` — cleanup with wipe options
- `UNDO` — restore from backup

Migration
- `MIGRATE` — SQLite/location migration

Seed
- `SEED` — seed data install

NPC/Dialogue
- `NPC` — NPC commands
- `TALK`, `REPLY` — dialogue flow

Wizard-bound (Core dispatch, Wizard required)
- `CONFIG` — settings management
- `PROVIDER` — model/provider config
- `INTEGRATION` — integration tasks
- `WIZARD` — Wizard lifecycle control

Binder
- `BINDER` — binder pick/compile/chapters

Runtime
- `STORY` — run story-format docs
- `RUN` — execute markdown via TS runtime (`RUN <file>` / `RUN PARSE <file>`)

Data
- `DATASET` — list/validate/build datasets

Files
- `FILE` — file operations
- `NEW`, `EDIT` — file editor

Maintenance
- `BACKUP`, `RESTORE`, `TIDY`, `CLEAN`, `COMPOST`

## Wizard Commands (uCODE + Wizard CLI)

`WIZARD` subcommands (from `core/commands/wizard_handler.py`):

- `WIZARD START`
- `WIZARD STOP`
- `WIZARD STATUS`
- `WIZARD REBUILD`

Shell equivalents:

```bash
python -m wizard.server --no-interactive
curl http://localhost:8765/health
```

## Vibe Commands (Integrated)

```
VIBE CHAT <prompt> [--no-context] [--model <name>] [--format text|json]
VIBE CONTEXT [--files a,b,c] [--notes "..."]
VIBE HISTORY [--limit N]
VIBE CONFIG
VIBE ANALYZE <path>
VIBE EXPLAIN <symbol>
VIBE SUGGEST <task>
```

Notes:
- Goblin endpoints are preferred for local dev: `http://localhost:8767/api/dev/vibe/*`
- Wizard endpoints are used if Goblin is unavailable: `http://localhost:8765/api/ai/*`
- Wizard may require `WIZARD_ADMIN_TOKEN`

## NL Routing (Prototype)

```
NL ROUTE <prompt> [--dry-run] [--no-context]
```

## Extension-Bound Commands

These only work if the extension exists (or a Wizard endpoint exists):

- `SONIC` — Sonic USB planning/build (extension + Sonic repo required)
- `MUSIC` — Songscribe/Groovebox actions (Wizard endpoints required)
- `EMPIRE` — planned, not yet wired in core

Extension command modules live under:

```
extensions/<extension>/commands/
extensions/<extension>/manifest.json
```

Core should only provide thin stubs that check availability and route to the extension when installed.

## TS Runtime + Markdown Processing (v1.3)

Core must parse Markdown and process data deterministically. In v1.3:

- `RUN <file>` uses the **TS runtime** through `TSRuntimeService`.
- Publishing uses the **TS renderer CLI** (`core/src/renderer/cli.ts`).
- Task indexing uses the **TS task indexer CLI** (`core/src/tasks/cli.ts`).

Renderer CLI:

```bash
node core/dist/renderer/cli.js --theme prose --vault ./vault --output ./vault/_site
```

Task indexer CLI:

```bash
node core/dist/tasks/cli.js --vault ./vault --db ./vault/.udos/state.db
```

Markdown scripting pattern (summary):

```markdown
---
state:
  count: 1
---

# Example

~~~set
count = count + 1
~~~

~~~if
count > 1
~~~

Count is now {{count}}.
```

For the full grammar and block types, see `docs/specs/typescript-markdown-runtime.md`.

## Vibe CLI + Shell Workflows

Common shell/Vibe integrations (v1.3 planning):

- `vibe chat` / `vibe --with-context` for local-first prompts.
- Goblin dev proxy: `/api/dev/vibe/*`.
- Wizard Vibe service: `/api/ai/complete` when enabled.

Roadmap alignment lives in:

- `VIBE-CLI-ROADMAP-ALIGNMENT.md`
- `VIBE-CLI-INTEGRATION-SUMMARY.md`

## v1.2 Command Inventory vs TS/Shell Equivalents

Where a TS or shell workflow exists, use it; otherwise the Python TUI remains canonical.

| Command | Component | TS/Shell Equivalent |
| --- | --- | --- |
| `RUN` | Core | TS runtime via `TSRuntimeService` (same runtime under the hood) |
| `DATASET` | Core | None (Python only) |
| `BINDER` | Core | Wizard `/api/binder/*` endpoints |
| `WIZARD` | Wizard | `python -m wizard.server` |
| `REPAIR` | Core | `bin/udos-self-heal.sh` |
| `BACKUP`/`RESTORE` | Core | Shell + tar/gzip under the hood |
| `RENDER` (no command) | Core | `node core/dist/renderer/cli.js` |
| `TASK INDEX` (no command) | Core | `node core/dist/tasks/cli.js` |

If a command has no TS/shell equivalent, keep it under Core.

## Link Updates

uCODE v1.3 replaces the v1.2 manual. All new references should point to:

- `docs/specs/uCODE-v1.3.md`
