# MCP Tools — Vibe Skills Integration (v1.4.4)

**Status:** Integrated (v1.4.4)
**Date:** 2026-02-20

This document supplements [mcp-tools.md](../../wizard/docs/api/tools/mcp-tools.md) with Vibe skill tools exposed through Wizard MCP.

---

## Vibe Skill Tools

### Skill Discovery & Metadata

- `vibe.skill_index`
  - List all available Vibe skills with metadata
  - No parameters
  - Returns: List of skills with name, description, version, action list

- `vibe.skill_contract`
  - Get full contract for a skill (actions, args, returns)
  - Parameters: `skill_name` (string)
  - Returns: Full skill contract definition

### Device Skill

- `vibe.device_list`
  - Enumerate devices with optional filtering
  - Parameters: `filter?` (string), `location?` (string), `status?` (string)
  - Returns: List of devices with metadata

- `vibe.device_status`
  - Check device health and status
  - Parameters: `device_id` (string)
  - Returns: Device status object (online/offline, metrics, etc.)

- `vibe.device_update`
  - Modify device configuration
  - Parameters: `device_id` (string), `config` (dict)
  - Returns: Updated device object

- `vibe.device_add`
  - Register new device
  - Parameters: `name` (string), `location?` (string), `config?` (dict)
  - Returns: Created device object

### Vault Skill

- `vibe.vault_list`
  - Show all vault keys
  - No parameters
  - Returns: List of key names (values redacted)

- `vibe.vault_get`
  - Retrieve secret value
  - Parameters: `key` (string)
  - Returns: Secret object (value redacted for audit)

- `vibe.vault_set`
  - Store or update secret
  - Parameters: `key` (string), `value` (string)
  - Returns: Status object

- `vibe.vault_delete`
  - Remove secret from vault
  - Parameters: `key` (string)
  - Returns: Status object

### Workspace Skill

- `vibe.workspace_list`
  - Enumerate workspaces
  - No parameters
  - Returns: List of workspace objects

- `vibe.workspace_switch`
  - Change active workspace
  - Parameters: `name` (string)
  - Returns: Current workspace object

- `vibe.workspace_create`
  - Create new workspace
  - Parameters: `name` (string), `template?` (string)
  - Returns: Created workspace object

- `vibe.workspace_delete`
  - Remove workspace
  - Parameters: `name` (string)
  - Returns: Status object

### Wizard Skill (Automation)

- `vibe.wizard_list`
  - Show available automations
  - No parameters
  - Returns: List of automation definitions

- `vibe.wizard_start`
  - Launch automation or task
  - Parameters: `project?` (string), `task?` (string), `config?` (dict)
  - Returns: Task object with ID and status

- `vibe.wizard_stop`
  - Halt running automation
  - Parameters: `task_id` (string)
  - Returns: Status object

- `vibe.wizard_status`
  - Check automation status
  - Parameters: `task_id?` (string)
  - Returns: Task status object(s)

### Network Skill

- `vibe.network_scan`
  - Scan network resources
  - No parameters
  - Returns: List of network resources and topology

- `vibe.network_connect`
  - Establish network connection
  - Parameters: `host` (string), `port?` (int), `protocol?` (string)
  - Returns: Connection object

- `vibe.network_check`
  - Diagnose network connectivity
  - Parameters: `host` (string)
  - Returns: Diagnostics object (latency, availability, etc.)

### Script Skill

- `vibe.script_list`
  - Enumerate available scripts
  - No parameters
  - Returns: List of script objects

- `vibe.script_run`
  - Execute script or flow
  - Parameters: `script_name` (string), `args?` (list), `timeout?` (float)
  - Returns: Execution result with output and exit code

- `vibe.script_edit`
  - Modify script content
  - Parameters: `script_name` (string), `content` (string)
  - Returns: Status object

### User Skill

- `vibe.user_list`
  - Enumerate users
  - No parameters
  - Returns: List of user objects (email redacted)

- `vibe.user_add`
  - Create new user
  - Parameters: `username` (string), `email?` (string), `role?` (string)
  - Returns: Created user object

- `vibe.user_remove`
  - Delete user account
  - Parameters: `username` (string)
  - Returns: Status object

- `vibe.user_update`
  - Modify user properties
  - Parameters: `username` (string), `email?`, `role?`, `permissions?` (dict)
  - Returns: Updated user object

### Help Skill

- `vibe.help_commands`
  - Show available commands
  - Parameters: `filter?` (string)
  - Returns: Command reference with usage examples

- `vibe.help_guide`
  - Show guide or tutorial
  - Parameters: `topic` (string)
  - Returns: Guide content

---

## Integration Pattern

### Skill Discovery Flow

```
MCP Client
    │
    ├──→ vibe.skill_index()
    │    ├─ Returns list of 9 skills
    │    └─ Metadata (name, description, version)
    │
    └──→ vibe.skill_contract("device")
         ├─ Returns device skill actions (list, status, update, add)
         ├─ Action arguments (required/optional)
         └─ Return types and schemas
```

### Skill Invocation Pattern

```
MCP Client
    │
    ├──→ vibe.device_list(filter="active", location="Brisbane")
    │    └─ Returns filtered device list
    │
    └──→ vibe.vault_get(key="api_token")
         └─ Returns secret (redacted in responses)
```

---

## Security Notes

- **Secret Redaction:** Vault values returned as "***REDACTED***" in MCP responses
- **Rate Limiting:** MCP rate limits apply to Vibe skill calls (120/min default)
- **Authorization:** Skill access controlled by Wizard auth guards
- **Audit Logging:** All skill invocations logged with correlation IDs

---

## Backend Status

**Current Status:** MCP tools defined; backend service calls pending

The following backends need implementation:

| Skill | Backend Status | Links |
|-------|---|---|
| device | ⏳ Pending | Device DB service |
| vault | ⏳ Pending | Secret store service |
| workspace | ⏳ Pending | Workspace manager |
| wizard | ⏳ Pending | Automation scheduler |
| network | ⏳ Pending | Network diagnostics |
| script | ⏳ Pending | Script runner |
| user | ⏳ Pending | Auth/user service |
| ask | ⏳ Pending | Vibe/OK language model |

---

## Example MCP Requests

### List All Skills

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "vibe_skill_index"
  },
  "id": 1
}
```

### Get Device Skill Contract

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "vibe_skill_contract",
    "arguments": {
      "skill_name": "device"
    }
  },
  "id": 2
}
```

### List Active Devices

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "vibe_device_list",
    "arguments": {
      "filter": "active",
      "location": "Brisbane"
    }
  },
  "id": 3
}
```

### Retrieve Vault Secret

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "vibe_vault_get",
    "arguments": {
      "key": "database_password"
    }
  },
  "id": 4
}
```

---

## References

- **Implementation:** `wizard/mcp/vibe_mcp_integration.py`
- **Integration Guide:** `docs/howto/VIBE-MCP-INTEGRATION.md`
- **Skill Mapper:** `core/services/vibe_skill_mapper.py`
- **MCP Server:** `wizard/mcp/mcp_server.py`
