# Wizard MCP Gateway

This directory hosts the MCP gateway(s) that expose Wizard + uCODE capabilities to Vibe.

## Goals (Phase 2 bootstrap)

- Provide a minimal tool surface for exploration:
  - `wizard.health`
  - `wizard.config.get`
  - `wizard.config.set`
  - `wizard.providers.list`
  - `wizard.plugin.command` (stub)
  - `ucode.command` (raw input router)
  - `ucode.dispatch` (allowlisted)
  - Vibe-style TUI wrapper output via `display` field

## Files

- `mcp_server.py` — MCP stdio server for Vibe
- `gateway.py` — HTTP client wrapper for Wizard APIs

## CLI Test Flags

`python mcp/wizard/server.py` supports quick checks:

- `--ucode "STATUS"` (allowlisted dispatch)
- `--ucode-command "OK explain core/tui/ucode.py"` (raw uCODE input)
- `--tools` (list MCP tool names from `/api/wizard/tools/mcp-tools.md`)

## Notes

- The gateway should use `/api/wizard` contracts as the source of truth.
- It should call Wizard services directly (in-process) or via HTTP depending on deployment.
