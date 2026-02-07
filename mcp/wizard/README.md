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

## Files

- `mcp_server.py` — MCP stdio server for Vibe
- `gateway.py` — HTTP client wrapper for Wizard APIs

## Notes

- The gateway should use `/api/wizard` contracts as the source of truth.
- It should call Wizard services directly (in-process) or via HTTP depending on deployment.
