# Vibe MCP Integration Guide

Status: canonicalized for Cycle D (2026-02-23)

## What Is Canonical

- MCP server runtime entrypoint: `wizard/mcp/mcp_server.py`
- MCP activation manager (single cross-platform script): `scripts/mcp_activation.py`
- MCP tool index source: `api/wizard/tools/mcp-tools.md` (fallback: `wizard/docs/api/tools/mcp-tools.md`)

## Activation Contract

Use one command path on all platforms:

```bash
uv run --project . scripts/mcp_activation.py <enable|disable|status|contract>
```

Command behavior:

- `enable`: injects canonical managed MCP block into `.vibe/config.toml` (idempotent)
- `disable`: removes managed block (idempotent)
- `status`: prints `enabled` or `disabled`
- `contract`: prints the exact managed TOML block

Managed block markers (contract boundary):

- `# BEGIN UCODE MANAGED MCP (WIZARD)`
- `# END UCODE MANAGED MCP (WIZARD)`

## Runtime Launch Contract

When enabled, `.vibe/config.toml` must include:

- `command = "uv"`
- `args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]`
- `transport = "stdio"`
- environment contains `PYTHONPATH = "."`

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
- This document replaces older instructions that referenced `/.venv/bin/python` directly and deprecated integration scaffolds.
