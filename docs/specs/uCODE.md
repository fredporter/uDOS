---
title: uCODE - Unified Terminal TUI
version: v1.0.1
date: 2026-01-28
status: Production
---

# uCODE: The Unified Terminal TUI for uDOS

## Overview

**uCODE** is the pivotal single-entry-point Terminal TUI for uDOS. It's the recommended way to launch, configure, and manage all uDOS components from a unified command interface.

> **See also:** [VIBE-CLI-ROADMAP-ALIGNMENT.md](../../VIBE-CLI-ROADMAP-ALIGNMENT.md) for the roadmap of Mistral Vibe CLI integration into uCODE (v1.3.2+). This doc lists all recommended commands for document execution, Obsidian/Notion sync, scheduling, and scripting workflows.

### Key Features

- ✅ **Auto-detection** of available components (core, wizard, extensions, app)
- ✅ **Graceful fallback** to core-only mode if components are missing
- ✅ **Integrated Wizard control** (start/stop/status) from the TUI
- ✅ **Extension/plugin management** (list, install, remove, package)
- ✅ **Dynamic command registry** based on available components
- ✅ **Core command dispatch** for all standard uDOS commands

### Component Detection

On startup, uCODE detects which components are installed:

| Component      | Purpose                                    | Required?   | Managed By |
| -------------- | ------------------------------------------ | ----------- | ---------- |
| **CORE**       | TUI runtime and command handlers           | ✅ Yes      | —          |
| **WIZARD**     | Always-on server, AI routing, integrations | ❌ Optional | —          |
| **EXTENSIONS** | Plugins, API, transport systems            | ❌ Optional | Wizard     |
| **APP**        | Desktop GUI application                    | ❌ Optional | —          |

**Note**: Extensions (api, transport) are subordinate to Wizard. They require Wizard to be installed and provide network/transport capabilities.

**Graceful Fallback**: If wizard or extensions are missing, uCODE still runs perfectly in core-only mode—no errors, no missing features.

---

## Usage

### Launching uCODE

```bash
# Via main entry point
python uDOS.py

# Or directly via module
python -m core.tui.ucode

# Or via shell script
./bin/start_udos.sh
```

### Basic Commands

```
STATUS              - Show system status and component detection
HELP                - Show all available commands
EXIT, QUIT          - Exit uCODE
```

### Wizard Commands (if available)

```
WIZARD start        - Start Wizard server (background, non-blocking)
WIZARD stop         - Stop Wizard server
WIZARD status       - Check Wizard status and health
WIZARD console      - Enter Wizard interactive TUI
WIZARD [page]       - Show Wizard page (status, ai, devices, quota, logs)
WIZ [cmd]           - Alias for WIZARD
```

### Plugin Commands (if available)

```
PLUGIN list         - List installed extensions/plugins
PLUGIN install      - Install new plugin
PLUGIN remove       - Remove plugin
PLUGIN pack         - Package plugin for distribution
EXT [cmd]           - Alias for PLUGIN
EXTENSION [cmd]     - Alias for PLUGIN
```

### Core TUI Commands

Any command not recognized as a uCODE command is dispatched to the Core TUI handler. Use:

```
HELP                - Core TUI help (shows all core commands)
NEW [file]          - Create new file
FILE [cmd]          - File operations
WORKFLOW [cmd]      - Workflow management
... and 90+ more core commands
```

---

## Examples

### Start Development Environment

```
[uCODE] > WIZARD start
  Starting Wizard Server...
  ✅ Wizard Server started (PID: 45821)

[uCODE] > WIZARD status
  ✅ Wizard running on http://127.0.0.1:8765
     Status: healthy
```

### List Installed Extensions

```
[uCODE] > PLUGIN list
  Installed Extensions:
    ✅ api             v1.0.1
    ✅ transport       v1.0.1
```

### Check System Status

```
[uCODE] > STATUS
  ✅ CORE         Core TUI runtime (v1.0.7)
  ✅ WIZARD       Wizard server & services (v1.0.7)
  ✅ EXTENSIONS   Extensible plugin system
  ✅ APP          Desktop GUI application (v1.0.7)

  🧙 Wizard Server control available: Use WIZARD [start|stop|status]
  🔌 Extension management available: Use PLUGIN [list|install|remove]
```

### Core-Only Mode (No Wizard/Extensions)

```
[uCODE] > STATUS
  ✅ CORE         Core TUI runtime (v1.0.7)
  ❌ WIZARD       Wizard server (not installed)
  ❌ EXTENSIONS   Extensions system (not installed)
  ❌ APP          Desktop app (not installed)

[uCODE] > WIZARD start
  ❌ Wizard component not available.

[uCODE] > NEW myfile.md
  ✅ Created: myfile.md
  (core TUI continues normally)
```

