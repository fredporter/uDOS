# How to Manage Secrets Safely
**Document Version:** 1.0
**Status:** Active
**Last Updated:** 2026-02-24

---

## Quick Start

### For New Setup
```bash
# 1. Copy template (safe to commit)
cp .env.example .env

# 2. Edit with YOUR LOCAL paths and non-sensitive config
nano .env
#   - Set UDOS_ROOT to your repo path
#   - Set USER_NAME, timezone, location
#   - Leave API keys empty

# 3. Run setup story (generates WIZARD_KEY automatically)
python uDOS.py  # Choose SETUP story

# 4. Start Wizard Dashboard
WIZARD start
export WIZARD_PORT="${WIZARD_PORT:-8765}"
export WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:${WIZARD_PORT}}"
# Visit: ${WIZARD_BASE_URL}/dashboard

# 5. Add your API keys via GUI (Settings > Integrations > Add Secret)
#    Wizard encrypts them to secrets.tomb
```

### For Existing Setup (Rotate Exposed Keys)
```bash
# If you see exposed secrets in git history:

# 1. Revoke keys immediately at their provider
#    - Mistral: https://console.mistral.ai (delete + create new)
#    - GitHub: https://github.com/settings/tokens
#    - OpenAI: https://platform.openai.com/account/api-keys
#    - etc.

# 2. Remove .env from git history (contact team lead for git-filter-repo)

# 3. Reset local secrets
uv run wizard/tools/reset_secrets_tomb.py

# 4. Start fresh
python uDOS.py  # SETUP story

# 5. Add new keys to Wizard dashboard
WIZARD start
```

---

## What Goes Where

### ✅ Safe in .env (commit to git)

```env
# User identity (non-sensitive)
USER_NAME=Fredrick
UDOS_TIMEZONE=America/Los_Angeles
UDOS_LOCATION=San Francisco
OS_TYPE=mac

# Paths
UDOS_ROOT=/Users/fredrick/Code/uDOS
UDOS_MEMORY_ROOT=${UDOS_ROOT}/memory
VAULT_ROOT=${UDOS_MEMORY_ROOT}/vault
VAULT_MD_ROOT=${VAULT_ROOT}

# Configuration flags (non-sensitive)
UDOS_LOG_LEVEL=INFO
UDOS_AUTOMATION=0
```

### ❌ NEVER in .env (even example versions!)

```env
# These MUST be empty or commented out:
MISTRAL_API_KEY=                    # ← Empty!
WIZARD_ADMIN_TOKEN=                 # ← Empty!
GITHUB_TOKEN=                       # ← Empty!
```

### 🔐 Goes in wizard/secrets.tomb (encrypted)

Everything sensitive is stored encrypted:
- API keys (Mistral, OpenAI, Anthropic, etc.)
- OAuth tokens (Gmail, Google Drive, Slack, etc.)
- Cloud credentials (AWS, Azure, GCP, etc.)
- GitHub webhook secrets
- Admin authentication tokens
- Personal access tokens
- Database credentials

---

## Step-by-Step: Add an API Key

### Via Wizard Dashboard (Recommended)

```bash
# 1. Start the dashboard
WIZARD start
export WIZARD_PORT="${WIZARD_PORT:-8765}"
export WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:${WIZARD_PORT}}"

# 2. Open browser
open "${WIZARD_BASE_URL}/dashboard"
# or visit manually: ${WIZARD_BASE_URL}/dashboard

# 3. Navigate to Settings > Integrations

# 4. Click "Add Secret" button

# 5. Fill in:
#    - Provider: "Mistral" (or your provider)
#    - Key Name: "mistral-api-key"
#    - Value: <your-actual-api-key>

# 6. Click "Save" — Wizard encrypts and stores it

# 7. Verify it works from the standard runtime
ucode
# Then run a simple operator or logic-assist prompt
```

### Via CLI (For Automation)

```bash
# Check current status
uv run wizard/tools/check_secrets_tomb.py

# Manually unlock and set a secret
cat > /tmp/set_secret.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, "/path/to/uDOS")

from wizard.services.secret_store import get_secret_store, SecretEntry
from datetime import datetime, timezone
import os

# Unlock using WIZARD_KEY from env
store = get_secret_store()
store.unlock(os.environ["WIZARD_KEY"])

# Create new entry
entry = SecretEntry(
    key_id="mistral-api-key",
    provider="mistral",
    value="your-actual-api-key-here",
    created_at=datetime.now(timezone.utc).isoformat(),
)

# Store it
store.set(entry)
print("✅ Secret stored successfully")
EOF

uv run /tmp/set_secret.py
```

