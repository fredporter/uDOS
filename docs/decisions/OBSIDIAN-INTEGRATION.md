# uDOS + Obsidian Integration Guide

**Version:** v1.3
**Updated:** 2026-02-17

> **⚠️ PATH UPDATE:** References to legacy vault assumptions should be read with the current vault contract:
> - Distributable scaffold: `vault/` (tracked, template only)
> - Canonical starter seed: `core/framework/seed/vault/` (tracked)
> - User runtime vault: `memory/vault/` (default, local)
> - System templates/runtime assets: `memory/system/` (local)

---

## Overview

uDOS is designed as a **local Obsidian companion app**. Instead of syncing with external services, uDOS shares your vault directly with Obsidian using an open-box format.

**No sync required!** Both apps read and write to the same local vault.

---

## Why Obsidian?

[Obsidian](https://obsidian.md) is a powerful, local-first markdown editor that complements uDOS perfectly:

- ✅ **Local-first** — All data stays on your device
- ✅ **Markdown native** — Same format as uDOS
- ✅ **Plugin ecosystem** — Extend functionality
- ✅ **Cross-platform** — Windows, macOS, Linux, mobile
- ✅ **Graph view** — Visualize knowledge connections
- ✅ **Independent** — Works without uDOS, uDOS works without it

---

## Setup

### 1. Install Obsidian

Download from [obsidian.md](https://obsidian.md)

### 2. Point to Your uDOS Vault

In Obsidian:
1. Click "Open folder as vault"
2. Navigate to your uDOS vault location:
   - Default: `memory/vault/`
   - Or your custom vault location (set `VAULT_ROOT`)

### 3. Start Using Both

- **Obsidian** — Rich editing, graph view, plugins
- **uDOS** — Automation, CLI, runtime execution, AI integration

Both apps share the same files in real-time!

---

## Recommended Workflow

### For Writing & Research (Obsidian)
- Daily notes
- Long-form writing
- Linking and backlinks
- Graph exploration
- Mobile sync (via Obsidian Sync or iCloud)

### For Execution & Automation (uDOS)
- Script execution
- AI assistance
- Workflow automation
- Command-line operations
- System integration

---

## Vault Structure

uDOS uses a template/seed/runtime split:

- `vault/` is the clean distribution scaffold.
- `core/framework/seed/vault/` is what seed installation copies.
- `memory/vault/` is where Obsidian should point for day-to-day usage.

```
memory/vault/              # Your personal vault
├── daily/                 # Daily notes
├── projects/              # Project folders
├── templates/             # Note templates
├── scripts/               # Executable scripts
└── ...

vault/                     # Distributable scaffold (tracked template)
core/framework/seed/vault/ # Canonical starter seed (tracked)
memory/system/             # System templates + runtime assets (local runtime)
memory/private/            # Secrets + credentials (gitignored)
```

**Tip:** Use Obsidian's template system with uDOS script templates for powerful workflows.

---

## File Compatibility

Both apps use standard Markdown:

- `.md` files work in both
- Frontmatter (YAML) supported
- Links: `[[wikilinks]]` and `[markdown](links)`
- Embeds: `![[image.png]]`
- Code blocks with syntax highlighting

**uDOS-specific:**
- `.script.md` — Executable scripts (still editable in Obsidian)
- Runtime blocks in frontmatter

---

## Migration from Other Tools (if needed)

If you are coming from another system:

1. **Export to Markdown**
   - Export Markdown (and CSV for tables) from your previous tool

2. **Import to Obsidian**
   - Use Obsidian's Markdown importer
   - Or copy files directly to your vault

3. **Clean up**
   - Convert database exports to Markdown tables
   - Update internal links
   - Remove vendor-specific formatting

---

## Best Practices

### Version Control
Use Git for your vault:
```bash
cd ~/Documents/uDOS/memory/vault
git init
git add .
git commit -m "Initial vault"
```

### Backup
- Obsidian Sync (official, paid)
- iCloud/Dropbox (folder sync)
- Git + GitHub (free, version controlled)
- uDOS backup scripts

### Organization
- Use folders for broad categories
- Use tags for cross-cutting concerns
- Use links for relationships
- Keep daily notes separate

---

## Troubleshooting

### Files not syncing?
- Both apps read/write instantly
- If changes don't appear, check file permissions
- Obsidian auto-reloads on external changes

### Conflicts?
- Avoid editing same file in both simultaneously
- Use Git for conflict resolution if needed
- uDOS scripts can check file locks

### Performance?
- Large vaults (>10k files) may be slow in Obsidian graph view
- Disable graph indexing for uDOS-only folders
- Use `.obsidian/workspace` to exclude system folders

---

## Advanced: Plugin Recommendations

Obsidian plugins that work well with uDOS:

- **Dataview** — Query your vault like a database
- **Templater** — Advanced templates (pair with uDOS scripts)
- **QuickAdd** — Macros and automation
- **Excalidraw** — Diagrams (uDOS can embed)
- **Tasks** — Task management (uDOS can parse)

---

## Support

- **Obsidian Help:** [help.obsidian.md](https://help.obsidian.md)
- **uDOS Docs:** `wiki/` and `docs/`
- **Community:** See `CONTRIBUTORS.md`

---

## Philosophy

> "The best tool is the one you have with you."

Use Obsidian when you want a GUI. Use uDOS when you want automation. Use both together for a powerful local-first knowledge system.

**No vendor lock-in. No sync fees. Just files.**

---

_Last updated: 2026-02-17_
