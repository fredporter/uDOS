# Dev Mode MCP Integration Guide

Status: canonical Dev Mode compatibility contract
Updated: 2026-03-05

## What Is Canonical

- MCP server runtime entrypoint: `wizard/mcp/mcp_server.py`
- MCP activation manager: `scripts/mcp_activation.py`
- MCP tool index source: `wizard/docs/api/tools/mcp-tools.md`

## Activation Contract

Use one command path on all platforms:

```bash
uv run --project . scripts/mcp_activation.py <enable|disable|status|contract>
```

Command behavior:

- `enable`: injects the managed MCP block into the Dev Mode contributor-tool config
- `disable`: removes the managed block
- `status`: prints `enabled` or `disabled`
- `contract`: prints the exact managed block

## Config Surface

The current external contributor-tool config surface is:

- target file: `.vibe/config.toml`

This remains a compatibility boundary while the external contributor tool still uses `.vibe/`.

Managed block markers:

- `# BEGIN UCODE MANAGED MCP (WIZARD)`
- `# END UCODE MANAGED MCP (WIZARD)`

## Runtime Launch Contract

When enabled, the managed block must include:

- `command = "uv"`
- `args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]`
- `transport = "stdio"`
- `PYTHONPATH = "."`

## Verification

1. Check activation state:

```bash
uv run --project . scripts/mcp_activation.py status
```

2. Check MCP server starts and can list tools:

```bash
uv run --project . wizard/mcp/mcp_server.py --tools
```

3. Validate MCP tests:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  wizard/tests/test_mcp_server.py
```

## Notes

- Avoid hand-editing the managed MCP block; use `scripts/mcp_activation.py`.
- The old `VIBE-MCP-INTEGRATION.md` document was composted after the v1.5.1 Dev Mode rename pass.
- `.vibe/config.toml` is still the live external contributor-tool config contract until that upstream layout changes.
