# 🧙 Wizard Dashboard - Getting Started

**Updated:** 2026-01-18
**Version:** 1.0.0

---

## 🚀 5-Minute Quick Start

### 1. Start the Wizard Server

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate

# Option A: Wizard + Interactive Console
python wizard/launch_wizard_dev.py

# Option B: Wizard Server Only (background)
python wizard/launch_wizard_dev.py --no-tui &
```

### 2. Open Dashboard

```bash
# In your browser:
http://127.0.0.1:8765/

# Or get JSON version:
curl http://127.0.0.1:8765/api/v1/index
```

### 3. Explore Features

- Click any feature card to jump to it
- Check API status indicators
- View configuration
- Try the Typo editor
- Monitor ports and services

### 4. Start TUI (Optional)

```bash
python -m core.tui.repl

# You'll see:
# ✓ Wizard Server running (6/8 APIs configured)
#   → Visit: http://127.0.0.1:8765/
```

Done! The dashboard is live. ✨

---

## 📋 Complete Feature Guide

### ⚙️ Configuration Dashboard

**Access:** http://127.0.0.1:8765/api/v1/config/dashboard

What it does:

- View all configuration files (wizard.json, .env, .env-local)
- Check which APIs are configured
- See environment variables
- Manage feature flags

**Example:**

```bash
curl http://127.0.0.1:8765/api/v1/config/dashboard
```

---

### ✏️ Typo Text Editor

**Access:** http://127.0.0.1:8765/typo

A modern markdown editor with:

- **Live preview** — See rendered markdown as you type
- **Split pane** — Edit on left, preview on right
- **Formatting toolbar** — Bold, italic, code, headings, lists
- **Statistics** — Word count, character count, line count
- **Export** — Download as markdown or HTML
- **Document API** — Manage documents programmatically

**Keyboard Shortcuts:**

- `Ctrl/⌘ + B` → Bold
- `Ctrl/⌘ + I` → Italic
- `Ctrl/⌘ + Shift + C` → Code block

**Example: Create a document via API**

```bash
curl -X POST http://127.0.0.1:8765/typo/api/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "My Note", "content": "# Hello\n\nThis is markdown"}'
```

---

### 🔤 Font Manager (Planned)

**Access:** http://127.0.0.1:8765/font-manager

Coming features:

- Upload custom fonts
- Preview fonts in TUI and app
- Set default fonts
- Create font themes
- Font licensing management

---

### 🎮 Grid Editor (Planned)

**Access:** http://127.0.0.1:8765/grid-editor

Coming features:

- Tile-based world editor
- Sprite placement tools
- Layer management
- Export/import worlds as JSON
- Real-time preview

---

### 🔔 Notifications

**Access:** http://127.0.0.1:8765/api/v1/config/notifications/history

View all system notifications:

- Server alerts
- API errors
- Integration events
- User messages

**Example:**

```bash
curl http://127.0.0.1:8765/api/v1/config/notifications/history
```

---

### 💬 Slack Integration

**Access:** http://127.0.0.1:8765/api/v1/slack/status

Set up Slack notifications:

1. Get Slack Bot Token from Slack Workspace
2. Add to `.env`: `SLACK_BOT_TOKEN=xoxb-...`
3. Check status: http://127.0.0.1:8765/api/v1/slack/status
4. Send messages: POST `/api/v1/slack/send`

**Example:**

```bash
curl -X POST http://127.0.0.1:8765/api/v1/slack/send \
  -H "Content-Type: application/json" \
  -d '{"channel": "#general", "text": "Hello from Wizard!"}'
```

---

### 🤖 AI Gateway

**Access:** http://127.0.0.1:8765/api/v1/ai/status

View available AI models:

- **Local models** (via Ollama):
  - mistral:small (3.7GB)
  - neural-chat (4.1GB)
  - mistral:latest (7.4GB)

- **Cloud models** (via OpenRouter):
  - Claude 3 Opus
  - Claude 3 Sonnet
  - GPT-4
  - Mistral Large
  - And 50+ others

**Check available models:**

```bash
curl http://127.0.0.1:8765/api/v1/ai/models
```

**Send completion request:**

```bash
curl -X POST http://127.0.0.1:8765/api/v1/ai/complete \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral:small", "prompt": "What is uDOS?"}'
```

---

### 📦 Plugin Repository

**Access:** http://127.0.0.1:8765/api/v1/plugin/search

Browse and install plugins:

- Search plugin catalog
- View details and ratings
- Install with one click
- Manage installed plugins

**Example:**

```bash
# List all plugins
curl http://127.0.0.1:8765/api/v1/plugin/list

# Get specific plugin
curl http://127.0.0.1:8765/api/v1/plugin/my-plugin
```

---

### 🐙 GitHub Monitor

**Access:** http://127.0.0.1:8765/api/v1/github/status

Monitor CI/CD pipelines:

- View workflow runs
- Check build status
- See test results
- Auto-retry on failure
- Receive notifications

**Example:**

```bash
# Check GitHub status
curl http://127.0.0.1:8765/api/v1/github/status

