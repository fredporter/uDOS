# GitHub Secrets & Webhooks Setup Guide for uDOS Wizard v1.3

**Quick Summary:**  
You need to set up GitHub webhook secrets so Wizard can receive GitHub events (push, PR, CI/CD workflows). Same applies to HubSpot API keys.

---

## Part 1: GitHub Webhook Secret Setup

### Step 1: Generate a Secure Secret

Run the secret generator tool:

```bash
python -m wizard.tools.generate_github_secrets
```

**Output:** A 32-character cryptographic secret + setup instructions.

**Save this secret!** You'll need it twice:
1. In GitHub webhook configuration
2. In Wizard dashboard

---

### Step 2: Add Secret to GitHub Repository

1. Go to your GitHub repository
2. Navigate to: **Settings → Webhooks → Add webhook**
3. Fill in:
   - **Payload URL:** `http://localhost:8765/api/github/webhook` (or your Wizard URL)
   - **Content type:** `application/json`
   - **Secret:** Paste the secret from Step 1
   - **Events to trigger:** Select:
     - `Push events`
     - `Pull request events`
     - `Workflow run events`
4. **Make sure "Active" is checked**
5. Click **Add webhook**

---

### Step 3: Save Secret to Wizard

Open Wizard Dashboard: `http://localhost:8765/#config`

Scroll to **"Quick Secret Setup"** section:

1. Find **"GitHub Webhook Secret"** field
2. Paste the secret
3. Click **"Save to Secret Store"**

**OR** use CLI (faster):

```bash
python -m wizard.tools.secret_store_cli set github-webhook-secret "YOUR_SECRET_HERE"
```

Replace `YOUR_SECRET_HERE` with the actual secret.

---

### Step 4: Verify Setup

1. Go to Wizard Dashboard: `http://localhost:8765/#webhooks`
2. Check that GitHub webhook shows: **"Secret configured"** ✅
3. Test from GitHub:
   - Go to your repo: **Settings → Webhooks → Recent Deliveries**
   - Click on a recent delivery
   - Check the Response code: `200` = success

---

## Part 2: HubSpot Integration Setup

### Option A: HubSpot Private App (Recommended)

#### Step 1: Create Private App

1. Visit: https://developers.hubspot.com/apps
2. Click **"Create app"**
3. Enter app name: `uDOS Integration`
4. Click **"Create"**

#### Step 2: Configure Permissions

In the app dashboard, go to **"Scopes"** tab and select:

- `crm.objects.contacts.read` & `write`
- `crm.objects.deals.read` & `write`
- `crm.objects.companies.read` & `write`
- `crm.lists.read` & `write`
- `automation.actions.create` & `execute`

Click **"Save"**

#### Step 3: Get Access Token

1. Go to **"Auth"** tab
2. Under **"Access tokens"**, copy your **"Private App Access Token"**
3. Token format: starts with `pat-` or is a long hex string (20+ chars)

#### Step 4: Save to Wizard

**CLI method (fastest):**

```bash
python -m wizard.tools.secret_store_cli set hubspot_api_key "YOUR_TOKEN_HERE"
```

**OR Dashboard:**

1. Go to `http://localhost:8765/#config`
2. Scroll to **"Quick Keys"** section
3. Find **"HubSpot API Key"** field
4. Paste token
5. Click **"Save"**

#### Step 5: Verify

1. Go to Wizard Dashboard → **Config → HubSpot**
2. Should show: **"API key verified"** ✅

---

### Option B: HubSpot CLI (For advanced users)

```bash
# Install HubSpot CLI
npm install -g @hubspot/cli

# Authenticate (opens browser)
hs init

# Create uDOS integration project
hs get-started

# Start local dev server
hs project dev
```

---

## Part 3: Secret Storage Architecture

### Where Secrets Live

```
┌─────────────────────────────────────┐
│   Wizard Secret Store (Encrypted)   │
│  wizard/security/key_store.py       │
├─────────────────────────────────────┤
│ • github_webhook_secret             │
│ • hubspot_api_key                   │
│ • github_token                      │
│ • mistral_api_key                   │
│ • openrouter_api_key                │
│ + More...                           │
└─────────────────────────────────────┘
         ↓
   (Never in .env or .git)
```

**Important:** Config files like `github_keys.json` and `hubspot_keys.json` store **references only**. Actual secrets live in the encrypted keystore.

---

## Part 4: Troubleshooting

### Problem: "Secret missing" in Webhooks dashboard

**Solution:**
```bash
# Check if secret was saved
python -m wizard.tools.secret_store_cli get github-webhook-secret

# If empty, re-run setup:
python -m wizard.tools.secret_store_cli set github-webhook-secret "YOUR_NEW_SECRET"
```

### Problem: Webhook requests fail with 401/403

**Possible causes:**
1. Secret doesn't match (GitHub secret ≠ Wizard secret)
2. Secret not saved to keystore
3. Wizard server isn't running

**Fix:**
```bash
# Restart Wizard
./bin/Launch-uCODE.command wizard

# Verify webhook status
curl http://localhost:8765/api/webhooks/status
```

### Problem: HubSpot token shows "invalid"

**Possible causes:**
1. Token is expired (rotate it in HubSpot)
2. Token has insufficient permissions (check scopes)
3. Token format incorrect (should start with `pat-` or be 30+ chars)

**Fix:**
1. Go to https://app.hubspot.com/private-apps
2. Regenerate token
3. Save new token to secret store:
```bash
python -m wizard.tools.secret_store_cli set hubspot_api_key "pat-YOUR_NEW_TOKEN"
```

---

## Part 5: Testing Webhooks

### Test GitHub Webhook

```bash
# From your repo after a push or PR, go to:
# GitHub → Settings → Webhooks → Recent Deliveries

# Click on delivery → Response
# Should see 200 with body: {"status": "received"}
```

### Test HubSpot Webhook (once configured)

```bash
# Wizard will sync contacts automatically
# Check sync status:
curl http://localhost:8765/api/hubspot/status

# Expected: {"enabled": true, "last_sync": "2026-02-05T..."}
```

---

## Part 6: Security Best Practices

✅ **DO:**
- Rotate secrets every 90 days
- Use strong webhook secrets (32+ chars)
- Enable webhook signature validation
- Log all webhook events (Wizard does this automatically)
- Restrict GitHub token permissions to minimum needed

❌ **DON'T:**
- Commit secrets to git (they're `.gitignored`)
- Share webhook secrets via email/chat
- Use same secret for multiple platforms
- Store secrets in plain text config files
- Leave webhooks exposed to the internet without HTTPS

---

## Part 7: Command Reference

```bash
# Generate secrets
python -m wizard.tools.generate_github_secrets

# Manage secrets
python -m wizard.tools.secret_store_cli get <key>
python -m wizard.tools.secret_store_cli set <key> <value>
python -m wizard.tools.secret_store_cli list

# Check webhook status
curl http://localhost:8765/api/webhooks/status

# View webhook logs
tail -f memory/logs/unified-wizard-2026-02-*.log | grep webhook

# Restart Wizard
./bin/Launch-uCODE.command wizard
```

---

## References

- **Spec:** [wizard-github-integration.md](../dev/docs/specs/wizard-github-integration.md)
- **Secret Store:** `wizard/security/key_store.py`
- **Webhook Routes:** `wizard/routes/webhook_routes.py`
- **GitHub API:** https://docs.github.com/en/developers/webhooks-and-events
- **HubSpot API:** https://developers.hubspot.com/docs/api/crm/contacts

---

**Last Updated:** 2026-02-05  
**Status:** v1.3 Complete
