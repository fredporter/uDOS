# Vibe uCLI Protocol — v1.4.4

**Status:** Implemented (v1.4.4 Round 4 Complete)

**Version:** v1.4.4
**Last updated:** 2026-02-20

---

## Overview

The **Vibe uCLI Protocol** maps uCLI command input directly to Vibe skills without shims or compatibility layers. This protocol enables:

1. **No-shim reformatting:** uCLI input → Vibe skill invocation (direct translation)
2. **Skill mapping:** Command category → Vibe skill namespace
3. **Three-stage dispatch:** uCODE commands → Shell passthrough → Vibe fallback

---

## Protocol Architecture

### Stage 1: uCODE Command Matching

**Purpose:** Identify canonical uDOS commands with high confidence.

**Registry:** Authoritative list from `core/tui/dispatcher.py`

```
P0 Commands (40+):
  HELP, HEALTH, VERIFY, PLACE, BINDER, DRAW, RUN, PLAY, RULE, LIBRARY
  MAP, ANCHOR, GRID, PANEL, GOTO, FIND, TELL, BAG, GRAB, SPAWN
  SAVE, LOAD, CONFIG, WIZARD, EMPIRE, SONIC, MUSIC, FILE, TALK, THEME
  SKIN, VIEWPORT, SCHEDULER, SCRIPT, USER, REBOOT, SETUP, REPAIR, DESTROY, LOG
  MIGRATE, UID, TOKEN, GHOST, READ, UNDO, COMPOST, CLEAN, DEV, NPC
```

**Matching Algorithm:**

1. Tokenize input: `words = input.strip().split(None, 1)`
2. Extract command: `cmd = words[0].upper()`
3. Check registry: Is `cmd` in `UCODE_COMMANDS`?
4. Calculate confidence:
   - **0.95+** → Exact match (command found, no ambiguity)
   - **0.80-0.95** → Fuzzy match (Levenshtein distance < 2)
   - **<0.80** → No match (proceed to Stage 2)

**Dispatch Decision:**

- Confidence ≥ 0.95: Execute immediately
- Confidence 0.80–0.95: Prompt user for confirmation
- Confidence < 0.80: Proceed to Stage 2

---

### Stage 2: Shell Passthrough

**Purpose:** Route valid shell syntax safely when no uCODE match exists.

**Safety Checks:**

1. **Syntax validation:** Ensure input is valid shell syntax (bash/sh)
2. **Allowlist check:** Permit only safe commands (e.g., `ls`, `cat`, `echo`, `grep`)
3. **Blocklist check:** Reject dangerous patterns:
   - Command injection: `` ` ``, `$(...)`, `|`
   - Exfiltration: `nc`, `curl`, `wget`
   - Privilege escalation: `sudo`, `su`
   - Filesystem abuse: `rm -rf /`, `chmod 000 /`

**Execution:**

- If safe and enabled: Execute via shell
- If unsafe or disabled: Proceed to Stage 3

---

### Stage 3: Vibe Fallback (Skill Routing)

**Purpose:** Route uncertain input to Vibe skills for AI-assisted handling.

**Skill Mapping:**

| **uCLI Category**       | **Vibe Skill**        | **Example Input**               | **Vibe Invocation**            |
|------------------------|----------------------|--------------------------------|-------------------------------|
| Device/System          | `device`             | `device list --active`         | `vibe device list --active`    |
| Vault/Secrets          | `vault`              | `vault get api_token`          | `vibe vault get api_token`     |
| Workspace              | `workspace`          | `workspace switch dev`         | `vibe workspace switch dev`    |
| Wizard/Automation      | `wizard`             | `wizard start --project xyz`   | `vibe wizard start --project xyz` |
| Network                | `network`            | `network scan`                 | `vibe network scan`            |
| Scripting              | `script`             | `script run myflow`            | `vibe script run myflow`       |
| User Management        | `user`               | `user add alice`               | `vibe user add alice`          |
| Help/Documentation     | `help`               | `help commands`                | `vibe help commands`           |
| General Query          | `ask`                | `what's my current status`     | `vibe ask what's my current status` |

**Vibe Invocation Format:**

```bash
vibe <skill> [args...] [--param value ...]
```

**Example Flows:**

```bash
# Stage 1 Match (0.95+ confidence)
$ ucli HELP
→ Executes immediately via uCODE handler

# Stage 1 Fuzzy Match (0.80-0.95, asks user)
$ ucli HLEP
→ "Did you mean HELP? (y/n/skip)"

# Stage 2 Shell Passthrough (no uCODE match, valid shell)
$ ucli ls -la
→ Executes via shell (if enabled and safe)

