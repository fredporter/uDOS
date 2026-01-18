# Configuration System - Complete Setup

**Date:** 2026-01-18  
**Status:** ✅ Ready for Production

---

## Configuration Architecture

uDOS uses a **three-tier configuration system** designed for security and flexibility:

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: wizard.json (Committed)                             │
├─────────────────────────────────────────────────────────────┤
│ Location: /Users/fredbook/Code/uDOS/public/wizard/config/   │
│ Committed: YES ✅                                           │
│ Contains: Feature flags, server settings, limits            │
│ Size: ~500 bytes                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: .env (Global Secrets)                               │
├─────────────────────────────────────────────────────────────┤
│ Location: ~/.uDOS/config/.env                              │
│ Committed: NO ❌ (gitignored)                              │
│ Contains: All API keys and credentials                      │
│ Size: ~1-2 KB                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: .env-local (Local Overrides)                        │
├─────────────────────────────────────────────────────────────┤
│ Location: ~/.uDOS/config/.env-local                        │
│ Committed: NO ❌ (gitignored)                              │
│ Contains: Development overrides (optional)                  │
│ Size: Variable                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## File Details

### 1. wizard.json (Committed Configuration)

**Path:** `public/wizard/config/wizard.json`

**Purpose:** Non-secret configuration that can be shared

**Editable Via:**

- Configuration Dashboard
- Direct file edit
- Version control

**Current Content:**

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
  "gmail_relay_enabled": true,
  "ai_gateway_enabled": true,
  "oauth_enabled": false,
  "github_webhook_secret": null,
  "github_allowed_repo": "fredporter/uDOS-dev",
  "github_default_branch": "main",
  "github_push_enabled": false,
  "hubspot_enabled": false,
  "notion_enabled": false,
  "icloud_enabled": false
}
```

---

### 2. .env (Global Secrets)

**Path:** `~/.uDOS/config/.env`

**Purpose:** API keys and credentials (all users, all projects)

**Editable Via:**

- Configuration Dashboard
- Text editor (nano, vim, etc)

**Template:** `public/wizard/config/.env.example`

**Structure:**

```env
# Comments explain each section

# AI Providers
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
MISTRAL_API_KEY=...

# Developer Services
GITHUB_TOKEN=ghp_...
GITLAB_TOKEN=glpat-...

# Cloud Services
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
GOOGLE_CLOUD_KEY_JSON={...}

# Integrations
NOTION_API_KEY=secret_...
SLACK_BOT_TOKEN=xoxb-...
HUBSPOT_PRIVATE_APP_TOKEN=pat-...

# Email
GMAIL_ADDRESS=user@gmail.com
GMAIL_APP_PASSWORD=...
```

**Security:**

- ✅ Protected by `.gitignore`
- ✅ Only user-readable: `chmod 600 ~/.uDOS/config/.env`
- ✅ Backed up separately from git
- ✅ Can be rotated per key

---

### 3. .env-local (Local Overrides)

**Path:** `~/.uDOS/config/.env-local` (optional)

**Purpose:** Development-only overrides

**Use Cases:**

- Test API keys for development
- Debug flags for local testing
- Custom ports or hosts
- Feature flags for experiments

**Example:**

```env
# Use test key for development only
OPENAI_API_KEY=sk-test-local-...

# Enable debug mode
DEBUG=true
VERBOSE_LOGGING=true

# Custom test settings
AI_BUDGET_DAILY=0.5
LOG_LEVEL=DEBUG
```

**Priority:** Overrides both wizard.json and .env

---

## Configuration Dashboard

**Access:** `http://localhost:8765/api/v1/config/dashboard`

### Features

✅ **Two-Panel Interface:**

1. **API Status Panel** (left)
   - Shows all configured APIs
   - Color-coded status indicators
   - Read-only display
2. **Config Editor Panel** (right)
   - Edit wizard.json, .env, .env-local
   - File dropdown selector
   - In-browser editor with syntax highlighting
   - Save/Reload buttons
   - File size and line count display

✅ **API Status Colors:**

- 🟢 **CONNECTED** - Key configured and has value
- 🟡 **PARTIAL** - Key exists but empty
- 🔴 **MISSING** - Key not configured

✅ **Keyboard Shortcuts:**

- `Ctrl+S` - Save file
- `Ctrl+A` - Select all
- Arrow keys - Navigation

---

## Setup Instructions

