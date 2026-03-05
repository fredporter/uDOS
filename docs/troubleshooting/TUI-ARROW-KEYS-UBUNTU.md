# TUI Arrow Keys on Ubuntu

Updated: 2026-03-05
Status: active troubleshooting note

If arrow keys print escape sequences or fail to navigate in `ucode`, use this recovery sequence.

## Symptoms

- `^[[A` / `^[[B` appears instead of cursor movement
- form selectors do not respond to arrow keys
- menu navigation falls back to numeric-only behavior

## Quick Fix

```bash
sudo apt-get install -y libreadline-dev libncurses5-dev python3-dev
UV_PROJECT_ENVIRONMENT=.venv uv pip install --python .venv/bin/python --upgrade --force-reinstall prompt_toolkit
```

Then restart terminal and run:

```bash
./bin/udos
```

## Verify

```bash
echo "$TERM"
./.venv/bin/python -c "import sys; print(sys.stdin.isatty(), sys.stdout.isatty())"
```

Expected:

- `TERM` is `xterm-256color` (or another `*-256color` terminal)
- both TTY checks return `True`

## Related

- [Troubleshooting Home](README.md)
- [Installation Guide](../INSTALLATION.md)
- [UCODE Offline Operator Runbook](../howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md)
