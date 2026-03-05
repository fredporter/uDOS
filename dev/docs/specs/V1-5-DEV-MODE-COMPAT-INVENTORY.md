# v1.5 Dev Mode Compatibility Inventory

Last Updated: 2026-03-05
Status: Active

This inventory tracks remaining `vibe` compatibility surface in the v1.5 stable repo after the TUI/MCP/runtime cutover.

## Canonical Rule

- Standard runtime: `ucode`
- Dev contributor lane: external Dev Mode contributor tool
- `vibe` naming remains only where compatibility with the external binary, legacy imports, or historical records still requires it

## Group A: Keep As Explicit Compatibility

- `wizard/extensions/assistant/vibe_cli_service.py`
  Reason: wraps the external `vibe` binary and `.vibe/` config layout
  Direction: keep module path stable, prefer `DevModeToolCli*` classes internally

- `wizard/services/vibe_service.py`
  Reason: legacy imports still expect `VibeService` and `VibeConfig`
  Direction: keep aliases only; canonical classes are `DevModeToolService` and `DevModeToolConfig`

- `wizard/services/provider_registry.py`
  Reason: legacy imports still expect `VibeProviderRegistry`
  Direction: keep alias only; canonical class is `ContributorProviderRegistry`

- `core/services/vibe_cli_handler.py`
  Reason: legacy contributor command path still imports this module
  Direction: keep module path, prefer `DevModeToolCliHandler` internally

- `core/services/vibe_skill_mapper.py`
  Reason: legacy contributor command path still imports this module
  Direction: keep module path, prefer `DevModeToolSkillMapper` internally

- `core/services/vibe_help_service.py`
- `core/services/vibe_tui_service.py`
- `core/services/vibe_setup_service.py`
  Reason: internal compatibility cluster for the contributor lane
  Direction: keep module paths for now, use Dev Mode canonical classes internally

## Group B: Renamed With Compatibility Aliases

- `core/services/vibe_device_service.py`
- `core/services/vibe_user_service.py`
- `core/services/vibe_workspace_service.py`
- `core/services/vibe_network_service.py`
- `core/services/vibe_script_service.py`
- `core/services/vibe_wizard_service.py`
- `core/services/vibe_sync_service.py`
- `core/services/vibe_binder_service.py`
- `core/services/vibe_vault_service.py`

Reason:
- these are compatibility-era service names, not active TUI/MCP architecture names
- they now expose canonical Dev Mode class names while preserving legacy aliases and module paths

Current state:
1. canonical Dev Mode class aliases and neutral logger names are in place
2. active runtime callers can migrate to canonical class names without breaking legacy imports
3. old module/class names remain as compatibility aliases until a later path-level cleanup

## Group C: Release/Profile Metadata

- `core/services/release_profile_service.py`
  Current compatibility markers:
  - legacy component alias `vibe`
  - legacy external tool path rooted at `repo/vibe`

Direction:
- canonical metadata uses `dev-tool`
- keep `vibe` as a compatibility component alias only where persisted manifests still reference it

## Group D: Historical Docs And Tests

- `core/tests/vibe_*`
- `wizard/tests/vibe_*`
- `wizard/docs/api/tools/VIBE-MCP-TOOLS.md`
- contributor and historical docs under `dev/docs/` and `docs/howto/`

Direction:
- keep while still useful as compatibility or migration records
- mark as historical or compatibility where needed
- do not treat as active runtime contract

## Group E: Compost Candidates

- references to `mistral-vibe`
- old repo URLs ending in `uDOS-vibe`
- obsolete installer/setup text that implies `vibe` is a peer runtime instead of a Dev Mode tool

## Broader Compatibility Inventory

### 1. Historical `vibe` references

- `docs/decisions/vibe-cli-*`
- historical examples in `docs/howto/UCODE-COMMAND-REFERENCE.md`
- template/history references under `core/framework/seed/`

Direction:
- keep as historical decision records or archive material
- do not treat as active runtime or release-surface terminology

### 2. Canonical localhost defaults

- `core/services/unified_config_loader.py`
- `core/services/background_service_manager.py`
- `core/tui/ucode.py`
- `wizard/config/oauth_providers.template.json`
- `wizard/config/port_registry.json`

Direction:
- these are active default/config surfaces, not doc drift
- they should be normalized through one runtime config contract in a later config pass, not blindly removed

### 3. Internal example localhost references

- `wizard/routes/notification_history_routes.py`
- `wizard/services/home_assistant/README.md`
- `wizard/services/home_assistant/PROVISIONING_SUMMARY.md`
- `wizard/config/README.md`
- `wizard/dashboard/UI-UPDATES.md`
- `wizard/ARCHITECTURE.md`

Direction:
- normalize when these internal docs/routes are next touched
- lower priority than active runtime compatibility cleanup

### 4. Test-only compatibility coverage

- `wizard/tests/test_mcp_gateway.py`
- `core/tests/*network_boundary*`
- `core/tests/*background_service_manager*`
- `core/tests/*dev_state_boundary*`

Direction:
- keep explicit localhost assertions where they prove boundary defaults
- update only if the canonical default endpoint contract changes

## Current Status

- Active TUI/MCP/runtime contract no longer depends on `vibe.core`
- Active operator-facing route/help/setup text no longer uses `vibe-cli`
- Compatibility services now have canonical Dev Mode class names with legacy aliases where updated
- Group B service family is canonicalized behind compatibility aliases
- Remaining repo-wide `vibe` and localhost references are categorized as historical, config-default, internal-example, or test-only surfaces

## Next Pass

1. Migrate release/profile metadata from `vibe` to `dev-tool`
2. Mark remaining `VIBE-*` docs as compatibility references or archive candidates
3. Decide whether the legacy module paths move under a dedicated compatibility namespace after v1.5.1
