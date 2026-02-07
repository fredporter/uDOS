# Service: ucode.dispatch

## Purpose
Dispatch uCODE commands via an API bridge for Vibe exploration.

## Request

- Method: `POST`
- Path: `/api/ucode/dispatch`
- Body:

```json
{
  "command": "HELP"
}
```

## Response (example)

```json
{
  "status": "success",
  "message": "...",
  "output": "..."
}
```

## MCP Tool Mapping

- Tool: `ucode.dispatch`
- Tool: `ucode.help` (sugar for `ucode.dispatch("HELP")`)
- Tool: `ucode.status` (sugar for `ucode.dispatch("STATUS")`)

## Notes

- Early phases must restrict command execution (allowlist only).
- Allowlist is controlled via `UCODE_API_ALLOWLIST` (comma-separated).
- Shell execution is not allowed through this API.
