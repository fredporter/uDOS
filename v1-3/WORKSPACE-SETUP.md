# v1.3.0 Workspace Setup

**Date:** 2026-02-03
**Status:** Active development branch

## ✅ Completed Setup

### 1. Copilot Configuration Fixed
- **Issue:** `github.copilot.advanced.debug.overrideChatModel` was trying to use `gpt-4-turbo` override
- **Fix:** Removed model overrides from all workspace folders:
  - `/core/.vscode/settings.json`
  - `/wizard/.vscode/settings.json`
  - `/extensions/.vscode/settings.json`
  - `/dev/goblin/.vscode/settings.json`
- **Result:** Now compatible with ChatGPT accounts

### 2. VS Code Extensions
Updated [.vscode/extensions.json](/.vscode/extensions.json):
- Removed: `udos.udos-vscode` (not ready for v1.3)
- Added: GitHub Copilot + Copilot Chat
- Core: Python + Pylance

## 📁 v1.3 Architecture

Per [MIGRATION.md](./MIGRATION.md):

```
v1-3/
├── core/          # Vault contract, core services
├── themes/        # Tailwind prose + theme packs
├── tauri-ui/      # Mac/Windows/Linux app
├── web-portal/    # Static publish target
├── wizard/        # LAN/beacon sharing layer
├── node/          # Optional node server
└── vault/         # Example vault structure
```

## 🎯 v1.3.0 Principles

### Vault First
- Default: `~/Documents/uDOS Vault`
- User picks location (like Obsidian)
- Content = Markdown + assets
- State = SQLite (`VAULT/.udos/state.db`)

### Editor: Typo
- Central editing surface
- Live preview (Tailwind `prose`)
- No proprietary formats

### Tasks = Markdown Truth
- Standard checkboxes: `- [ ]` / `- [x]`
- Optional metadata: `📅 2026-02-10`, `#tag`
- SQLite index for queries (Today/Overdue/etc)

### Export = Static First
- Render to `VAULT/_site/<theme>/`
- No server required for publishing/browsing
- Wizard only needed for LAN sharing

### Font Manager
- App-managed fonts in `VAULT/.udos/fonts/`
- Optional system install (explicit permission)
- Curated typography stack

## 🚫 What's Out of Scope

- Custom document models
- Proprietary sync
- Required server for single-device use
- Python TUI integration (that's core/, not v1-3)

## 🏗️ Next Steps

1. Tauri app: vault picker + folder watcher
2. Typo integration: editor component
3. Task indexer: Markdown → SQLite
4. Theme engine: `prose` baseline
5. Font manager: download + activate
6. Export: static site generator

## 📚 References

- [MIGRATION.md](./MIGRATION.md) — Full refactor plan
- [core/README.md](../core/README.md) — Core TUI (offline)
- [wizard/README.md](../wizard/README.md) — Wizard services (cloud)
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) — Boundaries
