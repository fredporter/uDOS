# 🔐 Secure Configuration Panel Guide

> Manage all API keys and secrets safely through the Wizard Server web interface with encryption, audit logging, and validation.

---

## Quick Start (3 Steps)

### Step 1: Launch Wizard Server

```bash
cd /Users/fredbook/Code/uDOS

# Activate venv (if not already active)
source .venv/bin/activate

# Launch Wizard with config panel
python wizard/launch_wizard_dev.py --no-tui
```

**Output:**

```
🧙 Wizard Server starting...
✅ Server listening on: http://127.0.0.1:8765
✅ Config panel: http://127.0.0.1:8765/api/v1/config/panel
```

### Step 2: Open Config Panel

**Open in browser:**

```
http://127.0.0.1:8765/api/v1/config/panel
```

You'll see a dashboard showing:

- Total keys configured
- Keys that are set vs. not set
- Validation status
- Organized by category (AI Providers, GitHub, OAuth, Integrations, Cloud Services)

### Step 3: Add/Update Keys

1. **Find the key field** (e.g., "GEMINI_API_KEY" under "AI Providers")
2. **Paste your new API key** into the password input field
3. **Click "Save"** button
4. You'll see a ✅ success message
5. **Repeat for each key** you need to add

**Done!** Keys are now encrypted and stored securely.

---

## How It Works

### Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Web Browser                             │
│  (Config Panel UI - no keys stored locally)              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS (over localhost)
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Wizard Server (8765)                         │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  FastAPI Routes (/api/v1/config/...)             │   │
│  │  ├─ POST   /keys/{name}    (set key)             │   │
│  │  ├─ GET    /status         (view status)         │   │
│  │  ├─ DELETE /keys/{name}    (delete key)          │   │
│  │  └─ GET    /panel          (serve UI)            │   │
│  └──────────────────────────────────────────────────┘   │
│                         ▼                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SecureConfigManager (secure_config.py)          │   │
│  │  ├─ Encryption (Fernet AES-256-GCM)              │   │
│  │  ├─ Key validation (format checks)               │   │
│  │  ├─ Audit logging (all access tracked)           │   │
│  │  └─ Secure deletion                              │   │
│  └──────────────────────────────────────────────────┘   │
│                         ▼                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Encrypted Storage                                │   │
│  │  ├─ keys.enc.json (encrypted, chmod 0o600)       │   │
│  │  ├─ keys.audit.log (all access tracked)          │   │
│  │  └─ .env local only (gitignored)                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Key Features

**1. Encryption at Rest**

- All keys stored in `keys.enc.json` using Fernet (AES-256-GCM)
- Encryption key from `UDOS_ENCRYPTION_KEY` env var
- Auto-generated if missing
- Never transmitted over network

**2. Audit Logging**

- Every key access logged to `keys.audit.log`
- Timestamp, action, key name, and details
- Cannot be disabled
- Used for security investigations

**3. Key Validation**

- OpenAI keys: starts with `sk-`
- Gemini keys: 30+ characters
- GitHub tokens: 40+ characters
- Provider-specific validation rules
- Shows validation status in UI

**4. No Secrets in Transit**

- Keys never exposed in logs
- Password fields in UI (masked)
- Validation without exposing values
- Safe for screen sharing/debugging

---

## Key Categories & Providers

### AI Providers (5 keys)

| Key Name             | Provider   | Format     | Example         |
| -------------------- | ---------- | ---------- | --------------- |
| `GEMINI_API_KEY`     | Google     | 30+ chars  | AIzaSy...       |
| `OPENAI_API_KEY`     | OpenAI     | sk- prefix | sk-proj-...     |
| `ANTHROPIC_API_KEY`  | Anthropic  | sk- prefix | sk-ant-...      |
| `MISTRAL_API_KEY`    | Mistral    | 32+ chars  | eJydUstuwzAM... |
| `OPENROUTER_API_KEY` | OpenRouter | sk- prefix | sk-or-...       |

**How to Get:**

- **Gemini:** https://makersuite.google.com/app/apikey
- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic:** https://console.anthropic.com/account/keys
- **Mistral:** https://console.mistral.ai/api-keys/
- **OpenRouter:** https://openrouter.ai/keys

---

### GitHub (2 keys)

| Key Name                | Format                   | Usage                |
| ----------------------- | ------------------------ | -------------------- |
| `GITHUB_TOKEN`          | 40+ chars (ghp\_ prefix) | Repo access, CI/CD   |
| `GITHUB_WEBHOOK_SECRET` | 32+ chars                | Webhook verification |

