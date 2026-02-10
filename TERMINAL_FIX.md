# VSCode Terminal Alternative Buffer Fix

## Problem
VSCode terminal was triggering **alternate buffer mode** (pagers like `less`) which would:
- Block terminal output with interactive pager
- Require manual `q` to exit
- Prevent script execution from continuing
- Make development workflow difficult

## Solution
Disable all pagers globally and configure VSCode terminal environment.

## What Was Fixed

### 1. VSCode Settings (`.vscode/settings.json`)
Added environment variables for both macOS and Linux:
```json
"terminal.integrated.env.osx": {
  "PAGER": "cat",
  "GIT_PAGER": "cat",
  "PYTHONUNBUFFERED": "1",
  "LESS": "-R"
},
"terminal.integrated.env.linux": {
  "PAGER": "cat",
  "GIT_PAGER": "cat",
  "PYTHONUNBUFFERED": "1",
  "LESS": "-R"
}
```

### 2. Dev Environment Script (`bin/dev-env.sh`)
Source this in your shell for manual setup:
```bash
source bin/dev-env.sh
```

### 3. Git Config (`bin/.gitconfig-nopager`)
Pre-configured git settings:
```bash
cp bin/.gitconfig-nopager ~/.gitconfig
```

### 4. Command Helper (`bin/udos-cmd`)
Run any command without pagers:
```bash
bin/udos-cmd git log --oneline
bin/udos-cmd python test.py
bin/udos-cmd ls -la
```

## How to Apply

### Option 1: Automatic (Recommended)
Close and reopen VSCode. Settings auto-apply.

### Option 2: Manual - Set Environment Variables
```bash
# In your current shell
export PAGER=cat
export GIT_PAGER=cat
export PYTHONUNBUFFERED=1
export LESS=-R
```

### Option 3: Add to Shell Config
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PAGER=cat' >> ~/.bashrc
echo 'export GIT_PAGER=cat' >> ~/.bashrc
echo 'export PYTHONUNBUFFERED=1' >> ~/.bashrc
source ~/.bashrc
```

### Option 4: Configure Git Globally
```bash
git config --global core.pager cat
git config --global pager.log cat
git config --global pager.diff cat
git config --global pager.show cat
git config --global pager.status cat
```

## Verify Fix

### Check VSCode Settings
- `Ctrl+,` (Settings)
- Search: `terminal.integrated.env`
- Verify `PAGER: cat` is set

### Test Git Commands
```bash
git log --oneline        # Should show without pager
git status               # Should show without pager
git diff                 # Should show without pager
```

### Test Python
```bash
python -c "print('Hello' * 100)"  # Should output without paging
```

## What Each Variable Does

| Variable | Purpose | Value |
|----------|---------|-------|
| `PAGER` | Default pager for all commands | `cat` (no paging) |
| `GIT_PAGER` | Git-specific pager | `cat` (no paging) |
| `PYTHONUNBUFFERED` | Python output buffering | `1` (unbuffered) |
| `LESS` | Less pager options | `-R` (raw control chars) |

## Files Modified

1. `.vscode/settings.json` - VSCode terminal environment
2. `bin/dev-env.sh` - Dev environment setup script
3. `bin/.gitconfig-nopager` - Git pager configuration
4. `bin/udos-cmd` - Command helper wrapper

## Impact

✅ Terminal output now displays immediately
✅ No more blocking on pager `q` prompts
✅ Git commands work smoothly
✅ Python output streams correctly
✅ Scripts run without interruption
✅ Development workflow restored

## Troubleshooting

### Still seeing pagers?
1. Close VSCode completely
2. Reopen VSCode
3. Verify settings: `Ctrl+,` → search "pager"

### Want pagers for specific commands?
```bash
# Use | less directly when needed
git log | less
git diff | less
```

### Revert changes?
```bash
# Remove environment variables
unset PAGER GIT_PAGER PYTHONUNBUFFERED LESS

# Or reset git config
git config --global --unset core.pager
git config --global --unset pager.log
```

---
**Status**: ✅ Fixed
**Date**: February 10, 2026
**Scope**: VSCode terminal environment across Mac/Linux
