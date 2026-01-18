# uCode Markdown App

> **Version:** App v1.0.4.3

A Tauri-based desktop application for creating and editing `.udos.md` markdown files with embedded uCODE tiles.

---

## Overview

### What It Does

- **Markdown Editor**: Rich markdown editing with preview
- **uCODE Support**: Embed executable uCODE tiles
- **Teletext Mode**: 40-column retro view
- **Offline-First**: Full functionality without internet
- **Cross-Platform**: macOS, Windows, Linux

### Relationship to TUI

| Feature | TUI | uCode Markdown App |
| ------- | --- | ------------------ |
| Interface | Terminal | Desktop window |
| Navigation | Tile numbers | File browser |
| Editing | vi-style | WYSIWYG |
| Preview | ASCII | Rich rendering |
| Platform | Any terminal | Desktop OS |

---

## Installation

### macOS

```bash
# From release
./install-macos.sh

# Or from source
cd app
npm install
npm run tauri:build
```

### Development

```bash
cd app
npm install
npm run tauri:dev
```

---

## Features

### Markdown Editing

- **Syntax highlighting** for markdown
- **Live preview** panel
- **YAML frontmatter** support
- **Table editor**
- **Code block support**

### uCODE Integration

Embed executable tiles in markdown:

```markdown
# My Guide

Here's how to check system status:

[SYSTEM|STATUS]

And here's how to run a script:

[RUN|memory/ucode/test.upy]
```

### Teletext Mode

Toggle teletext view for retro 40-column display:

- **40x25 character grid**
- **Block graphics**
- **Classic teletext colors**
- **Page navigation**

---

## File Format

### .udos.md Structure

```markdown
---
title: Guide Title
tile: 301
category: knowledge
tags: [survival, water]
---

# Guide Content

Regular markdown content here.

## Embedded Commands

[TILE|100]
[GUIDE|AI*LIST]

## Code Blocks

```python
print("Hello uDOS")
```

## Links to Other Tiles

See [Fire Making](tile:302) for more info.
```

### Frontmatter Fields

| Field | Required | Description |
| ----- | -------- | ----------- |
| `title` | Yes | Document title |
| `tile` | No | Associated tile number |
| `category` | No | Content category |
| `tags` | No | Searchable tags |
| `author` | No | Author name |
| `version` | No | Document version |

---

## Keyboard Shortcuts

### Global

| Shortcut | Action |
| -------- | ------ |
| Cmd/Ctrl+N | New file |
| Cmd/Ctrl+O | Open file |
| Cmd/Ctrl+S | Save |
| Cmd/Ctrl+Shift+S | Save as |
| Cmd/Ctrl+P | Print/Export |

### Editor

| Shortcut | Action |
| -------- | ------ |
| Cmd/Ctrl+B | Bold |
| Cmd/Ctrl+I | Italic |
| Cmd/Ctrl+K | Insert link |
| Cmd/Ctrl+Shift+C | Insert code block |
| Cmd/Ctrl+/ | Toggle comment |

### View

| Shortcut | Action |
| -------- | ------ |
| Cmd/Ctrl+Shift+P | Toggle preview |
| Cmd/Ctrl+Shift+T | Toggle teletext |
| Cmd/Ctrl+= | Zoom in |
| Cmd/Ctrl+- | Zoom out |

---

## Configuration

### Settings File

`~/.config/udos-markdown/settings.json`:

```json
{
  "editor": {
    "fontSize": 14,
    "fontFamily": "monospace",
    "wordWrap": true,
    "lineNumbers": true
  },
  "preview": {
    "enabled": true,
    "syncScroll": true
  },
  "teletext": {
    "defaultMode": false,
    "colorScheme": "classic"
  },
  "files": {
    "defaultPath": "~/udos/memory/docs",
    "autoSave": true,
    "autoSaveInterval": 30
  }
}
```

---

## Integration with TUI

### Launching from TUI

```bash
# Open file in app
OPEN document.udos.md --app

# Or use EDIT with --gui flag
EDIT document.udos.md --gui
```

### Sharing Files

Both TUI and App read the same file locations:

```
memory/
├── docs/           # User documents
├── inbox/          # Captured content
└── ucode/          # Scripts
```

---

## Building from Source

### Prerequisites

```bash
# Node.js 18+
node --version

# Rust
rustc --version

# Tauri CLI
cargo install tauri-cli
```

### Development Build

```bash
cd app
npm install
npm run tauri:dev
```

### Production Build

```bash
cd app
npm run tauri:build

# Output in:
# - app/src-tauri/target/release/bundle/
```

### Build Artifacts

| Platform | Output |
| -------- | ------ |
| macOS | `.dmg`, `.app` |
| Windows | `.msi`, `.exe` |
| Linux | `.deb`, `.AppImage` |

---

## Architecture

```
app/
├── src/                    # Svelte frontend
│   ├── lib/
│   │   ├── components/    # UI components
│   │   ├── stores/        # State management
│   │   └── utils/         # Utilities
│   ├── routes/            # Pages
│   └── app.html           # Template
├── src-tauri/             # Rust backend
│   ├── src/
│   │   ├── main.rs       # Entry point
│   │   ├── commands.rs   # IPC commands
│   │   └── file.rs       # File operations
│   └── Cargo.toml
├── static/                # Static assets
├── package.json           # Node config
└── version.json           # App version
```

---

## Troubleshooting

### App Won't Start

```bash
# Check logs
tail -f ~/Library/Logs/ucode-markdown/app.log

# Or run in terminal
./app/src-tauri/target/release/ucode-markdown
```

### Preview Not Rendering

```bash
# Clear cache
rm -rf ~/.config/udos-markdown/cache

# Reset settings
rm ~/.config/udos-markdown/settings.json
```

### Build Errors

```bash
# Clean and rebuild
cd app
rm -rf node_modules
rm -rf src-tauri/target
npm install
npm run tauri:build
```

---

## Related

- [TUI](tui/README.md) - Terminal interface
- [uCODE](../VISION.md#ucode) - uCODE syntax
- [File Commands](commands/files.md) - File operations

---

*Part of the [uDOS Wiki](README.md)*
