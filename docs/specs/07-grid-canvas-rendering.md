# uDOS v1.3.26+ — Grid Canvas and Text Rendering Spec

Status: active alignment spec for current uCLI/TUI behavior.

## 1) Goal

Define one rendering contract across uCLI, DRAW/GRID outputs, logs, and markdown exports:

- deterministic text layouts,
- width-safe Unicode rendering,
- object-aware panels for map/task/schedule/workflow surfaces,
- parity between terminal output and markdown diagram output.

## 2) Canvas Models

uDOS supports two display modes:

- Canonical canvas: fixed `80x30` for deterministic snapshots, CI, and replay parity.
- Adaptive canvas: terminal-width aware rendering for interactive uCLI sessions.

Rules:

- Canonical mode never probes runtime terminal size.
- Adaptive mode may read viewport columns and clamp/truncate accordingly.
- Both modes must produce stable ordering and deterministic content for the same input.

## 3) Text Rendering Capabilities

Current renderer behavior (Python core) aligns to width-aware helpers:

- visible width uses `display_width` (ANSI stripped),
- truncation uses ellipsis and visible-width clamping,
- right-padding uses visible-width padding,
- ANSI color is optional and must not break width math.

Character handling:

- ASCII-safe is always supported.
- Box/block glyphs are allowed (`█`, `░`, line-drawing chars).
- Emoji/wide glyphs are allowed in adaptive mode but must not shift column alignment.

## 4) Output Formats

Renderers may emit:

- `text`: plain/ANSI terminal output.
- `json`: structured lines/metadata for tests and integrations.
- `markdown`: fenced text diagram for docs/binders/workflows.

Markdown diagram contract:

````md
# <Title>

```text
<diagram lines>
```
````

This format is canonical for `DRAW MD ...` and `DRAW --md ...`.

## 5) uCLI Command Alignment

Grid/text surfaces align to these command lanes:

- `DRAW`:
  - demo/panels/block art/patterns
  - supports `--py|--ts`, `--md`, `--save`
- `GRID`:
  - calendar/table/schedule/map/dashboard runtime modes
- `MAP`, `PANEL`, `TELL`:
  - spatial/location views
- `PLAY MAP ...`:
  - map loop event/state surfaces
- `PLACE` and `BINDER`:
  - workspace/tag/chapter workflow views

All command outputs must preserve prompt/status integrity (no interleaved redraw corruption).

## 6) Object Types for Grid Panels

Grid renderers should model typed objects, not free-form strings only.

Minimum object families:

- `location`:
  - `loc_id`, `place_ref`, `layer`, `z`
- `task`:
  - `id`, `title`, `status`, `due`, `owner`, `loc_id?`
- `schedule_item`:
  - `start`, `end?`, `title`, `channel`, `loc_id?`
- `workflow_step`:
  - `id`, `title`, `state`, `depends_on[]`, `owner?`
- `event`:
  - `type`, `ts`, `summary`, `source`
- `object/sprite`:
  - `id`, `glyph`, `kind`, `loc_id`, `state`

Panel renderers should degrade gracefully when optional fields are missing.

## 7) Layout Modes (Current)

- `dashboard`: status + mission/log summary.
- `calendar`: day/week timeline.
- `schedule`: agenda rows (`time | item | location/workspace`).
- `table`: generic fixed-width tabular output.
- `map`: LocId/place overlays with legend.
- `workflow`: task chain/progress lane (text-first, deterministic).

## 8) Determinism and Ordering

- Tasks/events sort by stable keys (`time`, then `title/id`).
- Tables use explicit column ordering.
- Wrapping/truncation uses deterministic ellipsis rules.
- No tabs.
- Canonical `80x30` snapshots must pass line-count and width checks.

## 9) Advanced I/O Safety Requirements

Rendering pipeline must enforce single-writer output discipline:

- Input phase: prompt owns stdin.
- Render phase: renderer owns stdout.
- Background workers: no direct stdout writes outside render pipeline.

Terminal control safety:

- avoid cursor-home side effects on screen restore,
- clear full line before progressive redraw,
- never leave partial control-sequence artifacts in captured output.

## 10) Integration Targets

- Spatial overlays from place/location contracts.
- Task and schedule views from prompt/task workflow services.
- Workflow diagrams exportable to markdown for binder/docs usage.
- CI snapshot fixtures for canonical `80x30` and markdown diagram outputs.
