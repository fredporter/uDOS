# Dev TUI + Maintenance Commands (2026-01-25)

## Summary

- Added a dedicated Wizard Dev TUI for repair-first recovery workflows.
- Wired BACKUP/RESTORE/TIDY/CLEAN/COMPOST commands across Core and Wizard TUIs.
- Standardized .backup/.archive/.compost handling with Alpine-friendly path rules.

## Changes

- `wizard/dev_tui.py` — new Dev-only TUI with diagnostics + repair/backup tooling.
- `bin/launch_wizard_dev_tui.sh` + `bin/Launch-Wizard-Dev-TUI.command` — new launchers.
- `core/services/maintenance_utils.py` — shared maintenance helpers (backup/tidy/clean/compost).
- `core/commands/maintenance_handler.py` — Core TUI command handler.
- `core/tui/dispatcher.py` — routes maintenance commands.
- `wizard/wizard_tui.py` + `wizard/services/interactive_console.py` — maintenance commands in Wizard TUIs.
- `wizard/WIZARD-DEV-GUIDE.md` + `wizard/README.md` — updated docs.
- `wizard/routes/repair_routes.py` + `wizard/dashboard/src/routes/Repair.svelte` — compost cleanup + stats in dashboard.
- Added "Delete backup" control for the selected backup in Repair dashboard.
- Added queued backup endpoint and dashboard button (paced via scheduler).
- Scheduler now runs a background loop with resource-aware pacing and daily compost cleanup.
- Added compost retention config in `wizard.json` and surfaced scheduler status on dashboard.
- Added scheduler controls (tick/throughput/network gating) on dashboard.
- Created Goblin→Wizard migration checklist in `docs/howto/`.
- Added setup wizard endpoints under `/api/v1/setup/*` (ported from Goblin).
- Added scheduler task drill-down + backup metadata in Repair restore section.
- Added Setup dashboard page and scheduler task run detail drawer.
- Added API tests for setup + scheduler status.

## Notes

- DESTROY is Dev TUI only and requires explicit confirmation.
- CLEAN/TIDY move files into `.archive` (no deletions); COMPOST moves archive/backup/tmp into `/.compost`.
