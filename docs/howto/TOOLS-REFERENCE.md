# Tools Reference

Updated: 2026-03-03
Status: active operator index

## Purpose

This is the short front door for the uDOS tool surface.

Use it to find the right tool category quickly, then jump into the focused reference page for details.

## Surface Split

- Full operator surface: the uDOS TUI exposes the complete `ucode` command set.
- Vibe Dev Mode surface: Vibe exposes only the contributor subset used for setup, repair, config, repo inspection, and development operations.

Vibe Dev Mode subset:
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

- [System and Health](/Users/fredbook/Code/uDOS/docs/howto/TOOLS-SYSTEM-HEALTH-REFERENCE.md)
  Commands for health, verification, repair, identity, tokens, and viewport checks.
- [Navigation and Spatial](/Users/fredbook/Code/uDOS/docs/howto/TOOLS-SPATIAL-REFERENCE.md)
  Commands for maps, grids, anchors, movement, and search.
- [Data, Workspace, and Execution](/Users/fredbook/Code/uDOS/docs/howto/TOOLS-DATA-WORKSPACE-REFERENCE.md)
  Commands for binders, saving/loading, seeds, migration, config, places, scheduling, scripts, setup, run, and users.
- [Content and Creative](/Users/fredbook/Code/uDOS/docs/howto/TOOLS-CONTENT-CREATIVE-REFERENCE.md)
  Commands for stories, reading, games, drawing, sound, music, empire, formatting, undo, and destructive operations.

## Quick Start

For the canonical command surface, start with:
- [UCODE Command Reference](/Users/fredbook/Code/uDOS/docs/howto/UCODE-COMMAND-REFERENCE.md)
- [Workflow Scheduler Quickstart](/Users/fredbook/Code/uDOS/docs/howto/WORKFLOW-SCHEDULER-QUICKSTART.md)
- [Managed Wizard Operations](/Users/fredbook/Code/uDOS/docs/howto/MANAGED-WIZARD-OPERATIONS.md)

## Common Workflows

### Troubleshooting

Use:
- `ucode_health`
- `ucode_verify`
- `ucode_repair`
- `ucode_help`

These are available in both the full TUI and the Vibe Dev Mode subset.

### Project and Workspace Work

Use:
- `ucode_binder`
- `ucode_place`
- `ucode_scheduler`
- `ucode_script`
- `ucode_run`

Only `ucode_run` is exposed through Vibe Dev Mode. The rest remain TUI/operator surfaces.

### Content and Rendering

Use:
- `ucode_read`
- `ucode_story`
- `ucode_play`
- `ucode_draw`
- `ucode_print`
- `ucode_format`

Only `ucode_read` is exposed through Vibe Dev Mode. The rest remain TUI/operator surfaces.

## Notes

- Prefer the category pages for concrete usage examples.
- Prefer the UCODE command docs when you need the operator-facing command surface rather than the lower-level tool names.
- Prefer the Vibe skills docs only for the Dev extension lane; they do not represent the full uDOS operator surface.
