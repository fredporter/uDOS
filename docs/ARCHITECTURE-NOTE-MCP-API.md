# Architecture Note — API + MCP Separation

Date: 2026-02-06

## Decision

Create two new top-level directories:

- `/Users/fredbook/Code/uDOS/api/` — canonical API contracts and schemas for Wizard services.
- `/Users/fredbook/Code/uDOS/mcp/` — MCP gateway(s) and tool exposure for Vibe.

Wizard remains the implementation + companion web UI under `/Users/fredbook/Code/uDOS/wizard/`.

## Rationale

- **Separation of concerns**: contracts (`/api`) are independent from implementation (`/wizard`) and tool surface (`/mcp`).
- **Clarity**: eliminates confusion with `extensions/` and plugin concepts.
- **Future-proofing**: contracts can be versioned without relocating Wizard or MCP.
- **Single source of truth**: both Wizard services and MCP tools reference the same specs.

## Implications

- Wizard services should align to `/api` contracts.
- MCP gateway routes map to `/api` specs and call Wizard services.
- Companion web UI uses the same `/api` contracts for consistency.

## Next Steps

- Add initial Wizard service contracts under `/api/wizard/`.
- Scaffold MCP gateway under `/mcp/wizard/`.
- Document the first tool surface (ucode + wizard health/config).

