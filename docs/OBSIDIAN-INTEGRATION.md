# uDOS + Obsidian Integration Guide

**Version:** v1.3  
**Updated:** 2026-02-06

> **⚠️ PATH UPDATE:** References to legacy bank paths in older docs should be updated to:
> - User vault: `vault-md/` or `~/Documents/uDOS Vault/`
> - System templates: `memory/system/`

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
   - Default: `vault-md/`
   - Or your custom vault location (e.g., `~/Documents/uDOS Vault/`)

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

```
vault-md/                  # Your personal vault
├── daily/                 # Daily notes
├── projects/              # Project folders
├── templates/             # Note templates
├── scripts/               # Executable scripts
└── ...

memory/system/             # System templates + runtime assets (tracked)
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

## Migration from Notion (if needed)

If you were previously using Notion sync:

1. **Export from Notion**
   - Settings → Export → Markdown & CSV
   - Download your workspace

2. **Import to Obsidian**
   - Use Obsidian's Markdown importer
   - Or copy files directly to your vault

3. **Clean up**
   - Convert Notion databases to Markdown tables
   - Update internal links
   - Remove Notion-specific formatting

---

## Best Practices

### Version Control
Use Git for your vault:
```bash
cd ~/Documents/uDOS/memory/user
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

_Last updated: 2026-02-05_
