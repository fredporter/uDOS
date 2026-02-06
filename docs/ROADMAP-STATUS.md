# Roadmap Status (Single Source of Truth)

This file replaces the prior roadmap/todo/plan/milestone files and is the **only** live roadmap moving forward.
Archived sources live in `docs/.archive/2026-02-06-roadmap-merge/`.

---

## Status Summary

- **Milestones v1.3.0 → v1.3.7**: ✅ Complete (see archived records).
- **Current focus**: consolidate on shared GameState, new memory/system + vault-md layout, and app tooling polish.

---

## Recent Progress

- Migrated legacy bank paths → `memory/system/` and `vault-md/` paths; docs updated accordingly.
- Implemented plugin packaging flow (`PLUGIN pack`) and aligned catalog path to `distribution/plugins`.
- Implemented grid runtime distance calculation, sky view placeholder rendering, and character pixel mapping.
- Wired Talk handler to shared GameState (player id/stats/inventory).
- Documented binder `media/` folder support for non-uDOS-standard files.

---

## Preferred Next Milestone (Post‑v1.3.7)

### P0 — Consolidation & Verification
- ✅ Confirmed extension API references after the `memory/system` + `vault-md/` migration (no code refs to legacy bank paths remain).
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

- Vault/Theme Pack/Engine-Agnostic World contracts enforced.
- UGRID core, anchors, and world lenses complete.
- Wizard AI Modes, theme validation, and preview endpoints complete.
- App v1.3 refactor + Typo integration + converters complete.
- Groovebox → Songscribe stack complete.
- Beacon Portal + MeshCore + networking stack complete.
- Alpine baremetal + Windows entertainment distributions complete.

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
