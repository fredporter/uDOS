# SETUP WEBHOOK - Quick Reference Card

## 🎯 Command Cheat Sheet

```bash
# Full interactive setup (GitHub + HubSpot)
SETUP webhook

# GitHub webhooks only
SETUP webhook github

# HubSpot CRM only
SETUP webhook hubspot

# Show comprehensive help
SETUP webhook --help

# View local setup profile (name, location, role)
SETUP --profile

# Start Wizard server (access secrets)
WIZARD
```

---

## 🔄 Interactive Flow

```
START: SETUP webhook
  │
  ├─→ [Show intro & confirm]
  │   └─→ Press ENTER to continue
  │
  ├─→ GitHub Webhook Setup
  │   ├─→ Generate webhook secret
  │   ├─→ Browser opens → GitHub docs
  │   ├─→ You add webhook to repo
  │   ├─→ Press ENTER
  │   └─→ ✅ Secret saved to keystore
  │
  ├─→ HubSpot Setup
  │   ├─→ Browser opens → HubSpot apps
  │   ├─→ You create Private App
  │   ├─→ You get access token
  │   ├─→ Paste token in terminal
  │   └─→ ✅ Token saved to keystore
  │
  └─→ ✅ COMPLETE
      ├─→ Start Wizard: WIZARD
      ├─→ Open dashboard: http://localhost:8765
      └─→ Verify webhooks connected
```

---

## 🐙 GitHub Webhook Setup

### What Gets Created
- **Webhook secret** — Random secure string for signing requests
- **Webhook endpoint** — `http://localhost:8765/api/github/webhook`
- **Events** — Push, Pull requests, Issues

