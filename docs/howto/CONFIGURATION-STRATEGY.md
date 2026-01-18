# uDOS Configuration Architecture

**Last Updated:** 2026-01-18  
**Status:** Production Ready

---

## Overview

uDOS uses a **three-file configuration strategy** for maximum flexibility and security:

1. **wizard.json** - Public configuration (committed to git)
2. **.env** - User secrets (gitignored, personal)
3. **.env-local** - Local overrides (gitignored, optional)

---

## File Locations

### wizard.json (Committed)

```
/Users/fredbook/Code/uDOS/public/wizard/config/wizard.json
```

**Purpose:** Feature flags, server settings, limits  
**Committed:** YES ✅ (safe for git)  
**Contains:** No secrets

**Example:**

```json
{
  "host": "0.0.0.0",
  "port": 8765,
  "debug": false,
  "ai_budget_daily": 10.0,
  "plugin_repo_enabled": true
}
```

### .env (Global Secrets)

```
~/.uDOS/config/.env
```

**Purpose:** API keys, credentials (shared across all projects)  
**Committed:** NO ❌ (gitignored)  
**Contains:** All API keys

**Example:**

```env
# AI Providers
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Developer Services
GITHUB_TOKEN=ghp_...

# Cloud Services
AWS_ACCESS_KEY_ID=AKIA...
```

### .env-local (Local Overrides)

```
~/.uDOS/config/.env-local
```

**Purpose:** Local development overrides (optional)  
**Committed:** NO ❌ (gitignored)  
**Contains:** Test keys, development settings

**Example:**

```env
# Override for local testing
OPENAI_API_KEY=sk-test-local-...
DEBUG=true
```

---

## Configuration Priority

When loading settings:

```
wizard.json (base)
    ↓
.env (global secrets override json)
    ↓
.env-local (local overrides both)
```

**In Code:**

```python
# Load json config first
config = load_json('wizard.json')

# Override with env variables from .env
if os.getenv('OPENAI_API_KEY'):
    config['ai_provider'] = os.getenv('OPENAI_API_KEY')

# Local .env-local overrides everything
if os.getenv('LOCAL_OVERRIDE'):
    config['debug'] = True
```

---

## Configuration Dashboard

The Configuration Dashboard (`/api/v1/config/dashboard`) displays:

### Files Available for Editing:

1. **.env (secrets)** - API keys and credentials
2. **.env-local (overrides)** - Development overrides (if it exists)
3. **wizard.json (config)** - Feature configuration

### API Status Panel:

Shows which APIs are configured by checking for their keys in .env:

- 🟢 CONNECTED - Key configured in .env
- 🟡 PARTIAL - Key exists but empty
- 🔴 MISSING - Key not configured

---

## Setup Instructions

### 1. First Time Setup

Copy the template and add your keys:

```bash
# View template
cat /Users/fredbook/Code/uDOS/public/wizard/config/.env.example

# Create user config (only done once)
mkdir -p ~/.uDOS/config
cp /Users/fredbook/Code/uDOS/public/wizard/config/.env.example ~/.uDOS/config/.env

# Edit with your API keys
nano ~/.uDOS/config/.env
```

### 2. Add Your API Keys

Get keys from each provider:

```env
# OpenAI - https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-...

# Anthropic - https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-...

# GitHub - https://github.com/settings/tokens
GITHUB_TOKEN=ghp_...

# ... add more as needed
```

### 3. Verify Configuration

Check the Configuration Dashboard:

```
http://localhost:8765/api/v1/config/dashboard
```

The API Status panel should show status for each configured key.

---

## Docker / Deployment

When deploying, provide secrets via environment variables:

```bash
# Option 1: Environment variables
docker run \
  -e OPENAI_API_KEY=sk-proj-... \
  -e GITHUB_TOKEN=ghp_... \
  udos:latest

# Option 2: .env file in docker image
COPY .env /home/user/.uDOS/config/.env

# Option 3: Secrets manager (recommended)
# Mount secrets from AWS Secrets Manager, Vault, etc.
```

---

## Security Best Practices

### DO ✅

- Store all API keys in .env (never in wizard.json)
- Use environment variables for production
- Rotate keys regularly
- Use minimal permissions for each key
- Keep .env in ~/.uDOS/config/ (home directory)

### DON'T ❌

- Commit .env to git
- Store secrets in wizard.json
- Use production keys in development
- Share .env files
- Log or print API keys
- Hardcode credentials in code

---

## File Editing

Use the Configuration Dashboard to safely edit files:

```
⚙️ Configuration Dashboard
├── 📡 API Status (read-only)
└── 📝 Config Editor
    ├── .env (secrets)
    ├── .env-local (overrides)
    └── wizard.json (config)
```

**Features:**

- In-browser editor with syntax highlighting
- Save/Reload buttons
- File change tracking
- Status bar showing file size
- Keyboard shortcuts (Ctrl+S to save)

---

## Troubleshooting

### API Status Shows All MISSING

- [ ] Check if ~/.uDOS/config/.env exists
- [ ] Verify API keys are in correct format
- [ ] Check for typos in KEY names
- [ ] Restart server after adding keys

### Can't Save Config

- [ ] Check file permissions on ~/.uDOS/config/
- [ ] Verify directory exists and is writable
- [ ] Check server logs for errors

### Keys Not Being Loaded

- [ ] Verify keys are before equals sign (KEY=value)
- [ ] No spaces around equals: `KEY=value` not `KEY = value`
- [ ] No quotes needed: `KEY=value` not `KEY="value"`
- [ ] Comment lines start with # (no spaces before #)

---

## Environment Variable Reference

### AI Providers

```
OPENAI_API_KEY          - OpenAI GPT models
ANTHROPIC_API_KEY       - Claude API
GOOGLE_API_KEY          - Gemini models
MISTRAL_API_KEY         - Mistral models
```

### Developer Services

```
GITHUB_TOKEN            - GitHub API access
GITLAB_TOKEN            - GitLab API access
```

### Cloud Services

```
AWS_ACCESS_KEY_ID       - AWS S3, etc.
AWS_SECRET_ACCESS_KEY
GOOGLE_CLOUD_KEY_JSON   - GCP services
```

### Integrations

```
NOTION_API_KEY          - Notion workspace
SLACK_BOT_TOKEN         - Slack bot
HUBSPOT_PRIVATE_APP_TOKEN - HubSpot CRM
```

### Email

```
GMAIL_ADDRESS           - Gmail account
GMAIL_APP_PASSWORD      - Gmail app password
```

---

## Advanced: Custom Secrets

Add any custom secrets to your .env:

```env
# Custom application settings
MY_DATABASE_URL=postgresql://...
MY_API_SECRET=xyz123...
MY_WEBHOOK_SECRET=webhook_...
```

Access in code:

```python
import os
db_url = os.getenv('MY_DATABASE_URL')
api_secret = os.getenv('MY_API_SECRET')
```

---

## Related Documentation

- [Configuration Dashboard Guide](./CONFIGURATION-DASHBOARD.md)
- [API Reference](./API.md)
- [Deployment Guide](./DEPLOYMENT.md)

---

_Configuration Framework v1.1.0 - Wizard Server_
