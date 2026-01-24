# Core Subsystem Instructions

> **Scope:** `applyTo: ["core/**"]`

---

## Core Architecture

**Core** is the offline-first TUI runtime for uDOS. No GUI assumptions.

### Responsibilities

- Command parsing and routing
- Handler architecture (92+ commands)
- Services layer (140+ services)
- uPY interpreter (restricted Python)
- Alpine Linux primary targeting (musl, BusyBox)

### Non-Responsibilities

- ❌ Cloud connectivity
- ❌ Long-running servers (use Wizard)
- ❌ Web scraping or email (use Wizard)
- ❌ GUI rendering (use App)

---

## Command Handler Pattern

**ALWAYS** extend existing parent handlers. **NEVER** create standalone handlers.

```python
from core.commands.base_handler import BaseCommandHandler

class FileHandler(BaseCommandHandler):
    """Handles FILE, NEW, DELETE, etc."""

    def handle(self, command, params, grid, parser):
        if command == "NEW":
            return self._handle_new(params)
        elif command == "DELETE":
            return self._handle_delete(params)
        # ...

    def _handle_new(self, params):
        """Implementation for NEW command"""
        # Business logic here
        pass
```

### Key Handlers

- `ShakedownHandler` — System validation (47 tests)
- `RepairHandler` — Self-healing, git sync
- `FileHandler` — File operations
- `MaintenanceHandler` — TIDY/CLEAN workspace
- `BackupHandler` — Backup operations
- `WellbeingHandler` — User wellness features

---

## Services Layer

Shared logic lives in `core/services/`:

- `logging_manager.py` — **Canonical logger**
- `file_service.py` — File operations
- `database_manager.py` — SQLite interface
- `udos_md_parser.py` — Markdown parsing
- `path_validator.py` — Path safety checks

### Example Usage

```python
from core.services.logging_manager import get_logger

logger = get_logger('my-feature')
logger.info('[LOCAL] Operation started')
```

---

## Logging Requirements

### Required Tags

- `[LOCAL]` — Local device operation
- `[MESH]` — MeshCore P2P
- `[BT-PRIV]` — Bluetooth Private
- `[NFC]` — NFC contact
- `[QR]` — QR relay
- `[AUD]` — Audio transport

### Primary Log

`memory/logs/session-commands-YYYY-MM-DD.log` — **Check this first** for TUI errors

---

## Version Management

**NEVER hardcode versions.** Always use:

```bash
python -m core.version check
python -m core.version show
python -m core.version bump core build
```

Current: Core v1.1.0.0

---

## Alpine Linux Targeting

- No systemd assumptions (OpenRC on Alpine)
- Prefer musl-compatible dependencies; Pure Python preferred
- Use BusyBox-compatible shell tools
- Package and distribution via `apk` where applicable
- Test on actual Alpine Linux images where possible

---

## Testing

```bash
# Shakedown (47 tests)
./start_udos.sh
# Type: SHAKEDOWN

# Unit tests
pytest core/tests/ -v

# Integration tests
pytest memory/tests/ -v
```

---

## File Structure

```
core/
├── commands/           # Command handlers (92+)
├── services/          # Shared business logic (140+)
├── interpreters/      # uPY interpreter
├── ui/                # TUI components
├── config/            # Configuration
├── constants/         # Constants
├── docs/              # Core-specific docs
└── version.json       # Version metadata
```

---

## References

- [AGENTS.md](../../AGENTS.md)
- [docs/_index.md](../../docs/_index.md)
- [core/README.md](../../core/README.md)
- [core/docs/](../../core/docs/)

---

*Last Updated: 2026-01-13*
