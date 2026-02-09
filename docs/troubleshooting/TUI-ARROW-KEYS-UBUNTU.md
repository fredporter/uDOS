# TUI Arrow Keys Not Working - Ubuntu Fix

**Issue:** Arrow keys don't work in uDOS TUI on Ubuntu/Debian systems.

**Symptoms:**
- Arrow keys print escape sequences (e.g., `^[[A`, `^[[B`) instead of navigating
- Cannot navigate menus with ↑/↓ keys
- Form fields (date picker, number picker, bar selector) don't respond to arrows
- History navigation (↑/↓) doesn't work in command prompt

---

## Root Cause

Ubuntu/Debian systems require **system-level readline and ncurses libraries** for proper terminal input handling. The Python `prompt_toolkit` library depends on these system libraries to properly interpret arrow key escape sequences.

---

## Quick Fix

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y libreadline-dev libncurses5-dev python3-dev
```

### 2. Reinstall Python Dependencies

After installing system libraries, reinstall Python packages to ensure they're built with proper support:

```bash
source venv/bin/activate
pip install --upgrade --force-reinstall prompt_toolkit
```

### 3. Verify Fix

```bash
python3 -c "import prompt_toolkit; print(f'prompt_toolkit: {prompt_toolkit.__version__}')"
```

Should show version 3.0.0 or higher.

### 4. Test in TUI

Launch uDOS and test arrow key functionality:

```bash
./bin/Launch-uCODE.sh
```

Try:
- Pressing ↑/↓ to navigate command history
- Running `SETUP` and using arrow keys in form fields
- Using interactive menus with arrow navigation

---

## Alternative: Use Automated Installer

The installer script now automatically detects Ubuntu/Debian and installs dependencies:

```bash
./bin/install.sh --mode core
```

---

## Why This Happens

1. **Python built without readline support:** If Python was compiled without readline library headers available, the `readline` module won't have full functionality.

2. **Missing ncurses:** Terminal manipulation requires ncurses libraries at the system level.

3. **No development headers:** Without `-dev` packages, Python can't link to the native libraries during package installation.

---

## Verification Steps

### Check if readline is available:

```bash
python3 -c "import readline; print('Readline available')" 2>&1
```

Should print: `Readline available`

### Check terminal capabilities:

```bash
echo $TERM
# Should be: xterm-256color, screen-256color, or similar (not 'dumb')
```

### Test prompt_toolkit directly:

```python
from prompt_toolkit import prompt
result = prompt("Test: ")
# Arrow keys should work for editing
```

---

## Still Not Working?

### 1. Check Terminal Emulator

Some minimal terminal emulators don't support full escape sequences. Recommended:
- GNOME Terminal
- Konsole
- xterm
- Alacritty

Avoid:
- Basic xterm without proper terminfo
- Serial console
- Minimal SSH sessions without PTY

### 2. Check TERM Variable

```bash
export TERM=xterm-256color
```

Add to `~/.bashrc` or `~/.zshrc` to persist.

### 3. Fallback Mode

If arrow keys still don't work, uDOS automatically falls back to numeric input:

```
Interactive Menu:
  1. Option One
  2. Option Two
  3. Option Three

Choice (1-3): 2
```

This fallback ensures all functionality remains available even without arrow key support.

---

## For Other Distributions

### Fedora/RHEL/CentOS:
```bash
sudo dnf install readline-devel ncurses-devel python3-devel
```

### Arch Linux:
```bash
sudo pacman -S readline ncurses python
```

### Alpine Linux:
```bash
apk add readline-dev ncurses-dev python3-dev
```

### macOS:
```bash
brew install readline ncurses
```

---

## Technical Details

**What happens under the hood:**

1. User presses arrow key (e.g., ↑)
2. Terminal sends ANSI escape sequence: `\x1b[A`
3. `prompt_toolkit` uses system readline to interpret sequence
4. If readline is missing or broken, raw escape sequence is returned
5. Application sees `\x1b[A` instead of 'up' key event

**System libraries needed:**
- `libreadline` - Command-line editing and history
- `libncurses` - Terminal screen handling
- Python development headers - For building native extensions

---

## Related Documentation

- [INSTALLATION.md](../../INSTALLATION.md) - Full installation guide
- [TUI_FORM_SYSTEM.md](../specs/TUI_FORM_SYSTEM.md) - Form field documentation
- [INTERACTIVE-MENUS-IMPLEMENTATION.md](../specs/INTERACTIVE-MENUS-IMPLEMENTATION.md) - Menu system

---

**Last Updated:** 2026-02-09
**Applies To:** uDOS v1.3.x+
