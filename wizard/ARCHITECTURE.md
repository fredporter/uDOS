# Wizard Architecture

**Model:** Single Wizard service on 8765 with an optional Dev extension lane rooted at `/dev`.

---

## 🏗️ Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        WIZARD SERVER (8765)                  │
│                     Status: Active v1.5 lane                 │
│                                                              │
│  Assistant Gateway  | Plugin Repo  | Web Proxy (optional)    │
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

The historical Goblin server is not part of the active v1.5 architecture contract.

---

## 📂 Directory Structure

```
wizard/
├── server.py                  # Production server + interactive console runner
├── config/
│   └── wizard.json            # Production config (committed)
├── services/
│   ├── ai_gateway.py          # Assistant routing (local-first)
│   ├── dev_mode_service.py    # Dev extension lane activation/status/runtime checks
│   ├── dev_extension_service.py # /dev framework policy + GitHub contributor sync
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
│   ├── sync_executor.py       # Sync queue processing to local mirrors
│   ├── task_scheduler.py      # Organic cron scheduling
│   ├── workflow_manager.py    # Local project/task management
│   └── gmail_relay.py (hooks) # Wizard-only relay
├── routes/
│   ├── ai_routes.py           # /api/ai/* routes
│   ├── binder_routes.py       # /api/binder/* routes
│   ├── config_routes.py       # Core /api/config/* routes
│   ├── config_admin_routes.py # /api/admin-token/* + public export routes
│   ├── config_ssh_routes.py   # /api/config/ssh/* routes
│   ├── dev_routes.py          # /api/dev/* routes (Dev Mode control)
│   ├── github_routes.py       # /api/github/* routes
│   ├── provider_routes.py     # /api/provider/* routes
│   └── notification_history_routes.py
├── mcp/                       # MCP server gateway (AI ↔ Wizard bridge)
│   ├── gateway.py
│   ├── mcp_server.py
│   └── server.py
├── providers/                 # Assistant provider integrations
├── docs/                      # INTERACTIVE-CONSOLE.md, PORT-MANAGER.md, api/
│   └── api/                   # API specification docs (consolidated from api/wizard/)
├── web/
│   ├── portal/                # Off-web portal (consolidated from web-portal/)
│   └── modules/               # Composable Svelte UI modules
├── extensions/                # Wizard-only feature packs
├── tools/                     # Utilities (e.g., port-manager CLI wrapper)
├── tests/
└── version.json
```

> **Note:** Plugin distribution packages are now served from the repo-level `distribution/` directory (consolidated from `wizard/distribution/`).
> Vault contract:
> - `vault/` = distributable markdown scaffold (tracked)
> - `core/framework/seed/vault/` = canonical starter seed source (tracked)
> - `memory/vault/` = runtime user vault (local, gitignored)
>
> Dev extension contract:
> - `dev/` = versioned Dev extension framework/template root
> - `dev/files`, `dev/relecs`, `dev/dev-work`, `dev/testing` = local-only contributor work areas
> - Wizard owns install/uninstall/enable/disable lifecycle and keeps local mutable state separate from the tracked `dev/` scaffold

---

## 🎯 Responsibilities (Production)

- Assistant routing gateway (local-first, policy-controlled cloud burst)
- Dev extension management (status, enable, disable, restart, logs via `/api/dev/*`)
- Plugin repository distribution (from repo-level `distribution/`)
- Web proxy (optional; disabled when toggled off)
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
- MCP server gateway (Dev extension Vibe ↔ Wizard tool bridge)

Not in Wizard: TUI command handlers, core business logic, or the standard operator runtime path (those stay in Core).

## 📜 MD → HTML + Theme Pack Pipeline

- Wizard owns the renderer service that turns Markdown provenance (`memory/vault/`) into static HTML snapshots under `memory/vault/_site/<theme>` by following the Theme Pack contract (`../docs/Theme-Pack-Contract.md`) and the universal component guidance (`../docs/Universal-Components-Contract.md`).
- The renderer service must treat exported slots/data as simple objects (HTML strings + metadata) so it can satisfy both Wizard’s static portal (`wizard/portal-static/`) and any SvelteKit preview components. Refer to `wizard/docs/renderer-ui-standards.md` for the implementation boundary.
- Theme metadata feeds the portal UI, mission reports, and export status endpoints so every lane (portal, CLI, Dev extension tooling) agrees on typography tokens (`../docs/CSS-Tokens.md`) and slot names.

