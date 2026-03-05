# Wizard Configuration Management

Private local configuration for Wizard settings, secret storage, and v1.5 logic-assist policy.
**Local machine only - never committed to git.**

## 🎛️ Managing Configs

### Web Dashboard (Recommended)

Open `${WIZARD_BASE_URL:-http://127.0.0.1:${WIZARD_PORT:-8765}}/config` to:

- View all available configs
- Edit API keys in a secure, user-friendly interface
- See example/template formats
- Save changes locally
- Manage the shared `/.venv`, secret store, and plugin installers from one All-In-One view

### REST API

```bash
# List all config files
BASE_URL="${WIZARD_BASE_URL:-http://127.0.0.1:${WIZARD_PORT:-8765}}"
curl "$BASE_URL/api/config/files"

# Get a config (loads example if missing)
curl "$BASE_URL/api/config/files"

# Get Wizard settings
curl "$BASE_URL/api/config/wizard"
```

## 📋 Configuration Files

### Available Configs

- `wizard.json` — server settings and policies
- `github_keys.json` — GitHub token and webhooks
- `oauth_providers.json` — OAuth provider configs
- `memory/bank/typo-workspace/user/settings/logic-assist.md` — active logic-assist provider and budget policy
- `wizard/secrets.tomb` — encrypted local secret store

### File Locations (wizard.json)

The `file_locations` section controls where Wizard stores local data:

- `memory_root` — Default location for `memory/` (relative to repo root or absolute path)
- `vault_root` — Default location for `memory/vault/` (relative to repo root or absolute path)
- `repo_root` — Repo root override (`auto` uses uDOS.py marker)
- `repo_root_actual` — Read-only, detected local uDOS root
- `memory_root_actual` — Read-only, resolved local memory path
- `vault_root_actual` — Read-only, resolved user vault path

### Templates in Public Repo

- `wizard/config/*.template.json` — template payloads where still active
- `core/framework/seed/bank/typo-workspace/settings/logic-assist.md` — canonical logic-assist settings template

## 🔐 Security

✅ **Private configs NEVER committed to git**

- Actual `*_keys.json` files are gitignored
- Only `.example.json` and `.template.json` in public repo
- Private configs stay on local machine only
- Accessible only on localhost

## 🚀 Quick Start

1. Open `${WIZARD_BASE_URL:-http://127.0.0.1:${WIZARD_PORT:-8765}}/config`
2. Select a configuration or settings surface
3. Click "📋 View Example" to see the format
4. Add required secrets through the Wizard secret store
5. Edit and save locally
6. Integration is immediately available

## Manual Editing

Only edit local files directly when you intentionally need file-based recovery or automation.

## Status Check

```bash
uv run python wizard/config/check_config_status.py
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

1. Open `${WIZARD_BASE_URL:-http://127.0.0.1:${WIZARD_PORT:-8765}}/#config`
2. Expand "🔑 GitHub SSH Keys" section
3. Click "Test Connection" to check status
4. Click "View Public Key" to see your key
5. Or run the setup script: `./bin/setup_github_ssh.sh`

### REST API (SSH Management)

```bash
# Check SSH key status
BASE_URL="${WIZARD_BASE_URL:-http://127.0.0.1:${WIZARD_PORT:-8765}}"
curl "$BASE_URL/api/config/ssh/status"

# Get public key
curl "$BASE_URL/api/config/ssh/public-key"

# Test GitHub connection
curl -X POST "$BASE_URL/api/config/ssh/test-connection"

# View setup instructions
curl "$BASE_URL/api/config/ssh/setup-instructions"
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
