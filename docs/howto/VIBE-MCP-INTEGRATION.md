# Vibe MCP Integration Guide

**Status:** Integration complete (v1.4.4)
**Date:** 2026-02-20

---

## Overview

Vibe Skills are now integrated with the Wizard MCP (Model Context Protocol) server, exposing Vibe capabilities as MCP tools. This enables:

1. **Unified tool surface:** Vibe skills accessible through Wizard MCP
2. **AI-friendly interface:** Structured MCP tools for model interaction
3. **Extensible skill framework:** New skills can be added without modifying MCP server code
4. **Bidirectional:** uCODE commands + Vibe skills both exposed

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Client (Vibe)                          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                        ┌────────▼──────────┐
                        │ Wizard MCP Server │
                        │  (mcp_server.py)  │
                        └────────┬──────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
        │ Wizard Tools   │ │ uCODE Tools  │ │ Vibe Skills  │
        │ (config, auth) │ │ (dispatch)   │ │ (MCP bridge) │
        └────────────────┘ └──────────────┘ └──────┬───────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │ Vibe Skill Mapper │
                                          │  (Core Service)   │
                                          └───────────────────┘
                                                    │
                            ┌───────────────────────┼───────────────────────┐
                            │                       │                       │
                        ┌───▼────┐ ┌──────┐ ┌──────▼──┐ ┌────┐ ┌────────┐
                        │ Device │ │Vault │ │Workspace│ │User│ │Network │
                        │ Skill  │ │Skill │ │ Skill   │ │...│ │...     │
                        └────────┘ └──────┘ └─────────┘ └────┘ └────────┘
```

---

## Integration Module: `vibe_mcp_integration.py`

### Location

`wizard/mcp/vibe_mcp_integration.py` (~350 lines)

### Key Components

#### 1. VibeMCPIntegration Class

Central integration class that bridges Vibe skills with MCP interface.

```python
class VibeMCPIntegration:
    def __init__(self):
        """Initialize with Vibe skill mapper."""
        self.mapper = get_default_mapper()

    def skill_index(self) -> Dict[str, Any]:
        """Discover all Vibe skills."""

    def skill_contract(self, skill_name: str) -> Dict[str, Any]:
        """Get full skill contract (actions, args, returns)."""

    # Skill action methods:
    def device_list(...) -> Dict[str, Any]
    def device_status(...) -> Dict[str, Any]

    def vault_list(...) -> Dict[str, Any]
    def vault_get(...) -> Dict[str, Any]
    def vault_set(...) -> Dict[str, Any]

    def workspace_list(...) -> Dict[str, Any]
    def workspace_switch(...) -> Dict[str, Any]

    def wizard_list(...) -> Dict[str, Any]
    def wizard_start(...) -> Dict[str, Any]

    # ... and more for network, script, user, help skills
```

#### 2. Tool Registration Function

```python
def register_vibe_mcp_tools(mcp_server) -> None:
    """
    Register all Vibe skill tools with MCP server.

    Creates @mcp_server.tool() decorators for:
    - vibe_skill_index
    - vibe_skill_contract
    - vibe_device_* (list, status, update, add)
    - vibe_vault_* (list, get, set, delete)
    - vibe_workspace_* (list, switch, create, delete)
    - vibe_wizard_* (list, start, stop, status)
    - vibe_network_* (scan, connect, check)
    - vibe_script_* (list, run, edit)
    - vibe_user_* (list, add, remove, update)
    - vibe_help_* (commands, guide)
    """
```

#### 3. Global Accessor

```python
def get_vibe_mcp() -> VibeMCPIntegration:
    """Get or create singleton instance."""
```

---

## MCP Tools Exposed

### Discovery Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_skill_index` | — | List of all skills with metadata |
| `vibe_skill_contract` | `skill_name: str` | Full skill contract (actions, args, returns) |

### Device Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_device_list` | `filter?`, `location?`, `status?` | List of devices |
| `vibe_device_status` | `device_id: str` | Device health info |

### Vault Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_vault_list` | — | List of vault keys |
| `vibe_vault_get` | `key: str` | Secret value (redacted) |
| `vibe_vault_set` | `key: str`, `value: str` | Status |

### Workspace Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_workspace_list` | — | List of workspaces |
| `vibe_workspace_switch` | `name: str` | Current workspace |

### Wizard Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_wizard_list` | — | List of automations |
| `vibe_wizard_start` | `project?`, `task?`, `config?` | Task status |

### Network Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_network_scan` | — | Network resources |

### Script Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_script_list` | — | List of scripts |
| `vibe_script_run` | `script_name: str`, `args?`, `timeout?` | Execution result |

### User Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_user_list` | — | List of users |
| `vibe_user_add` | `username: str`, `email?`, `role?` | User object |

### Help Skill Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `vibe_help_commands` | `filter?` | Command reference |

---

## Integration in mcp_server.py

The Vibe MCP tools are registered in the main Wizard MCP server:

```python
# wizard/mcp/mcp_server.py

# ... existing Wizard tools ...

# ─────────────────────────────────────────────────────────────────────────────
# Vibe Skills MCP Tools Registration
# ─────────────────────────────────────────────────────────────────────────────

try:
    from vibe_mcp_integration import register_vibe_mcp_tools
    register_vibe_mcp_tools(mcp)
except ImportError:
    # Vibe MCP integration is optional
    pass
except Exception:
    # Log but don't fail if Vibe integration has issues
    pass


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## Development: Extending Vibe Skills

### Adding a New Skill

1. **Define skill contract** in `core/services/vibe_skill_mapper.py`:

```python
MY_SKILL = SkillContract(
    name="myskill",
    description="My custom skill",
    actions={
        "action1": SkillAction(
            name="action1",
            description="Do something",
            args=["param1"],
            optional_args=["param2"],
            returns_type="result",
        ),
    },
)

# Register in SKILL_REGISTRY
SKILL_REGISTRY["myskill"] = MY_SKILL
```

2. **Implement action methods** in `wizard/mcp/vibe_mcp_integration.py`:

```python
class VibeMCPIntegration:
    def myskill_action1(self, param1: str, param2: Optional[str] = None) -> Dict[str, Any]:
        """Implement action1."""
        return {
            "status": "success",
            "param1": param1,
            "param2": param2,
        }
```

3. **Register MCP tool** in `register_vibe_mcp_tools()`:

```python
@mcp_server.tool()
def vibe_myskill_action1(param1: str, param2: Optional[str] = None) -> Dict[str, Any]:
    """Do something with myskill."""
    return vibe.myskill_action1(param1, param2)
```

---

## Testing

### Test Vibe MCP Tools

```bash
# Test skill discovery
curl http://localhost:8765/api/vibe/skill/index

# Test skill contract
curl http://localhost:8765/api/vibe/skill/device/contract

# Test via MCP stdio (requires running Wizard MCP server)
echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "vibe_skill_index"}, "id": 1}' | \
  python -m wizard.mcp.mcp_server
```

### Test via Python

```python
from wizard.mcp.vibe_mcp_integration import get_vibe_mcp

vibe = get_vibe_mcp()

# List all skills
print(vibe.skill_index())

# Get device skill contract
print(vibe.skill_contract("device"))

# Call device list (backend pending)
print(vibe.device_list(filter="active"))
```

---

## Backend Integration (Future)

The MCP tools currently return "pending" status. To complete the integration:

1. **Device Skill Backend** — Implement actual device enumeration
2. **Vault Skill Backend** — Integrate with secret storage
3. **Workspace Skill Backend** — Connect to workspace manager
4. **Wizard Skill Backend** — Link to automation scheduler
5. **Network Skill Backend** — Add network diagnostics
6. **Script Skill Backend** — Hook to script runner
7. **User Skill Backend** — Connect to user/auth service
8. **Ask Skill Backend** — Wire to Vibe/OK language model

Each backend would call the actual service to execute the skill action and return real data.

---

## API Reference

### Vibe MCP Request Format

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
  "id": 1
}
```

### Vibe MCP Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    "_meta": {
      "status": "success",
      "message": "Device list",
      "timestamp": "2026-02-20T00:00:00Z"
    },
    "devices": [...],
    "count": 5
  },
  "id": 1
}
```

---

## Configuration

### Environment Variables

```bash
# Optional: Vibe MCP rate limiting (future)
VIBE_MCP_RATE_LIMIT_PER_MIN=120
VIBE_MCP_MIN_INTERVAL_SECONDS=0.05

# Optional: Vibe skill timeouts
VIBE_DEVICE_TIMEOUT_SEC=5.0
VIBE_VAULT_TIMEOUT_SEC=2.0
VIBE_WIZARD_TIMEOUT_SEC=10.0
```

---

## File Structure

```
wizard/
├── mcp/
│   ├── mcp_server.py                    (updated: Vibe registration)
│   ├── vibe_mcp_integration.py           (new: Vibe MCP bridge)
│   ├── gateway.py
│   └── ...
├── docs/
│   └── api/
│       └── tools/
│           └── mcp-tools.md             (update: add Vibe tools)
└── ...

core/
├── services/
│   ├── vibe_skill_mapper.py             (existing: Skill contracts)
│   ├── command_dispatch_service.py      (existing: Dispatch logic)
│   └── ...
└── ...
```

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-02-20 | Complete | Initial Vibe MCP integration |
| 1.1 | TBD | Pending | Backend service integration |
| 1.2 | TBD | Pending | Advanced skill composition |

---

## References

- **MCP Integration Module:** `wizard/mcp/vibe_mcp_integration.py`
- **Skill Mapper:** `core/services/vibe_skill_mapper.py`
- **MCP Server:** `wizard/mcp/mcp_server.py`
- **Vibe Protocol:** `docs/specs/VIBE-UCLI-PROTOCOL-v1.4.4.md`
- **Integration Guide:** `docs/howto/VIBE-UCLI-INTEGRATION-GUIDE.md`

---

## Next Steps

1. **Backend Integration** — Implement actual service calls for each skill
2. **Advanced Features** — Skill composition, chaining, conditional logic
3. **Performance Optimization** — Caching, async execution, batching
4. **Extended Skills** — Add domain-specific skills (gaming, data, etc.)
5. **Security Hardening** — Skill-level authorization, audit logging