## 🎨 Svelte UI Modules

- The Wizard portal UI and admin console are built as composable Svelte modules (see `web-admin/` for the control plane and `wizard/web/modules/` for portal-specific widgets). Both should consume the shared slots, theme metadata, and missions schema from the TS core so the static publishing lane doesn’t diverge from the interactive admin lane.
- Svelte modules live under `wizard/web/modules/` (create as needed) and export isolated components such as `ThemePicker`, `MissionQueue`, `ContributionReview`, and `PortalPreview`. These modules can be imported by both the portal static SPA and the SvelteKit admin UI (`web-admin/`) because they only rely on universal HTML/data contracts.
- Any new UI module must document its surface contract in `wizard/docs/renderer-ui-standards.md` so that both the MD→HTML pipeline and the interactive Svelte surfaces stay aligned without requiring a framework change.

---

## 🎮 Dev Extension Lane

**Entry model:** implicit contributor lane behind the active `dev` profile and installed `/dev/` extension
**Controlled by:** Wizard GUI plus `/api/dev/*` routes
**Framework root:** `/dev`

Dev extension responsibilities include:

- contributor status, health, restart, clear, and log surfaces
- gated Vibe/MCP contributor tooling
- local scripts/tests/workflows rooted under `/dev/`
- GitHub contributor sync and release-profile-aware checks

The Dev extension lane is not a second default runtime and must not be described as an explicit normal-user mode switch.

---

## Endpoints (Production `/api/*`)

- `/health` (no auth), `/api/status`, `/api/rate-limits`
- Assistant: `/api/ai/status`, `/api/ai/models`, `/api/ai/complete`, `/api/ai/query`, `/api/ai/context`, `/api/ai/analyze-logs`, `/api/ai/suggest`, `/api/ai/explain`
- Plugins: `/api/plugin/list`, `/api/plugin/{id}`, `/api/plugin/{id}/download`
- Proxy: `/api/web/fetch` (optional, gated by config)
- GitHub: `/api/github/health`, `/api/github/sync-cli`, `/api/github/issues`, `/api/github/pulls`, `/api/github/context/*` (devlog, roadmap, agents, copilot), `/api/github/logs/{log_type}`
- Dev extension: `/api/dev/health`, `/api/dev/status`, `/api/dev/activate`, `/api/dev/deactivate`, `/api/dev/restart`, `/api/dev/logs`
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
| Port Manager API    | 8765 | (under Wizard) |

See also: [extensions/PORT-REGISTRY.md](../extensions/PORT-REGISTRY.md)

---

## Security

- Device auth for all production endpoints; rate limits and budgets enforced.
- GitHub webhook signature validation when secret set.
- Dev extension features must remain permissioned behind profile, extension, and admin/dev checks.
- Private transports only for device↔Wizard payloads; never send data over public Bluetooth beacons.

---

## Configuration

- `wizard/config/wizard.json` (committed, versioned) — host/port, rate limits, budgets, service toggles, GitHub sync settings.
- Dev extension framework policy and contributor work templates live under `/dev`.

---

## Run

```bash
cd ~/uDOS
UV_PROJECT_ENVIRONMENT=.venv uv run python -m wizard.server           # server + interactive console
UV_PROJECT_ENVIRONMENT=.venv uv run python -m wizard.server --daemon  # daemon mode (no console)
```

To use the Dev extension lane:

```bash
# Enable the dev profile and install/activate the /dev extension through Wizard GUI,
# then use the /api/dev/* routes or the Dev Mode screen for contributor controls.
curl -X POST http://localhost:8765/api/dev/activate
```

---

_Updated: 2026-03-03 — v1.5 Dev extension lane alignment_
