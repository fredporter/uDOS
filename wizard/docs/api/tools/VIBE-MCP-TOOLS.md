# Vibe MCP Tools

**Status:** Active Dev extension subset
**Updated:** 2026-03-03

This document records the current Vibe-facing MCP contract for uDOS v1.5.

## Boundary

- Vibe is a contributor TUI inside the `/dev/` extension lane.
- It is available only when the `dev` profile is active and the `/dev/` extension is installed and enabled.
- It does not mirror the full operator `ucode` surface.

## Active Skill Set

Current Vibe skills:
- `ucode`
- `ucode-help`
- `ucode-setup`
- `ucode-dev`

These skills sit on top of the reduced MCP uCODE subset defined in `wizard/mcp/tools/ucode_mcp_registry.py`.

## Active uCODE MCP Subset

Generic lane:
- `ucode.tools.list`
- `ucode.tools.call`

Proxy lane:
- `ucode.health`
- `ucode.token`
- `ucode.help`
- `ucode.verify`
- `ucode.repair`
- `ucode.config`
- `ucode.run`
- `ucode.read`

Dispatch lane:
- `ucode.command`
- `ucode.dispatch` (deprecated alias)

## Excluded Operator Surfaces

The following stay in the standard `ucode` TUI and are not part of the Vibe Dev extension subset:
- binder and story workflows
- spatial/navigation commands
- gameplay and media commands
- destructive and recovery-heavy content flows

## Notes

- Use [mcp-tools.md](/Users/fredbook/Code/uDOS/wizard/docs/api/tools/mcp-tools.md) for the broader Wizard MCP inventory.
- Keep additions to the Vibe lane explicitly allowlisted and contributor-specific.
