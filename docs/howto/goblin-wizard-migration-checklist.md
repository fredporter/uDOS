# Goblin → Wizard Migration Checklist (2026-01-25)

## Priority 1 (Core user impact)

- **Setup wizard API**: Port `/api/v0/setup/wizard/*` from `dev/goblin/routes/setup.py` into Wizard routes.
- **Story submission flow**: Resolve TODO in `dev/goblin/src/routes/stories/[slug]/+page.svelte` (server submit).
- **Table save**: Implement file save TODO in `dev/goblin/src/routes/table/+page.svelte`.

## Priority 2 (Stability + observability)

- **Extension monitor enable/disable**: TODOs in `dev/goblin/core/services/extension_monitor.py`.
- **Map data conversion**: TODOs in `dev/goblin/core/services/maps/map_data_manager.py`.

## Priority 3 (Nice-to-have)

- **Voice handler**: TODOs in `dev/goblin/core/commands/voice_handler.py`.
- **Desktop open wizard**: `dev/goblin/src/routes/desktop/+page.svelte` still references old URL.

## Notes

- Migrations should land in `/wizard` and update `/docs` as canonical reference.
- Use `docs/decisions/` if any boundary or responsibility changes are required.
