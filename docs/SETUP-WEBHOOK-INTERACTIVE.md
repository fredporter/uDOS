# SETUP WEBHOOK - Interactive Integration Guide

> **vibe-cli Style UX** — Step-by-step guidance with automatic URL opening and secret storage.

## 🎯 Overview

`SETUP WEBHOOK` provides an interactive, guided experience for configuring GitHub webhooks and HubSpot CRM integration directly from the uDOS TUI.

### Key Features

✅ **Interactive Prompts**
- Step-by-step guidance for each integration
- Clear instructions on what to do
- "Press ENTER to continue" flow

✅ **Automatic URL Opening**
- Browser opens to GitHub/HubSpot configuration pages
- Works in headless environments (shows fallback links)
- No manual copy-pasting of URLs

✅ **Automatic Secret Storage**
- Secrets saved to Wizard's encrypted keystore
- Never stored in `.env` or `.git`
- Works completely offline after setup

✅ **Wizard Integration**
- Seamlessly integrates with Wizard Server
- Secrets available to all Wizard services
- Dashboard shows connection status

---

## 🚀 Quick Start

### Full Setup (GitHub + HubSpot)
```bash
SETUP webhook
```

### GitHub Webhooks Only
```bash
SETUP webhook github
```

### HubSpot CRM Only
```bash
SETUP webhook hubspot
```

### Help
```bash
SETUP webhook --help
```

---

## 📋 Step-by-Step Walkthrough

### Step 1: Start Interactive Setup

```bash
SETUP webhook
```

**Output:**
```
══════════════════════════════════════════════════════════════════
🔗  WEBHOOK SETUP - GitHub & HubSpot Integration
══════════════════════════════════════════════════════════════════

This setup will guide you through connecting:
  1. GitHub webhooks (push, pull request, issues)
  2. HubSpot CRM integration (contacts, deals, automation)

Each integration requires:
  • You create an app/key on the external platform
  • We save the secret to Wizard's encrypted keystore
  • Everything stays local - no data leaves your machine

Press ENTER to continue, or 'n' to skip:
```

### Step 2: GitHub Webhook Setup

If you press ENTER, you'll see:

```
══════════════════════════════════════════════════════════════════
🐙  GITHUB WEBHOOK SETUP
══════════════════════════════════════════════════════════════════

GitHub webhooks allow uDOS to listen for:
  • Repository push events
  • Pull request events
  • Issue creation/updates
  • Code reviews and discussions

Step 1: Generate a secure webhook secret
══════════════════════════════════════════════════════════════════

✅ Generated webhook secret: d7a8f9b2c3e4f...

Step 2: Add webhook to your GitHub repository
══════════════════════════════════════════════════════════════════

We'll open your GitHub repository settings...
  1. Go to your repo
  2. Settings → Webhooks → Add webhook
  3. Use these settings:

  Payload URL:     http://localhost:8765/api/github/webhook
  Content type:    application/json
  Secret:          [Will paste below]
  Events:          Push, Pull requests, Issues

Your GitHub webhooks page:
Press ENTER to open GitHub documentation:
```

**What happens:**
1. A browser window opens to GitHub's webhook documentation
2. You follow the steps to create a new webhook
3. You paste the secret shown above into GitHub settings

Then:

```
Now paste the webhook secret into GitHub settings, then return here.

Press ENTER when you've added the webhook to GitHub:
```

**After you press ENTER:**

```
Step 3: Save secret to Wizard keystore
══════════════════════════════════════════════════════════════════

Saving GitHub webhook secret to encrypted keystore...
✅ GitHub webhook secret saved!
```

### Step 3: HubSpot Setup

Next, you'll see similar prompts for HubSpot:

```
══════════════════════════════════════════════════════════════════
🎯  HUBSPOT CRM SETUP
══════════════════════════════════════════════════════════════════

HubSpot integration allows uDOS to:
  • Sync contacts from your CRM
  • Manage deals and pipelines
  • Automate tasks and workflows
  • Receive webhook notifications

Step 1: Create HubSpot Private App
══════════════════════════════════════════════════════════════════

You'll create a Private App in HubSpot with the following scopes:

  1. crm.objects.contacts.read
  2. crm.objects.contacts.write
  3. crm.objects.deals.read
  4. crm.objects.deals.write
  5. crm.objects.companies.read
  6. crm.lists.read
  7. automation.actions.read

Let's open HubSpot Developer Portal...
Press ENTER to open HubSpot apps:
```

