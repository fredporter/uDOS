# Wizard Architecture (Production)

**Model:** Single production server on 8765 (stable). Experimental work lives in `dev/goblin` on 8767. Wizard stays production-only.

---

## 🏗️ Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        WIZARD SERVER (8765)                  │
│                     Status: STABLE v1.1.0.0                  │
│                                                              │
│  Assistant Gateway  | Plugin Repo  | Web Proxy (stub)        │
│  Gmail Relay (opt)  | GitHub Monitor/Sync | Port Manager     │
│  Rate Limits        | Cost Tracking | VS Code Bridge         │
│  Notification History | Interactive Console (foreground)     │
└──────────────────────────────────────────────────────────────┘
          │
          │ Private transports only (mesh/BT-private/NFC/QR/AUD)
          │
┌──────────────────────────────────────────────────────────────┐
│                        USER DEVICES                          │
│             (no direct internet; go through Wizard)          │
└──────────────────────────────────────────────────────────────┘
```

Goblin (dev server) is separate: localhost:8767, `/api/v0/*`, experimental only.

---

## 📂 Directory Structure

```
wizard/
├── server.py                  # Production server + interactive console runner
├── config/
│   └── wizard.json            # Production config (committed)
├── services/
│   ├── ai_gateway.py          # Assistant routing (local-first)
│   ├── dev_mode_service.py    # Dev mode management (Goblin activation/coordination)
│   ├── github_integration.py  # GitHub CLI ops, issue/PR management
│   ├── github_monitor.py      # Actions self-healing
│   ├── github_sync.py         # Safe repo sync (pull/push flag)
│   ├── interactive_console.py # Foreground console
│   ├── port_manager.py        # Port registry + conflict detection
│   ├── port_manager_service.py# Port Manager API routes
│   ├── rate_limiter.py        # Per-device rate limits
│   ├── cost_tracker.py        # Budget tracking
│   ├── notification_history_service.py
│   ├── vscode_bridge.py       # VS Code extension bridge
│   ├── mistral_vibe.py        # Vibe CLI context/log analysis
│   ├── block_mapper.py        # Markdown mapping helpers
│   ├── (core) binder/compiler.py # Binder compilation (md/json/pdf/brief)
│   ├── sync_executor.py       # Sync queue processing to local mirrors
│   ├── sync_executor.py       # Sync queue processing to local mirrors
│   ├── task_scheduler.py      # Organic cron scheduling
│   ├── workflow_manager.py    # Local project/task management
│   └── gmail_relay.py (hooks) # Wizard-only relay
├── routes/
│   ├── ai_routes.py           # /api/ai/* routes
│   ├── binder_routes.py       # /api/binder/* routes
│   ├── dev_routes.py          # /api/dev/* routes (Dev Mode control)
│   ├── github_routes.py       # /api/github/* routes
│   └── notification_history_routes.py
├── providers/                 # Assistant provider integrations
├── distribution/              # Plugin packages (served via /api/plugin/*)
├── docs/                      # INTERACTIVE-CONSOLE.md, PORT-MANAGER.md
├── extensions/                # Wizard-only feature packs
├── tools/                     # Utilities (e.g., port-manager CLI wrapper)
├── tests/
└── version.json
```

---

-## 🎯 Responsibilities (Production)

- Assistant routing gateway (local-first, policy-controlled cloud burst)
- Dev Mode management (activate/deactivate Goblin dev server via `/api/dev/*`)
- Plugin repository distribution (from `distribution/plugins`)
- Web proxy (stubbed, validated; disabled if toggled off)
- Gmail relay (Wizard-only)
- GitHub integration (CLI ops, issue/PR management, sync, devlog/roadmap context)
- Port Manager API + CLI
- Device sessions, rate limiting, cost tracking
- Interactive console (foreground alongside server)
- VS Code bridge + notification history endpoints
- Binder compilation (multi-format output)
- Sync queue processing for local mirrors
- Task scheduling (organic cron under Wizard memory)
- Workflow management (local projects/tasks)
 - Workflow management (local projects/tasks)

Not in Wizard: TUI command handlers, core business logic, runtime execution (lives in Core/Goblin/App as appropriate).

## 📜 MD → HTML + Theme Pack Pipeline

- Wizard owns the renderer service that turns Markdown provenance (`vault/`) into static HTML snapshots under `_site/<theme>` by following the Theme Pack contract (`../docs/Theme-Pack-Contract.md`) and the universal component guidance (`../docs/Universal-Components-Contract.md`).
- The renderer service must treat exported slots/data as simple objects (HTML strings + metadata) so it can satisfy both Wizard’s static portal (`wizard/portal-static/`) and any SvelteKit preview components. Refer to `wizard/docs/renderer-ui-standards.md` for the implementation boundary.
- Theme metadata feeds the portal UI, mission reports, and export status endpoints so every lane (portal, CLI, Vibe) agrees on typography tokens (`../docs/CSS-Tokens.md`) and slot names.

## 🎨 Svelte UI Modules

- The Wizard portal UI and admin console are built as composable Svelte modules (see `web-admin/` for the control plane and the `wizard/web/` bundle for portal-specific widgets). Both should consume the shared slots, theme metadata, and missions schema from the TS core so the static publishing lane doesn’t diverge from the interactive admin lane.
- Svelte modules live under `wizard/web/modules/` (create as needed) and export isolated components such as `ThemePicker`, `MissionQueue`, `ContributionReview`, and `PortalPreview`. These modules can be imported by both the portal static SPA and the SvelteKit admin UI (`web-admin/`) because they only rely on universal HTML/data contracts.
- Any new UI module must document its surface contract in `wizard/docs/renderer-ui-standards.md` so that both the MD→HTML pipeline and the interactive Svelte surfaces stay aligned without requiring a framework change.

---

## 🎮 Dev Mode

**Activated via:** `DEV MODE activate` (in Core TUI)
**Controlled by:** `/api/dev/*` routes
**Backend:** Wizard starts/stops Goblin dev server (localhost:8767)

Dev Mode includes:

- Goblin dev server with experimental features
- Task scheduling, runtime executor
- Real-time WebSocket updates
- Full Wizard API access with dev features

Dev Mode is activated on-demand; Goblin runs independently on port 8767.

---

## Endpoints (Production `/api/*`)

- `/health` (no auth), `/api/status`, `/api/rate-limits`
- Assistant: `/api/ai/status`, `/api/ai/models`, `/api/ai/complete`, `/api/ai/query`, `/api/ai/context`, `/api/ai/analyze-logs`, `/api/ai/suggest`, `/api/ai/explain`
- Plugins: `/api/plugin/list`, `/api/plugin/{id}`, `/api/plugin/{id}/download`
- Proxy: `/api/web/fetch` (stub, gated by config)
- GitHub: `/api/github/health`, `/api/github/sync-cli`, `/api/github/issues`, `/api/github/pulls`, `/api/github/context/*` (devlog, roadmap, agents, copilot), `/api/github/logs/{log_type}`
- Dev Mode: `/api/dev/health`, `/api/dev/status`, `/api/dev/activate`, `/api/dev/deactivate`, `/api/dev/restart`, `/api/dev/logs`
- Binder: `/api/binder/compile`, `/api/binder/chapters`, `/api/binder/export`
- Console/TUI helpers: `/api/devices`, `/api/logs`, `/api/models/switch`, `/api/services/{service}/{action}`
- Port Manager: `/api/ports/*` (via router include)
- Notification history: `/api/notifications/*`
- VS Code bridge routes (included router)

Authentication: Bearer token required for `/api/*`; rate limits per device. GitHub webhook uses signature if configured.

---

## Ports

| Service             | Port | Access         |
| ------------------- | ---- | -------------- |
| Wizard (production) | 8765 | LAN/Internet   |
| Goblin (dev server) | 8767 | Localhost      |
| Port Manager API    | 8765 | (under Wizard) |

See also: [extensions/PORT-REGISTRY.md](../extensions/PORT-REGISTRY.md)

---

## Security

- Device auth for all production endpoints; rate limits and budgets enforced.
- GitHub webhook signature validation when secret set.
- Production only; experimental endpoints belong in Goblin, not Wizard.
- Private transports only for device↔Wizard payloads; never send data over public Bluetooth beacons.

---

## Configuration

- `wizard/config/wizard.json` (committed, versioned) — host/port, rate limits, budgets, service toggles, GitHub sync settings.
- No dev config here; dev/local experiments happen in `dev/goblin`.

---

## Run

```bash
cd ~/uDOS
source venv/bin/activate
python -m wizard.server           # server + interactive console
python -m wizard.server --daemon  # daemon mode (no console)
```

To activate Dev Mode:

```bash
# Via TUI
./bin/start_udos.sh
> DEV MODE activate

# Via REST API
curl -X POST http://localhost:8765/api/dev/activate
```

---

_Updated: 2026-01-22_
