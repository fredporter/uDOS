# MCP Bridge Decision

Status: active implementation reference  
Updated: 2026-03-03

## Purpose

This document records the MCP bridge role in the current uDOS architecture.

## Decision

Wizard provides the MCP bridge for managed tool and command access.
It exists to expose uDOS capabilities through a structured bridge without redefining the standard runtime boundary.

## Working Rules

- the standard interactive user experience is the v1.5 `ucode` TUI
- `vibe` uses MCP as part of Dev Mode operations
- Wizard owns MCP server behavior and managed bridge logic
- command execution should still converge on the canonical command/runtime surfaces rather than creating parallel behavior

## Current Implementation Shape

- `wizard/mcp/mcp_server.py` provides the stdio MCP server
- `.vibe/config.toml` registers MCP access for Dev Mode tooling
- command execution continues to rely on the shared command/runtime surfaces

## v1.5 Relevance

For v1.5, this decision governs:
- MCP bridge stability
- tool registration integrity
- Dev Mode bridge behavior
- alignment between MCP access and the `ucode`-first runtime model

## Related Documents

- `docs/decisions/v1-5-rebaseline.md`
- `docs/decisions/v1-5-ucode-tui-spec.md`
- `docs/decisions/WIZARD-SERVICE-SPLIT-MAP.md`
- `docs/howto/UCODE-COMMAND-REFERENCE.md`
