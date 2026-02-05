# VS Code Configuration & Error Solutions

**Status:** Applied to all workspaces  
**Target:** Fix 4 critical VS Code errors  

---

## Overview

All VS Code settings have been updated across the uDOS workspace to address:

1. **Terminal heredoc crashes** with git commit messages
2. **Python venv auto-activation** failures
3. **GitHub Copilot timeout** on long requests
4. **Local model conflicts** (Ollama, OpenAI, Codex)

---

## Applied Configurations

### 1. Root Workspace Settings

**Location:** `core/.vscode/settings.json`

Provides Python environment configuration for the main Core workspace with:
- Auto venv detection via `python.defaultInterpreterPath`
- Terminal shell initialization with bash login mode (`-l`, `-i`)
- Environment variables for VIRTUAL_ENV and PYTHONPATH
- Git settings to prevent autofetch delays
- Copilot model selection (gpt-4-turbo primary)

### 2. Per-Workspace Settings

Each workspace has its own `.vscode/settings.json`:

```
core/.vscode/settings.json          (relative: ../venv)
wizard/.vscode/settings.json        (relative: ../venv)
extensions/.vscode/settings.json    (relative: ../venv)
dev/goblin/.vscode/settings.json    (relative: ../../venv)
app/App.code-workspace              (workspace-level settings)
```

### 3. App Tauri Workspace

**Location:** `app/App.code-workspace`

Updated with Python environment settings alongside existing Svelte/TypeScript configs.

---

## Key Settings Explained

### Terminal Configuration (Fixes Error #2)

```json
{
  "terminal.integrated.defaultProfile.osx": "bash",
  "terminal.integrated.profiles.osx": {
    "bash": {
      "path": "/bin/bash",
      "args": ["-l"],           // Login shell - loads .bashrc/.bash_profile
      "icon": "terminal-bash"
    }
  },
  "terminal.integrated.env.osx": {
    "VIRTUAL_ENV": "${workspaceFolder}/../venv",
    "PATH": "${workspaceFolder}/../venv/bin:${env:PATH}"
  },
  "terminal.integrated.shellArgs.osx": ["-l", "-i"]  // Interactive login shell
}
```

**Effect:** Terminal automatically activates Python venv and uses correct `python` executable.

### Python Configuration (Fixes Error #2)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/../venv/bin/python",
  "python.terminal.executeInFileDir": true,
  "python.terminal.focusAfterLaunch": true
}
```

**Effect:** Copilot and Python extension always use venv interpreter, avoiding python/python3 confusion.

### Git Configuration (Fixes Error #1)

```json
{
  "git.autofetch": false,
  "git.confirmSync": false,
  "git.fetchOnPull": false
}
```

**Effect:** Disables background git operations that can interfere with terminal heredoc commands.

### Copilot Configuration (Fixes Errors #3 & #4)

```json
{
  "github.copilot.enable": {
    "*": true,
    "plaintext": false,
    "markdown": false,
    "yaml": true,
    "json": true,
    "python": true,
    "typescript": true,
    "javascript": true
  },
  "github.copilot.advanced.debug.overrideChatModel": "gpt-4-turbo",
  "github.copilot.advanced.debug.overrideChatApiUrl": "https://api.openai.com/v1/chat/completions"
}
```

**Effect:** 
- Single provider (Copilot with gpt-4-turbo) eliminates local model conflicts
- Disables Copilot in plaintext/markdown to avoid interference with documentation
- Configures OpenAI API endpoint explicitly to prevent fallback confusion

### Formatter Configuration (Fixes Error #4)

```json
{
  "editor.defaultFormatter": null,
  "[markdown]": {
    "editor.defaultFormatter": null,
    "editor.formatOnSave": false
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": false
  }
}
```

**Effect:** Prevents formatter conflicts with Copilot inline suggestions.

---

## Recommended Extensions

Install these to enhance the setup:

| Extension | Purpose | Install |
|-----------|---------|---------|
| **Commit Message Editor** | Avoid heredoc crashes | `adam-bender.commit-message-editor` |
| **Python Envy** | Auto venv activation | `teticio.python-envy` |
| **Python** | Core Python support | `ms-python.python` |
| **Pylance** | Type checking & IntelliSense | `ms-python.vscode-pylance` |
| **GitHub Copilot** | AI-assisted development | `github.copilot` |
| **GitHub Copilot Chat** | Extended chat interface | `github.copilot-chat` |

Install via:
```bash
code --install-extension adam-bender.commit-message-editor
code --install-extension teticio.python-envy
code --install-extension ms-python.python
```

---

## Verification Checklist

After applying these settings:

- [ ] Open terminal in VS Code (`` Ctrl+` ``)
- [ ] Check prompt shows `(venv)` prefix
- [ ] Run `python --version` → shows venv Python
- [ ] Run `which python` → points to `../venv/bin/python`
- [ ] Open Copilot Chat (`Cmd+Shift+I`)
- [ ] Test commit with multiline message (should use editor, not heredoc)
- [ ] Check `memory/logs/health-training.log` for startup verification

