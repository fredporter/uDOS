# Wizard Commands

> **Version:** Core v1.1.0.0

Commands for AI assistance, API management, and cloud integrations. These require **Dev Mode** or **Wizard Server**.

---

## OK

Multi-provider AI assistant for generation tasks.

### Syntax

```bash
OK MAKE <type> "<description>"
OK ASK "<question>"
OK STATUS [--providers|--compare]
OK PROVIDER <name>
OK FIX [file]
```

### Make Types

| Type | Description | Output |
| ---- | ----------- | ------ |
| `SEQUENCE` | Interaction diagram | Mermaid |
| `FLOWCHART` | Process flowchart | Mermaid |
| `SVG` | Vector graphic | SVG file |
| `ASCII` | Text art | ASCII |
| `TELETEXT` | Retro 40-col | Teletext |
| `WORKFLOW` | TypeScript workflow | .md file |
| `DOC` | Documentation | Markdown |
| `TEST` | Test cases | Python |

### Examples

```bash
OK MAKE SEQUENCE "user login process"
OK MAKE FLOWCHART "water purification steps"
OK MAKE SVG "fire triangle diagram"
OK MAKE ASCII "camp layout"
OK ASK "how do I use TILE codes?"
OK STATUS
OK STATUS --providers
OK PROVIDER mistral
OK FIX broken_script.py
```

### Provider Priority

1. **Mistral** (FREE - Codestral API)
2. **Claude** (Anthropic)
3. **Vibe CLI** (Offline via Ollama)
4. **Gemini** (Google)
5. **OpenAI** (GPT-4)

---

## AI

AI provider testing and management.

### Syntax

```bash
AI TEST <provider>
AI STATUS
AI PROMPTS
AI KEYS
AI HELP
```

### Examples

```bash
AI TEST mistral       # Test Mistral connection
AI TEST claude        # Test Claude connection
AI STATUS             # Check all providers
AI PROMPTS            # List available prompts
AI KEYS               # Check API key status
```

---

## QUOTA

API quota tracking and management.

### Syntax

```bash
QUOTA [STATUS|<provider>|RESET <provider>|HELP]
```

### Examples

```bash
QUOTA                 # Show all quotas
QUOTA STATUS          # Same as above
QUOTA mistral         # Show Mistral quota
QUOTA RESET mistral   # Reset counter
```

### Display

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

## GMAIL

Email integration via Wizard Server.

### Syntax

```bash
LOGIN GMAIL           # Authenticate
LOGOUT GMAIL          # Disconnect
GMAIL LIST            # List emails
GMAIL READ <id>       # Read email
GMAIL SEND "to" "subject" "body"
GMAIL SYNC            # Force sync
```

### Shortcuts

```bash
EMAIL LIST            # Same as GMAIL LIST
EMAIL READ <id>       # Same as GMAIL READ
SYNC GMAIL            # Same as GMAIL SYNC
```

### Notes

- **Wizard-only**: Requires Realm B or Dev Mode
- Uses OAuth2 authentication
- Emails not cached locally
- Wizard proxies requests, doesn't store data

---

## RESOURCE

AI resource and cost management.

### Syntax

```bash
RESOURCE [HELP|STATUS|ALLOCATE|RELEASE]
```

### Examples

```bash
RESOURCE              # Show resource status
RESOURCE HELP         # Show help
RESOURCE STATUS       # Detailed status
RESOURCE ALLOCATE claude --mission task-123
RESOURCE RELEASE task-123
```

---

## Configuration

### API Keys Setup

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

## Related

- [Wizard Server](../wizard/README.md) - Full wizard docs
- [Dev Mode](../wizard/README.md#dev-mode) - Enable wizard locally
- [CAPTURE](content.md#capture) - Web capture pipeline

---

*Part of the [Command Reference](README.md)*
