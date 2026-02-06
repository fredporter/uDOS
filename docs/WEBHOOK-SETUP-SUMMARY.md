# Webhook & Integration Setup Summary - uDOS v1.3

**Quick Links:**
- [GitHub Webhooks & HubSpot Setup Guide](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md)
- [Plugin Catalog & Renderer Troubleshooting](PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md)

---

## Your Questions Answered

### 1. GitHub Secrets Setup (for Webhooks)

**What you're seeing:** "Webhook not connected" in Wizard dashboard

**Why:** GitHub webhook secrets aren't configured in Wizard's secret store

**Quick Fix (3 minutes):**

```bash
# Step 1: Generate a secure secret
python -m wizard.tools.generate_github_secrets

# Step 2: Copy the secret it prints (long hex string)

# Step 3: Add to GitHub webhook
# GitHub → Your Repo → Settings → Webhooks → Add webhook
# - Payload URL: http://localhost:8765/api/github/webhook
# - Secret: (paste from Step 1)
# - Events: Push, Pull Request, Workflow Run
# - Active: ✓

# Step 4: Save to Wizard secret store
python -m wizard.tools.secret_store_cli set github-webhook-secret "YOUR_SECRET_FROM_STEP_2"

# Step 5: Verify
# Open Dashboard: http://localhost:8765/#webhooks
# Should show: "Secret configured" ✅
```

**Full Guide:** See [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md)

---

### 2. HubSpot Integration Setup

**What you're seeing:** "HubSpot not connected" in Wizard dashboard

**Why:** HubSpot API key not configured

**Quick Fix (5 minutes):**

```bash
# Step 1: Create HubSpot Private App
# Visit: https://developers.hubspot.com/apps
# Click: "Create app"
# Name: "uDOS Integration"

# Step 2: Configure Permissions
# In app dashboard → Scopes
# Select: contacts (read+write), deals, companies, lists, automation

# Step 3: Get Access Token
# Go to: Auth tab → Access tokens
# Copy: Private App Access Token

# Step 4: Save to Wizard
python -m wizard.tools.secret_store_cli set hubspot_api_key "pat-YOUR_TOKEN"

# Step 5: Verify
# Dashboard → Config → HubSpot
# Should show: "API key verified" ✅
```

**Full Guide:** See [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md) → Part 2

---

### 3. Plugin Catalog Errors (When Wizard Runs)

**What you're seeing:** Plugin catalog showing errors or not loading

**Why:** Discovery service can't scan `library/` directory, or required directories missing

**Quick Fix (2 minutes):**

```bash
# Check if library directory exists
ls -la library/

# If missing:
mkdir -p library themes vault-md vault-md/bank memory/system
chmod 755 library themes vault

# Verify catalog works
curl http://localhost:8765/api/plugins/catalog

# Should return: {"success": true, "total": N, "plugins": {...}}
```

**Full Guide:** See [PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md](PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md)

---

### 4. Renderer Control Plane Errors (When Wizard Runs)

**What you're seeing:** Renderer operations fail or return 500

**Why:** Theme paths missing, or renderer subprocess failed

**Quick Fix (2 minutes):**

```bash
# Ensure directories exist
mkdir -p themes vault

# Check if theme manifest exists
test -f themes/manifest.json || echo "Theme manifest missing"

# Test renderer directly
curl -s http://localhost:8765/api/render/status | jq '.'

# Should show: {"healthy": true, ...}

# If not, check logs:
tail -50 memory/logs/unified-wizard-*.log | grep -i "renderer\|error"
```

**Full Guide:** See [PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md](PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md) → Issue 2, 3, 5

---

## Pre-Startup Checklist

Before running Wizard, ensure:

```bash
✅ Required directories exist
mkdir -p library wizard/config themes vault-md vault-md/bank memory/system

✅ Permissions are correct
chmod 755 library wizard themes vault

✅ Python dependencies installed
pip install -r requirements.txt

✅ Optional: Node dependencies (for dashboard)
cd wizard/dashboard && npm install

✅ Environment clean (no stale lock files)
rm -f wizard/.lock wizard/discovery.lock

✅ Then launch Wizard
./bin/Launch-uCODE.command wizard

✅ Verify both systems started
curl http://localhost:8765/api/system/health
```

---

## Testing Both Systems

```bash
# Test 1: Plugin Catalog
curl -s http://localhost:8765/api/plugins/catalog | jq '.total'
# Should print number > 0

# Test 2: Renderer
curl -s http://localhost:8765/api/render/status | jq '.healthy'
# Should print: true

# Test 3: GitHub Webhook Status
curl -s http://localhost:8765/api/webhooks/status | jq '.webhooks.github'
# Should show: {"url": "...", "secret_configured": true, "secret_source": "secret_store"}

# Test 4: HubSpot Status (after API key setup)
curl -s http://localhost:8765/api/hubspot/status | jq '.'
# Should show: {"enabled": true, ...}
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Wizard Server                        │
│  (http://localhost:8765)                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Plugin Catalog System                           │   │
│  │ /api/plugins/catalog                            │   │
│  │ - Scans library/ directory                      │   │
│  │ - Returns all available plugins                 │   │
│  │ - Status: [See Troubleshooting Guide]           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Renderer Control Plane                          │   │
│  │ /api/render/* endpoints                         │   │
│  │ - Manages theme exports                         │   │
│  │ - Renders missions to static HTML               │   │
│  │ - Status: [See Troubleshooting Guide]           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Webhook Receivers                               │   │
│  │ /api/github/webhook                             │   │
│  │ /api/hubspot/webhook                            │   │
│  │ - Receive GitHub events                         │   │
│  │ - Sync HubSpot contacts                         │   │
│  │ - Secrets in wizard/security/key_store.py       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Secret Store (Encrypted)                        │   │
│  │ wizard/security/key_store.py                    │   │
│  │ - GitHub webhook secrets                        │   │
│  │ - HubSpot API keys                              │   │
│  │ - Never in .git or .env                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## File Locations Reference

| What | Where |
|------|-------|
| GitHub secrets tool | `wizard/tools/generate_github_secrets.py` |
| Secret store CLI | `wizard/tools/secret_store_cli.py` |
| Secrets storage | `wizard/security/key_store.py` |
| Plugin discovery | `wizard/routes/enhanced_plugin_routes.py` |
| Renderer control | `wizard/routes/renderer_routes.py` |
| Webhook endpoints | `wizard/routes/webhook_routes.py` |
| Config management | `wizard/routes/settings_unified.py` |
| Setup wizard | `wizard/routes/setup_routes.py` |
| Logs | `memory/logs/unified-wizard-*.log` |

---

## Next Steps

1. **Generate GitHub secret:** `python -m wizard.tools.generate_github_secrets`
2. **Add to GitHub:** GitHub → Settings → Webhooks
3. **Save to Wizard:** `python -m wizard.tools.secret_store_cli set github-webhook-secret "..."`
4. **Add HubSpot API key:** (same process with `hubspot_api_key`)
5. **Verify:** Open Dashboard → Config → Check statuses
6. **Test webhooks:** GitHub → Settings → Webhooks → Recent Deliveries (should show 200)

---

**Created:** 2026-02-05  
**Status:** v1.3 Complete  
**Audience:** Users setting up Wizard integrations

See also:
- [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md) - Full setup guide
- [PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md](PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md) - Detailed debugging
- [AGENTS.md](AGENTS.md) - Architecture reference
