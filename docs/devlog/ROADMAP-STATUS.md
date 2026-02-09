# Roadmap Status (Single Source of Truth)

This file replaces the prior roadmap/todo/plan/milestone files and is the **only** live roadmap moving forward.
Archived sources live in `docs/.archive/2026-02-06-roadmap-merge/`.

---

## Status Summary

- **Milestones v1.3.0 → v1.3.7**: ✅ Complete (see archived records).
- **Current focus**: Stabilization and polish for v1.4.0 release.
- **Outstanding (active)**: None — all P0 items complete.
- **Checklist**: See `docs/ROADMAP-CHECKLIST.md` for the active task list and owners.
- **Dev mode policy**: `/dev/` public submodule required and admin-only; see [docs/DEV-MODE-POLICY.md](docs/DEV-MODE-POLICY.md).
- **Core/Wizard boundary**: `core` is the base runtime; `wizard` is the brand for connected services. Core can run without Wizard (limited). Wizard cannot run without Core.
- **Logging API v1.3**: ✅ Implemented and tested. See [docs/LOGGING-API-v1.3.md](docs/LOGGING-API-v1.3.md).
- **Empire (private)**: Tracked separately in `empire/docs/EMPIRE-ROADMAP.md`.

---

## Recent Progress

- Completed Wizard service split with MCP gateway integration.
- Full vibe-cli integration with uCODE TUI complete.
- Vibe embed + minimal uCODE surface implemented.
- Dev mode gate enforcement finalized.
- Logging API v1.3 implemented and tested (2026-02-08).
- Empire business features split to dedicated `empire/docs/EMPIRE-ROADMAP.md`.
- Migrated legacy bank paths → `memory/system/` and `memory/vault/` paths; docs updated accordingly.
- Implemented plugin packaging flow (`PLUGIN pack`) and aligned catalog path to `distribution/plugins`.
- Implemented grid runtime distance calculation, sky view placeholder rendering, and character pixel mapping.
- Wired Talk handler to shared GameState (player id/stats/inventory).
- Documented binder `media/` folder support for non-uDOS-standard files.
- Scaffolded Empire private extension spine with minimal entrypoint and docs.
- Refactored Wizard server wiring: extracted auth, logging, system stats, scheduler runner, plugin repo, web proxy, and webhook helpers into services.
- Bumped versions: `uDOS` → `v1.3.9`, `Wizard` → `v1.1.2`.

---

## Preferred Next Milestone (Post‑v1.3.7)

### P0 — Version Bump + Wizard/Vibe Refactor (High Priority)
- ✅ Version bump to **v1.3.9** (Wizard services split, MCP gateway, Vibe full TUI replacement).
- ✅ Plan service boundaries + initial Wizard server extraction (auth/logs/system stats/scheduler/plugin repo/web proxy/webhooks).
- ✅ Bootstrap Vibe integration (embed) and minimal uCODE command exposure for exploration.
- ✅ Enforce Dev mode gate (admin-only + `/dev/` presence) and document the policy contract.
- ✅ Add MCP server tests to verify stdio tool wrapping and tool index parsing.
- ✅ Logging API v1.3 implementation complete and tested.

### P0 — Consolidation & Verification
- ✅ Confirmed extension API references after the `memory/system` + `memory/vault/` migration (no code refs to legacy bank paths remain).
- ✅ Removed deprecated bank directory after verification passes (archived to `memory/.archive/removed-bank-2026-02-06/`).
- ✅ Validated plugin packaging flow using `PLUGIN pack` against `distribution/plugins` index/manifest (packaged `api`).

### P1 — App Tooling (Spec-Level TODOs)
- ✅ Implemented Tauri file picker (toolbar `openFile`).
- ✅ Implemented Tauri folder picker (toolbar `openFolder`).
- ✅ Implemented save logic + Save As (toolbar `saveFile` / `saveFileDialog`).
- ✅ Implemented Finder reveal (toolbar `revealInFinder`).
- ✅ Query macOS system fonts via Tauri (`get_system_fonts` + FontManager update).

---

## Completed Highlights (v1.3.x)

- Wizard service split with MCP gateway complete.
- Full vibe-cli integration with uCODE TUI complete.
- Vibe embed + minimal uCODE surface complete.
- Dev mode gate enforcement complete.
- Logging API v1.3 complete.
- Vault/Theme Pack/Engine-Agnostic World contracts enforced.
- UGRID core, anchors, and world lenses complete.
- Wizard AI Modes, theme validation, and preview endpoints complete.
- App v1.3 refactor + Typo integration + converters complete.
- Groovebox → Songscribe stack complete.
- Beacon Portal + MeshCore + networking stack complete.
- Alpine baremetal + Windows entertainment distributions complete.

---

## Pre-v1.4 (Planned)

### P2 — Code Quality & Modularization
- [ ] Review long route factory functions for modularization opportunities:
  - `wizard/routes/ucode_routes.py` (~1200 lines)
  - `wizard/routes/config_routes.py` (~1350 lines)
  - `wizard/routes/provider_routes.py` (~1150 lines)
  - `core/commands/destroy_handler.py` (~1000 lines)
  - `core/commands/setup_handler.py` (~730 lines)
- [ ] Consider splitting nested route handlers into separate modules.
- [ ] Evaluate helper extraction patterns for repeated code blocks.

---

## Archived Sources (Read‑Only)

Moved on 2026-02-06:
- `docs/.archive/2026-02-06-roadmap-merge/ROADMAP-TODO.md`
- `docs/.archive/2026-02-06-roadmap-merge/DEV-PLAN-v1.3.2+.md`
- `docs/.archive/2026-02-06-roadmap-merge/DEV-PLAN-v1.3.3.md`
- `docs/.archive/2026-02-06-roadmap-merge/DEV-PLAN-v1.3.4.md`
- `docs/.archive/2026-02-06-roadmap-merge/DEV-PLAN-v1.3.5.md`
- `docs/.archive/2026-02-06-roadmap-merge/DEV-PLAN-v1.3.7.md`
- `docs/.archive/2026-02-06-roadmap-merge/DEV-WORKFLOW-v1.3.1.md`
- `docs/.archive/2026-02-06-roadmap-merge/v1.3.1-milestones.md`
