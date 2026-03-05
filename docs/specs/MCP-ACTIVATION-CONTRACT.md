# MCP Activation Contract (Canonical)

Date: 2026-02-23
Owner: Wizard MCP lane

## Objective

Define one deterministic, cross-platform contract for enabling/disabling Wizard MCP in Dev Mode contributor config.

## Canonical Script

- Path: `scripts/mcp_activation.py`
- Invocation: `uv run --project . scripts/mcp_activation.py <command>`
- Commands: `enable`, `disable`, `status`, `contract`

## Config Surface

- Target file: Dev Mode contributor MCP config (managed by setup tooling)
- Managed section boundaries:
  - `# BEGIN UCODE MANAGED MCP (WIZARD)`
  - `# END UCODE MANAGED MCP (WIZARD)`

The activation script owns only this bounded section and must not edit unrelated config.

## Managed MCP Block Requirements

The managed section must define:

- `[[mcp_servers]]`
- `name = "wizard"`
- `transport = "stdio"`
- `command = "uv"`
- `args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]`
- `[mcp_servers.env]` with at least `PYTHONPATH = "."`

## Behavioral Guarantees

- `enable` is idempotent.
- `disable` is idempotent.
- `status` prints only `enabled` or `disabled`.
- `enable` and `disable` create timestamped `.bak-<UTC timestamp>` backups.

## Out of Scope

- This contract does not manage tool/skill paths.
- This contract does not start/stop Wizard services.
- This contract does not mutate non-managed MCP server blocks.
