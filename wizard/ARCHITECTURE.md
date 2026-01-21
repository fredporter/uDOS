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
├── launch_wizard_dev.py       # Launcher (with/without console)
├── launch_wizard_tui.sh       # Shell wrapper
├── config/
│   └── wizard.json            # Production config (committed)
├── services/
│   ├── ai_gateway.py          # Assistant routing (local-first)
│   ├── github_monitor.py      # Actions self-healing
│   ├── github_sync.py         # Safe repo sync (pull/push flag)
│   ├── interactive_console.py # Foreground console
│   ├── port_manager.py        # Port registry + conflict detection
│   ├── port_manager_service.py# Port Manager API routes
│   ├── rate_limiter.py        # Per-device rate limits
│   ├── cost_tracker.py        # Budget tracking
│   ├── notification_history_service.py
│   ├── vscode_bridge.py       # VS Code extension bridge
│   └── gmail_relay.py (hooks) # Wizard-only relay
├── routes/
│   └── notification_history_routes.py
├── providers/                 # Assistant provider integrations
├── distribution/              # Plugin packages (served via /api/v1/plugin/*)
├── docs/                      # INTERACTIVE-CONSOLE.md, PORT-MANAGER.md
├── extensions/                # Wizard-only feature packs
├── tools/                     # Utilities (e.g., port-manager CLI wrapper)
├── tests/
└── version.json
```

---

## 🎯 Responsibilities (Production)

- Assistant routing gateway (local-first, policy-controlled cloud burst)
- Plugin repository distribution (from `distribution/plugins`)
- Web proxy (stubbed, validated; disabled if toggled off)
- Gmail relay (Wizard-only)
- GitHub monitor + webhook (`/api/v1/github/webhook`) and manual sync (`/api/v1/github/sync`)
- Port Manager API + CLI
- Device sessions, rate limiting, cost tracking
- Interactive console (foreground alongside server)
- VS Code bridge + notification history endpoints

Not in Wizard: TUI command handlers, core business logic, runtime execution (lives in Core/Goblin/App as appropriate).

---

## Endpoints (Production `/api/v1/*`)

- `/health` (no auth), `/api/v1/status`, `/api/v1/rate-limits`
- Assistant: `/api/v1/ai/status`, `/api/v1/ai/models`, `/api/v1/ai/complete`
- Plugins: `/api/v1/plugin/list`, `/api/v1/plugin/{id}`, `/api/v1/plugin/{id}/download`
- Proxy: `/api/v1/web/fetch` (stub, gated by config)
- GitHub: `/api/v1/github/webhook`, `/api/v1/github/sync`
- Console/TUI helpers: `/api/v1/devices`, `/api/v1/logs`, `/api/v1/models/switch`, `/api/v1/services/{service}/{action}`
- Port Manager: `/api/v1/ports/*` (via router include)
- Notification history: `/api/v1/notifications/*`
- VS Code bridge routes (included router)

Authentication: Bearer token required for `/api/v1/*`; rate limits per device. GitHub webhook uses signature if configured.

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
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python wizard/server.py           # server + interactive console
python wizard/server.py --no-interactive  # daemon mode

# With Dev Mode bundle
./Launch-Dev-Mode.command
```

---

_Updated: 2026-01-18_
