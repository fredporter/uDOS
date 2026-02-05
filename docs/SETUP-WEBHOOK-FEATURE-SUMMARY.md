# SETUP WEBHOOK - Feature Summary

> **New Command:** `SETUP webhook` with vibe-cli interactive UX for GitHub & HubSpot integration.

## 🎉 What's New

A complete interactive webhook setup experience directly from the uDOS TUI:

```bash
SETUP webhook              # Full setup (GitHub + HubSpot)
SETUP webhook github       # GitHub webhooks only
SETUP webhook hubspot      # HubSpot CRM only
SETUP webhook --help       # Show help
```

## ✨ Features

### Interactive Prompts (vibe-cli style)
- **Step-by-step guidance** — Clear instructions for each step
- **Automatic URL opening** — Browser opens GitHub/HubSpot configuration pages
- **Press ENTER to continue** — Intuitive flow, not command syntax
- **No manual config** — Everything automated, no file editing needed

### Automatic Secret Storage
- **Wizard keystore integration** — Secrets encrypted and stored securely
- **Atomic operations** — All-or-nothing setup, no partial states
- **Verification built-in** — Checks before saving

### GitHub Webhooks
```
1. Generate webhook secret (unique for each repo)
2. Browser opens GitHub webhook configuration
3. Paste secret into GitHub settings
4. Wizard saves secret to encrypted keystore
```

### HubSpot CRM
```
1. Browser opens HubSpot Developer Portal
2. Create Private App with required scopes
3. Get access token
4. Paste token into terminal
5. Wizard saves token to encrypted keystore
```

---

## 🚀 Quick Demo

### Full Setup

```bash
$ SETUP webhook
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

**After pressing ENTER:**

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

Your GitHub webhooks page:
Press ENTER to open GitHub documentation:
```

**Browser opens → user configures → returns to terminal:**

```
Now paste the webhook secret into GitHub settings, then return here.

Press ENTER when you've added the webhook to GitHub:

✅ GitHub webhook secret saved!

══════════════════════════════════════════════════════════════════
🎯  HUBSPOT CRM SETUP
══════════════════════════════════════════════════════════════════

[Similar flow for HubSpot...]

✅ HubSpot API key saved!

══════════════════════════════════════════════════════════════════
✅  WEBHOOK SETUP COMPLETE
══════════════════════════════════════════════════════════════════
```

---

## 📦 Implementation Details

### New Files Created

1. **`core/commands/webhook_setup_handler.py`** (280+ lines)
   - Main webhook setup handler
   - GitHub webhook generation and validation
   - HubSpot Private App setup
   - Interactive prompts and URL handling
   - Secret storage integration

2. **`docs/SETUP-WEBHOOK-INTERACTIVE.md`** (comprehensive guide)
   - Full walkthrough with examples
   - Step-by-step instructions for each integration
   - Troubleshooting guide
   - Security explanations

### Modified Files

1. **`core/commands/setup_handler.py`**
   - Added webhook command routing in `handle()` method
   - Updated docstring with webhook options
   - Lines changed: ~5 (new routing logic)

2. **`core/commands/help_handler.py`**
   - Updated SETUP command help entry
   - Added webhook to syntax and usage examples

### Architecture

```
SETUP webhook
    ↓
SetupHandler.handle()
    ↓ (detects "webhook")
WebhookSetupHandler.handle()
    ↓
_run_full_webhook_setup()  or  _setup_github_webhook()  or  _setup_hubspot()
    ↓
Interactive prompts → URL opening → Secret generation → Keystore storage
```

---

## 🔐 Security Model

### Secret Storage
```
Wizard Keystore (Encrypted)
├── github-webhook-secret        [GitHub webhook signing key]
├── hubspot_api_key              [HubSpot authentication token]
└── [other provider credentials]

Never stored in:
  ✗ .env (local settings only)
  ✗ Git repository
  ✗ Configuration files
  ✓ Wizard's secure keystore only
```

### Isolation
- **Core** (offline TUI) — No access to secrets
- **Wizard** (server) — Full keystore access with encryption
- **Integration** — Secrets only passed to external APIs when needed

---

## 📊 Command Reference

### Usage

```bash
# Full webhook setup (both GitHub & HubSpot)
SETUP webhook

# GitHub webhooks only
SETUP webhook github

# HubSpot CRM only
SETUP webhook hubspot

# Show help
SETUP webhook --help

# Check wizard installation
SETUP webhook --help  # Will show "Wizard Required" if not installed
```

### Output Formats

**Success:**
```
{
  "status": "success",
  "output": "═══ ✅  WEBHOOK SETUP COMPLETE ═══"
}
```

**Incomplete Setup:**
```
{
  "status": "warning",
  "output": "⚠️  Wizard Server Required for Webhook Setup"
}
```

---

## ✅ Testing

