Yep — here’s a v1.3 spec for an 80×30 “Grid Canvas” text renderer that core + Vibe CLI can use to output maps, calendars, schedules, tables, dashboards in a consistent uDOS teletext-style format.

You can drop this into v1-3/docs/07-grid-canvas-rendering.md.

⸻

uDOS v1.3 — Grid Canvas Text Rendering Spec

80×30 fixed grid output for CLI + TUI + logs

1) Goal

Provide a deterministic, themeable, text-only rendering layer that outputs any UI (maps, calendar, tables, schedules, dashboards) as an 80×30 character canvas, matching the uDOS grid philosophy and enabling:
	•	Vibe CLI output (terminal)
	•	Logs/run reports
	•	Offline-friendly “teletext” visuals
	•	Copy/paste stable layouts
	•	Remote/low-bandwidth display (beacons)

2) Canvas model

Dimensions (fixed)
	•	Width: 80 columns
	•	Height: 30 rows
	•	Coordinate system:
	•	x: 0..79
	•	y: 0..29
	•	Origin: top-left (0,0)

Character model
	•	Base cell is one Unicode codepoint.
	•	Default: ASCII-safe.
	•	Optional “extended glyph mode” allows box drawing characters.

Colour model (optional)
	•	ANSI colour output allowed as a renderer backend.
	•	Canonical output is plain text; colour is a decoration layer.

3) Output format (canonical)

A render produces:
	•	header (metadata)
	•	body (80×30 grid)
	•	footer (optional diagnostics)

Canonical packaging (recommended)

--- udos-grid:v1
size: 80x30
title: "Daily Schedule"
mode: "calendar"
theme: "mono"
ts: 2026-02-03T19:14:00+10:00
---

<30 lines of exactly 80 chars>

--- end ---

Rules:
	•	Exactly 30 lines in body.
	•	Each body line is exactly 80 visible columns (after stripping ANSI).
	•	No tabs. Newlines only at row boundaries.

4) Rendering pipeline

Stage A — Layout

Input data is transformed into layout primitives:
	•	Boxes / panels
	•	Text blocks
	•	Tables
	•	Lists
	•	Mini-maps
	•	Sparklines (optional)

Stage B — Draw

Primitives are drawn into a Canvas80x30 buffer.

Stage C — Emit backend
	•	plain: fixed-width text
	•	ansi: terminal coloured output
	•	json: machine-readable layout + buffer (for tests)

5) Primitives (minimum set)

5.1 Box

Draw a rectangle with border style.

box(x, y, w, h, style="single", title?)

Styles:
	•	single: + - |
	•	double: ╔═╗║ (optional)
	•	none: no border (panel spacing only)

5.2 Text block

Wrap and clip text to a region.

text(x, y, w, h, content, align="left", valign="top", wrap=true, ellipsis=true)

5.3 Table

Render rows/cols with optional headers.

table(x, y, w, h, columns, rows, opts)

Features:
	•	column widths fixed or auto-fit
	•	clipping
	•	row separators optional
	•	“selected row” highlight (ansi backend)

5.4 List

Bulleted or numbered list.

list(x, y, w, h, items, bullet="•" | "-" | ">" )

5.5 Mini-map (grid map)

Render your 80×30 world grid or a subwindow of it.

minimap(x, y, w, h, cells, focusCell?, overlays?)

Cells can be:
	•	empty
	•	occupied
	•	selected
	•	tagged (file markers, tasks, events)

6) Layout modes (built-in specs)

6.1 Dashboard mode

Use case: “today view” / mission status / node status

Layout:
	•	top banner (title + clock)
	•	left: mission queue
	•	right: stats (API quota, ollama models, node state)
	•	bottom: recent logs

6.2 Calendar mode (week/day)

Use case: tasks + schedule in 80×30

Two variants:
	•	Day: timeline left, tasks right
	•	Week: 7 columns, compact rows

Day template:
	•	0–1: header
	•	2–28: timeline (hours) + event blocks
	•	29: footer controls

6.3 Schedule mode (agenda)

Use case: upcoming items

Layout:
	•	header
	•	table: time | item | location (or LocId)
	•	footer: filters

6.4 Table mode

Use case: dataset preview, sqlite query results

Layout:
	•	header (query + row count)
	•	table region with scroll indicator
	•	footer (page/offset)

6.5 Map mode (LocId grid)

Use case: show L###-Cell overlays

Map area shows:
	•	cell labels at edges
	•	focus cell highlight
	•	overlay markers:
	•	T tasks
	•	N notes
	•	E events
	•	! alerts
	•	legend box on side/bottom

7) Determinism rules

To keep outputs stable (good for diff/logging):
	•	Sorting:
	•	tasks/events sorted by time, then title
	•	tables sorted by stable key unless user requests otherwise
	•	Wrapping:
	•	stable word wrap
	•	stable truncation (ellipsis)
	•	No dynamic terminal width detection in canonical mode.

8) API spec (TS)

Minimal core API:

export interface GridCanvasSpec {
  width: 80;
  height: 30;
  title?: string;
  theme?: string;
  mode?: "dashboard" | "calendar" | "schedule" | "table" | "map";
}

export interface RenderResult {
  header: Record<string, any>;
  lines: string[];      // 30 lines (80 chars each)
  rawText: string;      // header + lines + footer packaging
}

export interface RendererBackend {
  emit(result: RenderResult): string;  // plain or ansi
}

export interface Canvas80x30 {
  clear(fill?: string): void;
  box(x: number, y: number, w: number, h: number, style?: string, title?: string): void;
  text(x: number, y: number, w: number, h: number, content: string, opts?: any): void;
  table(x: number, y: number, w: number, h: number, columns: any[], rows: any[], opts?: any): void;
  minimap(x: number, y: number, w: number, h: number, cells: any, opts?: any): void;
  toLines(): string[]; // exactly 30 lines
}

CLI entrypoints:
	•	udos-core grid render --mode calendar --input tasks.json
	•	udos-core grid render --mode map --loc EARTH:SUR:L305-DA11 --layer 305

Vibe usage:
	•	Vibe calls the CLI tool and prints the output.
	•	Optional MCP tool wraps these for structured responses.

9) Example output (calendar day)

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

10) Integration points (v1.3)
	•	Spatial: map mode overlays from places and file_place_tags (SQLite)
	•	Tasks: agenda/calendar from tasks index
	•	Missions: dashboard panels from scheduler run logs
	•	Publishing: export run produces a final “report grid” for logs

⸻

11) What to implement first (small win)
	1.	Canvas80x30 buffer + box() + text()
	2.	table() primitive
	3.	calendar day mode template
	4.	map mode overlaying LocId markers

That’s enough for “wow” and sets the foundation.

⸻

If you want, I can also generate:
	•	a core/src/grid/ starter module (TS code)
	•	a couple of “golden test outputs” (snapshots) so your renderer stays deterministic
	•	a simple udos-core grid render CLI skeleton that Vibe can call immediately