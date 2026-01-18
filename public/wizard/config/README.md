# Wizard Config Overview

Sensitive configuration lives in this folder. Use the provided templates to create local-only files (gitignored) before running the Wizard server.

## Templates (copy → fill → keep private)

- `ai_keys.template.json` → `ai_keys.json` (Ollama/OpenRouter/Gemini/Anthropic keys)
- `oauth_providers.template.json` → `oauth_providers.json` (Google/GitHub/Spotify/Discord/Notion)
- `slack_keys.template.json` → `slack_keys.json` (Slack bot token, webhook, default channel, signing secret)
- `github_keys.example.json` → `github_keys.json` (GitHub personal access tokens)
- `notion_keys.example.json` → `notion_keys.json` (Notion integration token)
- `port_registry.json` (tracked) — service/port mapping for port-manager

## Quick status check (no secrets printed)

Run the local checker to confirm files exist and required keys are present:

```bash
python wizard/config/check_config_status.py
```

## Usage

1. Copy the relevant template to its non-tracked counterpart.
2. Populate values with real secrets.
3. Load into environment (e.g., `direnv`, `.env`, or process manager) **or** read from file in your startup scripts.
4. Never commit real secrets. The `.gitignore` protects the `*keys.json` files.

## Quick Checks

- Ensure `ai_keys.json` and `slack_keys.json` exist before enabling AI or Slack features.
- Verify `port_registry.json` matches local service ports before running port-manager.
- Keep OAuth redirect URIs aligned with `oauth_providers.json` (default `http://localhost:8765/oauth/callback`).