---

## Troubleshooting

### Issue: Terminal doesn't show `(venv)` prefix

**Solution:** 
```bash
# Add to ~/.zshrc or ~/.bashrc
if [ -f "$(pwd)/../venv/bin/activate" ]; then
    source ../venv/bin/activate
fi
```

### Issue: `python: command not found`

**Solution:**
```bash
# Verify venv exists
ls -la ../venv/bin/python

# Reload VS Code terminal (Ctrl+Shift+`)
```

### Issue: Copilot still times out

**Solution:**
- Use Copilot Chat (`Cmd+Shift+I`) instead of inline suggestions
- Break long requests into multiple smaller questions
- Check `github.copilot.advanced.debug.overrideChatModel` is set to `gpt-4-turbo`

### Issue: Git commit still hangs

**Solution:**
- Use Commit Message Editor extension
- Avoid heredoc syntax; use `git commit -m "..."` or editor mode
- Check `git.autofetch` is `false`

---

## Daily Usage

### Start Development Session

```bash
# 1. Open VS Code
code .

# 2. Open terminal (Ctrl+`)
# Terminal should auto-activate venv

# 3. Verify setup
python -m core.version check

# 4. Start TUI for testing
python -m core.tui

# 5. Log session
echo "[$(date)] Session started with venv" >> memory/logs/health-training.log
```

### Commit Changes (Safe Method)

```bash
# Option 1: Editor mode (recommended)
git commit

# Option 2: Short message
git commit -m "feature: add xyz"

# Option 3: Use extension
# Press Cmd+Shift+P → "Commit Message Editor"
```

---

## Impact Summary

| Error | Before | After |
|-------|--------|-------|
| **Heredoc crashes** | Terminal hangs on multiline commits | Uses editor for safe commit messages |
| **Venv confusion** | Mixed python/python3 versions | Always uses venv Python |
| **Copilot timeouts** | Long requests fail silently | gpt-4-turbo with explicit API routing |
| **Model conflicts** | Ollama ↔ OpenAI ↔ Codex fights | Single provider (Copilot) selected |

---

## Root Workspace File

A unified workspace file has been created at the repository root:

**Location:** `uDOS.code-workspace`

### Features

- **14 Folders:** All subdirectories visible in Explorer
  - 7 Public: Core, Wizard, Extensions, Knowledge, Library, Docs
  - 6 Dev: Goblin, Empire, Groovebox, App, Tests, Tools
  - 1 Local: Memory (logs, tests, credentials)

- **Workspace-Level Settings:** Applied to all folders
  - Python environment configuration
  - Terminal auto-activation
  - Git settings
  - Copilot configuration
  - File exclusions (node_modules, __pycache__, etc.)

- **Integrated Tasks:** Quick access to common operations
  - `🐍 Python: Check Version` — Verify core.version
  - `🧪 Python: Run Tests` — Full test suite
  - `💻 Core: Start TUI` — Launch Core TUI
  - `🧙 Wizard: Start Server` — Launch Wizard API
  - `🐛 Goblin: Start Dev Server` — Launch Goblin dev
  - `📦 Install Dependencies` — pip install -r requirements.txt
  - `✅ Setup Venv` — Create virtual environment
  - `📝 Health Check` — Run health dashboard
  - `🚀 Full Setup` — Complete initialization

- **Launch Configurations:** Debug different components
  - Python: Current File
  - Python: Core TUI
  - Wizard: Server Debug
  - Pytest: All Tests

### Open Root Workspace

```bash
cd /Users/fredbook/Code/uDOS
code uDOS.code-workspace
```

Or via VS Code:
1. `Cmd+K Cmd+O` → Select `uDOS.code-workspace`
2. Or drag `uDOS.code-workspace` onto VS Code window

### Folder Structure in Explorer

```
📁 uDOS (Workspace)
├── 🏠 Root
├── 📦 Core (Public)
├── 🧙 Wizard (Public)
├── 🔌 Extensions (Public)
├── 📚 Knowledge (Public)
├── 🗂️ Library (Public)
├── 📖 Docs (Public)
├── 👹 Goblin (Dev)
├── 🏰 Empire (Dev)
├── 🎸 Groovebox (Dev)
├── 🎯 App (Dev)
├── 🧪 Tests (Dev)
├── 🔧 Tools (Dev)
└── 💾 Memory (Local)
```

---

## Workspace Tasks Quick Reference

Run any task with `Cmd+Shift+B` (Build/Default) or `Cmd+Shift+P` → Tasks:

### Testing & Verification
```bash
# Full test suite
Cmd+Shift+P → "Run Task: 🧪 Python: Run Tests"

