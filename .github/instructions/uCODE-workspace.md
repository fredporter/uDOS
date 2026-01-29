# uCODE Workspace Instructions

> **Focus:** `/core/` + `/docs/` — TUI Runtime Development
> **Scope:** Command handlers, services, uPY interpreter, offline-first design

---

## Quick Start

```bash
# Launch uCODE interactive TUI
./bin/start_udos.sh

# Or via VS Code task: "Run uDOS Interactive"
```

---

## Core Architecture

### Command Handler Pattern

```python
from core.commands.base_handler import BaseCommandHandler

class MyHandler(BaseCommandHandler):
    def handle(self, command, params, grid, parser):
        if command == "MY_CMD":
            return self._handle_my_cmd(params)
```

**NEVER** create standalone handlers. Always extend parent handlers.

### Key Handlers

- `ShakedownHandler` — System validation (47 tests)
- `RepairHandler` — Self-healing, git sync
- `FileHandler` — File operations
- `MaintenanceHandler` — TIDY/CLEAN workspace

### Services Layer

Shared logic lives in `core/services/`:

```python
from core.services.logging_manager import get_logger

logger = get_logger('feature-name')
logger.info('[LOCAL] Operation started')
```

---

## Version Management

**NEVER hardcode versions.** Use:

```bash
python -m core.version check
python -m core.version bump core build
```

Current: Core v1.0.7.1

---

## Logging Requirements

**Tags:**

- `[LOCAL]` — Local device
- `[MESH]` — MeshCore P2P
- `[BT-PRIV]` — Bluetooth Private
- `[NFC]`, `[QR]`, `[AUD]` — Other transports

**Primary Log:** `memory/logs/session-commands-YYYY-MM-DD.log`

---

## Testing

```bash
# Shakedown (47 tests)
./start_udos.sh
# Type: SHAKEDOWN

# Unit tests
pytest core/tests/ -v
```

---

## Key Files

- `core/version.json` — Version metadata
- `core/version.py` — Version manager
- `core/commands/` — 92+ command handlers
- `core/services/` — 140+ shared services
- `docs/` — Engineering reference

---

## References

- [AGENTS.md](../AGENTS.md) — Core principles
- [docs/README.md](../docs/README.md) — Engineering index
- [core.instructions.md](../.github/instructions/core.instructions.md) — Detailed spec

---

_Workspace optimized for: Core TUI + offline-first design | Minimal context for fast Copilot rounds_
