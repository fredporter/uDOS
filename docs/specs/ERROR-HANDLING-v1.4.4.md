# Error Handling Contract — v1.4.4

**Status:** Specification Draft
**Target:** All Core command handlers implement this contract
**Version:** v1.4.4

---

## Overview

This document defines the uDOS Core error handling contract. All command handlers, services, and parsers must conform to this structure to ensure consistent error reporting, logging, and recovery guidance.

---

## Error Contract Schema

### Structure

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CommandError(Exception):
    """
    Structured error for user-facing command failures.

    Attributes:
        code: Machine-readable error code (e.g., 'ERR_INVALID_WORKSPACE')
        message: Human-readable error message (1-3 sentences)
        recovery_hint: Optional guidance for user recovery
        details: Optional structured data for logging/debugging
        cause: Optional root cause exception
    """
    code: str
    message: str
    recovery_hint: Optional[str] = None
    details: Optional[dict] = None
    cause: Optional[Exception] = None

    def __str__(self):
        return f"[{self.code}] {self.message}"

    def with_recovery(self, hint: str) -> 'CommandError':
        """Chainable method to add recovery guidance."""
        self.recovery_hint = hint
        return self
```

### Error Code Format

All error codes follow: `ERR_<DOMAIN>_<REASON>`

**Domain:** `WORKSPACE`, `BINDER`, `COMMAND`, `PARSER`, `STATE`, `IO`, `VALIDATION`, `AUTH`, `RUNTIME`, `PROVIDER`

**Examples:**
- `ERR_WORKSPACE_NOT_FOUND`
- `ERR_COMMAND_INVALID_ARG`
- `ERR_PARSER_SYNTAX`
- `ERR_STATE_INVALID_TRANSITION`
- `ERR_IO_FILE_NOT_READABLE`

---

## Error Categories & Handling Patterns

### User Errors (4xx-like)

User provided invalid input or requested invalid operation.

```python
raise CommandError(
    code="ERR_COMMAND_INVALID_SUBCOMMAND",
    message="Unknown subcommand 'foo' for PLACE.",
    recovery_hint="Run 'PLACE --help' to see valid subcommands."
)
```

**Logging Level:** `INFO` (expected user mistakes, not bugs)

### State Errors (4xx-like)

System is in invalid state for requested operation.

```python
raise CommandError(
    code="ERR_STATE_INCOMPATIBLE_TRANSITION",
    message="Cannot transition from PAUSED to LOADING. Only RUNNING -> PAUSED is valid.",
    recovery_hint="Use 'PLAY --status' to check current game state."
)
```

**Logging Level:** `WARNING` (unexpected but recoverable)

### Not Found Errors (404-like)

Requested resource does not exist.

```python
raise CommandError(
    code="ERR_WORKSPACE_NOT_FOUND",
    message="Workspace '@dev' does not exist.",
    recovery_hint="Run 'PLACE --list' to see available workspaces."
)
```

**Logging Level:** `WARNING`

### Service Errors (5xx-like)

Wizard or external dependency failed or unavailable.

```python
raise CommandError(
    code="ERR_PROVIDER_OFFLINE",
    message="AI provider 'ollama' is not responding.",
    recovery_hint="Start Wizard services: `ucli wizard start`. Check status: `HEALTH --verbose`."
)
```

**Logging Level:** `ERROR` (indicates infrastructure issue)

### Validation Errors (4xx-like)

Input failed schema validation.

```python
raise CommandError(
    code="ERR_VALIDATION_SCHEMA",
    message="Frontmatter YAML in 'Readme.md' does not match place schema: missing 'location_id'.",
    recovery_hint="Add 'location_id: L###-CC##' to frontmatter."
)
```

**Logging Level:** `WARNING`

### Parser Errors (4xx-like)

Markdown or command syntax is malformed.

```python
raise CommandError(
    code="ERR_PARSER_SYNTAX",
    message="Markdown tokenizer failed at line 42: unclosed code block.",
    recovery_hint="Check that all ``` blocks are closed properly."
)
```

**Logging Level:** `WARNING`

### System Errors (5xx-like)

Unexpected internal error; should not occur in normal operation.

```python
raise CommandError(
    code="ERR_RUNTIME_UNEXPECTED",
    message="Command executor crashed: null pointer in state machine.",
    recovery_hint="This is a bug. Please report with: `HEALTH --logs` output.",
    cause=original_exception
)
```

**Logging Level:** `ERROR` (always log cause)

---

## Implementation Patterns

### Pattern 1: Simple Validation

```python
def handle_foo(args):
    if not args.name:
        raise CommandError(
            code="ERR_COMMAND_INVALID_ARG",
            message="Argument '--name' is required.",
            recovery_hint="Provide a name: --name=my_workspace"
        )
    return execute_foo(args)
