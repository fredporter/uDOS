# uCLI Vibe Protocol Integration Guide

**Status:** Implementation started (v1.4.4)
**Date:** 2026-02-20

---

## Overview

This guide documents how to integrate the three-stage Vibe uCLI protocol into the existing `bin/ucli` script and related components.

---

## Phase 1: Core Services Implementation (✓ Complete)

### Services Created

1. **`core/services/command_dispatch_service.py`** (✓)
   - Three-stage dispatcher: uCODE → Shell → Vibe
   - Stage 1: Command matching with confidence scoring
   - Stage 2: Shell syntax validation with safety checks
   - Stage 3: Vibe skill routing
   - Configuration support
   - Debug mode with detailed tracing

2. **`core/services/vibe_skill_mapper.py`** (✓)
   - Skill contract definitions
   - 9 built-in skills: device, vault, workspace, wizard, ask, network, script, user, help
   - Skill validation and invocation formatting
   - Skill registry and discovery

3. **`core/tests/v1_4_4_command_dispatch_chain_test.py`** (✓)
   - 30+ test cases covering all three stages
   - Latency benchmark tests (<10ms S1, <50ms S2, <500ms S3)
   - Integration tests for full dispatch flow
   - Safety validation tests for shell passthrough

### Running Tests

```bash
# Run dispatch chain tests
pytest core/tests/v1_4_4_command_dispatch_chain_test.py -v

# Run specific test class
pytest core/tests/v1_4_4_command_dispatch_chain_test.py::TestStage1CommandMatching -v

# Run with latency profiling
pytest core/tests/v1_4_4_command_dispatch_chain_test.py::TestDispatchLatency -v
```

---

## Phase 2: bin/ucli Integration (In Progress)

### Integration Points

#### 2A: REPL Input Phase (Primary Entry Point)

**Location:** `bin/ucli` when starting interactive TUI

**Current Implementation:**
```bash
# Direct dispatcher invocation via uCODE
_dispatch_ucode() {
  local command_text="$1"
  # Routes to Wizard API or local dispatch
  ...
}
```

**Updated Implementation:**
Should wire the three-stage dispatcher:

```bash
_dispatch_via_three_stage() {
  local user_input="$1"

  # Route through Python dispatch service
  PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}" python3 - <<'PY' "$user_input"
import sys
from core.services.command_dispatch_service import CommandDispatchService, DispatchConfig

config = DispatchConfig(shell_enabled=True, debug=False)
dispatcher = CommandDispatchService(config)
result = dispatcher.dispatch(sys.argv[1])

# Handle result based on dispatch_to target
dispatch_to = result.get("dispatch_to")

if dispatch_to == "ucode":
    # Execute via existing _dispatch_ucode path
    from core.tui.dispatcher import CommandDispatcher
    exec_result = CommandDispatcher().dispatch(sys.argv[1])
    print(exec_result.get("output") or exec_result.get("rendered") or "")

elif dispatch_to == "shell":
    # Execute via shell (with safety checks already done)
    import subprocess
    subprocess.run(sys.argv[1], shell=True)

elif dispatch_to == "vibe":
    # Route to Vibe skill
    skill = result.get("skill", "ask")
    # Call Wizard Vibe/OK service
    ...
PY
}
```

#### 2B: Command Entry Point (Free-Form Input)

**Location:** `bin/ucli cmd <command>` subcommand

**Current Implementation:**
```bash
cmd)
  _dispatch_ucode "$*"
  ;;
```

**Updated Implementation:**
```bash
cmd)
  _dispatch_via_three_stage "$*"
  ;;
```

#### 2C: Debug Mode Support

**Location:** Add `--dispatch-debug` flag handling

```bash
# Usage: ucli cmd --dispatch-debug "HELP"
# Output includes stage info, confidence scores, latency

if [[ "$user_input" == "--dispatch-debug "* ]]; then
  _dispatch_via_three_stage "$user_input" "debug"
fi
```

---

## Phase 3: Vibe/OK Service Integration (Next Steps)

### Vibe Skill Dispatch Handler

**Location:** `wizard/mcp/mcp_server.py` or new `wizard/routes/vibe_skill_routes.py`

**Implementation Pattern:**

```python
# wizard/routes/vibe_skill_routes.py

def create_vibe_skill_routes(skill_registry):
    """Create API routes for Vibe skills."""
    router = APIRouter(prefix="/api/vibe", tags=["vibe"])

    @router.post("/skill/{skill_name}/{action}")
    async def invoke_skill(
        skill_name: str,
        action: str,
        args: Dict[str, Any],
        token: str = Depends(get_auth_token)
    ):
        """Invoke a Vibe skill action."""
        skill = skill_registry.get_skill(skill_name)
        if not skill:
            raise HTTPException(404, f"Unknown skill: {skill_name}")

        # Validate invocation
        is_valid, err = skill_registry.validate_invocation(skill_name, action, args)
        if not is_valid:
            raise HTTPException(400, err)

        # Execute skill action
        result = await execute_skill_action(skill, action, args, token)
        return result

    return router
```

### Skill Executor

The skill executor would:
1. Look up skill implementation (built-in or extension)
2. Call skill action handler
3. Format response per skill contract
4. Return via Vibe API

---

## Phase 4: Full Integration Checklist

### Code Changes