### What You Need
- GitHub account
- Repository with admin access
- (That's it!)

### Verification
```bash
WIZARD                              # Start Wizard
# Open: http://localhost:8765
# Settings → Webhooks
# You should see: ✅ GitHub webhook connected
```

---

## 🎯 HubSpot Setup

### What Gets Created
- **Private App** — OAuth-like app in HubSpot
- **Access Token** — Grants uDOS access to CRM data
- **Scopes** — Contacts, deals, companies, lists, automation

### What You Need
- HubSpot account (free or paid)
- Developer Portal access
- (That's it!)

### Verification
```bash
WIZARD                              # Start Wizard
# Open: http://localhost:8765
# Settings → Integrations → HubSpot
# Click "Sync contacts"
# You should see: ✅ HubSpot API connected
```

---

## 📍 Where Secrets Go

```
After SETUP webhook runs:

Wizard Keystore (Encrypted)
├── github-webhook-secret      ← GitHub webhook signing key
├── hubspot_api_key            ← HubSpot authentication token
└── [other integrations]

Your Machine
├── .env                        ← Local settings (name, location, role)
├── .git                        ← Your code (secrets NOT included)
└── wizard/security/            ← Encrypted keystore (git ignored)

Internet
└── None! Everything stays local after setup
```

---

## ⚡ Quick Start (2 Steps)

### Step 1: Run Setup
```bash
SETUP webhook
```

### Step 2: Verify
```bash
WIZARD                # Start Wizard
# Visit: http://localhost:8765
# Settings → Webhooks → see ✅ Connected
```

Done! Webhooks are ready.

---

## 🛠️ Troubleshooting Flowchart

```
Problem: Setup command not found
  └─→ Solution: Run from uDOS TUI
      $ SETUP webhook

Problem: "Wizard Server Required"
  └─→ Solution: Install Wizard
      $ cd wizard
      $ pip install -r requirements.txt

Problem: Browser won't open
  └─→ Solution: Copy the manual URL shown in terminal
      └─→ Paste in local browser

Problem: Secret not saving
  └─→ Solution 1: Check Wizard installed
      $ ls wizard/server.py
  └─→ Solution 2: Check keystore is accessible
      $ python -m wizard.tools.secret_store_cli status

Problem: Webhook not triggering (GitHub)
  └─→ Solution: Verify in repo settings
      $ Repo → Settings → Webhooks
      $ See 10 most recent deliveries
      $ Check: Payload URL, Secret match

Problem: HubSpot API not connecting
  └─→ Solution: Verify token is valid
      $ Token should start with "pat-"
      $ Check: Private App is installed
      $ Check: Token hasn't expired
```

---

## 📋 Pre-Setup Checklist

- [ ] **GitHub Account** — Have GitHub account? (Optional)
- [ ] **HubSpot Account** — Have HubSpot account? (Optional)
- [ ] **Wizard Installed** — Run: `ls wizard/server.py` returns file path
- [ ] **Internet Connection** — Needed for browser/OAuth
- [ ] **10 minutes** — Rough time for full setup

---

## ✅ Post-Setup Checklist

- [ ] GitHub webhook secret saved (if configured)
- [ ] HubSpot API key saved (if configured)
- [ ] Wizard server can access secrets
- [ ] Browser opens to `localhost:8765`
- [ ] Dashboard shows webhook status

---

## 🔗 Documentation Links

| Need | Link |
|------|------|
| **Full guide** | [SETUP-WEBHOOK-INTERACTIVE.md](SETUP-WEBHOOK-INTERACTIVE.md) |
| **Feature summary** | [SETUP-WEBHOOK-FEATURE-SUMMARY.md](SETUP-WEBHOOK-FEATURE-SUMMARY.md) |
| **Troubleshooting** | [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md) |
| **Technical details** | [PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md](PLUGIN-CATALOG-RENDERER-TROUBLESHOOTING.md) |
| **Wizard architecture** | [../wizard/README.md](../wizard/README.md) |

---

## 💻 Command Reference Table

| Command | Purpose | Example |
|---------|---------|---------|
| `SETUP webhook` | Full setup | `SETUP webhook` |
| `SETUP webhook github` | GitHub only | `SETUP webhook github` |
| `SETUP webhook hubspot` | HubSpot only | `SETUP webhook hubspot` |
| `SETUP webhook --help` | Show help | `SETUP webhook --help` |
| `SETUP --profile` | View settings | `SETUP --profile` |
| `WIZARD` | Start server | `WIZARD` |
| `HELP SETUP` | SETUP help | `HELP SETUP` |

---

## 🎨 UX Philosophy

This feature follows **vibe-cli principles**:

✅ **Tell, don't ask** — "Here's what to do"
✅ **Open URLs automatically** — No copy-pasting
✅ **ENTER to continue** — Natural flow
✅ **No manual config** — Automatic storage
✅ **Verify everything** — Built-in validation

---

## 🚀 What Happens Next?

```
After setup completes:

1. Wizard stores secrets in encrypted keystore
   ↓
2. Your TUI can request tokens via: Wizard API
   ↓
3. Integrations pull from Wizard when needed
   ↓
4. GitHub receives your webhook events
   ↓
5. HubSpot syncs your CRM data
   ↓
✅ Fully automated workflows
```

---

## 🔐 Security Model

```
You                  Wizard              GitHub/HubSpot
  │                   │                       │
  ├─ Run setup ─→     │                       │
  │                   │                       │
  │                ✅ Generate secret        │
  │                   │                       │
  │ ← Show secret ─┤  │                       │
  │                   │                       │
  │ ← Open URL ────────────────────────→ Browser
  │                   │                       │
  │ (You configure)   │                       │
  │                   │                       │
  │ (You paste token) │                       │
  │                   │                       │
  ├─ Paste in TUI ─→  │                       │
  │                ✅ Encrypt & store       │
  │                   │                       │
  │ ← ✅ Complete ─┤  │                       │
  │
  └─ Later: Only Wizard accesses secrets
     (Core TUI cannot see them)
```

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Install Wizard (first time) | 5 min |
| Setup GitHub webhook | 3 min |
| Setup HubSpot | 5 min |
| Full setup (both) | 8 min |
| Verify in Wizard dashboard | 2 min |
| **Total** | **~15 min** |

---

## 🎁 Bonus Features

### Skip Specific Providers
```bash
SETUP webhook github        # Only GitHub, skip HubSpot
SETUP webhook hubspot       # Only HubSpot, skip GitHub
```

### Reconfigure Later
```bash
SETUP webhook               # Run again to update secrets
```

### View Current Config
```bash
SETUP --profile            # Show your local identity
WIZARD                     # Check what's stored in keystore
```

---

## 🆘 Getting Help

1. **In-command help:**
   ```bash
   SETUP webhook --help
   ```

2. **Documentation:**
   - Quick ref: This file
   - Full guide: [SETUP-WEBHOOK-INTERACTIVE.md](SETUP-WEBHOOK-INTERACTIVE.md)
   - Troubleshooting: [GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md)

3. **Check logs:**
   ```bash
   memory/logs/wizard-*.log      # Wizard logs
   memory/logs/setup-*.log       # Setup logs
   ```

---

_Last Updated: February 5, 2026_
_Quick reference for SETUP webhook — vibe-cli interactive setup_
