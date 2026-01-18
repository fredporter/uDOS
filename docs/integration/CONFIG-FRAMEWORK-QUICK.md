# Wizard Config Framework - Quick Reference

## 🎯 Get Started (3 Steps)

### 1. Start Wizard Server

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python -m wizard.launch_wizard_dev --no-tui
```

Server will start on **http://localhost:8765**

### 2. Open the Dashboard

**Dashboard (Recommended):**

```
http://localhost:8765/api/v1/config/dashboard
```

Shows:

- Left side: API status list (Green/Yellow/Red status badges)
- Right side: Text editor with file dropdown
- Clean, simple design

**Standalone Editor:**

```
http://localhost:8765/api/v1/config/editor/ui
```

### 3. Edit & Save

- Select file from dropdown (.env or wizard.json)
- Edit content in text area
- Press **Ctrl+S** or click **Save**
- See status indicator update

## 📡 API Status Indicators

| Icon | Status    | Meaning                   |
| ---- | --------- | ------------------------- |
| 🟢   | Connected | Key set and validated     |
| 🟡   | Partial   | Key set but not validated |
| 🔴   | Missing   | Key not configured        |

**Categories included:**

- AI Providers (OpenAI, Google, Anthropic, Mistral)
- Developer (GitHub, GitLab, Slack)
- Cloud (AWS, GCP, Azure)
- Integrations (Notion, Gmail, HubSpot)

## 🔌 REST API Endpoints

### Framework Registry

```bash
# Get all APIs organized by category
curl http://localhost:8765/api/v1/config/framework/registry | jq

# Get just one category
curl http://localhost:8765/api/v1/config/framework/registry?category=ai_providers | jq
```

Response:

```json
{
  "status": "success",
  "total": 20,
  "categories": {
    "ai_providers": {
      "count": 4,
      "apis": [
        {
          "name": "OpenAI",
          "category": "ai_providers",
          "env_key": "OPENAI_API_KEY",
          "status": "CONNECTED",
          "docs_url": "https://platform.openai.com/docs"
        }
      ]
    }
  }
}
```

### Editor API

```bash
# List files
curl http://localhost:8765/api/v1/config/editor/files | jq

# Read file
curl http://localhost:8765/api/v1/config/editor/read/.env

# Write file
curl -X POST http://localhost:8765/api/v1/config/editor/write/.env \
  -H "Content-Type: application/json" \
  -d '{"content": "OPENAI_KEY=sk-...\nGOOGLE_KEY=..."}'
```

## 💾 File Management

### Supported Files

- `.env` - Environment variables (recommended)
- `wizard.json` - Wizard configuration
- Other YAML/JSON configs (if added to framework)

### Edit .env Format

```bash
# Comments start with #
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GITHUB_TOKEN=ghp_...
```

### Keyboard Shortcuts

| Shortcut | Action     |
| -------- | ---------- |
| Ctrl+S   | Save file  |
| Ctrl+A   | Select all |

### Status Indicators (Bottom Bar)

- 🟢 **Saved** - No unsaved changes
- 🟡 **Unsaved changes** - Changes pending save
- 🔴 **Error** - Save failed

## 🎨 Design Features

### Two-Panel Layout (Desktop)

```
┌─────────────────────────────────────────┐
│ Configuration Dashboard                 │
├──────────────────┬──────────────────────┤
│  API Status      │  Config Editor       │
│                  │                      │
│ 📡 AI Providers  │ File: [.env ▼]       │
│ ├─ 🟢 OpenAI    │ ┌────────────────┐   │
│ ├─ 🟡 Google    │ │ OPENAI_KEY=... │   │
│ └─ 🔴 Anthropic │ │ GOOGLE_KEY=... │   │
│                  │ │ ...            │   │
│ 💻 Developer    │ └────────────────┘   │
│ ├─ 🟢 GitHub    │ [💾 Save][🔄 Rel]   │
│ └─ 🔴 GitLab    │ ⏹️  Saved • 47 bytes │
└──────────────────┴──────────────────────┘
```

### Mobile Responsive

- **Desktop (>1024px):** Two-column layout
- **Tablet (768-1024px):** Stacked panels
- **Mobile (<768px):** Full-width editor

## 🔐 Security Notes

✅ **What's Secure:**

- File paths validated (no ../ traversal)
- Only known config files accessible
- Errors don't leak system info
- HTTPS recommended for production

⚠️ **What to Remember:**

- Don't commit .env to git
- Don't share dashboard URL publicly
- Regenerate keys periodically
- Use environment-specific configs

## 🧪 Testing Checklist

Run these commands to verify everything works:

```bash
# 1. Test framework endpoint
curl -s http://localhost:8765/api/v1/config/framework/registry | jq '.categories | keys'
# Should output: ["ai_providers", "cloud_services", "developer_tools", "integrations"]

