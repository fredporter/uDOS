# AGENTS.md — Wizard Subsystem

Last Updated: 2026-03-03
Milestone: v1.5 Python Runtime Consolidation
Status: Active

---

## Purpose

The `wizard` subsystem contains extended, networked functionality.

Wizard provides:
- OK Provider integrations (OpenAI, Mistral, Anthropic, etc.)
- Web server (FastAPI)
- API routes
- External service communication
- Cloud provider setup
- MCP server integration

---

## Architecture Rules

### Dependency Permissions

Wizard may use:
- Shared `/.venv` dependencies
- httpx, requests
- FastAPI
- Cloud provider SDKs
- External networking

Wizard must NOT:
- Duplicate core command logic
- Bypass ucode layer
- Create separate logging systems
- Override core configurations improperly

### Separation Boundary

```
wizard/        → Extended, networked
core/          → Minimal, deterministic
```

Wizard extends core but does not replace it.

---

## Runtime Model

Wizard operates as:
- Background service (wizardd)
- API server (FastAPI on port 58008)
- OK Provider gateway
- MCP server
- Shared `uv` + `/.venv` runtime owner for non-stdlib Python dependencies

Wizard requires:
- Internet access (for cloud providers)
- Valid credentials (.env configured)
- Port availability

---

## OK Provider Integration Rules

All OK Providers must:
- Route through wizard/services/ok_gateway.py
- Implement provider abstraction contract
- Normalise responses before execution
- Respect ucode command boundary
- Log provider usage

Provider adapters must be isolated and swappable.

---

## Testing Requirements

- Integration tests for provider adapters
- Mock external API calls in CI
- Route testing for all API endpoints
- No hardcoded credentials in tests

---

## Logging Policy

Wizard logs through:

```python
from core.utils.logging_config import get_logger
logger = get_logger("wizard", category="routes")
```

All provider calls must be logged with correlation IDs.

---

## OK Agent Behaviour Constraints

When generating code for wizard:

- Do not duplicate core command handlers
- Do not bypass provider abstraction
- Do not hardcode API keys
- Do not create direct file manipulation outside ucode
- Respect provider contract
- Use structured logging

If deterministic logic is needed → implement in core.

---

End of File