# View recent workflows
curl http://127.0.0.1:8765/api/v1/github/workflows
```

---

### 🔌 Port Manager

**Access:** http://127.0.0.1:8765/api/v1/ports/status

Monitor all service ports:

| Service       | Port | Purpose         |
| ------------- | ---- | --------------- |
| Wizard Server | 8765 | Main dashboard  |
| Goblin Dev    | 8767 | Dev experiments |
| API Server    | 8764 | Backend API     |
| Vite          | 5173 | Frontend dev    |

**Features:**

- Real-time port monitoring
- Conflict detection
- Process management
- Kill stuck processes
- Port availability checking

**Example:**

```bash
# Full status report
curl http://127.0.0.1:8765/api/v1/ports/status

# Kill process on specific port
curl -X POST http://127.0.0.1:8765/api/v1/ports/8767/kill
```

---

## 🔐 Configuration

### Setting Up API Keys

1. **Get your keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - GitHub: https://github.com/settings/tokens
   - Slack: https://api.slack.com/apps
   - Gmail: https://developers.google.com/gmail/api
   - Mistral: https://console.mistral.ai/
   - Google: https://console.cloud.google.com/
   - OpenRouter: https://openrouter.ai/

2. **Add to `.env` file:**

   ```bash
   # Create/edit ~/.uDOS/config/.env
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GITHUB_TOKEN=ghp_...
   SLACK_BOT_TOKEN=xoxb-...
   # ... etc
   ```

3. **Verify in Dashboard:**
   http://127.0.0.1:8765/api/v1/index → Look at `configured_apis`

---

## 🔗 API Quick Reference

### Health & Status

```bash
# Server health check
curl http://127.0.0.1:8765/health

# Full dashboard index (JSON)
curl http://127.0.0.1:8765/api/v1/index

# Server status with uptime
curl http://127.0.0.1:8765/api/v1/status

# Rate limit info
curl http://127.0.0.1:8765/api/v1/rate-limits
```

### Dashboard Pages

```bash
# HTML dashboard (open in browser)
http://127.0.0.1:8765/

# Configuration
http://127.0.0.1:8765/api/v1/config/dashboard

# Typo editor
http://127.0.0.1:8765/typo

# Notification history
http://127.0.0.1:8765/api/v1/config/notifications/history

# Slack status
http://127.0.0.1:8765/api/v1/slack/status

# AI models
http://127.0.0.1:8765/api/v1/ai/models

# Plugin list
http://127.0.0.1:8765/api/v1/plugin/list

# GitHub status
http://127.0.0.1:8765/api/v1/github/status

# Port status
http://127.0.0.1:8765/api/v1/ports/status
```

---

## 📱 Using from TUI

The TUI automatically detects the dashboard on startup:

```bash
$ python -m core.tui.repl

🎮 uDOS Lightweight TUI v1.0.0
Modern CLI for the refined core
✓ Wizard Server running (6/8 APIs configured)
  → Visit: http://127.0.0.1:8765/

location:default>
```

Copy the URL and open in your browser!

---

## 🐛 Troubleshooting

### "Connection refused"

```bash
# Make sure Wizard is running
python wizard/launch_wizard_dev.py

# Verify port 8765 is open
curl http://127.0.0.1:8765/health
```

### "API showing as missing"

```bash
# Check .env file
cat ~/.uDOS/config/.env

# Add your API key
OPENAI_API_KEY=sk-...

# Restart Wizard
```

### "Dashboard shows 0/8 APIs"

```bash
# Verify .env is in right location
~/.uDOS/config/.env

# Check file has API keys
grep API_KEY ~/.uDOS/config/.env

# Restart Wizard to reload config
```

### "Typo editor not loading"

```bash
# Check for JavaScript errors in browser console
# F12 → Console tab

# Verify route is registered
curl http://127.0.0.1:8765/typo

# Check Wizard logs
tail -f memory/logs/wizard-*.log
```

---

## 📚 Additional Resources

- **Full Documentation:** [DASHBOARD.md](DASHBOARD.md)
- **Quick Reference:** [DASHBOARD-QUICK.md](DASHBOARD-QUICK.md)
- **Wizard Server:** [README.md](README.md)
- **Goblin Dev Server:** [../../dev/goblin/README.md](../../dev/goblin/README.md)

---

## 🎯 Next Steps

1. **✅ Start Wizard Server** — Already running
2. **✅ Open Dashboard** — http://127.0.0.1:8765/
3. **🔲 Add API Keys** — Configure in `.env`
4. **🔲 Try Typo Editor** — http://127.0.0.1:8765/typo
5. **🔲 Start TUI** — `python -m core.tui.repl`
6. **🔲 Explore Features** — Try each feature

---

## 💡 Pro Tips

**Tip 1:** Open dashboard in separate browser tab

- Dashboard in browser: http://127.0.0.1:8765/
- TUI in terminal: `python -m core.tui.repl`
- Work in both simultaneously!

**Tip 2:** Use cURL for scripting

```bash
# Get all feature info
curl http://127.0.0.1:8765/api/v1/index | jq '.features'

# Check specific API status
curl http://127.0.0.1:8765/api/v1/index | jq '.configured_apis'
```

**Tip 3:** Pin dashboard to bookmark bar

- http://127.0.0.1:8765/ → Pin to favorites

**Tip 4:** Use Dashboard JSON for integrations

- API endpoint: `/api/v1/index`
- Returns: feature list, API status, endpoints, categories
- Perfect for custom dashboards or mobile apps

---

**Happy exploring! 🚀**

_Last Updated: 2026-01-18_
