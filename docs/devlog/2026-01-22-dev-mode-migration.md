# Dev Mode Migration Summary

**Date:** 2026-01-22  
**Status:** Complete  
**Scope:** Migrate dedicated dev mode scripts to Wizard Server feature

---

## Changes Overview

### 1. New Wizard Services & Routes

**Dev Mode Service** (`wizard/services/dev_mode_service.py`)

- Manages dev mode activation/deactivation
- Starts/stops Goblin dev server (port 8767)
- Tracks service status and uptime
- Provides health checks and logging

**Dev Mode Routes** (`wizard/routes/dev_routes.py`)

- `/api/v1/dev/health` — Health check
- `/api/v1/dev/status` — Get dev mode status
- `/api/v1/dev/activate` — Start dev mode
- `/api/v1/dev/deactivate` — Stop dev mode
- `/api/v1/dev/restart` — Restart dev mode
- `/api/v1/dev/logs` — Fetch dev logs

### 2. Core Command Handler

**Dev Mode Handler** (`core/commands/dev_mode_handler.py`)

- Routes `DEV MODE` command to Wizard API
- Supports: `activate`, `deactivate`, `status`, `restart`, `logs`, `health`
- Handles API connectivity errors gracefully
- Logs all operations

**Registered in:**

- `core/commands/__init__.py` (exported)
- `core/tui/dispatcher.py` (mapped to "DEV MODE" command)

### 3. Wizard Server Integration

**Modified:** `wizard/server.py`

- Mounted `dev_routes` with auth guard
- Routes registered before dashboard static files
- Uses standard rate limiting and monitoring

### 4. Cleanup (Archived)

Moved to `.archive/` (original files preserved):

- `bin/Launch-Dev-Mode.command` → `.archive/bin/`
- `wizard/launch_wizard_dev.py` → `.archive/wizard/`
- `bin/Launch-Wizard-Dev.command` → `.archive/bin/`

### 5. Documentation Updates

**INSTALLATION.md**

- Removed `python wizard/launch_wizard_dev.py`
- Added "Dev Mode (via Wizard Server)" section
- Documented REST API activation: `curl -X POST http://localhost:8765/api/v1/dev/activate`

**wizard/ARCHITECTURE.md**

- Added `dev_mode_service.py` to directory structure
- Added other migrated services (block_mapper, binder_compiler, notion_sync, etc.)
- Updated endpoints section with `/api/v1/dev/*` routes
- Added "Dev Mode" subsection explaining activation and coordination
- Updated "Run" section to use `python -m wizard.server`

**.github/copilot-instructions.md**

- Removed `bin/Launch-Dev-Mode.command` reference
- Updated to show TUI-based dev mode activation
- Documented REST API alternative

---

## Usage

### Via TUI (Core)

```bash
# Start Wizard Server
python -m wizard.server &

# Then in uDOS TUI
./bin/start_udos.sh
> DEV MODE activate
> DEV MODE status
> DEV MODE deactivate
> DEV MODE logs 100
```

### Via REST API

```bash
# Activate
curl -X POST http://localhost:8765/api/v1/dev/activate

# Check status
curl http://localhost:8765/api/v1/dev/status

# Get health
curl http://localhost:8765/api/v1/dev/health

# View logs (last 50 lines)
curl "http://localhost:8765/api/v1/dev/logs?lines=50"

# Deactivate
curl -X POST http://localhost:8765/api/v1/dev/deactivate
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│            Wizard Server (Port 8765)            │
├─────────────────────────────────────────────────┤
│  /api/v1/dev/* routes                           │
│  ├─ /activate        → DevModeService.activate()│
│  ├─ /deactivate      → DevModeService.deactivate()
│  ├─ /status          → DevModeService.get_status()
│  ├─ /health          → DevModeService.get_health()
│  └─ /logs            → DevModeService.get_logs() │
└─────────────────────────────────────────────────┘
              ↕ (subprocess.Popen)
┌─────────────────────────────────────────────────┐
│      Goblin Dev Server (Port 8767)              │
│   (started via python dev/goblin/goblin_server.py)
│   • Notion sync                                  │
│   • Task scheduling                              │
│   • Runtime executor                             │
│   • Experimental features                        │
└─────────────────────────────────────────────────┘
```

**Core TUI ↔ Wizard REST API:**

```
./bin/start_udos.sh
> DEV MODE activate
  ↓
  Wizard.DevModeService.activate()
  ↓
  subprocess.Popen(["python", "dev/goblin/goblin_server.py"])
```

---

## Key Points

✅ **Dev mode is now a Wizard feature**

- Centralized control and monitoring
- No dedicated launcher scripts needed
- Available via REST API for remote control

✅ **Backwards compatible**

- Old scripts archived, not deleted
- Can restore if needed from `.archive/`

✅ **Clean separation of concerns**

- Core handles user input (DEV MODE command)
- Wizard manages infrastructure (start/stop Goblin)
- Goblin remains experimental sandbox

✅ **Consistent with architecture**

- Follows Wizard-only services pattern
- Respects offline-first design
- Uses standard rate limiting and auth

---

## Files Changed

| File                                  | Change                        |
| ------------------------------------- | ----------------------------- |
| `wizard/services/dev_mode_service.py` | New                           |
| `wizard/routes/dev_routes.py`         | New                           |
| `core/commands/dev_mode_handler.py`   | New                           |
| `core/commands/__init__.py`           | Export DevModeHandler         |
| `core/tui/dispatcher.py`              | Register "DEV MODE" command   |
| `wizard/server.py`                    | Mount dev_routes              |
| `INSTALLATION.md`                     | Updated examples              |
| `wizard/ARCHITECTURE.md`              | Updated structure/endpoints   |
| `.github/copilot-instructions.md`     | Updated commands              |
| `.archive/bin/`                       | Archived 2 .command files     |
| `.archive/wizard/`                    | Archived launch_wizard_dev.py |

---

_Migration complete. Dev mode is now fully integrated into Wizard Server._