**What happens:**
1. Browser opens to https://developers.hubspot.com/apps
2. You click "Create app"
3. You name it "uDOS"
4. You configure the required scopes
5. You install and get the access token

Then:

```
Step 2: Copy and save your HubSpot API key
══════════════════════════════════════════════════════════════════

Paste your HubSpot API key (pat-xxx format):
(Leave blank to skip)

HubSpot API Key:
```

**You paste the token:**

```
HubSpot API Key: pat-us1-REDACTED

Saving HubSpot API key to Wizard keystore...
✅ HubSpot API key saved!
```

### Step 4: Summary

After both setups:

```
══════════════════════════════════════════════════════════════════
✅  WEBHOOK SETUP COMPLETE
══════════════════════════════════════════════════════════════════

✅ GitHub webhook configured
   • Secrets saved to Wizard keystore
   • Ready to receive repository events

✅ HubSpot integration configured
   • API key saved to Wizard keystore
   • Ready to sync CRM data

══════════════════════════════════════════════════════════════════

Next steps:
  1. Start Wizard server: WIZARD
  2. Open dashboard: http://localhost:8765
  3. Go to Settings → Webhooks
  4. Verify GitHub & HubSpot are 'Connected'

For troubleshooting:
  • See: docs/WEBHOOK-SETUP-SUMMARY.md
  • Detailed guide: docs/GITHUB-WEBHOOKS-HUBSPOT-SETUP.md

══════════════════════════════════════════════════════════════════
```

---

## 🔧 Individual Setup Workflows

### GitHub Webhooks Only

```bash
SETUP webhook github
```

This skips HubSpot and only configures GitHub:

1. Generate webhook secret
2. Open GitHub docs
3. Add webhook to your repo
4. Save secret to Wizard keystore

### HubSpot Only

```bash
SETUP webhook hubspot
```

This skips GitHub and only configures HubSpot:

1. Open HubSpot Developer Portal
2. Create Private App with required scopes
3. Paste access token
4. Save to Wizard keystore

---

## ✅ Verification Checklist

After running `SETUP webhook`:

- [ ] GitHub webhook secret generated
- [ ] GitHub webhook added to your repository
- [ ] HubSpot Private App created (if configured)
- [ ] HubSpot API key copied
- [ ] Secrets saved to Wizard keystore

### Verify Secrets Are Saved

```bash
# Start Wizard server
WIZARD

# Open dashboard
http://localhost:8765

# Check Settings → Webhooks
```

You should see:
- ✅ GitHub webhook connected
- ✅ HubSpot API connected

### Test GitHub Webhook

Make a push to your repository:

```bash
git add .
git commit -m "Test webhook"
git push
```

Wizard should receive the webhook event. Check:
- Wizard dashboard logs
- `/api/github/webhook` endpoint status

### Test HubSpot Integration

In Wizard dashboard:
1. Go to Settings → Integrations → HubSpot
2. Click "Sync contacts"
3. Check if contacts appear in the database

---

## 🛡️ Security & Storage

### Where Are Secrets Stored?

```
Wizard Keystore (Encrypted)
├── github-webhook-secret
├── hubspot_api_key
└── [other OAuth tokens, API keys]

.env (Local, Optional)
├── USER_NAME
├── USER_LOCATION
└── [other non-sensitive settings]
```

### Security Guarantees

✅ **Encrypted**
- All secrets encrypted in Wizard keystore
- Not visible in plaintext on disk

✅ **Local Only**
- Never sent to GitHub/HubSpot except during OAuth flow
- Stored only on your machine

✅ **Version Control Safe**
- Git ignores `wizard/security/*`
- `.env` is not tracked
- No secrets in code repository

