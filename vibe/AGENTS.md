# AGENTS.md — Vibe Subsystem

Last Updated: 2026-02-24
Milestone: v1.4.6 Architecture Stabilisation Phase
Status: Stable

---

## Purpose

The `vibe` subsystem integrates Mistral Vibe-CLI with uDOS.

Vibe provides:
- Vibe skill system
- OK Agent interaction layer
- Multi-provider routing
- ucode integration bridge
- Local/cloud provider abstraction

---

## Architecture Rules

### Integration Boundary

Vibe acts as the bridge between:

```
User → Vibe-CLI → OK Provider → ucode → Core
```

Vibe must NOT:
- Bypass ucode command layer
- Duplicate core logic
- Create separate runtime systems
- Override wizard provider logic

### Skills Contract

Each skill must:
- Define clear SKILL.md
- Specify allowed ucode commands
- Document provider requirements
- Provide deterministic routing

---

## Runtime Model

Vibe operates in:
- TUI contexts (via core/tui/ucode.py)
- API contexts (via wizard/routes)
- CLI contexts (via bin/vibe)

Vibe requires:
- Either local logic runtime access (GPT4All) OR cloud credentials
- Skill definitions in vibe/core/skills/
- Valid provider configuration

---

## Provider Routing Rules

Vibe must:
- Check local availability first (if configured)
- Fallback to cloud gracefully
- Log all provider calls
- Respect user's provider preference
- Normalise responses before execution

Provider selection order:
1. Explicit user override (--cloud flag)
2. Primary provider from config
3. Fallback chain
4. Error if none available

---

## Command Execution Priority

Critical: ucode commands must execute BEFORE provider calls.

```python
# Correct flow:
if valid_ucode_command(input):
    execute_ucode(input)
    return  # HARD STOP

# Only if not ucode:
response = call_provider(input)
normalise(response)
execute_if_valid(response)
```

No double execution.
No simultaneous execution.

---

## Testing Requirements

- Mock provider calls
- Test short-circuit logic
- Verify no double responses
- Test fallback chains
- Validate skill routing

---

## Logging Policy

Vibe logs through:

```python
from core.utils.logging_config import get_logger
logger = get_logger("vibe", category="skills")
```

All skill executions must be logged with:
- Skill name
- Action type
- Provider used
- Execution time
- Success/failure

---

## OK Agent Behaviour Constraints

When generating code for vibe:

- Do not bypass ucode execution
- Do not create double response paths
- Do not hardcode provider selection
- Do not override core command handlers
- Respect deterministic-first execution

If command-level logic is needed → use ucode.
If provider logic is needed → route through wizard.

---

## Known Issues (To Be Fixed)

1. Vibe-CLI hanging/blocking (stream not closing properly)
2. Local logic runtime integration failures (timeout/context issues)
3. Double response (ucode + provider both executing)
4. Provider selection not deterministic

See docs/decisions/OK-update-v1-4-6.md for architecture fixes.

---

End of File
