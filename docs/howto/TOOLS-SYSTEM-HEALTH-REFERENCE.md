# Tools: System and Health

Updated: 2026-03-03
Status: active how-to reference

## Scope

Use these tools for health checks, verification, repair, identity, access, and terminal capability checks.

Vibe Dev Mode exposes only the contributor subset from this page:
- `ucode_health`
- `ucode_verify`
- `ucode_repair`
- `ucode_help`
- `ucode_token`

The full TUI also exposes `ucode_uid` and `ucode_viewport`.

## Tools

### `ucode_health`

Check subsystem health and runtime status.

Example calls:
```python
ucode_health(check="")
ucode_health(check="db")
ucode_health(check="wizard")
ucode_health(check="vault")
```

### `ucode_verify`

Verify installation integrity and dependencies.

Example calls:
```python
ucode_verify(target="")
ucode_verify(target="install")
ucode_verify(target="config")
```

### `ucode_repair`

Repair configuration or runtime state.

Example calls:
```python
ucode_repair(action="")
ucode_repair(action="--install")
ucode_repair(action="--config")
ucode_repair(action="--vault")
```

### `ucode_help`

Discover commands by name or topic.

Example calls:
```python
ucode_help(command="")
ucode_help(command="HEALTH")
ucode_help(topic="data")
```

### `ucode_uid`

Show or rotate the device or user UID.

Example calls:
```python
ucode_uid(action="show")
ucode_uid(action="rotate")
```

### `ucode_token`

Manage access tokens.

Example calls:
```python
ucode_token(action="generate")
ucode_token(action="list")
ucode_token(action="generate", name="dev-session")
ucode_token(action="revoke", name="dev-session")
```

### `ucode_viewport`

Report terminal size and capabilities.

Example call:
```python
ucode_viewport()
```

## Common Uses

- check whether the runtime is healthy
- verify install drift before release or repair
- rotate tokens or identity values
- inspect terminal capabilities before rendering rich output
- use the Vibe Dev Mode subset when you need contributor-safe setup and repair operations instead of the full operator surface
