# Tools Reference

Updated: 2026-03-03
Status: active operator index

## Purpose

This is the short front door for the uDOS tool surface.

Use it to find the right tool category quickly, then jump into the focused reference page for details.

## Surface Split

- Full operator surface: the uDOS TUI exposes the complete `ucode` command set.
- Dev Mode contributor surface: only a reduced contributor subset is exposed for setup, repair, config, repo inspection, and development operations.

Dev Mode subset:
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

## Tool Categories

- [System and Health](TOOLS-SYSTEM-HEALTH-REFERENCE.md)
  Commands for health, verification, repair, identity, tokens, and viewport checks.
- [Navigation and Spatial](TOOLS-SPATIAL-REFERENCE.md)
  Commands for maps, grids, anchors, movement, and search.
- [Data, Workspace, and Execution](TOOLS-DATA-WORKSPACE-REFERENCE.md)
  Commands for binders, saving/loading, seeds, migration, config, places, scheduling, scripts, setup, run, and users.
- [Content and Creative](TOOLS-CONTENT-CREATIVE-REFERENCE.md)
  Commands for stories, reading, games, drawing, sound, music, empire, formatting, undo, and destructive operations.

## Quick Start

For the canonical command surface, start with:
- [UCODE Command Reference](UCODE-COMMAND-REFERENCE.md)
- [Workflow Scheduler Quickstart](WORKFLOW-SCHEDULER-QUICKSTART.md)
- [Managed Wizard Operations](MANAGED-WIZARD-OPERATIONS.md)

## Common Workflows

### Troubleshooting

Use:
- `ucode_health`
- `ucode_verify`
- `ucode_repair`
- `ucode_help`

These are available in both the full TUI and the Dev Mode subset.

### Project and Workspace Work

Use:
- `ucode_binder`
- `ucode_place`
- `ucode_scheduler`
- `ucode_script`
- `ucode_run`

Only `ucode_run` is exposed through Dev Mode. The rest remain TUI/operator surfaces.

### Content and Rendering

Use:
- `ucode_read`
- `ucode_story`
- `ucode_play`
- `ucode_draw`
- `ucode_print`
- `ucode_format`

Only `ucode_read` is exposed through Dev Mode. The rest remain TUI/operator surfaces.

## Notes

- Prefer the category pages for concrete usage examples.
- Prefer the UCODE command docs when you need the operator-facing command surface rather than the lower-level tool names.
- Dev Mode details are documented in `docs/howto/MISTRAL-VIVE-DEV-WORKSPACE.md`.