```

### Pattern 2: Conditional State Check

```python
def handle_play_start(args):
    game = get_current_game_state()
    if game.status != GameStatus.IDLE:
        raise CommandError(
            code="ERR_STATE_INCOMPATIBLE_TRANSITION",
            message=f"Cannot start game from {game.status.name} state.",
            recovery_hint="Finish or reset current game first with PLAY --reset."
        )
    return start_game(game, args)
```

### Pattern 3: External Service Check

```python
def handle_health_check(args):
    try:
        provider = get_provider("ollama")
        status = provider.ping()
    except ProviderOfflineError as e:
        raise CommandError(
            code="ERR_PROVIDER_OFFLINE",
            message="AI provider 'ollama' is not responding.",
            recovery_hint="Start Wizard: `ucli wizard start`",
            cause=e
        )
    return format_health_report(status)
```

### Pattern 4: Parser with Recovery

```python
def parse_markdown_doc(content: str):
    try:
        tokens = tokenize(content)
        ast = build_ast(tokens)
        return ast
    except TokenizeError as e:
        line_num = e.line_number
        raise CommandError(
            code="ERR_PARSER_SYNTAX",
            message=f"Markdown tokenizer failed at line {line_num}: {e.reason}",
            recovery_hint=f"Check syntax around line {line_num}. Common issues: unclosed code blocks, missing heading space.",
            cause=e
        )
```

---

## Logging Integration

### Logger Usage

```python
from core.services.logging_manager import get_logger

logger = get_logger(__name__)

def handle_command(args):
    try:
        return _execute(args)
    except CommandError as e:
        # Log with appropriate level
        if e.code.startswith("ERR_COMMAND_") or e.code.startswith("ERR_VALIDATION_"):
            logger.info(f"{e.code}: {e.message}")  # User error = INFO
        else:
            logger.error(f"{e.code}: {e.message}", exc_info=e.cause)  # System error = ERROR
        raise
```

### Logging Checklist

- [ ] Never log sensitive data (paths, auth tokens, credentials) at ERROR level.
- [ ] Log user errors (4xx) at INFO level.
- [ ] Log system errors (5xx) at ERROR level with `exc_info=True`.
- [ ] Include error code in all logs.
- [ ] Include recovery hint in user-facing error responses.

---

## HTTP Status Code Mapping

Used by Wizard routes to set response status.

| Error Code Pattern | HTTP Status | Example |
|---|---|---|
| `ERR_COMMAND_*`, `ERR_VALIDATION_*` | 400 Bad Request | ERR_COMMAND_INVALID_ARG |
| `ERR_STATE_*` | 409 Conflict | ERR_STATE_INCOMPATIBLE_TRANSITION |
| `ERR_*_NOT_FOUND` | 404 Not Found | ERR_WORKSPACE_NOT_FOUND |
| `ERR_AUTH_*` | 401 Unauthorized | ERR_AUTH_DENIED |
| `ERR_PROVIDER_*` | 503 Service Unavailable | ERR_PROVIDER_OFFLINE |
| `ERR_PARSER_*` | 422 Unprocessable Entity | ERR_PARSER_SYNTAX |
| `ERR_RUNTIME_*` | 500 Internal Server Error | ERR_RUNTIME_UNEXPECTED |

---

## Error Code Catalog (Planned)

To be populated during v1.4.4 Phase 1 audit. Format:

| Code | Message Template | Recovery Hint | Category |
|---|---|---|---|
| `ERR_WORKSPACE_NOT_FOUND` | Workspace '@{name}' does not exist. | Run 'PLACE --list' ... | State |
| `ERR_COMMAND_INVALID_ARG` | Argument '--{name}' is required. | Provide: --{name}=value | User |
| (more rows to be added) | ... | ... | ... |

---

## Validation Checklist for v1.4.4

- [ ] All command handlers have error handling.
- [ ] All errors use `CommandError` with proper code.
- [ ] All user-facing errors have recovery hints.
- [ ] No unhandled exceptions escape command layer.
- [ ] All errors logged via `get_logger()` with correct level.
- [ ] Error codes match pattern `ERR_<DOMAIN>_<REASON>`.
- [ ] Sensitive data never logged at ERROR level.
- [ ] HTTP status codes mapped correctly in Wizard routes.
- [ ] Error code catalog completed (95%+ of commands).

---

## References

- [docs/roadmap.md#v1.4.4](../roadmap.md#v144--core-hardening-demo-scripts--educational-distribution)
- [core/services/logging_manager.py](../../core/services/logging_manager.py)
- [core/README.md](../../core/README.md)
