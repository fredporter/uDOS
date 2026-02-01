# VS Code Setup - Quick Start Guide

**Status:** ✅ Complete  
**Date:** 2026-02-01  
**Workspace:** `uDOS.code-workspace` (unlimitedly expanded)

---

## 🚀 Get Started in 3 Steps

### Step 1: Open Root Workspace
```bash
cd /Users/fredbook/Code/uDOS
code uDOS.code-workspace
```

### Step 2: Verify Environment
```bash
# Terminal should show:
(venv) fred@mac uDOS %

# Or run health check task:
Cmd+Shift+P → "Run Task: 📝 Health Check"
```

### Step 3: Start Round 2 Setup
```bash
# Option A: Full automated setup
Cmd+Shift+P → "Run Task: 🚀 Round 2: Full Setup"

# Option B: Manual steps
1. Cmd+Shift+P → "Run Task: ✅ Setup Venv"
2. Cmd+Shift+P → "Run Task: 📦 Install Dependencies"
3. Cmd+Shift+P → "Run Task: 🧪 Python: Run Tests"
4. Cmd+Shift+P → "Run Task: 💻 Core: Start TUI"
```

---

## 📂 Workspace Structure (All Visible)

```
UDO  (uDOS.code-workspace)
├─ 🏠 Root                    ← Project root
├─ 📦 Core (Public)           ← Core runtime
├─ 🧙 Wizard (Public)         ← API/OAuth services
├─ 🔌 Extensions (Public)     ← Plugin system
├─ 📚 Knowledge (Public)      ← Knowledge base
├─ 🗂️ Library (Public)        ← Library tools
├─ 📖 Docs (Public)           ← Documentation
├─ 👹 Goblin (Dev)            ← Dev TUI server
├─ 🏰 Empire (Dev)            ← CRM integration
├─ 🎸 Groovebox (Dev)         ← Audio engine
├─ 🎯 App (Dev)               ← Tauri GUI
├─ 🧪 Tests (Dev)             ← Test suite
├─ 🔧 Tools (Dev)             ← Dev tools
└─ 💾 Memory (Local)          ← Logs & credentials
```

---

## ⚡ Essential Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| **Run Task** | `Cmd+Shift+P` → "Run Task" |
| **Debug** | `Cmd+Shift+D` |
| **Terminal** | `` Ctrl+` `` |
| **Search Workspace** | `Cmd+Shift+F` |
| **Jump to File** | `Cmd+P` |
| **Jump to Symbol** | `Cmd+Shift+O` |
| **Go to Definition** | `Cmd+Click` |
| **Rename Symbol** | `F2` |
| **Format Code** | `Shift+Option+F` |
| **Comment Line** | `Cmd+/` |
| **Reload Window** | `Cmd+R` |

---

## 🎯 Common Tasks

### Testing & Verification

```bash
# Run all tests
Cmd+Shift+P → "Run Task: 🧪 Python: Run Tests"

# Check version
Cmd+Shift+P → "Run Task: 🐍 Python: Check Version"

# Health dashboard
Cmd+Shift+P → "Run Task: 📝 Health Check"
```

### Development Servers

```bash
# Core TUI (blocks terminal)
Cmd+Shift+P → "Run Task: 💻 Core: Start TUI"

# Wizard API (background)
Cmd+Shift+P → "Run Task: 🧙 Wizard: Start Server"

# Goblin Dev (background)
Cmd+Shift+P → "Run Task: 🐛 Goblin: Start Dev Server"
```

### Environment Setup

```bash
# Create virtual environment
Cmd+Shift+P → "Run Task: ✅ Setup Venv"

# Install dependencies
Cmd+Shift+P → "Run Task: 📦 Install Dependencies"

# Complete setup
Cmd+Shift+P → "Run Task: 🚀 Round 2: Full Setup"
```

---

## 🐍 Python Environment

### Terminal Environment Variables

Automatically set in every terminal:

```bash
VIRTUAL_ENV=/Users/fredbook/Code/uDOS/venv
PATH=/Users/fredbook/Code/uDOS/venv/bin:$PATH
PYTHONPATH=/Users/fredbook/Code/uDOS
PROJECT_ROOT=/Users/fredbook/Code/uDOS
```

### Verify Python

```bash
# Check Python version
python --version

# Check venv location
which python

# Expected output:
/Users/fredbook/Code/uDOS/venv/bin/python
```

---

## 🔧 VS Code Configuration

### Root Settings File

**Location:** `uDOS.code-workspace`

**Key Settings:**
- Python interpreter: `${workspaceFolder}/venv/bin/python`
- Terminal shell: bash with login mode (`-l`)
- Copilot model: gpt-4-turbo
- Git autofetch: disabled
- Excluded: `__pycache__`, `node_modules`, `.git`

### Folder-Specific Settings

Override workspace settings per folder:

- `core/.vscode/settings.json`
- `wizard/.vscode/settings.json`
- `extensions/.vscode/settings.json`
- `dev/goblin/.vscode/settings.json`
- `app/App.code-workspace`

---

## 🆘 Troubleshooting

### Problem: Terminal doesn't show `(venv)`

**Solution:**
```bash
# Manually activate
source venv/bin/activate

# Reload terminal
Ctrl+Shift+`
```

### Problem: `python: command not found`

**Solution:**
```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python → /Users/fredbook/Code/uDOS/venv/bin/python
```

### Problem: Copilot still times out

**Solution:**
- Use Copilot Chat (`Cmd+Shift+I`) instead of inline
- Break long requests into smaller questions
- Check model is set to gpt-4-turbo

### Problem: Git commit hangs

**Solution:**
- Use Commit Message Editor extension
- Avoid heredoc syntax (`<<EOF`)
- Check `git.autofetch` is false

### Problem: Folders not showing in Explorer

**Solution:**
```bash
# Reload workspace
Cmd+R

# Or reopen with workspace file:
code uDOS.code-workspace
```

---

## 📋 Pre-Round 2 Checklist

- [ ] Opened `uDOS.code-workspace`
- [ ] Terminal shows `(venv)` prefix
- [ ] `which python` → venv path
- [ ] Ran health check task successfully
- [ ] Can see all 14 folders in Explorer
- [ ] Core TUI starts without errors
- [ ] Test suite runs and passes
- [ ] Copilot Chat responds normally
- [ ] Git commits work without hanging
- [ ] Logged setup completion to `memory/logs/`

---

## 📖 Full Documentation

For detailed information, see:

- [VSCODE-SETUP.md](VSCODE-SETUP.md) — Complete guide
- [WIZARD-ROUND2-PLAN.md](WIZARD-ROUND2-PLAN.md) — Round 2 plan
- [AGENTS.md](AGENTS.md) — Architecture rules
- [ROADMAP.md](ROADMAP.md) — Development timeline

---

## ✅ Status

| Component | Status |
|-----------|--------|
| Workspace file | ✅ `uDOS.code-workspace` created |
| Settings | ✅ Applied to all 14 folders |
| Terminal config | ✅ Venv auto-activation |
| Python interpreter | ✅ Configured to `/venv/bin/python` |
| Tasks | ✅ 9 tasks configured |
| Debug configs | ✅ 4 launch configurations |
| Extensions | ✅ Recommended list created |
| Documentation | ✅ Complete |

---

**Ready for Round 2!**

```bash
code uDOS.code-workspace
Cmd+Shift+P → "Run Task: 🚀 Round 2: Full Setup"
```

