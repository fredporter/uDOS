# Wizard Configuration Management

Private configuration files for API keys, secrets, and system settings.
**Local machine only - never committed to git.**

## 🎛️ Managing Configs

### Web Dashboard (Recommended)

Open [http://localhost:8765/#config](http://localhost:8765/#config) to:

- View all available configs
- Edit API keys in a secure, user-friendly interface
- See example/template formats
- Save changes locally

### REST API

```bash
# List all config files
curl http://localhost:8765/api/v1/config/files

# Get a config (loads example if missing)
curl http://localhost:8765/api/v1/config/ai_keys

# Save a config
curl -X POST http://localhost:8765/api/v1/config/ai_keys \
  -H "Content-Type: application/json" \
  -d '{"content": {...}}'

# View example/template
curl http://localhost:8765/api/v1/config/ai_keys/example

# Reset to example/template
curl -X POST http://localhost:8765/api/v1/config/ai_keys/reset
```

## 📋 Configuration Files

### Available Configs

- `ai_keys.json` — AI provider credentials (Mistral, OpenRouter, Ollama)
- `github_keys.json` — GitHub token and webhooks
- `notion_keys.json` — Notion API credentials
- `oauth_providers.json` — OAuth provider configs
- `slack_keys.json` — Slack bot token and secrets
- `wizard.json` — Server settings and policies

### Templates in Public Repo

- `*_keys.example.json` — Full working example with all required fields
- `*_keys.template.json` — Minimal template for getting started

## 🔐 Security

✅ **Private configs NEVER committed to git**

- Actual `*_keys.json` files are gitignored
- Only `.example.json` and `.template.json` in public repo
- Private configs stay on local machine only
- Accessible only on localhost

## 🚀 Quick Start

1. Open [http://localhost:8765/#config](http://localhost:8765/#config)
2. Select a configuration (e.g., "AI Provider Keys")
3. Click "📋 View Example" to see the format
4. Get your API key from the provider
5. Edit and save locally
6. Integration is immediately available

## Legacy: Manual File Copy

Before using the dashboard, you could manually copy templates:

```bash
cp wizard/config/ai_keys.example.json wizard/config/ai_keys.json
nano wizard/config/ai_keys.json
```

**This still works**, but the dashboard is easier.

## Status Check

```bash
python wizard/config/check_config_status.py
```
