# v1.3.0 Quick Reference

**Current Status:** Setup complete, ready for development
**Date:** 2026-02-03

---

## ✅ Fixed: Copilot Extension Error

**Error:** `The '' model is not supported when using Codex with a ChatGPT account`

**Cause:** `github.copilot.advanced.debug.overrideChatModel` was set to `gpt-4-turbo` in workspace settings, attempting to override the API endpoint.

**Fix:** Removed model overrides from:
- [core/.vscode/settings.json](../core/.vscode/settings.json)
- [wizard/.vscode/settings.json](../wizard/.vscode/settings.json)
- [extensions/.vscode/settings.json](../extensions/.vscode/settings.json)
- [dev/goblin/.vscode/settings.json](../dev/goblin/.vscode/settings.json)

**Result:** Workspace now uses standard GitHub Copilot (compatible with ChatGPT accounts).

---

## 📂 v1.3 Structure

```
v1-3/
├── README.md               # Architecture overview
├── MIGRATION.md            # Refactor plan from /app/
├── WORKSPACE-SETUP.md      # Current setup status
├── CHECKLIST.md            # Development milestones
├── QUICK-REFERENCE.md      # This file
├── core/                   # Vault contract, schemas
├── themes/                 # Theme packs (prose baseline)
├── tauri-ui/               # Desktop app (Svelte + Tauri)
├── web-portal/             # Static publish target
├── wizard/                 # LAN beacon services
├── node/                   # Container deployment
├── vault/                  # Example vault structure
└── docs/                   # Architecture docs
```

---

## 🎯 v1.3 Core Concepts

| Concept | Implementation |
|---------|----------------|
| **Vault** | User folder (like Obsidian), default: `~/Documents/uDOS Vault` |
| **Editor** | Typo (Markdown WYSIWYG) |
| **Tasks** | Markdown checkboxes + SQLite index |
| **Export** | Static HTML (no server required) |
| **Themes** | Tailwind Typography `prose` + theme packs |
| **Fonts** | App-managed, optional system install |
| **Sharing** | Wizard LAN beacon (optional, later) |

---

## 🚀 Development Commands

### Check setup
```bash
cat v1-3/WORKSPACE-SETUP.md
cat v1-3/CHECKLIST.md
```

### Verify structure
```bash
ls -la v1-3/
tree v1-3/ -L 2
```

### Start development
```bash
cd v1-3/tauri-ui/
# (Tauri commands TBD)
```

---

## 📋 Current Phase: Phase 1

**Goal:** Vault + editor foundation

- [x] Remove Copilot overrides
- [x] Update workspace extensions
- [x] Document v1.3 architecture
- [ ] Verify folder structure
- [ ] Create vault contract schema
- [ ] Design SQLite state schema

**Next:** Phase 2 (Tauri vault picker)

---

## 🔗 Key Files

| File | Purpose |
|------|---------|
| [MIGRATION.md](./MIGRATION.md) | Full refactor plan |
| [WORKSPACE-SETUP.md](./WORKSPACE-SETUP.md) | Setup status |
| [CHECKLIST.md](./CHECKLIST.md) | Task list |
| [docs/00-dev-brief.md](./docs/00-dev-brief.md) | Architecture |

---

## 🚫 Out of Scope

- Python TUI (that's `/core/`, not v1-3)
- Custom document models
- Proprietary sync
- Required server for single-device use

---

## 💡 Tips

1. **Boundaries:** Check [.github/copilot-instructions.md](../.github/copilot-instructions.md)
2. **Vault lives outside repo:** Don't commit vault content
3. **Static first:** Export works without Wizard
4. **Markdown truth:** No proprietary formats

---

**Ready to start:** Yes ✅
