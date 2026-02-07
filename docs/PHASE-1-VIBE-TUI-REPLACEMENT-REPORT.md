# Phase 1 Report — Vibe Full TUI Replacement (v1.3.8)

Date: 2026-02-06
Owner: uDOS/Wizard
Scope: Baseline audit of current uCODE TUI and Wizard surfaces to inform full replacement plan and service split.

---

## Summary

uCODE today is a self-contained terminal UX with its own input system, command dispatcher, rendering, and UI components. Wizard already has a service-heavy internal structure and a companion FastAPI web GUI. This makes the “Vibe as primary TUI + Wizard as backend services + GUI companion” plan feasible with a staged MCP gateway and minimal disruption.

---

## Current uCODE TUI Entry Points

**Entry**
- `/Users/fredbook/Code/uDOS/uDOS.py` launches `core/tui/ucode.py` and runs `uCODETUI.run()`.

**Main loop**
- `uCODETUI.run()` is the terminal event loop and routes all input modes and commands. It wires:
  - `CommandDispatcher` for uCODE commands.
  - `ContextualCommandPrompt` with `prompt_toolkit` fallback.
  - `CommandSelector` (TAB menu).
  - `FKeyHandler` (F1–F8 shortcuts).
  - `TUIStatusBar` (status line with server + system stats).

**Input modes**
- `OK …` and `?` prefix => command mode
- `/` prefix => slash mode (command or shell)
- no prefix => “question mode” (best-effort command routing)

**Key UX surfaces**
- Command dispatcher: `/Users/fredbook/Code/uDOS/core/tui/dispatcher.py`
- Renderer: `/Users/fredbook/Code/uDOS/core/tui/renderer.py`
- Status bar: `/Users/fredbook/Code/uDOS/core/tui/status_bar.py`
- F-key shortcuts: `/Users/fredbook/Code/uDOS/core/tui/fkey_handler.py`
- Command selector: `/Users/fredbook/Code/uDOS/core/ui/command_selector.py`
- Input/prompt layer: `/Users/fredbook/Code/uDOS/core/input/*`
- Game/Session state: `/Users/fredbook/Code/uDOS/core/tui/state.py`

---

## Current uCODE Command Routing

**Command dispatcher**
- `CommandDispatcher` maps commands to handlers (navigation, system, wizard, data, etc.).
- It synchronizes shared game state with handlers.

**Special commands** (handled directly by `uCODETUI`)
- `STATUS`, `HELP`, `PROMPT`, `OFVIBE`, `ONVIBE`, `OK LOCAL`, `OK EXPLAIN`, `OK DIFF`, `OK PATCH`, `EXIT/QUIT`, `FKEYS`.

This matters because we need to decide which commands become **MCP tools** and which become **Vibe-native instructions** or **prompts**.

---

## Wizard Surfaces (Current)

**Server**
- `/Users/fredbook/Code/uDOS/wizard/server.py` is the main FastAPI server (device auth, rate limiting, cost tracking, core services).

**Companion GUI**
- `/Users/fredbook/Code/uDOS/wizard/web/` is a FastAPI + HTMX + Alpine web UI.

**Routes**
- `/Users/fredbook/Code/uDOS/wizard/routes/*` exposes a broad API surface (AI, datasets, plugins, workflow, etc.).

**Services (selected)**
- `/Users/fredbook/Code/uDOS/wizard/services/ok_gateway.py`
- `/Users/fredbook/Code/uDOS/wizard/services/rate_limiter.py`
- `/Users/fredbook/Code/uDOS/wizard/services/monitoring_manager.py`
- `/Users/fredbook/Code/uDOS/wizard/services/task_scheduler.py`
- `/Users/fredbook/Code/uDOS/wizard/services/plugin_registry.py`
- `/Users/fredbook/Code/uDOS/wizard/services/vibe_service.py`
- `/Users/fredbook/Code/uDOS/wizard/services/mistral_vibe.py`

The service layer already exists; we need to formalize it into **small service boundaries** with a **single MCP gateway**.

---

## Initial Service Boundary Proposal (Draft)

These are proposed groupings based on current files and routes. We will refine after deeper audit.

**Wizard Core**
- Auth, rate limiting, config, logging, system info

**AI/Model Services**
- OK gateway, model router, provider integration

**Workflow + Jobs**
- Task scheduler, workflow manager, notification history

**Assets + Data**
- Datasets, artifacts, binder, library, vault

**Plugins + Extensions**
- Plugin registry, repository, pack manager, validation

**Monitoring + Health**
- Monitoring manager, diagnostics, health checks

**Companion GUI**
- Web UI only, calls service APIs

---

## Vibe Replacement Strategy (Phase 1 Outputs)

**Goal**: enable Vibe to be the primary UI with minimal uCODE command exposure for exploration.

**Initial MCP tool surface (suggested)**
- `ucode.help()`
- `ucode.status()`
- `ucode.dispatch(command: str)` (restricted to safe commands during exploration)

**Wizard MCP tools (starter set)**
- `wizard.health()`
- `wizard.config.get()` / `wizard.config.set()`
- `wizard.providers.list()`

---

## Risks & Notes

- uCODE TUI currently mixes **UI** and **command routing** (e.g., `OK` commands). We’ll need a clean split between “core commands” and “UI-only helpers” to make MCP stable.
- Some commands call shell execution (slash mode). For Vibe we’ll need explicit approvals or a dedicated sandbox policy.
- Wizard services already include Vibe-related files (`mistral_vibe.py`, `vibe_service.py`) that may be reusable or need consolidation.

---

## Next Steps (Phase 2 Prep)

1. Produce a precise command-to-tool matrix (which uCODE commands become MCP tools, which become Vibe prompts).
2. Define MCP gateway location and wiring strategy (under `/wizard` or `/mcp`).
3. Build minimal MCP server + Vibe config (`/.vibe/config.toml`) and expose `ucode.help`, `ucode.status`, `ucode.dispatch`.
4. Run Vibe locally and validate the experience before porting any UI features.
