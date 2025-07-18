# 📦 uDOS Package System v1.0

**Purpose**: Centralized package management for bundled applications and utilities.

## 🎯 Package Structure

```
package/
├── README.md           # This file
├── manifest.json       # Package definitions  
├── install-queue.txt   # Startup installation queue
├── docs/               # Package documentation
├── editors/            # Text editors and IDEs
├── utils/              # Command-line utilities
│   ├── ripgrep.md     # Fast text search
│   ├── bat.md         # Syntax-highlighted file viewer
│   ├── fd.md          # Fast file finder
│   ├── glow.md        # Terminal markdown renderer
│   ├── fzf.md         # Fuzzy finder
│   └── jq.md          # JSON processor
├── development/        # Development tools
│   ├── vscode-extension.md  # VS Code extension
│   └── gemini-cli.md       # AI assistant
└── assets/            # Package assets and resources
```

## ⚡ Auto-Installation at Startup

Packages marked in `install-queue.txt` are installed automatically during uDOS startup. This ensures essential tools are available immediately.

## 🔧 Integrated uCode Commands

Each package gets corresponding uCode/VB commands:
- `EDIT <file>` - Launch default text editor
- `CREATE <type>` - Create new files with templates
- `VIEW <file>` - View files with syntax highlighting

## 📋 Package Categories

### 📝 Text Editors
- **nano** - Simple command-line editor
- **micro** - Modern terminal editor
- **helix** - Modal editor with LSP support

### 🔍 Utilities  
- **ripgrep** - Fast text search with regex support
- **fd** - Fast file finder (modern find replacement)
- **bat** - Syntax-highlighted file viewer with Git integration
- **glow** - Terminal markdown renderer
- **fzf** - Fuzzy finder for interactive selection
- **jq** - JSON processor for data manipulation

### 🛠️ Development
- **VS Code Extension** - uDOS language support and integration
- **Gemini CLI** - AI assistant for intelligent development
- **git** - Version control
- **curl** - HTTP client

## 🚀 Usage

```bash
# Install all packages
./uCode/ucode.sh PACKAGE INSTALL ALL

# Install specific package
./uCode/ucode.sh PACKAGE INSTALL nano

# List available packages
./uCode/ucode.sh PACKAGE LIST

# Show package info
./uCode/ucode.sh PACKAGE INFO micro
```

*Package system integrates with uDOS filename conventions - no complex folder structures needed by users.*
