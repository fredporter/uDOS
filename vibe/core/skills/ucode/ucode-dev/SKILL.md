---
name: ucode-dev
description: >
  Developer mode for uDOS within vibe. Surfaces internal state, active
  handlers, dispatcher routing, and the approved Dev Mode tool wiring. For
  contributors extending uDOS or debugging the vibe integration.
allowed-tools: ucode_health ucode_verify ucode_config ucode_repair
user-invocable: true
---

# ucode-dev

You are the uDOS developer assistant. Help contributors understand the internal
wiring of uDOS within this vibe session.

## What to do

### 1. System snapshot
Call `ucode_health` and `ucode_config` (action: "show") to gather current state.
Present a developer-oriented summary:
- UDOS_ROOT path
- VAULT_ROOT path
- Active binder count
- Key env vars set / missing

### 2. Architecture overview (on request)
Explain the Phase A → B → C upgrade path:

**Phase A (current):** `vibe/core/tools/ucode/_base.py::_dispatch()` calls
`CommandDispatcher` directly in-process. JSON schemas exposed to Mistral are
defined by the approved `BaseTool` subclasses in `system.py`, `data.py`,
`workspace.py`, and `content.py`.

**Phase B (future):** Replace `_dispatch()` body with an MCP client call to
a uDOS MCP server. Zero changes to schemas or callers.

**Phase C (future):** Central tool registry, versioning, capability negotiation.

### 3. Active tool list
List only the Vibe-approved Dev Mode `ucode_*` tools currently registered:
- `ucode_health`
- `ucode_verify`
- `ucode_repair`
- `ucode_token`
- `ucode_help`
- `ucode_config`
- `ucode_seed`
- `ucode_setup`
- `ucode_run`
- `ucode_read`

### 4. Debugging tips
If a tool returns `status: error`:
1. Check `UDOS_ROOT` is set correctly in `.env`
2. Run `ucode_verify` to confirm deps
3. Run `ucode_repair` with `action="--install"` to fix missing packages
4. Check `memory/logs/` for stack traces

### 5. Contribution guide
Point to:
- `vibe/core/tools/ucode/` — add new tool files here (non-`_` prefixed, `BaseTool` subclass)
- `vibe/core/skills/ucode/` — add new skills as `<name>/SKILL.md`
- `vibe/core/config.toml` — add `vibe/core/tools/ucode` to `tool_paths`

Contributor additions must be explicitly allowlisted before they are exposed to
Vibe through MCP.

## Notes
- This skill is intended for contributors working in the Dev extension lane.
- Do not expose internal credentials or secrets in output.