✅ **Isolated from Core**
- Core (offline TUI) has NO access to secrets
- Only Wizard Server has keystore access
- Secrets require explicit Wizard authorization

---

## 🐛 Troubleshooting

### "Wizard Server Required"

**Error:**
```
⚠️  Wizard Server Required for Webhook Setup

Webhook integration requires Wizard Server...
```

**Solution:**
1. Navigate to wizard directory: `cd wizard`
2. Install dependencies: `pip install -r requirements.txt`
3. Run setup: `python -m wizard.tools.check_provider_setup`
4. Return to uDOS: `SETUP webhook`

### Browser Won't Open

**In headless environments** (SSH, containers):
- The tool prints a manual URL
- Copy-paste the link into a local browser
- Complete the external app setup
- Return to the terminal and press ENTER

### Secret Not Saving

**Error:**
```
⚠️  Could not save secret. Check Wizard keystore is accessible.
```

**Solutions:**
1. Verify Wizard is installed: `ls wizard/server.py`
2. Check keystore tool: `python -m wizard.tools.secret_store_cli status`
3. Ensure no permission issues: `ls -la wizard/security/`

### GitHub Webhook Not Triggering

**Check:**
1. Wizard server is running: `WIZARD`
2. Webhook is in GitHub settings: `Repo → Settings → Webhooks`
3. Check webhook delivery logs in GitHub
4. Verify payload URL: `http://localhost:8765/api/github/webhook`

See full troubleshooting: [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md)

### HubSpot API Not Connecting

**Check:**
1. API key starts with `pat-`
2. Private App has required scopes
3. Private App is "Installed"
4. Token hasn't expired (create new one if needed)

---

## 📚 Related Documentation

| Topic | File |
|-------|------|
| Quick Reference | [WEBHOOK-SETUP-SUMMARY.md](WEBHOOK-SETUP-SUMMARY.md) |
| Detailed Setup Guide | [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md) |
| Troubleshooting | [PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md](PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md) |
| Wizard Architecture | [../wizard/README.md](../wizard/README.md) |
| GitHub Webhooks Docs | https://docs.github.com/webhooks |
| HubSpot Developer Portal | https://developers.hubspot.com |

---

## 💡 Tips & Tricks

### Skip Prompts (Advanced)

If you want to skip interactive prompts:

```bash
# GitHub only (no HubSpot prompts)
SETUP webhook github

# HubSpot only (no GitHub prompts)
SETUP webhook hubspot
```

### Reconfigure Later

To change secrets later:

```bash
# Full setup again
SETUP webhook

# Or specific provider
SETUP webhook github    # Replace GitHub secret
SETUP webhook hubspot   # Replace HubSpot key
```

### View Current Configuration

```bash
# Show Wizard keystore contents
python -m wizard.tools.secret_store_cli list

# Show setup profile (local .env)
SETUP --profile
```

### Test Without Wizard

You can still use `SETUP` for local identity without webhooks:

```bash
# Local setup only (offline)
SETUP

# View your local profile
SETUP --profile
```

---

## 🎯 Next Steps

1. **Run webhook setup:** `SETUP webhook`
2. **Start Wizard:** `WIZARD`
3. **Open dashboard:** `http://localhost:8765`
4. **Enable integrations:** Settings → Webhooks
5. **Test with actual data:** Make a GitHub push or HubSpot sync

---

## ⚙️ Command Reference

```bash
# Main interactive setup
SETUP webhook

# GitHub webhooks only
SETUP webhook github

# HubSpot CRM only
SETUP webhook hubspot

# Show help
SETUP webhook --help

# Local setup (no webhooks)
SETUP

# View all settings
SETUP --profile

# Edit settings manually
SETUP --edit

# Clear all settings
SETUP --clear
```

---

## 🤝 Support

For issues or questions:
- Check troubleshooting above
- See linked documentation files
- Review Wizard server logs: `memory/logs/wizard-*.log`
- Check GitHub webhook delivery: Repo → Settings → Webhooks

---

_Last Updated: February 5, 2026_
_vibe-cli style interactive setup for GitHub & HubSpot webhooks_
