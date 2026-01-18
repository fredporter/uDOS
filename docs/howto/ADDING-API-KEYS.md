# Adding API Keys to uDOS Configuration

**Quick Start:** Edit `~/.uDOS/config/.env` to add your API keys  
**Location:** `http://localhost:8765/api/v1/config/dashboard`

---

## Step 1: Open Configuration Dashboard

```
http://localhost:8765/api/v1/config/dashboard
```

You'll see:

- **📡 API Status** - Shows which APIs are configured (read-only)
- **📝 Config Editor** - Edit configuration files

---

## Step 2: Select .env File

In the "File:" dropdown, select:

```
.env (secrets)
```

This is where you add your API keys.

---

## Step 3: Get Your API Keys

### OpenAI (GPT-4, etc)

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-`)

### Anthropic (Claude)

1. Go to https://console.anthropic.com/
2. Navigate to API Keys
3. Create a key (starts with `sk-ant-`)

### Google (Gemini)

1. Go to https://ai.google.dev/
2. Get your API key from Google Cloud Console
3. Copy the key (starts with `AIza`)

### Mistral AI

1. Go to https://console.mistral.ai/
2. Create an API key
3. Copy the key

### GitHub

1. Go to https://github.com/settings/tokens
2. Create "Personal access token (classic)"
3. Select `repo` scope
4. Copy the token (starts with `ghp_`)

### AWS

1. Go to https://console.aws.amazon.com/iam/
2. Create access key
3. You'll get both Access Key ID and Secret Access Key

---

## Step 4: Paste into .env File

The editor shows your current .env file. Format is:

```
KEY=value
KEY2=value2
```

Add your keys:

```env
# AI Providers
OPENAI_API_KEY=sk-proj-abc123...
ANTHROPIC_API_KEY=sk-ant-def456...
GOOGLE_API_KEY=AIzaSyD...
MISTRAL_API_KEY=xyz789...

# Developer Services
GITHUB_TOKEN=ghp_abc123...

# Cloud Services
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

---

## Step 5: Save and Verify

1. Click **💾 Save** button (or Ctrl+S)
2. You'll see status: "✓ Saved"
3. Go to API Status panel - should show **🟢 CONNECTED** for configured APIs

---

## What Gets Stored Where

```
┌─ Committed to Git ─────────────────────┐
│ wizard.json                            │
│ (features, limits, server settings)    │
└────────────────────────────────────────┘
                ↓
        NEVER COMMIT
┌─ Local Secrets (gitignored) ───────────┐
│ ~/.uDOS/config/.env                    │
│ (API keys, credentials)                │
│                                        │
│ ~/.uDOS/config/.env-local (optional)   │
│ (local development overrides)          │
└────────────────────────────────────────┘
```

---

## API Key Format Examples

### Environment Variable Pattern

All keys follow the pattern:

```
PROVIDER_TYPE_API_KEY=actual-key-value
```

Examples:

```
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
AWS_ACCESS_KEY_ID=AKIA...
```

### Rules

- ✅ No spaces around `=`: `KEY=value`
- ✅ No quotes needed: `KEY=value` not `KEY="value"`
- ❌ Don't include the `$` from GitHub/AWS instructions
- ❌ Don't add extra newlines at the end

---

## Verify Configuration

### In Dashboard

API Status panel shows:

- 🟢 **CONNECTED** - Key found and configured
- 🟡 **PARTIAL** - Key exists but empty
- 🔴 **MISSING** - Key not configured

### In Terminal

```bash
# Check if key exists
grep OPENAI_API_KEY ~/.uDOS/config/.env

# Expected output:
# OPENAI_API_KEY=sk-proj-abc123...
```

---

## Local Development Overrides

Use `.env-local` for testing with different keys:

1. Create `~/.uDOS/config/.env-local`
2. Add override keys:
   ```env
   # Use test key for development
   OPENAI_API_KEY=sk-test-local-...
   DEBUG=true
   ```
3. `.env-local` overrides `.env` automatically

---

## Troubleshooting

### Keys Not Appearing in API Status

**Problem:** Added key but still shows 🔴 MISSING

**Solution:**

1. Verify spelling of KEY name (case-sensitive)
2. Check for spaces around `=`
3. Restart server: `pkill -f uvicorn`
4. Wait 3 seconds, reload dashboard

### Can't Save .env File

**Problem:** Click Save but nothing happens

**Solution:**

1. Check file permissions: `ls -l ~/.uDOS/config/.env`
2. Should be readable/writable: `-rw-------`
3. If not: `chmod 600 ~/.uDOS/config/.env`
4. Try again

### API Key Not Working

**Problem:** Key is configured but API calls fail

**Solution:**

1. Verify key value is complete (no truncation)
2. Check key hasn't expired or been revoked
3. Verify correct key type (e.g., not billing key for API key)
4. Check API rate limits haven't been exceeded
5. Test key manually: `curl -H "Authorization: Bearer ${YOUR_KEY}" https://api.provider.com/v1/test`

---

## Security Notes

- ✅ Never share your `.uDOS/config/.env` file
- ✅ Keep backups of important keys
- ✅ Rotate keys regularly
- ✅ Use minimal permissions for each key
- ✅ Use separate keys for dev/prod
- ✅ Set expiration dates if provider supports it
- ❌ Never paste keys in chat or logs
- ❌ Never commit .env to git

---

## Next Steps

1. ✅ Add API keys to `.env`
2. ✅ Verify in API Status panel
3. 🎯 Use in uDOS commands and workflows
4. 📚 Read specific provider documentation

---

_Configuration Dashboard v1.1.0 - Wizard Server_