# Stage 3 Vibe Fallback (no uCODE/shell, AI handling)
$ ucli how do I update my profile
→ Routes to `vibe ask how do I update my profile`
```

---

## Skill Contracts

### Device Skill

**Invocation:**
```bash
vibe device <action> [--filter value] [--location value]
```

**Actions:**
- `list` — Enumerate devices
- `status` — Check device health
- `update` — Modify device config
- `add` — Register new device

**Returns:**
```json
{
  "status": "success",
  "devices": [
    { "id": "d1", "name": "laptop", "location": "brisbane", "status": "online" }
  ],
  "count": 1
}
```

---

### Vault Skill

**Invocation:**
```bash
vibe vault <action> --key <name> [--value value]
```

**Actions:**
- `list` — Show all vault keys
- `get` — Retrieve secret
- `set` — Store secret
- `delete` — Remove secret

**Returns:**
```json
{
  "status": "success",
  "key": "api_token",
  "value": "***" // redacted in transit
}
```

---

### Workspace Skill

**Invocation:**
```bash
vibe workspace <action> [--name name]
```

**Actions:**
- `list` — Show workspaces
- `switch` — Change workspace
- `create` — New workspace
- `delete` — Remove workspace

---

### Wizard Skill

**Invocation:**
```bash
vibe wizard <action> [--project name]
```

**Actions:**
- `start` — Launch automation
- `stop` — Halt automation
- `status` — Check running tasks
- `list` — Show available automations

---

### Ask Skill (General Query)

**Invocation:**
```bash
vibe ask <question>
```

**Behavior:**
- Routes natural language queries to Vibe/OK service
- Uses local Mistral model or cloud fallback
- No command structure required

**Returns:**
```json
{
  "status": "success",
  "response": "Your current status is...",
  "source": "local" | "cloud"
}
```

---

## Three-Stage Dispatch Flow (Pseudocode)

```python
def dispatch_input(user_input: str, conf: Config) -> Dict[str, Any]:
    """
    Three-stage dispatch chain.

    Stage 1: uCODE command matching (high confidence)
    Stage 2: Shell passthrough (syntax safe)
    Stage 3: Vibe fallback (AI handling)
    """
    logger = get_logger(__name__)
    debug = "--dispatch-debug" in user_input

    if debug:
        actual_input = user_input.replace("--dispatch-debug ", "", 1)
    else:
        actual_input = user_input

    # ─────────────────────────────────────────────────────────────────────
    # STAGE 1: uCODE Command Matching
    # ─────────────────────────────────────────────────────────────────────

    logger.debug("STAGE 1: Attempting uCODE command match")
    command, confidence = match_ucode_command(actual_input)

    if debug:
        logger.info(f"  → Match: {command}, confidence: {confidence:.1%}")

    if confidence >= 0.95:
        logger.debug("  → High confidence, executing uCODE")
        result = execute_ucode_command(command, actual_input)
        if debug:
            logger.info(f"  → Result: {result.get('status')}")
        return result

    if confidence >= 0.80:
        logger.debug("  → Medium confidence, ask user")
        choice = ask_user(f"Did you mean: {command}? (y/n/skip)")
        if choice == "y":
            result = execute_ucode_command(command, actual_input)
            if debug:
                logger.info(f"  → Result: {result.get('status')}")
            return result
        elif choice == "skip":
            # Continue to Stage 2
            pass
        else:
            # User said no, stop here
            return {"status": "cancelled", "message": "Command cancelled"}

    # ─────────────────────────────────────────────────────────────────────
    # STAGE 2: Shell Passthrough
    # ─────────────────────────────────────────────────────────────────────

    if conf.shell_enabled:
        logger.debug("STAGE 2: Attempting shell validation")
        is_safe, reason = validate_shell_syntax(actual_input, conf)

        if debug:
            logger.info(f"  → Syntax check: {reason}")

        if is_safe:
            logger.debug("  → Safe shell command, executing")
            result = execute_shell_command(actual_input)
            if debug:
                logger.info(f"  → Execution complete")
            return result

    # ─────────────────────────────────────────────────────────────────────
    # STAGE 3: Vibe Fallback
    # ─────────────────────────────────────────────────────────────────────

    logger.debug("STAGE 3: Routing to Vibe skill")
    skill = infer_vibe_skill(actual_input)
    if debug:
        logger.info(f"  → Inferred skill: {skill}")

    result = route_to_vibe_skill(skill, actual_input)
    if debug:
        logger.info(f"  → Vibe response: {result.get('status')}")

    return result
