# 📦 uDOS Package Index

Complete reference for all uDOS packages with installation and usage information.

## 🔍 Utilities

### [ripgrep](./utils/ripgrep.md) - Ultra-Fast Text Search
- **Purpose**: Fast text search with regex support
- **Installation**: `./uCode/packages/install-ripgrep.sh`
- **Key Features**: VS Code integration, AI workflows, mission search
- **VS Code Task**: "🔍 Search with ripgrep"

### [fd](./utils/fd.md) - Fast File Finder  
- **Purpose**: Modern replacement for `find` command
- **Installation**: `./uCode/packages/install-fd.sh`
- **Key Features**: Intuitive syntax, template discovery, mission management
- **VS Code Task**: "🔍 Find files with fd"

### [bat](./utils/bat.md) - Syntax-Highlighted File Viewer
- **Purpose**: Enhanced `cat` with syntax highlighting and Git integration
- **Installation**: `./uCode/packages/install-bat.sh`  
- **Key Features**: Code display, log viewing, dashboard integration
- **VS Code Task**: "📄 View with bat"

### [glow](./utils/glow.md) - Terminal Markdown Renderer
- **Purpose**: Beautiful markdown viewing in terminal
- **Installation**: `./uCode/packages/install-glow.sh`
- **Key Features**: Mission review, documentation browser, dashboard display
- **VS Code Task**: "📖 View markdown with glow"

### [fzf](./utils/fzf.md) - Fuzzy Finder
- **Purpose**: Interactive file and content selection
- **Installation**: `./uCode/packages/install-fzf.sh`
- **Key Features**: Interactive navigation, template browser, quick actions
- **Integration**: Command history, Git workflows, dashboard navigation

### [jq](./utils/jq.md) - JSON Processor
- **Purpose**: Command-line JSON manipulation and processing
- **Installation**: `./uCode/packages/install-jq.sh`
- **Key Features**: Mission data processing, package management, API responses
- **Integration**: Dashboard statistics, configuration processing

## 🛠️ Development Tools

### [VS Code Extension](./development/vscode-extension.md) - uDOS IDE Integration
- **Purpose**: Complete uDOS development environment in VS Code
- **Installation**: Automatic during uDOS setup or via extension manager
- **Key Features**: uScript language support, command integration, Chester AI
- **Components**: Syntax highlighting, IntelliSense, templates, themes

### [Gemini CLI](./development/gemini-cli.md) - AI Development Assistant
- **Purpose**: Google Gemini AI integration for intelligent assistance
- **Installation**: `./uCode/packages/install-gemini.sh`  
- **Key Features**: Code analysis, mission planning, documentation generation
- **Integration**: Chester companion system, error diagnosis, optimization

## 📝 Text Editors

### nano - Simple Command-Line Editor
- **Purpose**: Lightweight text editor for quick edits
- **Installation**: Auto-installed (Homebrew)
- **uCode Commands**: `EDIT`, `CREATE`
- **Priority**: 1 (highest)

### micro - Modern Terminal Editor  
- **Purpose**: Feature-rich terminal editor with mouse support
- **Installation**: Auto-installed (Homebrew)
- **uCode Commands**: `EDIT`, `CREATE`, `MICRO`
- **Priority**: 2

### helix - Modal Editor with LSP
- **Purpose**: Advanced modal editor with built-in language server support
- **Installation**: Optional (Homebrew)
- **uCode Commands**: `HX`, `HELIX`
- **Priority**: 3

## 🚀 Quick Installation

### Install All Essential Packages
```bash
# Via package manager
./uCode/packages/manager-simple.sh install-all

# Via VS Code tasks
# Press Cmd+Shift+P → "Tasks: Run Task" → "📦 Install All Packages"
```

### Install Individual Packages
```bash
# Text search
./uCode/packages/install-ripgrep.sh

# File finding  
./uCode/packages/install-fd.sh

# File viewing
./uCode/packages/install-bat.sh

# Markdown rendering
./uCode/packages/install-glow.sh

# Fuzzy finding
./uCode/packages/install-fzf.sh

# JSON processing
./uCode/packages/install-jq.sh

# AI assistance
./uCode/packages/install-gemini.sh
```

## 📊 Package Status

### Check Installation Status
```bash
# Quick check
./uCode/packages/manager-simple.sh list

# Detailed status
cat ./package/manifest.json | jq '.packages'

# VS Code integration check
code --list-extensions | grep udos
```

### Validation
```bash
# Validate all packages
./uCode/validate-installation.sh full

# Quick validation
./uCode/validate-installation.sh quick
```

## 🔧 Integration Features

### VS Code Task Integration
All packages include VS Code task definitions for seamless IDE integration:
- Press `Cmd+Shift+P`
- Type "Tasks: Run Task"  
- Select package-specific tasks

### uScript Integration
All command-line tools are available in uScript automation:
```uScript
' Search for TODO items
RUN "rg 'TODO' ./uMemory/ --type md"

' Find mission files  
RUN "fd 'mission-.*\.md$' ./uMemory/missions/"

' View with syntax highlighting
RUN "bat " + filename

' Render markdown
RUN "glow " + readme_file

' Process JSON data
RUN "echo '" + json_data + "' | jq '.results[]'"
```

### Dashboard Integration
Packages contribute to uDOS dashboard functionality:
- **ripgrep**: Content analysis and search statistics
- **fd**: File discovery and organization metrics  
- **bat**: Enhanced log and code viewing
- **glow**: Beautiful documentation rendering
- **jq**: Data processing and formatting
- **AI**: Intelligent analysis and recommendations

## 📚 Documentation

Each package includes comprehensive documentation:
- Installation instructions
- Usage examples  
- uDOS-specific workflows
- VS Code integration
- Configuration options
- Best practices

## 🔄 Package Management Commands

```bash
# List available packages
./uCode/packages/manager-simple.sh list

# Install specific package
./uCode/packages/manager-simple.sh install <package-name>

# Update all packages  
./uCode/packages/manager-simple.sh update

# Check package status
./uCode/packages/manager-simple.sh status <package-name>

# Remove package
./uCode/packages/manager-simple.sh remove <package-name>
```

---

*Complete package ecosystem for enhanced uDOS development workflows.*
