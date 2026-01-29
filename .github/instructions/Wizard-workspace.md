# Wizard Workspace Instructions

> **Focus:** `/wizard/` + `/docs/` — Server & API Development
> **Scope:** Always-on services, AI routing, APIs, cloud integration

---

## Quick Start

```bash
# Start Wizard Server (Port 8765)
source .venv/bin/activate
python -m wizard.server

# Or via VS Code task: "Wizard: Start Server"
```

---

## Wizard Architecture

### Responsibilities

- AI model routing (Ollama local-first, OpenRouter cloud-optional)
- Webhooks and APIs
- Email relay (Gmail) — Wizard ONLY
- Packaging, distribution, sync
- Dev tooling and Agent gateways

### Non-Responsibilities

- ❌ Core runtime logic (use Core)
- ❌ Breaking offline assumptions (Core must work standalone)
- ❌ Exposing child devices to web

---

## API Surface (Production `/api/v1/*`)

| Endpoint              | Purpose               |
| --------------------- | --------------------- |
| `/health`             | Health check          |
| `/api/v1/status`      | Server status         |
| `/api/v1/ai/models`   | List available models |
| `/api/v1/ai/complete` | Model completion      |
| `/api/v1/plugin/*`    | Plugin repository     |
| `/api/v1/github/*`    | GitHub webhook/sync   |

---

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
