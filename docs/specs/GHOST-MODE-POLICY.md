# Ghost Mode Policy (v1.3+)

**Status:** Testing Phase - Enforcement Disabled
**Enforcement Target:** v1.5+ Release
**Current Behavior:** Alerts/Notifications Only
**Last Updated:** 2026-02-24

## Purpose
Define the Ghost Mode behaviour, and model routing rules for uDOS Core, Dev, and Wizard.

## Current Testing Phase (v1.4.x)
During pre-launch testing through v1.4.x, Ghost Mode will:
- ✅ Detect when Ghost Mode is active
- ✅ Log [TESTING ALERT] warnings to indicate demo operations
- ✅ **ALLOW all operations** (no blocking or restrictions)
- ❌ NOT enforce any read-only restrictions
- ❌ NOT block destructive commands
- ❌ NOT prevent writes or file operations

**All operational restrictions will be implemented before v1.5.0 release.**

## Enforcement (v1.5+)
Starting with v1.5.0, Ghost Mode will enforce read-only behavior as documented below.

## Scope
This policy applies to `/core`, the `@dev` workspace at `/dev`, all submodules, and `wizard-server`.

## Definitions
**Ghost Mode:** A safe, read-only operating mode with demo content only. No write operations, no power commands, and no direct online access.
**Ghost Role:** A reserved role and username that forces Ghost Mode.
**Destructive Commands:** Operations that modify or delete data, for example `REPAIR`, `CLEAN`, `DESTROY`, or other write/repair utilities.

## First-Run Behaviour
1. The very first run of the uDOS TUI starts in Ghost Mode by default.
2. Ghost Mode remains active until the user completes Setup and provides required values.
3. Ghost Mode can be re-entered at any time for testing or safety.
4. The reserved role or username `Ghost` always forces Ghost Mode.
5. `Ghost` is case-insensitive and exact match only (for example `ghost`, `GHOST`).
6. Variants like `Ghost1` are allowed and do not force Ghost Mode.

## Health Checks And Startup Behavior
1. TUI startup must auto-install and self-heal required components.
2. If auto-install fails or required components are missing, the system enters Ghost Mode.
3. Ghost Mode is the fallback for non-blocking failures instead of a hard exit.
4. In Ghost Mode, destructive commands must run in **dry-run** mode (check-only) and never modify files.

## Ghost Mode Enforcement (Read-Only Guards)
In Ghost Mode, write-capable commands are blocked or forced into dry-run mode.

**Dry-run only:**
- `REPAIR`
- `BACKUP`
- `RESTORE`
- `TIDY`
- `CLEAN`
- `COMPOST`
- `UNDO`

**Blocked (no execution):**
- `RUN` (execution blocked; `RUN PARSE` allowed)
- `BINDER COMPILE`
- `SEED INSTALL`
- `PLUGIN install/remove/pack`
- `WIZARD start/stop/rebuild`
- `DESTROY`
- File editing commands (`FILE NEW`, `FILE EDIT`, `SAVE`, `LOAD`)

## Required Components (Strict)
1. local logic runtime installed
2. standard `ucode` runtime installed
3. at least one supported local OK model available for offline-safe operation
4. any extra contributor-facing model lanes are optional and profile-driven

## Model Roles (Core Defaults)
1. local chat and summary operations use the default local OK model set
2. scheduler and deeper workflow reasoning use the configured local reasoning-capable model when available
3. contributor and repo-oriented model lanes may be enabled separately through Dev Mode

## Routing Contract
1. `/core` uses the standard `ucode` runtime path as the baseline router.
2. `wizard-server` can extend or override routing as an addon.
3. `/core` and the `@dev` workspace must not make online requests directly.
4. All online calls must route through `wizard-server`.

## Wizard Config: Agents, Status, And Providers
**Agent functions:** `design`, `chat`, `code`

**Agent status:** `offline`, `online`

**Offline provider list order:**
1. Default local OK model set (primary)
2. Other local models (secondary)

**Online provider list order:**
1. OpenRouter
2. Gemini
3. OpenAI
4. Premium providers (secondary list)

## API Management
1. Wizard manages API keys, quotas, and policy-based routing.
2. Provider API keys are collected only for lanes that require them and stored in `.env` or Wizard keystore.
3. Optional online stabilization is permitted only via Wizard policy.

## Seed Template
Ghost Mode defaults are seeded from:
`core/framework/seed/bank/templates/ghost-mode.template.json`