# Health dashboard
Cmd+Shift+P → "Run Task: 📝 Health Check"

# Version check
Cmd+Shift+P → "Run Task: 🐍 Python: Check Version"
```

### Development Servers
```bash
# Core TUI (blocking)
Cmd+Shift+P → "Run Task: 💻 Core: Start TUI"

# Wizard server (background)
Cmd+Shift+P → "Run Task: 🧙 Wizard: Start Server"

# Goblin dev server (background)
Cmd+Shift+P → "Run Task: 🐛 Goblin: Start Dev Server"
```

### Initialization
```bash
# One-time setup
Cmd+Shift+P → "Run Task: ✅ Setup Venv"
Cmd+Shift+P → "Run Task: 📦 Install Dependencies"

# Full initialization
Cmd+Shift+P → "Run Task: 🚀 Full Setup"
```

---

## Debug Configurations

### Python Debugging

Launch configurations available via `Cmd+Shift+D`:

1. **Python: Current File**
   - Debug the open Python file
   - Set breakpoints with `F9`

2. **Python: Core TUI**
   - Debug Core TUI startup
   - Useful for testing command routing

3. **Wizard: Server Debug**
   - Debug Wizard API endpoints
   - Watch request/response handling

4. **Pytest: All Tests**
   - Debug test execution
   - Inspect test failures in-editor

### Using Debugger

```
1. Set breakpoint: Click left margin (or F9)
2. Launch config: Cmd+Shift+D → Select configuration
3. Step through: F10 (step over), F11 (step in)
4. Inspect variables: Hover or use Debug Console
5. Stop: Shift+F5
```

---

## Multi-Workspace Search & Navigation

### Search Across All Folders

Use `Cmd+Shift+F` to search all workspace folders:

```
Example: Search "router" to find:
├── wizard/routes/api_routes.py
├── extensions/api/routes/webhook.py
├── core/runtime/router.py
```

### Jump Between Folders

`Cmd+P` → Start typing folder name:
```
core:      → Jump to core/ folder files
wizard:    → Jump to wizard/ folder files
tests:     → Jump to tests/ folder files
docs:      → Jump to docs/ folder files
```

### File Outline (Quick Navigation)

`Cmd+Shift+O` → Navigate to symbol within current file
`Cmd+T` → Jump to symbol in workspace

---

## Environment Variables (Workspace-Level)

Automatically set in every terminal:

```bash
VIRTUAL_ENV="/Users/fredbook/Code/uDOS/venv"
PATH="/Users/fredbook/Code/uDOS/venv/bin:$PATH"
PYTHONPATH="/Users/fredbook/Code/uDOS"
PROJECT_ROOT="/Users/fredbook/Code/uDOS"
```

Access in Python:
```python
import os
venv_path = os.environ.get('VIRTUAL_ENV')
project_root = os.environ.get('PROJECT_ROOT')
```

---

## Per-Folder Settings

Individual folder `.vscode/settings.json` files override root settings if needed:

```
core/.vscode/settings.json          (overrides for Core)
wizard/.vscode/settings.json        (overrides for Wizard)
extensions/.vscode/settings.json    (overrides for Extensions)
dev/goblin/.vscode/settings.json    (overrides for Goblin)
app/App.code-workspace              (Tauri-specific configs)
```

To apply folder-specific setting:
```jsonc
{
  "settings": {
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true
  }
}
```

---

## Git Integration

### Git Settings Applied

- **Auto-fetch:** Disabled (prevents background hangs)
- **Confirm sync:** Disabled (faster pushes)
- **Fetch on pull:** Disabled (manual control)

### Recommended Git Extensions

Installed via recommendations:
- **Git History** — View commit history
- **Git Graph** — Visual branch visualization
- **GitLens** — Code authorship & blame

### Safe Commit Workflow

```bash
# 1. Stage changes
Cmd+Shift+G → Stage files

