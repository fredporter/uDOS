# uDOS v1.3 Refactor Scaffold (drop-in folder)

Drop this `/v1-3/` folder into the root of `github.com/fredporter/uDOS`.

This folder is a **safe staging area** for the v1.3 refactor:
- It does not overwrite existing folders.
- It defines the **contracts** (vault, themes, missions, contributions).
- It scaffolds the **core engine** (TS deterministic transforms) and **Wizard node** services.
- It optionally supports **Tauri UI** for app/control-plane components.

## What to do next (dev round)
1. Read: `v1-3/docs/00-dev-brief.md`
2. Decide UI lane:
   - Browser-first Portal (Wizard serves) OR
   - Tauri App UI (desktop shell) + local services
3. Implement the first “vertical slice”:
   - A Job markdown file → core render/parse/sqlite → run report → contribution bundle

## Folder map
- `vault/` (optional: for v1.3 experiments, Obsidian-compatible)
- `core/` deterministic TS engine placeholders (md/json/sqlite/diff/render)
- `themes/` theme packs contract + starter packs
- `wizard/` node services contract + placeholders
- `tauri-ui/` optional desktop UI lane (control-plane / admin)
- `web-portal/` optional browser UI lane (static + minimal)
- `node/` container deployment skeleton

**v1.3 scaffold date:** 2026-02-03
