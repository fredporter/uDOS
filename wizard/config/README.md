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
curl http://localhost:8765/api/v1/config/assistant_keys

# Save a config
curl -X POST http://localhost:8765/api/v1/config/assistant_keys \
  -H "Content-Type: application/json" \
  -d '{"content": {...}}'

# View example/template
curl http://localhost:8765/api/v1/config/assistant_keys/example

# Reset to example/template
curl -X POST http://localhost:8765/api/v1/config/assistant_keys/reset
```

## 📋 Configuration Files

### Available Configs

- `assistant_keys.json` — AI provider credentials (Mistral, OpenRouter, Ollama)
- `github_keys.json` — GitHub token and webhooks
- `notion_keys.json` — Notion API credentials
- `oauth_providers.json` — OAuth provider configs
- `slack_keys.json` — Slack bot token and secrets
- `wizard.json` — Server settings and policies

### File Locations (wizard.json)

The `file_locations` section controls where Wizard stores local data:

- `memory_root` — Default location for `memory/` (relative to repo root or absolute path)
- `repo_root` — Repo root override (`auto` uses uDOS.py marker)
- `repo_root_actual` — Read-only, detected local uDOS root
- `memory_root_actual` — Read-only, resolved local memory path

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

## 🔑 GitHub SSH Keys

SSH keys for GitHub authentication are managed separately from API configs.

### Why SSH Keys Are Different

- **Private Key**: Stored in `~/.ssh/` (system standard, never in config folder)
- **Public Key**: Safe to share, added to GitHub
- **Local Only**: Keys never committed to any git repo
- **System Standard**: Uses OS-native SSH directory location

### Setup

The easiest way is using the included setup script:

```bash
# Interactive setup (recommended)
./bin/setup_github_ssh.sh

# Auto setup with defaults
./bin/setup_github_ssh.sh --auto

# Check status
./bin/setup_github_ssh.sh --status

# View help
./bin/setup_github_ssh.sh --help
```

### Via Dashboard

1. Open [http://localhost:8765/#config](http://localhost:8765/#config)
2. Expand "🔑 GitHub SSH Keys" section
3. Click "Test Connection" to check status
4. Click "View Public Key" to see your key
5. Or run the setup script: `./bin/setup_github_ssh.sh`

### REST API (SSH Management)

```bash
# Check SSH key status
curl http://localhost:8765/api/v1/config/ssh/status

# Get public key
curl http://localhost:8765/api/v1/config/ssh/public-key

# Test GitHub connection
curl -X POST http://localhost:8765/api/v1/config/ssh/test-connection

# View setup instructions
curl http://localhost:8765/api/v1/config/ssh/setup-instructions
```

### Key Locations

- **Private Key**: `~/.ssh/id_ed25519_github` (or your custom name)
- **Public Key**: `~/.ssh/id_ed25519_github.pub`
- **SSH Config Dir**: `~/.ssh/`

### Manual Setup

```bash
# Generate ed25519 key (recommended)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -C "your@email.com"

# Or RSA key (wider compatibility)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_github -C "your@email.com"

# View your public key
cat ~/.ssh/id_ed25519_github.pub

# Test connection
ssh -T git@github.com

# Configure git to use the key
git config --global core.sshCommand "ssh -i ~/.ssh/id_ed25519_github"
```

### After Setup

1. Copy your public key
2. Add to GitHub: https://github.com/settings/keys
3. Test: `ssh -T git@github.com`
4. Use `git clone git@github.com:user/repo.git` for SSH clones

## Security Notes

✅ **SSH Key Security:**

- Private keys stay in `~/.ssh/` (OS standard location)
- Never shared or committed to git
- Protected by file permissions (600)
- Backup your `~/.ssh/` directory regularly
- Public keys are safe to share

✅ **API Key Security:**

- Config files stay in `wizard/config/` (local only)
- All `*_keys.json` files gitignored
- Only examples/templates in public repo
- Never sync or backup to cloud
