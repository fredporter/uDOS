# 🧙 Wizard Dashboard - Feature Documentation

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2026-01-18

---

## Overview

The Wizard Dashboard is the central control center for the uDOS Wizard Server. It provides:

- **Feature Index** — All available pages and services
- **API Status** — Real-time status of configured APIs
- **Quick Links** — Fast access to common tasks
- **Management Tools** — Configuration, monitoring, and editing

The dashboard is automatically discovered by the TUI on startup via the `/api/v1/index` endpoint.

---

## Access Points

### Browser

```
http://127.0.0.1:8765/
```

### JSON API (for TUI/Clients)

```
GET http://127.0.0.1:8765/api/v1/index
```

### TUI Integration

The TUI will automatically check for Wizard Server on startup:

```
✓ Wizard Server running (6/8 APIs configured)
  → Visit: http://127.0.0.1:8765/
```

---

## Feature Pages

### ⚙️ Configuration

**Status:** Active
**URL:** `/api/v1/config/dashboard`
**Category:** Settings

Manage all uDOS configuration files:

- `wizard.json` — Feature flags and settings
- `.env` — API keys and secrets
- `.env-local` — Machine-specific overrides

**Features:**

- Real-time config editing
- API key status checking
- File dropdown selector
- Live validation

---

### 🔤 Font Manager

**Status:** Planned
**URL:** `/font-manager`
**Category:** Design

Upload, manage, and select custom fonts for the TUI and apps.

**Features (Coming):**

- Font upload
- Font preview
- Font selection
- Global font settings

---

### ✏️ Text Editor (Typo)

**Status:** Building
**URL:** `/typo`
**Category:** Editing

Fresh rich text editor with Tailwind styling and live preview.

Based on: https://github.com/rossrobino/typo

**Features:**

- Live Markdown preview
- Word count
- Rich text formatting (bold, italic, code)
- Export as Markdown or HTML
- Document management API

**Keyboard Shortcuts:**

- `⌘B` — Bold
- `⌘I` — Italic
- `⌘+Shift+C` — Code

---

### 🎮 Grid Editor

**Status:** Planned
**URL:** `/grid-editor`
**Category:** Content

Edit tile-based worlds and spatial layouts for game/world data.

**Features (Coming):**

- Tile palette
- Placement tools
- Layer management
- Export/import worlds

---

### 🔔 Notifications

**Status:** Active
**URL:** `/api/v1/config/notifications/history`
**Category:** Monitoring

View and manage system notifications.

**Features:**

- Notification history
- Filter by type
- Clear old notifications
- Export logs

---

### 💬 Slack Integration

**Status:** Active
**URL:** `/api/v1/slack/status`
**Category:** Integrations

Connect and manage Slack notifications and messages.

**Requirements:**

- `SLACK_BOT_TOKEN` configured in .env

**Features:**

- Send notifications to Slack
- Receive incoming webhooks
- Message templates
- Channel management

---

### 🤖 AI Gateway

**Status:** Active
**URL:** `/api/v1/ai/status`
**Category:** AI

View available AI models and routing status.

**Supported Models:**

- **Local (Ollama):**
  - `mistral:small` (3.7GB)
  - `neural-chat` (4.1GB)
  - `mistral:latest` (7.4GB)

- **Cloud (OpenRouter):**
  - Claude 3 Opus
  - Claude 3 Sonnet
  - Mistral Large
  - GPT-4
  - Others...

**Features:**

- Model listing
- Router status
- Cost tracking
- Local/cloud selection

---

### 📦 Plugin Repository

**Status:** Active
**URL:** `/api/v1/plugin/search`
**Category:** Plugins

Browse and install plugins for uDOS.

**Features:**

- Plugin search
- Installation
- Updates
- Version management

---

### 🐙 GitHub Monitor

**Status:** Active
**URL:** `/api/v1/github/status`
**Category:** DevOps

View GitHub Actions CI/CD pipeline and build status.

**Features:**

- Workflow status
- Build history
- Auto-retry on failure
- Notifications

---

### 🔌 Port Manager

**Status:** Active
**URL:** `/api/v1/ports/status`
**Category:** Infrastructure

Monitor and manage service ports.

**Key Ports:**
| Service | Port | Status |
|---------|------|--------|
| Wizard Server | 8765 | ✓ |
| Goblin Dev | 8767 | ⊘ |
| API Server | 8764 | ✓ |
| Vite Dev | 5173 | ✓ |

**Features:**

- Real-time monitoring
- Port availability check
- Process management
- Port conflict detection

---

## Dashboard JSON Structure

The `/api/v1/index` endpoint returns:

```json
{
  "dashboard": {
    "name": "Wizard Dashboard",
    "description": "Main control center for uDOS Wizard Server",
    "version": "1.0.0",
    "timestamp": "2026-01-18T12:00:00Z"
  },
  "features": [
    {
      "id": "config",
      "name": "⚙️ Configuration",
      "description": "Manage wizard.json, .env files, and API keys",
      "url": "/api/v1/config/dashboard",
      "category": "settings",
      "status": "active"
    },
    ...
  ],
  "api_endpoints": [...],
  "configured_apis": {
    "openai": false,
    "anthropic": true,
    "google": false,
    ...
  },
  "categories": [...]
}
```

---

## API Endpoints

### Core Endpoints

