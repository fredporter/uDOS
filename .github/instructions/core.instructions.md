# Core Instructions

**Scope:** `core/**` — Offline TUI runtime, Alpine Linux primary

## Critical Rules

1. **Extend parent handlers** — NEVER standalone handlers
2. **Use services** — Shared logic in `core/services/`
3. **Canonical logger** — `from core.services.logging_manager import get_logger`
4. **No cloud** — Core is offline-first (no web/email/scraping)
5. **Version management** — `python -m core.version` (never hardcode)
6. **Required log tags** — `[LOCAL]`, `[MESH]`, `[BT-PRIV]`, `[NFC]`, `[QR]`, `[AUD]`

## Key Files

- Primary log: `memory/logs/session-commands-YYYY-MM-DD.log`
- Handlers: `core/commands/` (extend BaseCommandHandler)
- Services: `core/services/` (logging_manager, file_service, database_manager)
- Tests: `core/tests/`

## References

- [AGENTS.md](../../AGENTS.md) — Project spine
- [core/README.md](../../core/README.md) — Core docs
