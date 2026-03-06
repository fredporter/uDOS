# v1.5 ucode TUI Decision

Status: active source of truth  
Updated: 2026-03-06

## Purpose

Define the canonical v1.5 viewport and rendering contract for `ucode` TUI, aligned with UGRID.

## Core Rule

All viewport sizing is specified as **characters**: `WIDTHxHEIGHT` (columns x rows).  
Pixel classes (watch/tablet/laptop/desktop) are advisory only.

## Viewport Tiers (Character Matrix)

| Tier | Device class | Pixel reference (typical) | Character viewport (W x H) |
|---|---|---|---|
| V0 | Watch minimum | tiny terminal/overlay | `25x25` (minimum supported) |
| V1 | Compact handheld | ~640x360 class | `40x25` |
| V2 | Tablet portrait | ~1024x768 class | `64x32` |
| V3 | Tablet landscape | ~1280x800 class | `80x40` |
| V4 | Laptop baseline | ~1366x768 class | `100x40` |
| V5 | Desktop baseline | ~1600x900 class | `120x50` |
| V6 | Widescreen HD (1280p class) | `1280x720` | `80x45` |
| V7 | Widescreen FHD (1920x1080 class) | `1920x1080` | `120x67` |

Notes:
- `25x25` is the hard minimum viewport for v1.5.
- Terminal runtime may exceed these sizes; renderer must clamp/pad deterministically.
- ASCII-safe operation is required at every tier.

## Configuration Contract (.env / user.json)

The active viewport is registered by variable, not by implicit terminal assumptions.

Primary key:
- `UDOS_VIEWPORT_SIZE_CH=<width>x<height>` (example: `80x40`)

Compatibility keys:
- `UDOS_VIEWPORT_COLS=<width>`
- `UDOS_VIEWPORT_ROWS=<height>`

Supported storage lanes:
- `.env` (highest priority)
- `memory/bank/private/user.json` (user-scoped fallback)

`user.json` examples:

```json
{
  "UDOS_VIEWPORT_SIZE_CH": "80x40"
}
```

or:

```json
{
  "viewport": {
    "size_ch": "120x67",
    "cols": 120,
    "rows": 67
  }
}
```

## Architecture Boundary

Frontend shell (Bubble Tea + Lip Gloss):
- owns layout/input/rendering and mode transitions
- respects measured+configured viewport contract

Backend (`core`/`wizard`):
- emits structured events
- owns execution, policy, orchestration

## Rendering Rules

- crop-then-pad over uncontrolled wrap
- deterministic ordering and stable line widths
- teletext/block glyph support is additive; ASCII fallback is mandatory
- narrow viewport fallback must keep command usability and status visibility

## UGRID Alignment

UGRID remains deterministic-first with canonical snapshots (`80x30`) and adaptive runtime rendering for live sessions.  
This TUI decision and `docs/specs/07-grid-canvas-rendering.md` now share one viewport model.

## Related

- `docs/specs/07-grid-canvas-rendering.md`
- `docs/specs/TUI-KEYBINDINGS-v1.5.md`
- `docs/specs/UCODE-DISPATCH-CONTRACT.md`