### First Time Setup

```bash
# 1. Create config directory
mkdir -p ~/.uDOS/config

# 2. Copy template
cp /Users/fredbook/Code/uDOS/public/wizard/config/.env.example \
   ~/.uDOS/config/.env

# 3. Edit with your keys
nano ~/.uDOS/config/.env

# 4. Set secure permissions
chmod 600 ~/.uDOS/config/.env

# 5. Verify
grep "^[A-Z]" ~/.uDOS/config/.env | wc -l
# Should show your API key count
```

### Adding Keys via Dashboard

1. Open: `http://localhost:8765/api/v1/config/dashboard`
2. Select file: `.env (secrets)`
3. Add keys in format: `KEY=value`
4. Click 💾 Save
5. Verify in API Status panel: should show 🟢 CONNECTED

---

## Load Order

When ConfigFramework initializes:

```python
# 1. Load wizard.json (defaults)
config = load_json('wizard.json')

# 2. Load and merge .env (overrides json)
env_vars = load_env_file('.env')
config.update(env_vars)

# 3. Load and merge .env-local (final override)
if env_local_exists():
    local_vars = load_env_file('.env-local')
    config.update(local_vars)

# Result: config has final merged values
```

**Priority:** wizard.json < .env < .env-local

---

## Files Overview

| File         | Location                | Type      | Committed | Size     | Purpose         |
| ------------ | ----------------------- | --------- | --------- | -------- | --------------- |
| wizard.json  | `public/wizard/config/` | JSON      | ✅ YES    | ~500 B   | Server config   |
| .env         | `~/.uDOS/config/`       | Secrets   | ❌ NO     | ~1-2 KB  | API keys        |
| .env-local   | `~/.uDOS/config/`       | Overrides | ❌ NO     | Variable | Dev overrides   |
| .env.example | `public/wizard/config/` | Template  | ✅ YES    | ~1 KB    | Key reference   |
| .gitignore   | `public/wizard/config/` | Git       | ✅ YES    | <100 B   | Protect secrets |

---

## Available APIs

The system can configure these APIs:

### AI Providers (4 APIs)

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Mistral AI

### Developer Services (2 APIs)

- GitHub
- GitLab

### Cloud Services (2 APIs)

- AWS
- Google Cloud

### Integrations (3 APIs)

- Notion
- Slack
- HubSpot

---

## Security Checklist

- ✅ `.env` is gitignored
- ✅ `.env-local` is gitignored
- ✅ `~/.uDOS/config/.env` has `chmod 600`
- ✅ Template `.env.example` is committed (no real keys)
- ✅ No API keys in wizard.json
- ✅ No secrets in logs
- ✅ Dashboard doesn't reveal key values
- ✅ Keys are read-only in API Status panel

---

## Deployment

### Docker

```dockerfile
# Option 1: Provide via environment
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Option 2: Copy .env at build time
COPY .env /home/user/.uDOS/config/.env

# Option 3: Mount at runtime
# docker run -v ~/.uDOS/config:/home/user/.uDOS/config ...
```

### Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: udos-secrets
type: Opaque
data:
  OPENAI_API_KEY: c2stcHJvai1...
  GITHUB_TOKEN: Z2hwXy4u...
---
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: udos-secrets
        key: OPENAI_API_KEY
```

### Environment Variables

```bash
export OPENAI_API_KEY="sk-proj-..."
export GITHUB_TOKEN="ghp_..."
python -m public.wizard.server
```

---

## Related Documentation

- [Adding API Keys Guide](./ADDING-API-KEYS.md)
- [Configuration Strategy](./CONFIGURATION-STRATEGY.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Reference](./API.md)

---

## Support

**Configuration Issues?**

1. Check `~/.uDOS/config/` exists and is readable
2. Verify `.env` format: `KEY=value` (no spaces)
3. Reload dashboard and clear browser cache
4. Check server logs: `/tmp/wizard_server.log`

**Lost API Keys?**

1. Regenerate keys from provider
2. Update `.env` with new keys
3. Verify in Configuration Dashboard
4. Test API integration

**Want to Add More APIs?**

1. Edit `config_framework.py` APIRegistry list
2. Add provider to ENDPOINT_TIERS
3. Add key documentation to `.env.example`
4. Restart server

---

**Status:** Production Ready ✅  
**Version:** Configuration Framework v1.1.0  
**Last Updated:** 2026-01-18
