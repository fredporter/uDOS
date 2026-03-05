# uCODE Command Reference

Version: Core v1.5+
Updated: 2026-03-04

This guide covers uDOS commands (ucode) which are **backend services**, not UI features.

Offline operations runbook:
- `docs/howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md`

Certified v1.5 demo pack:
- `docs/examples/ucode_v1_5_release_pack/README.md`

## Multi-Context Command Execution

uDOS commands execute in multiple contexts. Commands are **case-insensitive** —
outputs appear in CAPS for display clarity only.

### 1. ucode / Operator Direct Commands (v1.5+ — Primary Interactive Path)

Run ucode commands directly from the standard runtime. The external Dev Mode
contributor tool remains a contributor-only surface. Three input styles are
supported:

#### `:command` — Colon prefix (recommended, always ucode)
```
:map
:health
:find tokyo
:status
:help
:sonic status
:file select --workspace @vault
```
The colon prefix **always routes to ucode**, bypassing contributor-tool built-ins. Use this
for commands that share a name with a contributor-tool slash command (`help`, `config`,
`status`) or whenever you want unambiguous ucode dispatch regardless of casing.

#### `/command` — Slash prefix (complementary, contributor-tool built-ins take priority)
```
/map
/health
/find tokyo
/sonic status
/library list
```
The slash prefix follows the existing contributor-tool priority chain: built-in
commands are checked first (`/help`, `/config`, `/status`), then ucode picks up
the rest. Works for 57 of the 60 ucode commands without any conflict.

| Slash input | Routes to | Reason |
|---|---|---|
| `/map` | ucode MAP | Not a contributor-tool built-in |
| `/health` | ucode HEALTH | Not a contributor-tool built-in |
| `/sonic` | ucode SONIC | Not a contributor-tool built-in |
| `/help` | **Dev Mode tool `/help`** | Contributor-tool built-in wins |
| `/config` | **Dev Mode tool `/config`** | Contributor-tool built-in wins |
| `/status` | **Dev Mode tool `/status`** | Contributor-tool built-in wins |

Use `:help`, `:config`, `:status` to reach the ucode versions of those three.

#### Plain command (no prefix)
```
map
health
FIND tokyo
MAP --list
STATUS
```
- **Single-word input** (any case): dispatched to ucode if the word exactly
  matches a command — `health`, `Health`, `HEALTH` all work.
- **Multi-word input**: the first word must be ALL-CAPS to prevent natural
  language from being accidentally intercepted. Use `:` or `/` prefix for
  lowercase multi-word commands.

| Input | Routes to | Reason |
|---|---|---|
| `health` | ucode HEALTH | Single word — unambiguous |
| `map` | ucode MAP | Single word |
| `FIND tokyo` | ucode FIND | Multi-word, first word ALL-CAPS |
| `:find tokyo` | ucode FIND | Colon prefix |
| `find me a file` | **OPERATOR** | Multi-word, lowercase first word — natural language |
| `help me with this` | **OPERATOR** | Multi-word, lowercase — goes to operator planning |

### 2. Operator Interactive
```bash
ucode
# User: "show me the map"
# → OPERATOR infers intent → routes to ucode MAP guidance
```

### 3. Dev Mode Contributor Tooling
```bash
vibe
# User: "!ucode MAP"
# → Executes shell command via Dev Mode tooling
```

Dev Mode use is valid only when the `dev` profile is enabled and the `@dev` workspace scaffold at `/dev` is installed and activated through Wizard-managed controls. The external contributor tool is not a peer standard runtime.

### 4. Shell/Script Execution
```bash
# Canonical shared runtime
UV_PROJECT_ENVIRONMENT=.venv uv run --group dev python -m pytest core/tests/ucode_release_demo_pack_test.py

# Direct execution
ucode MAP

# Background task
ucode SETUP WIZARD --background

# Check progress
ucode UCODE OPERATOR STATUS
ucode STATUS TASK_ID
```

Template browsing and duplication now use the same seeded/default/user contract:

```bash
ucode UCODE TEMPLATE LIST
ucode UCODE TEMPLATE LIST missions
ucode UCODE TEMPLATE READ captures CAPTURE-template
ucode UCODE TEMPLATE DUPLICATE submissions DEVICE-SUBMISSION-template my-device-template
```

Research, enrich, generate, and import flows now use the same file-backed shell path:

```bash
ucode UCODE RESEARCH prompt shell://input local assist cost policy
ucode UCODE ENRICH prompt shell://input wizard queue health summary
ucode UCODE GENERATE prompt shell://input release readiness note
ucode UCODE RESEARCH LIST
ucode UCODE RESEARCH READ <note-id>
ucode UCODE RESEARCH IMPORT WORKFLOW <workflow_id> <note-id> research
ucode UCODE RESEARCH IMPORT BINDER <binder_id> <note-id> research
ucode WORKFLOW IMPORT RESEARCH <workflow_id> <note-id> research
ucode BINDER IMPORT-RESEARCH <binder_id> <note-id> research
ucode UCODE DELIVERABLE VALIDATE WORKFLOW @memory/vault/workflows/<workflow_id>/workflow.json
```

### 5. Python API (Internal)
```python
from core.services.command_dispatch_service import CommandDispatchService
dispatcher = CommandDispatchService()
result = dispatcher.dispatch("MAP")
```

---

## Command Categories

This guide is organized by:
- TypeScript-backed command paths (Node runtime required, /core/tsrun)
- Python ucode command surface (core dispatcher, /core stdlib-only)
- Wizard commands (networking, GUI, packaging, /wizard)
- Extension commands (/extensions, /sonic)

Seed template families exposed through the Python `UCODE` surface:
- `workflows`
- `missions`
- `captures`
- `submissions`

## Environment Configuration

### Keymap Profiles (Wizard Web UI)
- Dashboard page: `Wizard -> Hotkeys`
- API: `GET /api/ucode/hotkeys`, `GET /api/ucode/keymap`, `POST /api/ucode/keymap`
- Profiles: `mac-obsidian`, `mac-terminal`, `linux-default`, `windows-default`

### Core Environment Variables
```bash
# Keymap
export UDOS_KEYMAP_PROFILE=mac-obsidian
export UDOS_KEYMAP_OS=mac  # mac|linux|windows
export UDOS_KEYMAP_SELF_HEAL=1

# Message theming (terminal output only)
export UDOS_THEME=<theme>
export UDOS_MESSAGE_THEME=fantasy  # Not TUI-specific
export UDOS_MAP_LEVEL=dungeon      # Spatial context, not UI
```

**Note**: Former `UDOS_TUI_*` variables renamed to clarify they control backend message formatting, not UI rendering. `ucode` is the active interactive interface; the external contributor tool remains Dev Mode-only.

Legacy pre-`vibe-cli` interactive references were composted here:
- `docs/.compost/tui-legacy-2026-02/TUI-MIGRATION-PLAN.md`
- `docs/.compost/tui-legacy-2026-02/VIBE-UCLI-INTEGRATION-GUIDE.md`

Active migration notes for current operators:
- `docs/howto/MIGRATION-NOTES-LEGACY-FLOWS.md`

## Selector and Input Contract

Selector behavior for `/ucode` addon commands is standardized by:

- `docs/specs/UCODE-SELECTOR-INTEGRATION-BRIEF.md`

Readiness and validation workflow:

- `docs/howto/UCODE-SELECTOR-READINESS.md`
- `./bin/check-ucode-selectors.sh`

Required behavior for selector-enabled commands:

1. Detect interactive mode first (`isatty` / shell TTY).
2. Prefer selector tools in interactive mode:
   - file selection: `fzf` + `fd`
   - menu selection: `gum`
   - python prompts: `PyInquirer` or `pick`
3. Fallback to non-interactive flags when selectors are unavailable or TTY is absent (`--file`, `--files`, `--choice`).
4. Keep command outputs shell-safe and scriptable.

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
- `WORKFLOW LIST [TEMPLATES|RUNS]`
- `WORKFLOW NEW <template> <workflow_id> [key=value ...]`
- `WORKFLOW RUN <workflow_id>`
- `WORKFLOW STATUS <workflow_id>`
- `WORKFLOW APPROVE <workflow_id>`
- `WORKFLOW ESCALATE <workflow_id>`
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

Current dispatch registry (54 commands) is defined in:
- `core/config/ucode_command_contract_v1_3_20.json`
- `core/services/command_dispatch_service.py` (runtime matcher)

Contract command set:

`ANCHOR`, `BAG`, `BINDER`, `CLEAN`, `COMPOST`, `CONFIG`, `DESTROY`, `DEV`, `DRAW`, `EMPIRE`, `FILE`, `FIND`, `GHOST`, `GOTO`, `GRAB`, `GRID`, `HEALTH`, `HELP`, `LIBRARY`, `LOAD`, `LOGS`, `MAP`, `MIGRATE`, `MODE`, `MUSIC`, `NPC`, `PANEL`, `PLACE`, `PLAY`, `READ`, `REBOOT`, `REPAIR`, `RESTART`, `RULE`, `RUN`, `SAVE`, `SCHEDULE`, `SCHEDULER`, `SCRIPT`, `SETUP`, `SKIN`, `SONIC`, `SPAWN`, `TALK`, `TELL`, `THEME`, `TOKEN`, `UID`, `UNDO`, `USER`, `VERIFY`, `VIEWPORT`, `WIZARD`, `WORKFLOW`

Notes:
- Legacy `NEW` and `EDIT` are consolidated into `FILE NEW` and `FILE EDIT`.
- `UCODE` offline utility commands (`UCODE DEMO|DOCS|SYSTEM|CAPABILITIES|PLUGIN|UPDATE`) are available in current runtime flow.
- the standard v1.5 shell now uses the canonical logic input contract inside `ucode.py`: deterministic input is normalized into command, workflow, knowledge, or guidance routes before any Dev-only contributor fallback
- `UCODE SYSTEM INFO` includes minimum-spec validation for `2 cores / 4.0 GB RAM / 5.0 GB free storage`.
- `UCODE SYSTEM INFO` includes a first field-validation round marker with local sample size and rebaseline targets.
- `UCODE PLUGIN INSTALL <name>` creates a local plugin scaffold entry for capability discovery (`UCODE CAPABILITIES`).
- `UCODE METRICS` reports local-only usage metrics from `memory/ucode/metrics/` by default (no network export).
- Set `UDOS_UCODE_ROOT` to move the `UCODE` offline asset/cache root.

### v1.5 Logic Input Routing

The standard shell path is:

```text
terminal input
-> logic input handler
-> command | workflow | knowledge | guidance
-> file-backed artifacts and logs
```

Examples:

```bash
workflow status wf-v15-001
# -> WORKFLOW STATUS wf-v15-001

browse knowledge missions
# -> UCODE TEMPLATE LIST missions

duplicate template submissions/DEVICE-SUBMISSION-template to my-device-template
# -> UCODE TEMPLATE DUPLICATE submissions DEVICE-SUBMISSION-template my-device-template

research local assist budget control
# -> UCODE RESEARCH prompt shell://input research local assist budget control

help me organize binder tasks
# -> OPERATOR guidance in standard runtime
# -> Dev-only contributor fallback when @dev is active and deterministic routing does not apply
```

### Maintenance Storage Policy (v1.3.13+)

- `BACKUP` writes to `/.compost/<date>/backups/<scope>/`
- `RESTORE` and `UNDO` read latest from `/.compost/<date>/backups/<scope>/`
- `TIDY` and `CLEAN` move files to `/.compost/<date>/trash/<timestamp>/<scope>/`
- `COMPOST` migrates older local dirs (`.archive`, `.backup`, `.tmp`, `.temp`) into `/.compost/<date>/archive/...`
- `HEALTH CHECK housekeeping --scope vault|knowledge|dev|repo [--apply]` previews or applies scoped cleanup
- `TIDY vault|knowledge|dev` and `CLEAN vault|knowledge|dev` use Markdown-first cleanup rules instead of blind directory wipes
- `/.compost` is elastic: older entries are removed by age and older duplicate versions are pruned once enough newer copies exist
- v1.5 `DESTROY`/`RESTORE` assumes an open-box split between runtime code and persisted user Markdown/data libraries

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
- `SONIC BOOTSTRAP [--no-overwrite]`
- `SONIC SUBMISSION LIST [pending|approved|rejected]`
- `SONIC SUBMISSION SUBMIT --file path/to/device.json`
- `SONIC SUBMISSION APPROVE <submission_id>`
- `SONIC SUBMISSION REJECT <submission_id> [reason]`
- `SONIC PLAN ...`
- `SONIC RUN ... --confirm`

Wizard API equivalents:
- `GET /api/platform/sonic/status`
- `POST /api/sonic/db/rebuild` (or `POST /api/sonic/sync`)
- `POST /api/sonic/bootstrap/current`
- `GET /api/sonic/submissions`
- `POST /api/sonic/submissions`
- `POST /api/sonic/submissions/{submission_id}/approve`
- `POST /api/sonic/submissions/{submission_id}/reject`
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