### Via Setup Story (Initial Setup Only)

```bash
# During first SETUP story, you'll be prompted for:
# - Username
# - Timezone
# - Location
# - Optional: API keys (will ask for Mistral, etc.)

# Answers are stored in secrets.tomb automatically
python uDOS.py  # Choose SETUP
```

---

## Troubleshooting

### "Secret store is locked"

```bash
# Check what's wrong
uv run wizard/tools/check_secrets_tomb.py

# If WIZARD_KEY is missing:
export WIZARD_KEY=<your-64-char-key>

# If that doesn't work, check .env
cat .env | grep WIZARD_KEY

# Still stuck? Reset (destructive, re-run SETUP)
uv run wizard/tools/reset_secrets_tomb.py
```

### "API key not found when running commands"

```bash
# Verify it was saved
uv run wizard/tools/check_secrets_tomb.py
# Look for output showing "mistral-api-key" in entries

# If missing, re-add it via dashboard
WIZARD start
# Settings > Integrations > Add Secret

# Verify the key works
ucode  # Then run a simple operator or provider-backed prompt
```

### "What if I forgot my WIZARD_KEY?"

⚠️ **This is not recoverable** — WIZARD_KEY is the only encryption key.

**Your options:**
1. If you remember it, update .env
2. If you have it saved elsewhere (password manager), use that value
3. If it's completely lost, reset everything:
   ```bash
   uv run wizard/tools/reset_secrets_tomb.py
   python uDOS.py  # Re-run SETUP
   ```

### "How do I rotate a key?"

**Option A: Via Dashboard (Easiest)**
```bash
WIZARD start
# Settings > Integrations > [Provider] > Rotate
```

**Option B: Via CLI**
```bash
# 1. Get current value (if you need to copy it)
uv run wizard/tools/check_secrets_tomb.py

# 2. Delete old entry
python << 'EOF'
import sys, os
sys.path.insert(0, ".")
from wizard.services.secret_store import get_secret_store

store = get_secret_store()
store.unlock(os.environ["WIZARD_KEY"])
# Remove old entry (API doesn't expose this yet)
# Use dashboard instead
EOF

# 3. Add new entry
uv run wizard/tools/secret_store_cli.py set mistral-api-key <new-key>
```

---

## GitHub Integration Consolidation

### Current State
GitHub tokens are referenced in multiple places:
- Dev Mode contributor-tool UI runtime — token send path
- Dev Mode contributor-tool update notifier — release fetching
- `wizard/services/wizard_config.py` — Webhook config

### Recommended Consolidation
Use the unified `GitHubIntegration` class:

```python
# Instead of scattered code:
# Legacy Dev Mode compatibility imports may still come from the external
# contributor-tool runtime when older integrations are in use.

# Get token (from secrets.tomb)
token = GitHubIntegration.get_token()

# Get webhook secret
webhook_secret = GitHubIntegration.get_webhook_secret()

# Verify webhook signature
if GitHubIntegration.verify_webhook(payload, signature):
    print("Webhook is authentic")
```

This ensures:
- ✅ Single source of truth for GitHub credentials
- ✅ All access goes through secrets.tomb
- ✅ Consistent logging and auditing
- ✅ Easier rotation and testing

---

## Security Checklist

- [ ] `.env` contains **no** API keys
- [ ] All API keys are in `wizard/secrets.tomb`
- [ ] `WIZARD_KEY` is set in .env (unique per machine)
- [ ] `.env` is in `.gitignore`
- [ ] `secrets.tomb` is in `.gitignore`
- [ ] CI workflow runs secrets detection
- [ ] All exposed keys are rotated/revoked
- [ ] Team members know to use Wizard dashboard for secrets
- [ ] Pre-commit hooks prevent accidental commits (optional)

---

## References

- [ENV-STRUCTURE-V1.1.0.md](../specs/ENV-STRUCTURE-V1.1.0.md) — Design spec
- [2026-02-24-security-audit.md](../devlog/2026-02-24-security-audit.md) — Incident report
- `wizard/tools/check_secrets_tomb.py` — Status tool
- `wizard/tools/reset_secrets_tomb.py` — Reset tool
- `wizard/tools/secret_store_cli.py` — CLI management
