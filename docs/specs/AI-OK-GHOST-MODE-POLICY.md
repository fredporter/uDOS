# AI OK Ghost Mode Policy (v1.3+)

**Status:** Draft
**Last Updated:** 2026-02-06

## Purpose
Define the offline-first AI policy, Ghost Mode behavior, and model routing rules for uDOS Core, Dev, and Wizard.

## Scope
This policy applies to `/core`, `/dev`, all submodules, and `wizard-server`.

## Definitions
**Ghost Mode:** A safe, read-only operating mode with demo content only. No write operations, no power commands, and no direct online access.
**Ghost Role:** A reserved role and username that forces Ghost Mode.
**Destructive Commands:** Operations that modify or delete data, for example `REPAIR`, `CLEAN`, `DESTROY`, or other write/repair utilities.

## First-Run Behavior
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
- File editing commands (`NEW`, `EDIT`, `SAVE`, `LOAD`)

## Required Components (Strict)
1. `ollama` installed
2. `vibe-cli` installed
3. `mistral-small` pulled
4. `mistral-large` pulled
5. `devstral-small-2` pulled

## Model Roles (Core Defaults)
1. Chat and summaries use `mistral-small`.
2. Scheduler and deep workflow reasoning use `mistral-large`.
3. Code and repo operations use `devstral-small-2`.

## Routing Contract
1. `/core` uses the Vibe-CLI router as the baseline router.
2. `wizard-server` can extend or override routing as an addon.
3. `/core` and `/dev` must not make online requests directly.
4. All online calls must route through `wizard-server`.

## Wizard Config: Agents, Status, And Providers
**Agent functions:** `design`, `chat`, `code`

**Agent status:** `offline`, `online`

**Offline provider list order:**
1. Default Mistral set (primary)
2. Other Ollama models (secondary)

**Online provider list order:**
1. OpenRouter
2. Gemini
3. OpenAI
4. Premium providers (secondary list)

## API Management
1. Wizard manages API keys, quotas, and policy-based routing.
2. Mistral API key is collected during Setup and stored in `.env` or Wizard keystore.
3. Optional online stabilization is permitted only via Wizard policy.

## Seed Template
Ghost Mode defaults are seeded from:
`core/framework/seed/bank/templates/ghost-mode.template.json`