## Dev Mode Prefix Cheat Sheet

| Prefix | Example | Behaviour |
|---|---|---|
| `:` | `:map tokyo` | Always ucode — any case, any word count |
| `/` | `/map tokyo` | Contributor-tool built-ins first, ucode fallthrough |
| `!` | `!ls -la` | Bash shell passthrough |
| (none, single word) | `health` | ucode if exact match — any case |
| (none, multi-word ALL-CAPS) | `MAP tokyo` | ucode if first word exact match |
| (none, multi-word lower) | `help me` | Operator / logic-assist planning — natural language preserved |

**Three commands use the contributor tool's `/` and need `:` for ucode access:**
- `:help` → ucode HELP (command reference) vs `/help` → contributor-tool help
- `:config` → ucode CONFIG (wizard config) vs `/config` → contributor-tool config editor
- `:status` → ucode STATUS (system status) vs `/status` → contributor-tool status

## Quick Checks

```bash
HEALTH
HEALTH CHECK housekeeping --scope knowledge
HEALTH CHECK housekeeping --scope dev --apply
VERIFY
FILE SELECT --files readme.md,docs/STATUS.md
UCODE DEMO LIST
UCODE DOCS --query reference
UCODE SYSTEM INFO
UCODE CAPABILITIES --filter core
UCODE PLUGIN LIST
UCODE METRICS
UCODE TEMPLATE LIST
UCODE RESEARCH LIST
WORKFLOW LIST TEMPLATES
RULE LIST
DRAW PAT LIST
RUN DATA LIST
WIZARD CHECK
```

## FILE SELECT Examples

```bash
# Non-interactive single file
FILE SELECT --file readme.md

# Non-interactive multi-file
FILE SELECT --files readme.md,docs/STATUS.md

# Interactive selector in a workspace
FILE SELECT --workspace @sandbox

# Interactive single-select
FILE SELECT --workspace @vault --single
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

## Message Themes (Terminal Output)

uCode message wording can be lightly themed for spatial/map consistency.

- Scope: Terminal message formatting only (not GUI/CSS/webview styling)
- Base env: `UDOS_THEME=<theme>`
- Message theme: `UDOS_MESSAGE_THEME=fantasy|role-play|explorer|scientist|pilot|captain-sailor|pirate|adventure|scavenge-hunt|traveller|dungeon|foundation|galaxy|stranger-things|lonely-planet|doomsday|hitchhikers`
- Map-level hint: `UDOS_MAP_LEVEL=dungeon|foundation|galaxy|...`

## Z-Layer + TOYBOX Gameplay Lens

Use this pattern when changing gameplay lens:

```bash
# TOYBOX dungeon profile + dungeon-style messages
PLAY TOYBOX SET hethack
export UDOS_MAP_LEVEL=dungeon
export UDOS_MESSAGE_THEME=dungeon

# TOYBOX galaxy profile + galaxy-style messages
PLAY TOYBOX SET elite
export UDOS_MAP_LEVEL=galaxy
export UDOS_MESSAGE_THEME=pilot
```

Notes:
- `PLAY TOYBOX SET ...` changes gameplay profile state
- `UDOS_MAP_LEVEL` and `UDOS_MESSAGE_THEME` control terminal message wording
- z/elevation (`-Zz`, `z_min`, `z_max`, stairs/ramps/portals) is **spatial/map data** (game layer), not UI styling
- "Z-Layer" refers to vertical spatial coordinates in gameplay, not rendering layers
- `PLAY LENS STATUS` surfaces readiness + recommendation hints from progression requirements
- `PLAY LENS SCORE [lens]` returns lens-specific scorecards (variables + scoped metrics + tier)
- `PLAY LENS CHECKPOINTS [lens]` returns progression checkpoints and next-blocked hint
- `PLAY PROFILE STATUS [--group <id>] [--session <id>]` resolves user variables with optional overlay scopes
- `PLAY PROFILE GROUP|SESSION SET|CLEAR ...` manages optional group/session overlay values
- `SKIN CHECK` and `SKIN STATUS` may return advisory `policy_flag` values (`skin_lens_mismatch`, `skin_lens_unmapped`, `skin_lens_progression_drift`) without enforcement in dev rounds
- `SKIN SHOW <name>` reports explicit gameplay metadata contract validity from `themes/*/theme.json`