```

---

## Dispatch Metrics & Latency Budget

**Expected Latency:**

| **Stage** | **Latency Budget** | **Notes**                                 |
|-----------|------------------|------------------------------------------|
| Stage 1   | < 10 ms          | Tokenization + registry lookup            |
| Stage 2   | < 50 ms          | Syntax validation + safety checks         |
| Stage 3   | < 500 ms         | Vibe lookup (fast) + Vibe/OK inference    |
| **Total** | **< 560 ms**     | User should see result in <1s typical     |

**Optimization Tactics:**

- Cache Stage 1 matches across command invocation batches
- Parallelize Stage 2/3 checks when Stage 1 confidence < 0.80
- Use dispatch debug mode (`--dispatch-debug`) for latency profiling

---

## Integration Points

### bin/ucli

**Current:** Routes input to uCODE dispatcher via Wizard API or local dispatch

**Updated:** Wire three-stage dispatcher at REPL input phase

```bash
# bin/ucli (dispatch entry point)
_dispatch_input() {
  local user_input="$1"
  PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}" python3 - <<'PY' "$user_input"
import sys
from core.services.command_dispatch_service import dispatch_input
from core.config.config import load_config

config = load_config()
result = dispatch_input(sys.argv[1], config)
# Render result
print(result.get("rendered") or result.get("output") or "")
PY
}
```

### Vibe Skill Handler

**Location:** `wizard/mcp/mcp_server.py` (MCP tool interface)

**Skill Registration:** Each Vibe skill is auto-discovered from `wizard/vibe/skills/` directory

```python
# wizard/vibe/skills/device.py
class DeviceSkill:
    """Device management skill."""

    def list(self, filter: str = None, location: str = None) -> Dict:
        """List devices matching filter."""
        ...
```

---

## Implementation Checklist

- [x] Create `core/services/command_dispatch_service.py` (three-stage dispatcher)
- [x] Create `core/services/shell_validation_service.py` (safety checks)
- [x] Create `core/services/vibe_skill_mapper.py` (skill inference + routing)
- [x] Update `bin/ucli` to wire dispatcher at REPL input phase
- [x] Add `--dispatch-debug` flag support for diagnostics
- [x] Create comprehensive test suite:
  - [x] Stage 1: 20+ command matching & confidence tests
  - [x] Stage 2: Shell validation (safe/unsafe) tests
  - [x] Stage 3: Vibe skill routing tests
  - [x] Integration: End-to-end dispatch scenarios
- [x] Add latency benchmarks and regression alerts
- [x] Document Vibe skill contract for community extensions

---

## Examples

### Example 1: High-Confidence uCODE Match

```
Input:  HELP
Stage 1: HELP (confidence: 1.0)
Action: Execute immediately
Output: [uCODE help text]
```

### Example 2: Fuzzy Command Match

```
Input:  HLEP
Stage 1: HELP (confidence: 0.86)
User:   Did you mean HELP? (y/n/skip)
Choice: y
Action: Execute HELP
Output: [uCODE help text]
```

### Example 3: Shell Passthrough

```
Input:  ls -la /tmp
Stage 1: No match (confidence: 0.0)
Stage 2: Syntax validation passes, safe command
Action: Execute via shell
Output: [directory listing]
```

### Example 4: Vibe Fallback

```
Input:  how do I reset my password?
Stage 1: No match (confidence: 0.0)
Stage 2: Not shell syntax
Stage 3: Inferred skill: "ask"
Action: Route to Vibe ask skill
Output: [Vibe/OK response]
```

### Example 5: Dispatch Debug Mode

```
Input:  --dispatch-debug PLACE list
Output:
  [STAGE 1] Match: PLACE, confidence: 1.0
  [STAGE 1] High confidence, executing uCODE
  [STAGE 1] Result: success
  [Output] [place list results]
```

---

## Notes

- **No backwards-compat shims:** Input is reformatted on-the-fly, not aliased
- **Vibe skills are discoverable:** Each skill exports a contract (name, actions, args, returns)
- **Shell sandbox:** Stage 2 uses a strict allowlist; dangerous patterns are always rejected
- **Latency visibility:** `--dispatch-debug` shows where time is spent across stages
- **Extensible:** New Vibe skills can be added without modifying dispatcher logic

---

## References

- [uCLI Command Contract v1.3.20](uCLI-COMMAND-DISPATCH-v1.4.4.md)
- [Vibe Skill Architecture](../decisions/vibe-spec-v1-4.md)
- [Shell Safety Policy](shell_safety_policy.md)