**How to Get:**

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`, `read:user`
4. Copy the token (shown only once!)

---

### OAuth (8 keys)

| Service       | Client ID             | Client Secret             |
| ------------- | --------------------- | ------------------------- |
| **Google**    | `GOOGLE_CLIENT_ID`    | `GOOGLE_CLIENT_SECRET`    |
| **GitHub**    | `GITHUB_OAUTH_ID`     | `GITHUB_OAUTH_SECRET`     |
| **Microsoft** | `MICROSOFT_CLIENT_ID` | `MICROSOFT_CLIENT_SECRET` |
| **Apple**     | `APPLE_CLIENT_ID`     | `APPLE_CLIENT_SECRET`     |

**How to Get:**

- **Google:** https://console.cloud.google.com/apis/credentials
- **GitHub:** https://github.com/settings/oauth-apps
- **Microsoft:** https://entra.microsoft.com/
- **Apple:** https://developer.apple.com/account/resources/identifiers/list

---

### Integrations (7 keys)

| Service         | Key                   | Format            |
| --------------- | --------------------- | ----------------- |
| **Slack**       | `SLACK_API_TOKEN`     | xoxb- prefix      |
| **Notion**      | `NOTION_API_KEY`      | 32+ chars         |
| **HubSpot**     | `HUBSPOT_API_KEY`     | 40+ chars         |
| **Gmail**       | `GMAIL_API_KEY`       | JSON (in .env)    |
| **Nounproject** | `NOUNPROJECT_API_KEY` | alphanumeric      |
| **iCloud**      | `ICLOUD_API_KEY`      | Provider-specific |
| **Twilio**      | `TWILIO_API_KEY`      | alphanumeric      |

---

### Cloud Services (5 keys)

| Service        | Key                     |
| -------------- | ----------------------- |
| OpenAI Org     | `OPENAI_ORG_ID`         |
| Anthropic Org  | `ANTHROPIC_ORG_ID`      |
| AWS Access     | `AWS_ACCESS_KEY_ID`     |
| AWS Secret     | `AWS_SECRET_ACCESS_KEY` |
| Cloud Provider | `CLOUD_PROVIDER_TOKEN`  |

---

## REST API Reference

> For programmatic key management (advanced users)

### Get Configuration Status

```bash
curl http://127.0.0.1:8765/api/v1/config/status
```

**Response:**

```json
{
  "total_keys": 27,
  "keys_set": 5,
  "keys_validated": 4,
  "encryption_enabled": true,
  "by_category": {
    "ai_providers": {
      "total": 5,
      "set": 3,
      "validated": 2,
      "keys": ["GEMINI_API_KEY", "OPENAI_API_KEY", "MISTRAL_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"]
    },
    ...
  }
}
```

### List All Keys (no values)

```bash
curl http://127.0.0.1:8765/api/v1/config/keys
```

### Set a Key

```bash
curl -X POST http://127.0.0.1:8765/api/v1/config/keys/GEMINI_API_KEY \
  -H "Content-Type: application/json" \
  -d '{
    "value": "AIzaSy...",
    "provider": "Google",
    "category": "ai_providers"
  }'
