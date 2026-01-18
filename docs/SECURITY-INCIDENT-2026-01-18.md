# 🔐 Secrets Security Incident & Recovery

**Status:** 🚨 CRITICAL - API Keys Exposed in Git History  
**Date:** 2026-01-18  
**Action:** Immediate Key Rotation Required

---

## What Happened

Live API keys were committed to the repository:

**Exposed Keys:**
- ✗ `GEMINI_API_KEY` (Google) - in `wizard/config/ai_keys.json`
- ✗ `OPENAI_API_KEY` (OpenAI) - sk-proj-xxxx format
- ✗ `MISTRAL_API_KEY` (Mistral)
- ✗ `NOUNPROJECT_API_KEY` & `NOUNPROJECT_API_SECRET`

**Location in Git History:**
- `wizard/config/ai_keys.json`
- `public/wizard/config/ai_keys.json`
- Synced to public repo `uDOS-core`

---

## Immediate Actions (DO NOW)

### 1. Revoke Exposed Keys

**Google Gemini:**
1. Go to: https://aistudio.google.com/apikey
2. Find the exposed key
3. Delete it
4. Create new key and save to `.env`

**OpenAI:**
1. Go to: https://platform.openai.com/account/api-keys
2. Find the exposed key (check creation date = today)
3. Delete/revoke it
4. Create new key and save to `.env`

**Mistral:**
1. Go to: https://console.mistral.ai/api-keys
2. Revoke the exposed key
3. Create new key and save to `.env`

**Noun Project:**
1. Go to: https://nounproject.com/account/api
2. Revoke both API key and secret
3. Create new credentials and save to `.env`

### 2. Set Up Local Secrets (.env)

```bash
# 1. Create .env from template
cp .env.template .env

# 2. Edit with your NEW API keys
nano .env

# 3. Generate config files from .env
./bin/setup-secrets.sh

# 4. Verify configs were created
ls wizard/config/ai_keys.json
ls public/wizard/config/ai_keys.json
```

---

## What's Fixed

### ✅ New Security Model

**Before (INSECURE ❌):**
```
git repo
  ├── wizard/config/ai_keys.json         ← LIVE KEYS IN GIT
  └── public/wizard/config/ai_keys.json  ← EXPOSED TO PUBLIC
```

**After (SECURE ✅):**
```
git repo (committed)
  ├── .env.template                      ← Template only, no secrets
  ├── .gitignore                         ← Excludes all .env files
  └── docs/howto/SECRETS-MANAGEMENT.md   ← Setup guide

Local machine (never committed)
  ├── .env                               ← Your actual keys
  └── wizard/config/ai_keys.json         ← Generated from .env
```

### ✅ Files Changed

**New Files:**
- `.env.template` - Template for all secrets
- `.env.example` - Example format
- `bin/setup-secrets.sh` - Auto-generates configs from .env
- `docs/howto/SECRETS-MANAGEMENT.md` - Comprehensive guide

**Updated Files:**
- `.gitignore` - 62 new secret exclusion patterns
- `wizard/config/` - Removed from git tracking
- `public/wizard/config/` - Removed from git tracking

**Removed from Git:**
- `public/wizard/config/ai_keys.json` (was tracked, now gitignored)

---

## Setup for Development

### Step 1: Create .env
```bash
cp .env.template .env
```

### Step 2: Add Your NEW API Keys
```bash
nano .env
```

Example .env:
```
GEMINI_API_KEY=AIzaSy...     # New key from Google AI Studio
OPENAI_API_KEY=sk-proj-...   # New key from OpenAI
MISTRAL_API_KEY=xxx          # New key from Mistral
GITHUB_TOKEN=ghp_xxx         # Your GitHub PAT
```

### Step 3: Generate Configs
```bash
./bin/setup-secrets.sh
```

Output:
```
✅ Created wizard/config/ai_keys.json
✅ Created public/wizard/config/ai_keys.json
✅ Created wizard/config/github_keys.json
```

