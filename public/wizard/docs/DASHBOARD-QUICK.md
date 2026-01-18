# 🧙 Wizard Dashboard - Quick Reference

**Last Updated:** 2026-01-18

---

## Quick Links

### Browser Access

```
http://127.0.0.1:8765/          → Main dashboard (HTML)
```

### API Access

```
curl http://127.0.0.1:8765/api/v1/index
```

### In TUI

```
TUI automatically shows:
✓ Wizard Server running (6/8 APIs configured)
  → Visit: http://127.0.0.1:8765/
```

---

## All Features at a Glance

| #   | Feature           | URL                                    | Status      | Category       |
| --- | ----------------- | -------------------------------------- | ----------- | -------------- |
| 1   | ⚙️ Configuration  | `/api/v1/config/dashboard`             | 🟢 Active   | Settings       |
| 2   | 🔤 Font Manager   | `/font-manager`                        | 🟡 Planned  | Design         |
| 3   | ✏️ Typo Editor    | `/typo`                                | 🟡 Building | Editing        |
| 4   | 🎮 Grid Editor    | `/grid-editor`                         | 🟡 Planned  | Content        |
| 5   | 🔔 Notifications  | `/api/v1/config/notifications/history` | 🟢 Active   | Monitoring     |
| 6   | 💬 Slack          | `/api/v1/slack/status`                 | 🟢 Active   | Integrations   |
| 7   | 🤖 AI Gateway     | `/api/v1/ai/status`                    | 🟢 Active   | AI             |
| 8   | 📦 Plugins        | `/api/v1/plugin/search`                | 🟢 Active   | Plugins        |
| 9   | 🐙 GitHub Monitor | `/api/v1/github/status`                | 🟢 Active   | DevOps         |
| 10  | 🔌 Port Manager   | `/api/v1/ports/status`                 | 🟢 Active   | Infrastructure |

---

## Status Legend

| Symbol | Meaning                           |
| ------ | --------------------------------- |
| 🟢     | Active - Ready to use             |
| 🟡     | Building/Planned - In development |
| 🔴     | Error - Issue needs attention     |

---

## Feature Matrix

### By Category

**⚙️ Settings**

- Configuration

**🎨 Design**

- Font Manager

**✏️ Editing**

- Typo Editor

**📄 Content**

- Grid Editor

**📊 Monitoring**

- Notifications

**🔗 Integrations**

- Slack Integration
- Notifications

**🤖 AI**

- AI Gateway

**📦 Plugins**

- Plugin Repository

**🐙 DevOps**

- GitHub Monitor

**🔌 Infrastructure**

- Port Manager

---

## API Configuration Status

The dashboard checks these APIs:

```
OpenAI         → $OPENAI_API_KEY
Anthropic      → $ANTHROPIC_API_KEY
Google         → $GOOGLE_API_KEY
Mistral        → $MISTRAL_API_KEY
OpenRouter     → $OPENROUTER_API_KEY
GitHub         → $GITHUB_TOKEN
Slack          → $SLACK_BOT_TOKEN
Gmail          → $GMAIL_CREDENTIALS
```

**View Status:**

```
http://127.0.0.1:8765/api/v1/index
→ Look at: configured_apis
```

---

## Common Tasks

### Check Server Status

```bash
curl http://127.0.0.1:8765/health
```

### Get Dashboard JSON

```bash
curl http://127.0.0.1:8765/api/v1/index
```

### View Configuration

Open browser: http://127.0.0.1:8765/api/v1/config/dashboard

### Edit Text (Typo)

Open browser: http://127.0.0.1:8765/typo

### Check Port Status

Open browser: http://127.0.0.1:8765/api/v1/ports/status

### View AI Models

```bash
curl http://127.0.0.1:8765/api/v1/ai/models
```

### Check Slack Connection

Open browser: http://127.0.0.1:8765/api/v1/slack/status

---

## Keyboard Shortcuts (Typo Editor)

| Shortcut    | Action     |
| ----------- | ---------- |
| `⌘B`        | Bold       |
| `⌘I`        | Italic     |
| `⌘+Shift+C` | Code block |
| `⌘+Shift+H` | Heading    |

---

## Environment Variables

### Required for Full Functionality

```bash
OPENAI_API_KEY              # For OpenAI models
ANTHROPIC_API_KEY           # For Claude models
GITHUB_TOKEN                # For GitHub integration
SLACK_BOT_TOKEN            # For Slack notifications
```

### Optional

```bash
GOOGLE_API_KEY             # For Google services
MISTRAL_API_KEY            # For Mistral models
OPENROUTER_API_KEY         # For OpenRouter models
GMAIL_CREDENTIALS          # For Gmail integration
```

---

## Features by Maturity

### Production Ready ✅

- Configuration
- Notifications
- Slack Integration
- AI Gateway
- Plugin Repository
- GitHub Monitor
- Port Manager

### In Development 🔨

- Typo Editor (basic functionality working)

### Planned 📋

- Font Manager
- Grid Editor

---

## Port Information

```
Wizard Server:     8765 (main dashboard)
Goblin Dev:        8767 (experimental features)
API Server:        8764 (backend API)
Vite Dev:          5173 (frontend dev)
Tauri Dev:         Various (native app)
```

**View all ports:**
http://127.0.0.1:8765/api/v1/ports/status

---

## Troubleshooting

**Dashboard won't load?**

```bash
# Check if server is running
curl http://127.0.0.1:8765/health

# Restart server
python wizard/launch_wizard_dev.py
```

**API showing as missing?**

```bash
# Check .env file
cat ~/.uDOS/config/.env | grep API_KEY

# Add your keys if missing
nano ~/.uDOS/config/.env
```

**TUI not showing Wizard status?**

```bash
# Make sure Wizard is running first
python wizard/launch_wizard_dev.py

# Then start TUI
python -m core.tui.repl
```

---

## Next Steps

1. **Explore Dashboard** → http://127.0.0.1:8765
2. **Check API Status** → `/api/v1/index`
3. **Try Typo Editor** → `/typo`
4. **View Ports** → `/api/v1/ports/status`
5. **Configure APIs** → Add your keys to `.env`

---

**Last Updated:** 2026-01-18
