# Dev Mode Tooling Setup Guide

This guide covers the v1.5 Dev Mode contributor lane.

The standard runtime remains `ucode`. Dev Mode is available only when the `dev` profile is enabled and the `/dev/` extension scaffold is installed and activated through Wizard-owned controls.

## Target Model

- standard runtime stays on `ucode`
- Dev Mode is an installed extension lane, not a second default runtime
- Wizard GUI owns Dev Mode install, uninstall, enable, disable, and status
- `/dev/` is the versioned Dev Mode framework and distro template root
- `vibe` remains contributor-only TUI tooling behind the active Dev Mode gate

## 1. Prepare The Base Environment

From repo root:

```bash
uv venv venv
uv sync --extra udos-wizard
```

Policy for this repo:

- use `venv/` only
- do not use `.venv/`

## 2. Install Dev Mode Through Wizard

Use Wizard GUI to:

- install the `dev-mode` extension
- enable the `dev` certified profile
- activate Dev Mode

Required framework markers:

- `/dev/extension.json`
- `/dev/AGENTS.md`
- `/dev/DEVLOG.md`
- `/dev/project.json`
- `/dev/tasks.md`
- `/dev/completed.json`

If `/dev/` or its framework files are missing, Dev Mode must remain unavailable.

## 3. Validate The Contributor Bridge

Project config is committed in `.vibe/config.toml`.

Canonical MCP launcher values:

- `command = "uv"`
- `args = ["run", "--project", ".", "wizard/mcp/mcp_server.py"]`

Canonical MCP activation check:

```bash
uv run --project . scripts/mcp_activation.py status
uv run --project . wizard/mcp/mcp_server.py --tools
```

## 4. Enter Dev Mode TUI

Once Wizard has installed and activated the Dev Mode extension:

```bash
vibe trust
vibe
```

This is contributor-only TUI behavior. It must not replace the standard `ucode` runtime path.

## 5. Local vs Template Data

`/dev/` is the versioned framework and distro template surface.

Local mutable working data must stay separate from the remote template truth. Local-only working areas may exist under:

- `/dev/files`
- `/dev/relecs`
- `/dev/dev-work`
- `/dev/testing`

These are local working paths, not the canonical extension template payload.

## Common Misconfigurations

### Symptom: Wizard shows Dev Mode unavailable

Check:

- `/dev/` exists
- `/dev/extension.json` exists
- the `dev` profile is enabled
- the Dev Mode extension is installed and activated in Wizard GUI

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

## Notes

- This guide supersedes older instructions that treated Dev Mode tooling as a general setup path.
- Keep historical material in `docs/.compost/` only.
