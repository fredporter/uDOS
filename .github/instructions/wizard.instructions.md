# Wizard Subsystem Instructions

> **Scope:** `applyTo: ["wizard/**"]`

---

## Wizard Architecture

**Wizard Server** is the always-on service layer for uDOS.

### Responsibilities

- AI model routing (Ollama + OpenRouter)
- Webhooks and API integrations
- Web scraping and email relay (Gmail)
- Packaging and distribution
- Dev tooling and Agent gateways
- Cloud integration (Wizard ONLY)

### Non-Responsibilities

- ❌ Duplicating Core runtime logic
- ❌ Breaking offline Core assumptions
- ❌ Exposing child devices to web

---

## Model Routing Policy

**See:** [docs/decisions/wizard-model-routing-policy.md](../../docs/decisions/wizard-model-routing-policy.md)

### Default Behavior

- **Local-first:** Devstral Small 2 via Ollama
- **Cloud:** Disabled by default
- **Escalation:** Only when policy allows

### Routing Algorithm

1. Try local (Ollama/Devstral) first
2. Escalate to cloud only when:
   - Task tagged `burst`
   - Local fails twice
   - Policy classification requires cloud capability
3. **Never escalate** if:
   - Task tagged `private`
   - Secrets detected
   - Budget exhausted
   - User disabled cloud

### Task Classification

```python
{
    "task_id": "...",
    "actor": "...",
    "workspace": "core | app | wizard | extensions | docs",
    "intent": "code | test | docs | design | ops",
    "privacy": "private | internal | public",
    "urgency": "low | normal | high"
}
```

---

## AI Provider Integration

### Supported Providers

- **Ollama** (local, default)
- **OpenRouter** (cloud, optional)
- **Anthropic** (via OpenRouter)
- **Google Gemini** (via OpenRouter)
- **Mistral** (via OpenRouter or local)

### Configuration

```python
# wizard/config/ai_keys.json (local-only, gitignored)
{
    "ollama": {
        "endpoint": "http://127.0.0.1:11434",
        "default_model": "devstral-small-2"
    },
    "openrouter": {
        "api_key": "sk-or-...",
        "endpoint": "https://openrouter.ai/api/v1",
        "enabled": false
    }
}
```

---

## Gmail Relay

**Wizard only** — never from Core or user devices.

```python
from wizard.services.gmail_relay import send_email

send_email(
    to="recipient@example.com",
    subject="...",
    body="...",
    from_alias="wizard@udos.local"
)
```

---

## Logging Requirements

### Required Tags

- `[WIZ]` — Wizard operation
- `[GMAIL]` — Gmail relay
- `[LOCAL]` — Local Wizard operation
- `[CLOUD]` — Cloud API call

### Cloud Escalation Logging

**MUST** log every cloud escalation:

```python
logger.info('[CLOUD] Escalated to OpenRouter', extra={
    'task_id': task_id,
    'reason': 'local_failure',
    'model': 'anthropic/claude-3.5-sonnet',
    'estimated_cost': 0.015,
    'privacy_level': 'internal'
})
```

---

## Dev Mode / TUI Interface

**Coming in v1.0.2.0**

Features:
- Wizard Server TUI dashboard
- Real-time model routing status
- Cost tracking display
- Dev mode integration with Core TUI
- Vibe agent interface

---

## Version Management

Current: Wizard v1.1.0.0

Update via:
```bash
python -m core.version bump wizard patch
```

---

## Development

```bash
# Activate venv
source .venv/bin/activate

# Run Wizard Server
python wizard/server.py

# Dev Mode (with API)
./Dev-Mode.command
```

---

## Testing

```bash
# Run tests
pytest wizard/tests/ -v

# Test AI providers
python wizard/tools/test_providers.py
```

---

## Security

- **API keys:** Store in `wizard/config/ai_keys.json` (gitignored)
- **OAuth:** Use `wizard/config/oauth_providers.json` (gitignored)
- **Secrets scanning:** Always enabled before cloud calls
- **Redaction:** Auto-redact detected secrets

---

## File Structure

```
wizard/
├── providers/          # AI provider integrations
├── services/          # Server services
├── config/            # Configuration (gitignored secrets)
├── tools/             # Dev tools
├── tests/             # Test suite
├── server.py          # Main server
└── version.json       # Version metadata
```

---

## References

- [AGENTS.md](../../AGENTS.md)
- [docs/_index.md](../../docs/_index.md)
- [docs/decisions/wizard-model-routing-policy.md](../../docs/decisions/wizard-model-routing-policy.md)
- [wizard/README.md](../../wizard/README.md)

---

*Last Updated: 2026-01-13*