# 2. Test editor files endpoint
curl -s http://localhost:8765/api/v1/config/editor/files | jq '.files'
# Should output: [".env", "wizard.json", ...]

# 3. Test read endpoint
curl -s http://localhost:8765/api/v1/config/editor/read/.env | jq '.filename'
# Should output: ".env"

# 4. Open in browser and verify:
# - Dashboard loads without errors
# - API status list shows ~20 APIs
# - Editor loads .env content
# - Can edit and save
# - Status indicator updates
```

## 🐛 Troubleshooting

### Dashboard Won't Load

```bash
# Check if server is running
curl http://localhost:8765/health

# Check routes are registered
curl -I http://localhost:8765/api/v1/config/dashboard
# Should return 200 OK
```

### Editor Doesn't Save

```bash
# Check file exists
ls -la ~/.udos/.env

# Check permissions
chmod 644 ~/.udos/.env

# Test API directly
curl -X POST http://localhost:8765/api/v1/config/editor/write/.env \
  -H "Content-Type: application/json" \
  -d '{"content": "TEST=1"}'
```

### API Status Shows Missing for Connected APIs

```bash
# Framework checks for env vars
# Make sure .env file exists and has content:
cat ~/.udos/.env

# Check specific key
grep OPENAI_API_KEY ~/.udos/.env
```

## 📚 Related Documentation

- [CONFIG-FRAMEWORK-COMPLETE.md](CONFIG-FRAMEWORK-COMPLETE.md) - Full architecture
- [public/wizard/services/config_framework.py](public/wizard/services/config_framework.py) - Service code
- [public/wizard/routes/config_editor.py](public/wizard/routes/config_editor.py) - Editor routes
- [public/wizard/routes/config_dashboard.py](public/wizard/routes/config_dashboard.py) - Dashboard routes

## 🎯 Common Tasks

### Add a New API to Registry

Edit `/public/wizard/services/config_framework.py`:

```python
def _build_registry(self):
    self.registry = [
        # ... existing APIs ...
        APIRegistry(
            name="My New API",
            category="integrations",
            env_key="MY_API_KEY",
            status=ConfigStatus.MISSING,
            docs_url="https://docs.myapi.com",
            description="Integration with My API"
        ),
    ]
```

### Add a New Config File

Edit `ConfigFramework.get_config_files()`:

```python
def get_config_files(self) -> Dict[str, str]:
    return {
        ".env": str(self.config_dir / ".env"),
        "wizard.json": str(self.config_dir / "wizard.json"),
        "myconfig.yaml": str(self.config_dir / "myconfig.yaml"),  # New!
    }
```

### Apply Framework to Another Module

1. Copy ConfigFramework service to new location
2. Create similar dashboard + editor routes
3. Customize API registry for that module
4. Register routes in server

---

**Version:** ConfigFramework v1.0.0.0
**Status:** ✅ Ready to Use
**Last Updated:** 2026-01-18
