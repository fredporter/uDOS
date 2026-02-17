# Service: ucode

## Purpose
uCODE bridge APIs for command dispatch, metadata, and hotkey/keymap configuration.

## Dispatch Command

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

## Metadata Endpoints

- `GET /api/ucode/allowlist`
- `GET /api/ucode/commands`
- `GET /api/ucode/hotkeys`
- `GET /api/ucode/keymap`
- `POST /api/ucode/keymap`

### `GET /api/ucode/keymap` Response (example)

```json
{
  "status": "ok",
  "active_profile": "mac-obsidian",
  "configured_profile": "mac-obsidian",
  "self_heal": true,
  "configured_self_heal": true,
  "detected_os": "mac",
  "os_override": "auto",
  "available_profiles": [
    "linux-default",
    "mac-obsidian",
    "mac-terminal",
    "windows-default"
  ],
  "available_os_overrides": ["auto", "mac", "linux", "windows"]
}
```

### `POST /api/ucode/keymap` Request (example)

```json
{
  "profile": "mac-obsidian",
  "self_heal": true,
  "os_override": "auto"
}
```

Notes:
- `profile` must be one of `available_profiles`.
- `self_heal` must be boolean.
- `os_override` must be one of `auto|mac|linux|windows`.
- The endpoint updates live env vars and persists Wizard config keys:
  - `ucode_keymap_profile`
  - `ucode_keymap_self_heal`
  - `ucode_keymap_os`

## MCP Tool Mapping

- Tool: `ucode.dispatch`
- Tool: `ucode.help` (sugar for `ucode.dispatch("HELP")`)
- Tool: `ucode.status` (sugar for `ucode.dispatch("STATUS")`)

## Notes

- Early phases must restrict command execution (allowlist only).
- Allowlist is controlled via `UCODE_API_ALLOWLIST` (comma-separated).
- Shell execution is not allowed through this API.
- Dashboard Hotkeys page is the primary UI for keymap settings.
