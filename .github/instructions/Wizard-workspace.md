## Wizard Workspace Quick Guide

**Focus:** `/wizard/`, `/docs/` — server/API dev, always-on services

### Essentials
- Run server: `source .venv/bin/activate && python -m wizard.server`
- Local-first model routing; cloud per policy
- Gmail relay is Wizard-only; log cloud with `[CLOUD]`
- No Core logic duplication; keep offline assumptions intact

### Key Endpoints (`/api/v1/*`)
- `/health`, `/status`, `/ai/models`, `/ai/complete`, `/plugin/*`, `/github/*`

### References
- [AGENTS.md](../../AGENTS.md)
- [docs/decisions/wizard-model-routing-policy.md](../../docs/decisions/wizard-model-routing-policy.md)
- [wizard/README.md](../../wizard/README.md)

## Model Routing Policy

**Default:** Local-first (Ollama + Devstral Small 2)

1. Try local Ollama first
2. Escalate to cloud only if:
   - Task tagged `burst`
   - Local fails twice
   - Policy classification requires it
3. **Never escalate** if:
   - Task tagged `private`
   - Secrets detected
   - Budget exhausted

---

## Configuration

**File:** `wizard/config/wizard.json` (committed)

```json
{
  "host": "0.0.0.0",
  "port": 8765,
  "ai_budget_daily": 10.0,
  "ai_budget_monthly": 100.0,
  "plugin_repo_enabled": true,
  "github_webhook_secret": null
}
```

**Secrets:** `wizard/config/ai_keys.json` (gitignored)

---

## Logging Requirements

**Tags:**

- `[WIZ]` — Wizard operation
- `[GMAIL]` — Gmail relay
- `[CLOUD]` — Cloud API call
- `[LOCAL]` — Local Wizard operation

**Cloud Escalation:** Always log with reason and cost estimate

---

## Version Management

Current: Wizard v1.1.0.0

```bash
python -m core.version bump wizard patch
```

---

## Key Files

- `wizard/server.py` — Main FastAPI server
- `wizard/config/` — Configuration (secrets gitignored)
- `wizard/services/` — Server services
- `wizard/providers/` — AI provider integrations
- `wizard/routes/` — API routes
- `wizard/version.json` — Version metadata

---

## References

- [AGENTS.md](../AGENTS.md) — Core principles
- [wizard/README.md](../../wizard/README.md) — Server overview
- [wizard.instructions.md](../.github/instructions/wizard.instructions.md) — Detailed spec

---

_Workspace optimized for: Wizard Server + API development | Minimal context for fast Copilot rounds_
