# Dev Mode Tooling Setup Guide

This guide covers optional Dev Mode contributor tooling setup.
The standard runtime remains `ucode`; use this guide only when you need the `vibe` Dev Mode surface.

## Target Model

- optional global Dev Mode tooling install
- Single Python environment in repo root: `venv/`
- Project-local Vibe wiring in `.vibe/config.toml`
- ucode command-set delivered through repo-local tools/skills and Wizard MCP

## 1. Install Dev Mode Tooling

```bash
curl -fsSL https://vibe.mistral.ai/install.sh | sh
```

Verify:

```bash
vibe --version
```

## 2. Prepare Project Environment

From repo root:

```bash
uv venv venv
uv sync --extra udos-wizard
```

## 3. Validate Local Dev Mode Config

Project config is committed in `.vibe/config.toml`.

Canonical MCP launcher values:

- `command = "uv"`
- `args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]`

Canonical MCP activation command (cross-platform):

```bash
uv run --project . scripts/mcp_activation.py enable
```

## 4. Trust and Launch Dev Mode

From repo root:

```bash
vibe trust
vibe
```

## 5. Quick Health Checks

### MCP process check

```bash
uv run --project . wizard/mcp/mcp_server.py --tools
```

### Skill/tool path check

Ensure these paths exist:

- `vibe/core/skills/ucode`
- `vibe/core/tools/ucode`

## Common Misconfigurations

### Symptom: MCP server fails to start

Fix:

```bash
uv sync --extra udos-wizard
uv run --project . scripts/mcp_activation.py status
uv run --project . wizard/mcp/mcp_server.py --tools
```

### Symptom: skills or tools do not appear in Dev Mode

Fix:

```bash
vibe trust
```

Then restart `vibe` from repo root.

### Symptom: mixed environments (`venv` and `.venv`)

Policy for this repo:

- Use `venv/` only
- Do not use `.venv/`

## Notes

- This guide supersedes old instructions that treated Dev Mode tooling as the default runtime.
- Keep historical material in `docs/.compost/` only.