# 2. Open commit message editor (recommended)
Cmd+Shift+P → "Git: Commit"

# 3. Type message in editor (avoids heredoc)

# 4. Push
git push origin branch-name
```

---

## Troubleshooting Workspace Issues

### Issue: Folders not showing in Explorer

**Solution:**
```bash
# Reload workspace
Cmd+R

# Or close/reopen VS Code with workspace:
code uDOS.code-workspace
```

### Issue: Settings from one folder override others

**Solution:**
- Root-level settings in `uDOS.code-workspace` apply to all
- Folder-level `.vscode/settings.json` only override within that folder
- Check folder settings if behavior is unexpected

### Issue: Terminal still not activating venv

**Solution:**
```bash
# Verify workspace file has correct Python path
cat uDOS.code-workspace | grep defaultInterpreterPath

# Manually activate if needed:
source venv/bin/activate

# Reload terminal: Ctrl+Shift+`
```

### Issue: Tasks not appearing

**Solution:**
```bash
# Reload workspace
Cmd+R

# Verify tasks.json is valid JSON
Cmd+Shift+P → "Tasks: Open User Tasks"
```

---

## Performance Tips

### Optimize Search Speed

Reduce excluded folders if searching is slow:

```json
"search.exclude": {
  "**/node_modules": true,
  "**/.venv": true
}
```

### Reduce File Watching

If VS Code feels sluggish:

```json
"files.watcherExclude": {
  "**/node_modules/**": true,
  "**/.git/**": true,
  "**/dist/**": true
}
```

### Disable Expensive Extensions

Check which extensions are running:
- `Cmd+Shift+P` → "Developer: Show Running Extensions"
- Disable non-essential extensions for this workspace

---

## Next Steps

### 1. Load Root Workspace
```bash
code uDOS.code-workspace
```

### 2. Verify Setup
```bash
# Terminal should show (venv) prefix
Ctrl+`

# Run health check
Cmd+Shift+P → "Run Task: 📝 Health Check"
```

### 3. Test All Components
```bash
# Run test suite
Cmd+Shift+P → "Run Task: 🧪 Python: Run Tests"

# Start Core TUI
Cmd+Shift+P → "Run Task: 💻 Core: Start TUI"

# Start Wizard server
Cmd+Shift+P → "Run Task: 🧙 Wizard: Start Server"
```

### 4. Log Session
```bash
echo "[$(date)] Workspace configured: uDOS.code-workspace loaded successfully" >> memory/logs/health-training.log
```

### 5. Proceed with Core Setup
- Start TUI and run full test suite
- Verify all services launch without errors
- Log results to `memory/logs/daily-2026-02-01.md`

---

## Summary

| Component | Location | Command |
|-----------|----------|---------|
| **Workspace File** | `uDOS.code-workspace` | `code uDOS.code-workspace` |
| **Root Settings** | `uDOS.code-workspace` → settings | Applied globally to all folders |
| **Tasks** | `uDOS.code-workspace` → tasks | `Cmd+Shift+P` → "Run Task" |
| **Debugger** | `uDOS.code-workspace` → launch | `Cmd+Shift+D` → Select config |
| **Extensions** | `uDOS.code-workspace` → extensions | Recommended for installation |
| **Folder Settings** | `{folder}/.vscode/settings.json` | Folder-specific overrides |
| **Health Check** | `memory/tests/health_dashboard.py` | Integrated task |
| **Logs** | `memory/logs/` | Session & health logs |

---

**Last Updated:** 2026-02-01  
**Workspace:** uDOS.code-workspace (root)  
**Applied Folders:** 14 (all subdirectories)  
**Status:** ✅ Full Workspace Ready for Core Setup