```

### Delete a Key

```bash
curl -X DELETE http://127.0.0.1:8765/api/v1/config/keys/GEMINI_API_KEY
```

### Validate Key Format

```bash
curl -X POST http://127.0.0.1:8765/api/v1/config/validate/GEMINI_API_KEY
```

### Export as .env (Requires Admin Token)

```bash
curl http://127.0.0.1:8765/api/v1/config/export?secret_token=$UDOS_ADMIN_TOKEN
```

---

## File Generation (After Adding Keys)

Once you've added all your keys via the web panel, generate the config files:

```bash
./bin/setup-secrets.sh
```

**What it does:**

1. Reads `.env` file (which you'll populate from the UI)
2. Generates `wizard/config/ai_keys.json`
3. Generates `wizard/config/github_keys.json`
4. Generates `wizard/config/oauth_providers.json`
5. Sets proper file permissions (0o600)

**Output:**

```
✅ wizard/config/ai_keys.json created
✅ wizard/config/github_keys.json created
✅ wizard/config/oauth_providers.json created
✅ File permissions: 0o600 (owner-read-only)
```

---

## Verification Checklist

After adding keys, verify they're working:

### 1. Check File Permissions

```bash
ls -la wizard/config/*_keys.json
```

Should show:

```
-rw------- (0o600) - owner can read/write only
```

### 2. Verify Encryption

```bash
file wizard/config/keys.enc.json
# Should show: "data" (binary encrypted file)
```

### 3. Check Audit Log

```bash
tail -20 wizard/config/keys.audit.log
```

Should show recent key operations:

```
[2026-01-18T10:30:45.123Z] ACTION: SET_KEY | KEY: GEMINI_API_KEY | STATUS: success | PROVIDER: Google
[2026-01-18T10:31:12.456Z] ACTION: GET_KEY | KEY: GEMINI_API_KEY | STATUS: success
[2026-01-18T10:31:45.789Z] ACTION: VALIDATE_KEY | KEY: GEMINI_API_KEY | STATUS: valid
```

### 4. Test with Your Code

```python
import os
from dotenv import load_dotenv

# Load .env (generated by setup-secrets.sh)
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"✅ API key loaded: {api_key[:10]}...")
```

---

## Troubleshooting

### "Port 8765 already in use"

```bash
# Kill existing process
kill $(lsof -ti:8765)

# Or use port manager
./bin/port-manager kill :8765

# Then try again
python wizard/launch_wizard_dev.py --no-tui
```

### "Module 'cryptography' not found"

```bash
# Install encryption library
pip install cryptography

# Verify
python -c "from cryptography.fernet import Fernet; print('✅ OK')"
```

### "keys.enc.json: Permission denied"

```bash
# Fix permissions
chmod 0o600 wizard/config/keys.enc.json
chmod 0o600 wizard/config/keys.audit.log
```

### "UDOS_ENCRYPTION_KEY not set"

```bash
# Generate a new one
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Export to shell
export UDOS_ENCRYPTION_KEY="<generated key>"

# Or add to .env
echo "UDOS_ENCRYPTION_KEY=<generated key>" >> .env
```

### Keys not appearing in UI

1. **Refresh the page** (F5 or Cmd+R)
2. **Check browser console** (F12 → Console tab)
3. **Verify server is running** - Check terminal for errors
4. **Check firewall** - Port 8765 might be blocked

### "Invalid key format" validation error

Different providers have different key formats:

| Provider | Format Rule            | Fix                                         |
| -------- | ---------------------- | ------------------------------------------- |
| OpenAI   | Must start with `sk-`  | Copy full key from dashboard                |
| Gemini   | Must be 30+ characters | Ensure you copied the complete key          |
| GitHub   | Must start with `ghp_` | Use Personal Access Token (not OAuth token) |
| Notion   | Must be 32+ characters | Copy from Notion API page                   |

---

## Security Best Practices

### ✅ DO

- ✅ Use unique, strong API keys for each service
- ✅ Rotate keys regularly (monthly recommended)
- ✅ Keep `.env` file secure (gitignored)
- ✅ Monitor audit logs regularly
- ✅ Use the web panel over editing files manually
- ✅ Enable 2FA on provider accounts
- ✅ Set expiration dates on API keys (if provider supports)

### ❌ DON'T

- ❌ Commit `.env` or `*_keys.json` to git
- ❌ Share API keys in chat or email
- ❌ Paste keys in commit messages or logs
- ❌ Use the same key across environments (dev/prod)
- ❌ Leave old keys in .env after rotation
- ❌ Enable unnecessary scopes/permissions on keys

---

## Advanced Usage

### Programmatic Key Management

```python
from wizard.services.secure_config import SecureConfigManager, KeyCategory

# Initialize manager
config = SecureConfigManager()

# Set a key
config.set_key(
    name="GEMINI_API_KEY",
    value="AIzaSy...",
    category=KeyCategory.AI_PROVIDERS,
    provider="Google"
)

# Get a key (decrypted)
key = config.get_key("GEMINI_API_KEY", decrypt=True)

# List all keys in a category
all_ai_keys = config.get_all_keys(category=KeyCategory.AI_PROVIDERS, include_values=False)

# Export as .env
env_content = config.export_env()
with open(".env", "w") as f:
    f.write(env_content)

# Check status
status = config.get_status()
print(f"Keys set: {status['keys_set']}/{status['total_keys']}")
```

### Audit Log Analysis

```bash
# Find all key sets
grep "ACTION: SET_KEY" wizard/config/keys.audit.log

# Find failed validations
grep "STATUS: invalid" wizard/config/keys.audit.log

# Find recent changes
tail -100 wizard/config/keys.audit.log | grep "SET_KEY\|DELETE_KEY"

# Count keys per provider
grep "PROVIDER:" wizard/config/keys.audit.log | sort | uniq -c
```

### Key Rotation Procedure

```bash
# 1. Generate new key on provider website
# (e.g., OpenAI → Settings → API Keys → Create new)

# 2. In config panel, paste new key and save
# (browser: http://127.0.0.1:8765/api/v1/config/panel)

# 3. Verify new key works in tests
./bin/test-secrets.sh

# 4. Revoke old key on provider website
# (mark for deletion after verification period)

# 5. Check audit log
tail -20 wizard/config/keys.audit.log
```

---

## Integration with CI/CD

### GitHub Actions

Store secrets in GitHub:

```yaml
# .github/workflows/deploy.yml
- name: Use API Keys
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python -c "import os; print(f'Keys loaded: {len(os.environ)}')"
```

### Local Development

```bash
# Load from .env (generated by setup-secrets.sh)
export $(cat .env | grep -v '^#' | xargs)

# Or use python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()"
```

---

## Support & Further Help

**Related Documentation:**

- [SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md) - Detailed setup guide
- [SECURITY-INCIDENT-2026-01-18.md](../SECURITY-INCIDENT-2026-01-18.md) - Incident recovery procedures
- [AGENTS.md](../../AGENTS.md) - Architecture and design principles

**Quick Reference:**

- Config Panel: `http://127.0.0.1:8765/api/v1/config/panel`
- API Docs: `http://127.0.0.1:8765/docs` (debug mode only)
- Setup Script: `./bin/setup-secrets.sh`
- Port Manager: `./bin/port-manager status`

---

_Last Updated: 2026-01-18_  
_Version: 1.0.0 (Stable)_
