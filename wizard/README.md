# Wizard Server (Production)

**Status:** v1.1.0.0 (Stable)
**Port:** 8765
**Scope:** Production-only services (assistant routing, plugin repo, proxy, relays, GitHub monitor/sync, port manager, distribution)

> Experimental work lives in [dev/goblin](../dev/goblin/README.md) (localhost-only, `/api/v0/*`). Wizard stays stable and production-facing.

---

## What Wizard Provides

- Assistant routing gateway (local-first, optional cloud burst per policy)
- Interactive console (foreground alongside server) with status, services, GitHub, poke URL, help/exit
- GitHub monitor + safe sync (webhook + manual `/api/v1/github/*`)
- Port Manager API/CLI integration
- Plugin repository (`/api/v1/plugin/*`) backed by `distribution/plugins`
- Web proxy placeholder (`/api/v1/web/fetch`) with validation stubs
- Gmail relay toggle (Wizard-only), plus space for Notion/iCloud/OAuth/sync handlers
- VS Code bridge + notification history routes
- Cost tracking + rate limiting, device sessions, assistant model listing/completion

---

## Quick Start

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python wizard/server.py               # interactive console + server
# or run without console
python wizard/server.py --no-interactive

# Dev Mode launcher (Wizard included)
./Launch-Dev-Mode.command
```

Logs: see memory/logs (wizard-server-YYYY-MM-DD.log and session-commands-YYYY-MM-DD.log).

---

## API Surface (production `/api/v1/*`)

- Health & status: `/health`, `/api/v1/status`, `/api/v1/rate-limits`
- Assistant gateway: `/api/v1/ai/status`, `/api/v1/ai/models`, `/api/v1/ai/complete`
- Plugin repo: `/api/v1/plugin/list`, `/api/v1/plugin/{id}`, `/api/v1/plugin/{id}/download`
- Web proxy (stub): `/api/v1/web/fetch`
- GitHub: `/api/v1/github/webhook`, `/api/v1/github/sync`
- TUI/console helpers: `/api/v1/devices`, `/api/v1/logs`, `/api/v1/models/switch`, `/api/v1/services/{service}/{action}`
- Port Manager routes: included via `wizard.services.port_manager_service`
- VS Code bridge: included via `wizard.services.vscode_bridge`
- Notification history: `/api/v1/notifications/*`

Auth: all `/api/v1/*` require device auth (Bearer token). Rate limits apply per device.

---

## Components

- `server.py` — FastAPI app, assistant gateway, plugin repo, web proxy stub, Gmail relay flag, GitHub webhook/sync, VS Code bridge, Port Manager, notification history, interactive console runner.
- `services/` — Assistant gateway, rate limiter, cost tracking, GitHub monitor/sync, interactive console, port manager, notification history, vscode bridge, gmail relay hooks.
- `routes/` — Notification history and other route helpers.
- `providers/` — Assistant provider integrations.
- `distribution/` — Plugin packages and manifests (served via plugin routes).
- `config/` — `wizard.json` (committed, versioned) for host/port, rate limits, budgets, service toggles, GitHub sync settings.
- `launch_wizard_dev.py` / `launch_wizard_tui.sh` — Convenience launchers (also wired into VS Code tasks and Dev Mode).

---

## Configuration (wizard/config/wizard.json)

```json
{
  "host": "0.0.0.0",
  "port": 8765,
  "debug": false,
  "requests_per_minute": 60,
  "requests_per_hour": 1000,
  "ai_budget_daily": 10.0,
  "ai_budget_monthly": 100.0,
  "plugin_repo_enabled": true,
  "plugin_auto_update": false,
  "web_proxy_enabled": true,
  "gmail_relay_enabled": false,
  "ai_gateway_enabled": true,
  "github_webhook_secret": null,
  "github_allowed_repo": "fredporter/uDOS-dev",
  "github_default_branch": "main",
  "github_push_enabled": false
}
```

---

## Port Manager (Wizard-owned)

- CLI: `bin/port-manager status|conflicts|kill|available|reassign|env`
- API: exposed via `wizard.services.port_manager_service` under `/api/v1/ports/*`
- Integrated into launchers (Wizard/Goblin/Tauri dev scripts) for pre-flight conflict checks.

---

## GitHub Monitor & Sync

- Webhook endpoint `/api/v1/github/webhook` (workflow_run, check_run, push on allowed repo)
- Self-healing Actions retry + pattern detection (via `wizard.services.github_monitor`)
- Safe sync service (`wizard.services.github_sync`) with pull default; push requires enable flag.

---

## Security

- Device authentication required for all `/api/v1/*` endpoints.
- Rate limits per device; budgets enforced for assistant gateway calls.
- Signature validation for GitHub webhooks when secret is configured.
- Production-only network access; user devices connect via private transports (mesh/QR/audio/Bluetooth-private/NFC).

---

## Wizard-owned integrations (placement)

- Notion webhooks/sync: Wizard-only handlers; bidirectional sync endpoints belong here.
- iCloud/backup relays: Wizard-only relays; never Core/App.
- OAuth/token exchange: All auth flows terminate in Wizard handlers; distribute scoped tokens to devices.
- HubSpot CRM: Moved to Empire server (dev/empire) — it only syncs Empire's contacts.db to HubSpot.

---

## Related Docs

- [wizard/ARCHITECTURE.md](ARCHITECTURE.md)
- [wizard/docs/INTERACTIVE-CONSOLE.md](docs/INTERACTIVE-CONSOLE.md)
- [wizard/docs/PORT-MANAGER.md](docs/PORT-MANAGER.md)
- [docs/decisions/wizard-model-routing-policy.md](../docs/decisions/wizard-model-routing-policy.md)
- [dev/goblin/README.md](../dev/goblin/README.md) (experimental server)

---

_Updated: 2026-01-18_
