# uDOS v1.3 — Grid Canvas Text Rendering Spec

80×30 fixed canvas for CLI + TUI + logs

## 1) Goal

Deterministic, themeable, text-only rendering for:

- Vibe CLI output (terminal + logs)
- Fixed-width teletext visuals
- Copy/paste stable layouts
- Remote/low-bandwidth displays (beacons)
- Dashboards, maps, calendars, tables, schedules

## 2) Canvas model

- **Dimensions:** width 80, height 30; origin (0,0) top-left.
- **Character:** one Unicode codepoint per cell, ASCII-safe by default; optional extended glyph mode.
- **Colour:** ANSI colouring allowed as backend but canonical output is plain text (colour layer optional).

## 3) Output format (canonical)

A render package contains:

```
--- udos-grid:v1
size: 80x30
title: "Daily Schedule"
mode: "calendar"
theme: "mono"
ts: 2026-02-03T19:14:00+10:00
---

<30 lines of exactly 80 chars>

--- end ---
```

Rules:

- Exactly 30 body lines, each 80 visible columns (ANSI stripped).
- No tabs; newline only per row.

## 4) Rendering pipeline

1. **Layout:** transform data into primitives (boxes, text, tables, lists, mini-maps, sparklines).
2. **Draw:** render primitives into a Canvas80x30 buffer.
3. **Emit:** backend can output `plain`, `ansi`, or `json` (for tests).

## 5) Primitives

### 5.1 Box
`box(x, y, w, h, style="single", title?)` with optional borders (`single`, `double`, `none`).

### 5.2 Text block
`text(x, y, w, h, content, opts={align, wrap, ellipsis})` word-wraps/clips.

### 5.3 Table
`table(x, y, w, h, columns, rows, opts)` supports fixed widths, row separators, selected rows (ansi).

### 5.4 List
`list(x, y, w, h, items, bullet)` for bulleted/numbered lists.

### 5.5 Mini-map
`minimap(x, y, w, h, cells, focus?, overlays?)` shows grid world + overlays (T tasks, N notes, E events, ! alerts).

## 6) Layout modes

### 6.1 Dashboard
- Top banner (title+clock)
- Left: mission queue
- Right: stats (quota, models, node)
- Bottom: recent logs

### 6.2 Calendar
- Day variant: timeline rows, events
- Week variant: 7 columns
- Layout uses header (rows 0-1), timeline (2-28), footer row 29.

### 6.3 Schedule (agenda)
- Header + table (time | item | location/LocId) + footer filters.

### 6.4 Table
- Header (query + row count), table region, footer (page/offset).

### 6.5 Map
- Shows LocId grid with edge labels, focus highlight, overlay markers, legend.

## 7) Determinism rules

- Sort tasks/events by time/title.
- Tables sort by stable key unless overridden.
- Word wrap/truncation deterministic (ellipsis).
- Canonical mode never probes terminal width.

## 8) API spec (TS)

```ts
export interface GridCanvasSpec {
  width: 80;
  height: 30;
  title?: string;
  theme?: string;
  mode?: "dashboard" | "calendar" | "schedule" | "table" | "map";
}

export interface RenderResult {
  header: Record<string, unknown>;
  lines: string[];
  rawText: string;
}

export interface RendererBackend {
  emit(result: RenderResult): string;
}

export interface Canvas80x30 {
  clear(fill?: string): void;
  box(x: number, y: number, w: number, h: number, style?: string, title?: string): void;
  text(x: number, y: number, w: number, h: number, content: string, opts?: any): void;
  table(x: number, y: number, w: number, h: number, columns: any[], rows: any[], opts?: any): void;
  minimap(x: number, y: number, w: number, h: number, cells: any, opts?: any): void;
  toLines(): string[]; // 30 lines
}
```

CLI:

- `udos-core grid render --mode calendar --input tasks.json`
- `udos-core grid render --mode map --loc EARTH:SUR:L305-DA11 --layer 305`

Vibe usage:

- Vibe calls the CLI and prints output; optional MCP wraps responses.

## 9) Example (calendar day)

```
--- udos-grid:v1
size: 80x30
title: "Boss — Tue 3 Feb 2026"
mode: "calendar"
theme: "mono"
---

+------------------------------------------------------------------------------+
| 09:00  Standup                 | Tasks (Today)                               |
| 10:00  Build v1.3 grid renderer| [ ] Wire vault picker                        |
| 11:00  Review themes           | [ ] Index tasks → sqlite                     |
| 12:00  Lunch                   | [x] Add spatial schema                       |
| 13:00  Focus: Typo editor      | [ ] Export _site (prose)                     |
| 14:00  Beacon testing          |                                             |
|                                                                              |
|                                                                              |
|                                                                              |
+------------------------------------------------------------------------------+
--- end ---
```

## 10) Integration

- Spatial: map mode overlays from places/file_place_tags.
- Tasks: agenda/calendar from task index.
- Missions: dashboard panels from scheduler logs.
- Publishing: final “report grid” exported for logs.

## 11) First tasks

1. Canvas buffer + `box()`/`text()`.
2. `table()` primitive.
3. Calendar day template.
4. Map mode LocId overlays.

> We can also deliver starter TS module, golden snapshots, or CLI skeleton upon request.