| Endpoint              | Method | Auth | Purpose                |
| --------------------- | ------ | ---- | ---------------------- |
| `/health`             | GET    | No   | Health check           |
| `/api/v1/index`       | GET    | No   | Dashboard index (JSON) |
| `/`                   | GET    | No   | Dashboard index (HTML) |
| `/api/v1/status`      | GET    | Yes  | Server status          |
| `/api/v1/rate-limits` | GET    | Yes  | Rate limit status      |

### Feature Endpoints

| Feature   | Endpoint                   | Method   | Auth |
| --------- | -------------------------- | -------- | ---- |
| Config    | `/api/v1/config/dashboard` | GET      | Yes  |
| Typo      | `/typo`                    | GET      | No   |
| Typo API  | `/typo/api/documents`      | GET/POST | Yes  |
| AI        | `/api/v1/ai/status`        | GET      | Yes  |
| AI Models | `/api/v1/ai/models`        | GET      | Yes  |
| Slack     | `/api/v1/slack/status`     | GET      | Yes  |
| Plugins   | `/api/v1/plugin/search`    | GET      | Yes  |
| GitHub    | `/api/v1/github/status`    | GET      | Yes  |
| Ports     | `/api/v1/ports/status`     | GET      | Yes  |

---

## Configured APIs Status

The dashboard shows which external APIs are configured:

### API Keys Checked

- ✅ **OpenAI** — `OPENAI_API_KEY`
- ✅ **Anthropic** — `ANTHROPIC_API_KEY`
- ✅ **Google** — `GOOGLE_API_KEY`
- ✅ **Mistral** — `MISTRAL_API_KEY`
- ✅ **OpenRouter** — `OPENROUTER_API_KEY`
- ✅ **GitHub** — `GITHUB_TOKEN`
- ✅ **Slack** — `SLACK_BOT_TOKEN`
- ✅ **Gmail** — `GMAIL_CREDENTIALS`

### Status Indicators

- 🟢 **Connected** — API key configured and ready
- 🔴 **Missing** — API key not configured

---

## Quick Links

Fast access to common features:

| Link             | Purpose               |
| ---------------- | --------------------- |
| 📊 Server Status | `/api/v1/status`      |
| 🔄 Rate Limits   | `/api/v1/rate-limits` |
| 🤖 AI Models     | `/api/v1/ai/models`   |
| ❤️ Health Check  | `/health`             |

---

## Feature Categories

Organized dashboard sections:

| Icon | Category       | Features          |
| ---- | -------------- | ----------------- |
| ⚙️   | Settings       | Configuration     |
| 🎨   | Design         | Font Manager      |
| ✏️   | Editing        | Typo Editor       |
| 📄   | Content        | Grid Editor       |
| 📊   | Monitoring     | Notifications     |
| 🔗   | Integrations   | Slack, Gmail      |
| 🤖   | AI             | AI Gateway        |
| 📦   | Plugins        | Plugin Repository |
| 🐙   | DevOps         | GitHub Monitor    |
| 🔌   | Infrastructure | Port Manager      |

---

## Usage from TUI

The TUI automatically detects the Wizard Dashboard on startup:

```bash
$ python -m core.tui

🎮 uDOS Lightweight TUI v1.0.0
Modern CLI for the refined core
✓ Wizard Server running (6/8 APIs configured)
  → Visit: http://127.0.0.1:8765/
Type HELP for commands

location:default>
```

Open the link in your browser to access the full dashboard.

---

## Usage from Scripts/API

Get dashboard data in JSON format:

```python
import requests

response = requests.get("http://127.0.0.1:8765/api/v1/index")
dashboard = response.json()

# List all features
for feature in dashboard["features"]:
    print(f"{feature['name']} → {feature['url']}")

# Check API status
for api_name, configured in dashboard["configured_apis"].items():
    status = "✓" if configured else "✗"
    print(f"{status} {api_name}")
```

---

## Next Steps

### Immediate

- [x] Create dashboard index
- [x] Add feature listing
- [x] Show API status
- [x] Integrate with TUI
- [ ] Add authentication for sensitive features

### Short Term

- [ ] Implement Font Manager
- [ ] Complete Typo editor (document management)
- [ ] Build Grid Editor
- [ ] Add real-time monitoring

### Future

- [ ] Mobile responsive design
- [ ] Dark/Light theme toggle
- [ ] Custom layouts
- [ ] Widget system
- [ ] Real-time updates via WebSocket

---

## Troubleshooting

### Dashboard not loading

```bash
# Check if Wizard Server is running
curl http://127.0.0.1:8765/health

# Check server logs
tail -f memory/logs/wizard-*.log
```

### APIs showing as missing

```bash
# Verify .env configuration
cat ~/.uDOS/config/.env | grep API_KEY

# Update .env with your keys
nano ~/.uDOS/config/.env
```

### TUI not detecting Wizard

```bash
# Ensure Wizard is running on port 8765
python wizard/launch_wizard_dev.py

# Check connectivity
curl http://127.0.0.1:8765/api/v1/index
```

---

## Architecture

```
Wizard Server (port 8765)
├── Dashboard Index (/)
│   ├── HTML UI (/index)
│   └── JSON API (/api/v1/index)
├── Configuration (/api/v1/config/)
│   ├── Dashboard UI
│   ├── Editor (Micro)
│   └── API endpoints
├── Typo Editor (/typo)
│   ├── UI
│   └── Document API
└── Other Features
    ├── AI Gateway
    ├── GitHub Monitor
    ├── Port Manager
    └── etc...

TUI (port 8764)
└── Startup checks /api/v1/index
    └── Shows available features
```

---

**Ready to explore?** Open http://127.0.0.1:8765 in your browser! 🚀