### Step 4: Verify
```bash
# Check configs exist
ls -la wizard/config/ai_keys.json
cat wizard/config/ai_keys.json  # Should have YOUR new keys

# Check .env is gitignored
git status  # Should NOT show .env or config/*keys.json
```

---

## For Team Members

**Each team member must:**

1. ✅ Pull latest code (`git pull`)
2. ✅ Copy template: `cp .env.template .env`
3. ✅ Get NEW API keys (see above for each provider)
4. ✅ Edit `.env` with their credentials
5. ✅ Run: `./bin/setup-secrets.sh`
6. ✅ Verify: `ls wizard/config/ai_keys.json`

**What NOT to do:**
- ❌ Never commit `.env` file
- ❌ Never share `.env` file
- ❌ Never put secrets in code
- ❌ Never commit config files with secrets

---

## Preventing This in Future

### ✅ Automated Prevention

GitHub now blocks pushes with detected secrets:

```
remote: error: GH013: Repository rule violations found
remote: - GITHUB PUSH PROTECTION
remote:   Push cannot contain secrets
```

This prevents accidental pushes of new secrets.

### ✅ .gitignore Protection

All `.env` and `*_keys.json` files are now in `.gitignore`:

```bash
# These will NEVER be committed:
.env
.env.local
wizard/config/ai_keys.json
wizard/config/*_keys.json
public/wizard/config/*_keys.json
# ... etc
```

---

## Recovery from Git History

To remove exposed keys from git history (optional, recommended):

### Option 1: Using git-filter-repo (easiest)
```bash
# Install
pip install git-filter-repo

# Remove all key files from history
git filter-repo --invert-paths --path 'wizard/config/ai_keys.json' \
                --path 'public/wizard/config/ai_keys.json'

# Force push (after verification)
git push --force-with-lease origin main
```

### Option 2: Using BFG (faster for large repos)
```bash
# Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
bfg --delete-files "ai_keys.json"
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force-with-lease origin main
```

### Option 3: Manual (for this repo, not recommended)
- Create new repo
- Cherry-pick safe commits only
- Force push (old history discarded)

---

## Monitoring & Audit

### Check for remaining secrets
```bash
# Scan for common secret patterns
git log -p -S "api_key\|OPENAI\|GEMINI\|secret" -- . | head -100

# Scan in entire history
git log --all --source -S "sk-proj" | head -20
```

### GitHub Security Tab
1. Go to: `https://github.com/fredporter/uDOS-dev/security`
2. Check "Secret scanning" results
3. Verify all exposed keys are revoked

---

## Documentation

**See also:**
- `docs/howto/SECRETS-MANAGEMENT.md` - Full guide
- `.env.template` - Template for all secrets
- `bin/setup-secrets.sh` - Auto-generation script
- `.gitignore` - All exclusion patterns

---

## Key Rotation Schedule

Recommend rotating keys on this schedule:

| Key Type | Rotation | Reason |
|----------|----------|--------|
| API Keys (AI, third-party) | **Every 90 days** | Standard security practice |
| GitHub Tokens | **Every 90 days** | Standard security practice |
| OAuth Secrets | **Every 6 months** | Lower risk if rotated less frequently |
| Database Passwords | **Every 180 days** | Follow org policy |

---

## Emergency Key Rotation

If a key is compromised:

1. **Immediately revoke** in provider console
2. **Create new key**
3. **Update .env**: `APIKEY_NAME=new-key-here`
4. **Regenerate configs**: `./bin/setup-secrets.sh`
5. **Test** new key in development
6. **Deploy** new config to production
7. **Monitor** for old key usage (should see errors)

---

**Status:** ✅ Security improvements deployed  
**Next Steps:** Rotate exposed keys (see above)  
**Commit:** d6a1cdf (Pushed to uDOS-dev/main)

_For questions, see SECRETS-MANAGEMENT.md or contact team lead._