---

## Architecture

### Component Detection Flow

```
uCODE startup
  ↓
ComponentDetector scans:
  core/           ← Always present
  wizard/         ← Optional
  extensions/     ← Optional
  app/            ← Optional
  ↓
Load version.json for each available component
  ↓
Build dynamic command registry
  ↓
Show banner + component status
  ↓
Enter REPL loop
```

### Command Dispatch

```
User input
  ↓
Parse command
  ↓
Is it a uCODE command? (STATUS, HELP, WIZARD, PLUGIN, EXIT)
  ↓ Yes → Execute handler
  ↓ No → Dispatch to Core TUI
  ↓
Display result
  ↓
Return to prompt
```

### Wizard Server Control

```
WIZARD start
  ↓
Check if already running (HTTP health check)
  ↓
If running: return
  ↓ If not:
Spawn subprocess: python wizard/server.py
  ↓
Poll /health endpoint (max 10 seconds)
  ↓
When healthy: return success
```

---

## Component Behaviors

### If CORE is missing

uCODE will fail to start. Core is non-negotiable.

### If WIZARD is missing

- ❌ WIZARD commands unavailable
- ✅ Core TUI runs normally
- ✅ All other features work
- ℹ️ Message shown at startup

Example:

```
[uCODE] > WIZARD start
  ❌ Wizard component not available.
```

### If EXTENSIONS is missing

- ❌ PLUGIN commands unavailable
- ✅ Core TUI runs normally
- ✅ Wizard (if present) works normally
- ℹ️ Message shown at startup

Example:

```
[uCODE] > PLUGIN list
  ❌ Extensions component not available.
```

### If APP is missing

- Detected but not exposed via uCODE
- Can still launch via separate script if needed
- No impact on other components

---

## Configuration

uCODE reads configuration from:

- `wizard/config/wizard.json` (if Wizard is available)
- `core/config/` (core configuration)
- Environment variables (as needed)

No additional uCODE-specific configuration is required.

---

## Troubleshooting

### uCODE won't start

Check Python imports:

```bash
python -c "from core.tui.ucode import uCODETUI; print('OK')"
```

### Wizard won't start

Check Wizard dependencies:

```bash
python -m wizard.server --help
```

Check port availability:

```bash
lsof -i :8765
```

### Extensions not detected

Verify extensions folder structure:

```bash
ls -la extensions/
# Should have: api/, transport/, docs/, README.md
```

### Commands not routing correctly

Try explicit HELP:

```
[uCODE] > HELP
# Shows all available commands
```

Try explicit core HELP:

```
[uCODE] > CORE HELP
# Shows core TUI commands
```

---

## Migration from Old Launchers

### Old way (separate launchers):

```bash
# Terminal 1
./bin/start_udos.sh           # Core TUI

# Terminal 2
python wizard/wizard_tui.py    # Wizard TUI

# Terminal 3
python wizard/dev_tui.py       # Dev recovery TUI
```

### New way (unified uCODE):

```bash
# Terminal 1 (single entry point)
python uDOS.py

# Within uCODE:
[uCODE] > WIZARD start       # Start Wizard server
[uCODE] > WIZARD console     # Enter Wizard TUI (if needed)
[uCODE] > [core commands]    # Run any core command
```

---

## Implementation Details

### Files

- **Main**: `core/tui/ucode.py` (483 lines)
- **Entry point**: `uDOS.py` (updated)
- **Module entry**: `core/tui/ucode_main.py`

### Classes

- `ComponentDetector` — Detect and validate components
- `uCODETUI` — Main TUI class with command routing

### Dependencies

- `core.tui.dispatcher` (Core command dispatch)
- `core.tui.renderer` (Output rendering)
- `core.tui.state` (Game state management)
- `core.input.SmartPrompt` (Advanced input)
- `core.services.logging_manager` (Logging)
- Standard library: subprocess, requests, json, logging

---

## Future Enhancements

- [ ] Wizard subprocess restart/respawn detection
- [ ] Plugin auto-update checks
- [ ] Component health dashboard (real-time updates)
- [ ] Macro/script support for automation
- [ ] Per-component log streaming
- [ ] Component dependency resolution
- [ ] Hot-reload for extensions

---

## See Also

- [AGENTS.md](../AGENTS.md) — Development philosophy
- [wizard/README.md](../wizard/README.md) — Wizard Server docs
- [extensions/README.md](../extensions/README.md) — Extensions docs
- [core/README.md](../core/README.md) — Core TUI docs

---

**Status**: Production v1.0.1
**Maintained by**: uDOS Engineering
**Last Updated**: 2026-01-28
