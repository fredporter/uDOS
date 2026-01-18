# Wizard Server

> **Version:** Wizard v1.0.2.1

The Wizard Server is a dedicated always-on machine in **Realm B** that provides AI services, web access, and cloud integrations while keeping user devices offline-first.

---

## Overview

### Two-Realm Architecture

| Realm | Type | Internet | Description |
| ----- | ---- | -------- | ----------- |
| **A** | User Devices | ❌ No | Tiny Core nodes, desktops, mobiles |
| **B** | Wizard Server | ✅ Yes | Always-on, web-capable, AI pipelines |

### What Wizard Does

- **AI Services**: Mistral, Claude, Gemini, OpenAI, Ollama
- **Web Access**: Web scraping, API calls
- **Gmail Relay**: Email integration
- **Content Capture**: URL-to-markdown pipeline
- **Model Management**: Download and serve local models

### What Wizard Never Does

- Expose child devices to the web
- Store user data in cloud
- Make outbound calls without consent
- Track user activity

---

## Dev Mode

Dev Mode enables Wizard Server capabilities on your development machine.

### Enable Dev Mode

```bash
DEV MODE ON        # Enable wizard features
DEV MODE OFF       # Disable and return to offline
DEV MODE STATUS    # Check current state
DEV MODE HELP      # Show help
```

### What Dev Mode Enables

| Feature | Description |
| ------- | ----------- |
| AI Commands | OK MAKE, OK ASK, AI TEST |
| Web Access | CAPTURE, web scraping |
| Gmail Relay | GMAIL commands |
| API Quotas | QUOTA management |

### Dev Mode Indicators

```
🧙 DEV MODE ACTIVE
Provider: mistral (FREE)
API Keys: 3 configured
```

---

## AI Commands

### OK - AI Assistant

Multi-provider AI assistant for generation tasks.

```bash
# Make things
OK MAKE SEQUENCE "user login process"
OK MAKE FLOWCHART "water purification"
OK MAKE SVG "fire triangle diagram"
OK MAKE ASCII "camp layout"
OK MAKE TELETEXT "survival tips page"

# Ask questions
OK ASK "how do I use TILE codes?"

# Manage providers
OK STATUS
OK STATUS --providers
OK PROVIDER mistral
```

### Provider Priority

1. **Mistral** (FREE - Codestral API)
2. **Claude** (Anthropic)
3. **Vibe CLI** (Offline)
4. **Gemini** (Google)
5. **OpenAI** (GPT-4)

### AI TEST - Provider Testing

```bash
AI TEST mistral       # Test Mistral connection
AI TEST claude        # Test Claude connection
AI TEST STATUS        # Check all providers
AI HELP               # Show AI help
```

---

## QUOTA - API Management

Track and manage AI API quotas.

```bash
QUOTA STATUS          # Show all quotas
QUOTA mistral         # Show specific provider
QUOTA RESET mistral   # Reset quota counter
QUOTA HELP            # Show help
```

### Quota Display

```
╔═══════════════════════════════════════╗
║           API Quota Status            ║
╠═══════════════════════════════════════╣
║ Mistral    ████████░░  80/100  $0.00  ║
║ Claude     ██░░░░░░░░  20/100  $2.40  ║
║ Gemini     █░░░░░░░░░  10/100  $0.50  ║
╚═══════════════════════════════════════╝
```

---

## GMAIL - Email Integration

Gmail relay for notifications and email-based workflows.

### Setup

```bash
LOGIN GMAIL           # Authenticate with Gmail
LOGOUT GMAIL          # Disconnect
```

### Usage

```bash
GMAIL LIST            # List recent emails
GMAIL READ <id>       # Read email content
GMAIL SEND "to" "subject" "body"
GMAIL SYNC            # Force sync
EMAIL LIST            # Shortcut for GMAIL LIST
```

### Notes

- **Wizard-only**: Requires Realm B
- **OAuth2**: Uses secure OAuth flow
- **No storage**: Emails not cached locally
- **Relay only**: Wizard proxies, doesn't store

---

## CAPTURE - Web Pipeline

See [Content Commands - CAPTURE](commands/content.md#capture)

```bash
CAPTURE https://example.com/article
CAPTURE --pipeline recipe https://recipe.com
CAPTURE LIST
CAPTURE PROCESS --all
```

---

## Configuration

### API Keys

Create `wizard/config/ai_keys.json`:

```json
{
  "mistral": "your-mistral-key",
  "anthropic": "your-claude-key",
  "google": "your-gemini-key",
  "openai": "your-openai-key"
}
```

### Cost Tracking

Configure in `wizard/config/ai_costs.json`:

```json
{
  "mistral": {
    "input_per_1k": 0.0,
    "output_per_1k": 0.0
  },
  "claude": {
    "input_per_1k": 0.015,
    "output_per_1k": 0.075
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Wizard Server                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │   AI    │  │  Gmail  │  │   Capture   │ │
│  │ Providers│  │  Relay  │  │  Pipeline   │ │
│  └────┬────┘  └────┬────┘  └──────┬──────┘ │
│       │            │              │         │
│  ┌────┴────────────┴──────────────┴────┐   │
│  │         Private Transports           │   │
│  │    (MeshCore / BT-Private / NFC)     │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │  User Devices   │
          │   (Realm A)     │
          └─────────────────┘
```

---

## Related

- [Transport Policy](../VISION.md#transport-policy)
- [OK Command](commands/wizard.md#ok)
- [CAPTURE Command](commands/content.md#capture)
- [Dev Mode](commands/system.md#dev)
- [Library Credits](../CREDITS.md#-wizard-library-credits) - Wizard library open-source credits

---

*Part of the [uDOS Wiki](README.md)*