- [ ] Wire `_dispatch_via_three_stage` into `bin/ucli` REPL input phase
- [ ] Add `--dispatch-debug` flag support to `bin/ucli cmd`
- [ ] Create `wizard/routes/vibe_skill_routes.py` for skill API endpoint
- [ ] Create `wizard/vibe/skill_executor.py` for skill invocation handler
- [ ] Wire skill routes into main Wizard FastAPI app
- [ ] Create built-in skill handlers:
  - [ ] Device skill implementation
  - [ ] Vault skill implementation
  - [ ] Workspace skill implementation
  - [ ] Wizard automation skill implementation
  - [ ] Ask/query skill implementation (delegates to OK/Vibe)

### Testing

- [ ] Unit tests: dispatcher, skill mapper, validators ✓
- [ ] Integration tests: full dispatch flow
- [ ] Safety tests: shell injection attempts, blocklisted commands
- [ ] Latency tests: benchmark dispatch stages
- [ ] E2E tests: Stage 1 → uCODE, Stage 2 → shell, Stage 3 → Vibe

### Documentation

- [ ] Update `bin/ucli --help` with dispatch details
- [ ] Add dispatch debugging guide (`docs/howto/DEBUG-DISPATCH.md`)
- [ ] Add Vibe skill development guide (`docs/howto/VIBE-SKILL-DEVELOPMENT.md`)
- [ ] Add skill contract examples for each built-in skill

### Release

- [ ] Mark v1.4.4 dispatch tasks complete in roadmap
- [ ] Update CHANGELOG with dispatch protocol additions
- [ ] Create migration guide for v1.3.x → v1.4.4 dispatch changes

---

## Testing the Implementation

### 1. Test Stage 1 (uCODE Matching)

```bash
# High confidence exact match
../bin/ucli-dispatch-integration.sh "HELP"
# Expected: Stage 1 → ucode

# Typo with fuzzy matching
../bin/ucli-dispatch-integration.sh "HLEP" --debug
# Expected: Stage 1 → confirm (confidence 0.80+)

# Unknown command
../bin/ucli-dispatch-integration.sh "XYZABC" --debug
# Expected: Stage 3 → vibe (skill: ask)
```

### 2. Test Stage 2 (Shell Passthrough)

```bash
# Safe shell command
../bin/ucli-dispatch-integration.sh "ls -la /tmp" --debug
# Expected: Stage 2 → shell

# Unsafe shell command
../bin/ucli-dispatch-integration.sh "nc localhost 1234" --debug
# Expected: Stage 2 rejected, Stage 3 → vibe
```

### 3. Test Stage 3 (Vibe Fallback)

```bash
# Natural language query
../bin/ucli-dispatch-integration.sh "how do I reset my password?" --debug
# Expected: Stage 3 → vibe (skill: ask)

# Device-related query
../bin/ucli-dispatch-integration.sh "show me all devices" --debug
# Expected: Stage 3 → vibe (skill: device)
```

### 4. Run Full Test Suite

```bash
cd /Users/fredbook/Code/uDOS
pytest core/tests/v1_4_4_command_dispatch_chain_test.py -v --tb=short
```

---

## Integration Checkpoints

### Checkpoint 1: Dispatcher Services (✓ 2026-02-20)
- [x] Core dispatcher created
- [x] Skill mapper created
- [x] Test suite created (_30+ tests_)
- [x] Protocol spec documented

### Checkpoint 2: bin/ucli Wiring (In Progress)
- [ ] REPL dispatch integration
- [ ] Debug mode integration
- [ ] Confidence confirmation flow
- [ ] Error handling

### Checkpoint 3: Vibe Skill API (Pending)
- [ ] Skill routes created
- [ ] Skill executor created
- [ ] Built-in skills implemented
- [ ] Skill discovery endpoint

### Checkpoint 4: Testing & Release (Pending)
- [ ] Full test coverage
- [ ] Performance benchmarks
- [ ] Documentation complete
- [ ] Roadmap marked complete

---

## References

- Protocol Spec: [VIBE-UCLI-PROTOCOL-v1.4.4.md](../specs/VIBE-UCLI-PROTOCOL-v1.4.4.md)
- Dispatcher Service: [command_dispatch_service.py](../core/services/command_dispatch_service.py)
- Skill Mapper: [vibe_skill_mapper.py](../core/services/vibe_skill_mapper.py)
- Test Suite: [v1_4_4_command_dispatch_chain_test.py](../core/tests/v1_4_4_command_dispatch_chain_test.py)
- Roadmap: [roadmap.md](../roadmap.md) (v1.4.4 section)

---

## Notes

- **No shims:** Input is reformatted on-the-fly, not aliased or proxied
- **Vibe skills are discoverable:** Each skill exports a full contract
- **Shell sandbox is strict:** Only explicitly safe commands allowed
- **Latency visibility:** `--dispatch-debug` shows timing for each stage
- **Extensible:** New Vibe skills can be added without modifying dispatcher

---

## Version History

| Version | Date       | Status              | Notes                            |
|---------|------------|---------------------|----------------------------------|
| 1.0     | 2026-02-20 | Initial Draft       | Core services implementation     |
| 1.1     | TBD        | Integration Phase   | bin/ucli wiring + Vibe API      |
| 1.2     | TBD        | Testing             | Full test coverage + benchmarks |
| 1.3     | TBD        | Release             | v1.4.4 stable release           |
