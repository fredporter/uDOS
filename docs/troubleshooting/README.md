# TUI Troubleshooting - Quick Reference

Quick solutions for common TUI issues.

---

## UCODE Offline Operations

For no-network operation and fallback recovery procedures, use:

- [UCODE-OFFLINE-OPERATOR-RUNBOOK.md](../howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md)

---

## Arrow Keys Not Working (Ubuntu/Debian)

**Quick Fix:**
```bash
sudo apt-get install -y libreadline-dev libncurses5-dev python3-dev
UV_PROJECT_ENVIRONMENT=.venv uv pip install --python .venv/bin/python --upgrade --force-reinstall prompt_toolkit
```

**Full Guide:** [TUI-ARROW-KEYS-UBUNTU.md](TUI-ARROW-KEYS-UBUNTU.md)

---

## Form Fields Not Interactive

**Symptoms:**
- No arrow key support in forms
- Simple text prompts instead of visual widgets
- "Fallback mode" message

**Check:**
1. Terminal type: `echo $TERM` (should be `xterm-256color` or similar)
2. TTY status: `python3 -c "import sys; print(sys.stdin.isatty())"`
3. prompt_toolkit installed: `pip list | grep prompt-toolkit`

**Fix:**
```bash
export TERM=xterm-256color
UV_PROJECT_ENVIRONMENT=.venv uv pip install --python .venv/bin/python prompt_toolkit>=3.0.0
```

---

## Command History Not Working

**Issue:** ↑/↓ keys don't navigate command history

**Solutions:**
1. Install system dependencies (Ubuntu):
   ```bash
   sudo apt-get install libreadline-dev
   ```

2. Check if running in proper terminal (not pipe or redirect)

3. Verify prompt_toolkit is active:
   ```python
   from core.input.smart_prompt import SmartPrompt
   prompt = SmartPrompt()
   print(f"Fallback mode: {prompt.use_fallback}")
   # Should be False for full features
   ```

---

## Menu Navigation Issues

**Symptoms:**
- Arrow keys print escape codes in menus
- Can't navigate with ↑/↓

**Quick Fix:**
Same as "Arrow Keys Not Working" above.

**Fallback:** All menus support numeric input (1, 2, 3, etc.) as fallback.

---

## Tab Completion Not Working

**Check:**
1. Using active interface: `vibe` (interactive) or `./bin/ucode` (direct command)
2. Not in piped/redirected mode: `./bin/ucode ... | tee` disables TAB
3. `uv` environment is synced: `uv sync`

**Fix:**
```bash
uv sync
vibe
```

---

## Installation Issues

### uv pip install fails

**Error:** "Failed building wheel for [package]"

**Solution:** Install Python development headers:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# Fedora/RHEL
sudo dnf install python3-devel gcc

# macOS
xcode-select --install
```

### Virtual environment not activating

**Symptom:** `/.venv` is missing or shell activation assumptions are stale

**Check:**
```bash
ls -la .venv/bin/python
# Should exist
```

**Fix:**
```bash
rm -rf .venv
uv venv .venv --python 3.12
UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --dev
```

---

## Terminal Compatibility

### Recommended Terminals

✅ **Full Support:**
- GNOME Terminal
- Konsole
- iTerm2 (macOS)
- Windows Terminal
- Alacritty
- Kitty

⚠️ **Limited Support:**
- Basic xterm
- Screen/tmux (may need TERM adjustment)

❌ **Not Supported:**
- Serial console
- Dumb terminal (TERM=dumb)
- Piped input/output

### Setting Proper TERM

```bash
# Add to ~/.bashrc or ~/.zshrc
export TERM=xterm-256color
```

Or for tmux:
```bash
# In ~/.tmux.conf
set -g default-terminal "screen-256color"
```

---

## Diagnostic Commands

### Check System Dependencies
```bash
# Ubuntu/Debian
dpkg -l | grep -E "readline|ncurses"

# Should show:
# libreadline-dev
# libncurses5-dev
```

### Check Python Modules
```bash
uv run python -c "
import sys
try:
    import prompt_toolkit
    print(f'✓ prompt_toolkit {prompt_toolkit.__version__}')
except ImportError:
    print('✗ prompt_toolkit not installed')

try:
    import readline
    print('✓ readline available')
except ImportError:
    print('✗ readline not available')

print(f'✓ stdin.isatty: {sys.stdin.isatty()}')
print(f'✓ stdout.isatty: {sys.stdout.isatty()}')
"
```

### Check Virtual Environment
```bash
uv run python -c 'import sys; print(sys.executable)'

uv pip list | grep -E "prompt|fastapi|rich"
# Should show all installed
```

---

## Environment Variables

Set these if experiencing issues:

```bash
# Force proper terminal type
export TERM=xterm-256color

# Enable debug logging for SmartPrompt
export DEBUG_SMARTPROMPT=1

# Disable Wizard autostart (if having port conflicts)
export WIZARD_AUTOSTART=0

# Use custom Wizard URL
export WIZARD_BASE_URL=http://localhost:8765
```

Add to `~/.bashrc` or `~/.zshrc` to persist.

---

## Getting More Help

1. **Enable Debug Mode:**
   ```bash
   export DEBUG_SMARTPROMPT=1
   vibe
   ```

2. **Check Logs:**
   ```bash
   tail -f memory/logs/udos/ucode/*.jsonl
   ```

3. **Run Health Check:**
   ```bash
   uv run python -m core.services.self_healer
   ```

4. **System Info:**
   ```bash
   uv run python -m core.version
   ```

---

## Related Documentation

- [TUI-ARROW-KEYS-UBUNTU.md](TUI-ARROW-KEYS-UBUNTU.md) - Ubuntu arrow key fix
- [Legacy TUI Smart Fields Guide](../.compost/tui-legacy-2026-02/TUI-SMART-FIELDS-GUIDE.md) - Archived pre-`vibe-cli` interactive guidance
- [INSTALLATION.md](../../INSTALLATION.md) - Installation guide
- [Legacy TUI Migration Plan](../.compost/tui-legacy-2026-02/TUI-MIGRATION-PLAN.md) - Archived TUI migration context

---

**Last Updated:** 2026-02-09
**Applies To:** uDOS v1.3.x+
