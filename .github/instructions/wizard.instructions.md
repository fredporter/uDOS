wizard/
## Wizard Instructions

**Scope:** `wizard/**` — Always-on services (AI routing, APIs, cloud integration)

## Critical Rules

1. Wizard only; do not duplicate Core logic
2. Local-first (Ollama); cloud only per policy
3. Log cloud escalations with `[CLOUD]`, record model + reason + cost
4. Gmail relay is Wizard-only
5. Version via `python -m core.version bump wizard ...` (never hardcode)

## Key Paths

- Server: `wizard/server.py`
- Services: `wizard/services/`
- Providers: `wizard/providers/`
- Version: `wizard/version.json`

## Quick Commands

- Run: `python wizard/server.py`
- Tests: `pytest wizard/tests/ -v`

## References

- [AGENTS.md](../../AGENTS.md)
- [docs/decisions/wizard-model-routing-policy.md](../../docs/decisions/wizard-model-routing-policy.md)
- [wizard/README.md](../../wizard/README.md)
