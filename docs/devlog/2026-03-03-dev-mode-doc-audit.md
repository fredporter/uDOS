# 2026-03-03 Dev Mode Doc Audit

Status: Completed

This audit captured the remaining stale Dev Mode references after the v1.5 Dev Mode spec alignment pass.

## Updated In This Pass

- Wizard Dev API service doc
- Wizard Dev Mode screen labels
- Wizard UCode console Dev labels
- Dev-specific OK coding error text
- high-traffic Dev setup and command docs
- `/dev/` extension framework governance files

## Remaining Stale References

No active v1.5 runtime or high-traffic setup/docs roots remain in this audit set.

Historical or archival material may still mention older Dev Mode/Goblin language and should only be normalized if those files are promoted back into active guidance.

## Working Rule

When touching the remaining files:

- keep `ucode` as the standard runtime
- describe Dev Mode as a Wizard-gated `/dev/` extension lane
- keep `vibe` contributor-only
- avoid reviving Goblin as active release truth unless a file is explicitly historical

## Cleared Since Audit

- `wizard/ARCHITECTURE.md`
- `core/tui/ucode.py`
- `docs/dev/GETTING-STARTED.md`
- `docs/examples/COMMAND-WORKFLOWS.md`
- `core/commands/setup_handler.py`
- `core/commands/setup_handler_helpers.py`
- `core/framework/seed/bank/system/tui-setup-story.md`
- `wizard/services/monitoring_manager.py`
- `wizard/mcp/mcp_server.py`
