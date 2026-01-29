## uCODE Workspace Quick Guide

**Focus:** `/core/`, `/docs/` — TUI runtime

### Essentials
- Launch TUI: `./bin/start_udos.sh`
- Extend `BaseCommandHandler`; no standalone handlers
- Use `core/services/` and the canonical logger
- Offline-first; no cloud calls from Core

### References
- [AGENTS.md](../../AGENTS.md)
- [core/README.md](../../core/README.md)
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