### Automated Test
```bash
python3 -c "
from core.commands.setup_handler import SetupHandler
handler = SetupHandler()
result = handler.handle('SETUP', ['webhook', '--help'], None, None)
print('✅ SETUP webhook --help works')
"
```

### Manual Test
```bash
# Test help
SETUP webhook --help

# Test GitHub only (requires ENTER input)
# SETUP webhook github

# Test HubSpot only (requires ENTER input)
# SETUP webhook hubspot
```

---

## 🎯 Integration with Existing Commands

### Related Commands

| Command | Purpose |
|---------|---------|
| `SETUP` | Local identity setup (unchanged) |
| `SETUP webhook` | **NEW** — Interactive webhook setup |
| `SETUP --profile` | View current configuration |
| `SETUP --help` | Show all setup options |
| `WIZARD` | Start Wizard server |
| `HELP SETUP` | Show SETUP command help |

### HELP System Updated

```bash
HELP SETUP
```

Now shows:
```
SETUP
  Local setup & webhook configuration (vibe-cli interactive)
  
  Syntax:
    SETUP [webhook|<provider>|--profile|--edit|--clear|--help]
  
  Examples:
    SETUP webhook          # Interactive webhook setup
    SETUP github           # Setup GitHub provider
    SETUP --profile        # View current settings
```

---

## 🔄 Migration Path

### For Existing Users

**Old Way (manual configuration):**
```bash
# Edit docs
# Follow GITHUB-WEBHOOKS-HUBSPOT-SETUP.md
# Run multiple CLI commands
# Edit .env files
python -m wizard.tools.generate_github_secrets
python -m wizard.tools.secret_store_cli set github-webhook-secret "..."
```

**New Way (interactive):**
```bash
SETUP webhook
# Follow prompts
# Automatic URL opening
# Automatic secret storage
```

---

## 📚 Documentation

### Main Documentation
- **[SETUP-WEBHOOK-INTERACTIVE.md](SETUP-WEBHOOK-INTERACTIVE.md)** — Complete guide with examples
- **[WEBHOOK-SETUP-SUMMARY.md](WEBHOOK-SETUP-SUMMARY.md)** — Quick reference
- **[GITHUB-WEBHOOKS-HUBSPOT-SETUP.md](GITHUB-WEBHOOKS-HUBSPOT-SETUP.md)** — Detailed technical guide

### In-Command Help
```bash
SETUP webhook --help        # Comprehensive help
HELP SETUP                  # General SETUP help
```

---

## 🐛 Troubleshooting

### Common Issues

**Q: "Wizard Server Required"**
A: Install Wizard first: `cd wizard && pip install -r requirements.txt`

**Q: Browser won't open**
A: Manual URL shown in terminal, copy-paste into local browser

**Q: Secret not saving**
A: Verify Wizard is installed: `ls wizard/server.py`

**Q: Webhook not triggering**
A: Check GitHub webhook delivery logs in repo settings

See [SETUP-WEBHOOK-INTERACTIVE.md](SETUP-WEBHOOK-INTERACTIVE.md#-troubleshooting) for detailed troubleshooting.

---

## 💡 Design Philosophy

### vibe-cli UX Principles

1. **Tell, don't ask** — "Here's what to do" not "What do you want?"
2. **Open URLs automatically** — No manual copy-pasting
3. **Press ENTER to continue** — Natural, conversational flow
4. **Atomic operations** — All-or-nothing, no partial states
5. **Automatic everything** — Secrets, validation, storage

### Compared to Alternative Approaches

| Approach | vibe-cli SETUP webhook | CLI args | Config file | GUI |
|----------|----------------------|----------|-------------|-----|
| **User Flow** | Interactive prompts | Command-line args | Manual editing | Point & click |
| **URL Opening** | Automatic | Manual | Manual | Automatic |
| **Validation** | Built-in | User required | User required | Built-in |
| **Secret Storage** | Automatic | User runs CLI | Manual edits | Automatic |
| **Works Offline** | Yes (after setup) | Yes | Yes | Requires server |
| **Headless Friendly** | Fallback links | Optimal | Optimal | N/A |

---

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] OAuth flow automation for direct GitHub/HubSpot auth
- [ ] QR code for mobile-based setup (long tokens)
- [ ] Batch setup for multiple integrations
- [ ] Vault migration tool (move secrets between machines)
- [ ] Webhook event simulator for testing
- [ ] Multi-provider orchestration (sync GitHub ↔ HubSpot)

---

## 📝 Summary

**SETUP webhook** transforms webhook configuration from:
> Manual file editing + CLI commands + external documentation

To:
> Interactive guided experience with automatic URL opening and secret storage

Perfect for:
- ✅ First-time users
- ✅ Quick setup workflows
- ✅ Teams with shared machines
- ✅ Automated onboarding
- ✅ Headless environments (with fallback links)

---

_Last Updated: February 5, 2026_
_Part of uDOS v1.3 — vibe-cli integration feature_
