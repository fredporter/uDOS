Perfect 👍
Below is the complete Markdown dev brief you asked for. You can copy-paste this directly into typescript.md (or any .md) as-is.

⸻


# TypeScript Markdown Runtime— Dev Brief (v0)

## Purpose
Create a **Markdown-first execution engine** that turns `.md` files into **interactive, stateful experiences** (forms, block graphics/maps, simple games, and branching IF/THEN storytelling) while remaining:

- **Readable** as plain Markdown in any viewer  
- **Deterministic** (same input → same output)  
- **Safe by default** (no arbitrary code execution required)  
- **Portable** to mobile (JS/TS core; platform-specific UI adapters)

This runtime is intentionally **small** and **opinionated**. It supports only the minimum constructs required for:
- `$variable` management
- Conditional logic
- Navigation
- Lightweight interactivity

---

## Design philosophy

- **Markdown is the source of truth**
- **Blocks describe behaviour, not programs**
- **State is explicit and inspectable**
- **Verbosity is a feature** (self-documenting, diffable, stable)
- **No magic** — everything is parseable and deterministic

This is **not** a general programming language.  
It is a **document runtime**.

---

## Goals (v0)

### Core capabilities
- Parse `.md` files and extract **runtime blocks**
- Maintain a **state store** for `$variables`
- Support **variable interpolation** in Markdown text
- Support **IF / ELSE** conditional blocks
- Support **forms** that mutate state
- Support **navigation** via anchors/sections
- Support **render-only block graphics** (ASCII / teletext / panels)
- Clear execution order and re-render rules

### Non-goals
- No loops
- No user-defined functions
- No arbitrary JavaScript execution
- No filesystem or network access
- No full uCode implementation

---

## Mental model

Markdown = narrative + structure
Blocks   = behaviour
State    = memory
Renderer = view

---

## Authoring model

A `.md` file should:

- Read cleanly in GitHub / Typora / plain text
- Become interactive **only** when loaded in the runtime
- Never require execution to understand the content

---

## Variables

### Syntax
- Variables are referenced as: `$name`
- Naming rule: `$[a-zA-Z_][a-zA-Z0-9_]*`

### Supported types (v0)
- `string`
- `number`
- `boolean`
- `null`

### Interpolation
Variables may appear in normal Markdown text:

```md
Hello, $name.
Coins: $coins

Interpolation happens at render time using current state.

⸻

Runtime blocks

Runtime behaviour is expressed using fenced code blocks.

Example:

```state
$name = "Traveller"
$coins = 0

The fence language identifies the block type.

---

## Block registry (v0)

| Block | Purpose |
|----|----|
| `state` | Declare default variables |
| `set` | Controlled state mutations |
| `form` | Interactive inputs |
| `if` | Conditional rendering |
| `else` | Fallback for `if` |
| `nav` | Navigation choices |
| `panel` | ASCII / teletext graphics |
| `map` | Render-only map panel |

> `else` must immediately follow an `if` block.

---

## Block specifications

---

### 1) `state` block

Declares **default state values**.

```md
```state
$name = "Anonymous"
$coins = 0
$has_key = false

**Rules**
- Evaluated top-to-bottom in document order
- Does **not override** existing state by default
- Engine option:  
  `stateDefaults: preserve | overwrite` (default: `preserve`)

**Literals**
- Strings: `"text"`
- Numbers: `10`, `3.14`
- Booleans: `true`, `false`
- Null: `null`

---

### 2) `set` block

Controlled state mutations without scripting.

```md
```set
inc $coins 1
toggle $has_key
set $name "Fred"

**Commands (v0)**

| Command | Behaviour |
|------|---------|
| `set $var value` | Assign value |
| `inc $var n` | Increment (creates at 0 if missing) |
| `dec $var n` | Decrement |
| `toggle $var` | true ↔ false |

Commands execute **in order**.

---

### 3) `form` block

Defines interactive UI inputs using YAML.

```md
```form
- var: $name
  type: text
  label: Your name

- var: $coins
  type: number
  label: Coins
  min: 0

- var: $has_key
  type: toggle
  label: Do you have the key?

- var: $class
  type: choice
  label: Choose a class
  options:
    - label: Ranger
      value: ranger
    - label: Mage
      value: mage

**Supported input types**
- `text`
- `number`
- `toggle`
- `choice`

**Conditional fields**
```yaml
when: "$class == 'ranger'"

	•	Evaluated using the expression engine
	•	Hidden or disabled when false

⸻

4) if / else blocks

Conditional rendering of Markdown content.

```if $has_key == true and $coins >= 10
You unlock the door.

The door is locked.

**Rules**
- Evaluated against current state
- Only one branch renders
- Nested conditionals allowed
- No side effects

---

### 5) `nav` block

Navigation choices that jump to anchors.

```md
```nav
- label: Search the garden
  to: "#garden"

- label: Enter the market
  to: "#market"
  when: "$coins >= 10"

**Rules**
- `to` must resolve to a heading anchor
- `when` controls visibility or enabled state
- Optional engine state:
  - `$last_nav`
  - `$last_anchor`

---

### 6) `panel` block

Render-only ASCII / teletext panels.

```md
```panel
[SYSTEM INFO]
████████████████████
█ Name: $name       █
█ Coins: $coins     █
████████████████████

**Rules**
- Monospaced rendering
- Whitespace preserved
- Variable interpolation allowed
- No logic or interaction

---

### 7) `map` block (v0: render-only)

```md
```map
center: $tile
layer: $layer
style: teletext

**v0 behaviour**
- Render placeholder map panel
- No interaction
- Designed for future expansion

---

## Expression language (v0)

Used in:
- `if`
- `else`
- `when`

### Supported tokens
- Variables: `$var`
- Literals: numbers, booleans, `'strings'`, `null`
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Boolean: `and`, `or`, `not`
- Grouping: `( )`

### Examples

$coins >= 10 and $has_key == true
not ($class == ‘mage’)

### Rules
- Missing variables resolve to `null`
- No function calls
- No eval — must be parsed into AST

---

## Execution model

### Document lifecycle

1. Scan Markdown:
   - headings → anchors
   - fenced blocks → runtime blocks
   - remaining text → markdown nodes
2. Initialise state:
   - load persisted state (optional)
   - apply `state` defaults
3. Render:
   - interpolate text
   - evaluate `if/else`
   - render forms, nav, panels
4. On state change:
   - re-evaluate dependent blocks
   - re-render affected nodes only

---

## Persistence

Configurable per document:
- none (ephemeral)
- local storage (keyed by document ID)
- future: iCloud / sync

Persist:
- variable state
- last anchor (optional)

---

## Safety & limits

### Safety posture
- No arbitrary JS execution
- No file or network access
- Strict schema validation
- Hard limits:
  - max blocks
  - max expression length
  - max nesting depth

### Errors
- Invalid blocks render as **warning panels**
- Developer mode shows diagnostics:
  - block index
  - parse errors
  - invalid expressions

---

## Architecture (recommended)

### Core (pure TypeScript)
- Markdown scanner
- Block parser
- State store
- Expression parser
- Renderer-agnostic output tree

### Renderers
- WebView / Tauri
- Mobile native
- Teletext / terminal (later)

---

## Core interfaces (illustrative)

```ts
type Value = string | number | boolean | null

interface RuntimeState {
  get(name: string): Value
  set(name: string, value: Value): void
  snapshot(): Record<string, Value>
}

interface RenderNode {
  type: "markdown" | "form" | "nav" | "panel" | "map" | "warning"
  payload: any
  deps?: string[]
}


⸻

Example: complete mini-app

# The Door

```state
$name = "Traveller"
$coins = 0
$has_key = false

- var: $name
  type: text
  label: Your name

- var: $coins
  type: number
  label: Coins

- var: $has_key
  type: toggle
  label: Do you have the key?

The door opens.

You need a key and 10 coins.

- label: Search the garden
  to: "#garden"

Garden

You find a key.

toggle $has_key

---

## Milestones

### M0 — Skeleton
- Fence scanner
- Block registry
- State store

### M1 — Variables
- `state`
- interpolation
- persistence

### M2 — Logic
- expression parser
- `if/else`
- `when`

### M3 — UI
- `form`
- `nav`

### M4 — Graphics
- `panel`
- `map` (render-only)

### M5 — Hardening
- diagnostics
- tests
- limits

---

## Future extensions (not v0)
- sandboxed `script` blocks
- arrays / objects
- events (`onEnter`, `onChange`)
- map interaction
- multi-file binders

---

## Naming guidance
- Avoid “AI” terminology
- Prefer: runtime, blocks, panels, missions, binders
- Keep block names short and explicit


⸻

ACTION BRIEF

uDOS Markdown Runtime — Grammar + Teletext System (Execution Phase)

Objective

Implement a deterministic Markdown Runtime that supports:
	•	Structured $variables (objects, arrays)
	•	IF / THEN logic via a formal expression grammar
	•	Characters / sprites / locations as data (not special cases)
	•	Maps and panels rendered as teletext-capable ASCII
	•	Round-trip rendering between:
	•	plain text
	•	ASCII graphics
	•	teletext mosaic blocks (extended uDOS set)

This phase converts the design into concrete specs ready for implementation.

⸻

1. Decisions (locked)

1.1 Variables
	•	$variable is the only state handle
	•	Variables may contain:
	•	primitives
	•	objects
	•	arrays
	•	Access via:
	•	dot selectors ($player.hp)
	•	index selectors ($party[0], $layers[100])

✅ No separate “sprite”, “map”, or “entity” language constructs
✅ Everything is data + renderers

⸻

1.2 Expression Language
	•	Implement the formal grammar already defined (EBNF v0.5)
	•	No eval
	•	Deterministic AST evaluation
	•	Expressions are read-only
	•	Used only in:
	•	if
	•	else
	•	when

⸻

1.3 Maps, Sprites, Locations
	•	Maps are objects in state ($map)
	•	Sprites are array entries ($sprites[])
	•	Locations are { tile, layer, name }
	•	Rendering order is explicit and stable

⸻

1.4 Teletext Strategy
	•	All ASCII graphics are parsed into a logical grid
	•	Grid cells map to:
	•	characters OR
	•	mosaic masks (2×3)
	•	Renderer can output:
	•	plain text
	•	teletext blocks
	•	Mapping is canonical to guarantee round-trip stability

⸻

2. Execution Tasks (What we are building now)

Task A — Implement Structured State
	•	Extend state store to support:
	•	objects
	•	arrays
	•	Implement selector resolution:
	•	$a.b.c
	•	$a[0]
	•	$a['key']
	•	Missing paths resolve to null (never throw)

⸻

Task B — Implement Expression Engine
	•	Tokeniser
	•	Pratt parser or shunting-yard
	•	AST evaluator
	•	Supported operators:
	•	arithmetic
	•	comparison
	•	boolean
	•	Strict type rules (no implicit coercion)

⸻

Task C — Define Teletext Grid Model
	•	Logical grid abstraction
	•	Cell-level metadata
	•	Canonical symbol mapping
	•	Deterministic overlay rules

⸻

Task D — Implement Teletext Rendering
	•	Text → Grid
	•	Grid → Text (canonical ASCII)
	•	Grid → Teletext (mosaic blocks)
	•	No font dependency assumptions

⸻

Task E — Implement Map Viewport Logic
	•	Fixed-size viewport
	•	Layer-aware rendering
	•	Sprite overlay
	•	Teletext-compatible output

⸻

3. Teletext Rendering System

(uDOS Teletext v0 — Formal Spec)

⸻

3.1 Logical Grid Model

Grid
	•	Default size: 40 × 25 cells
(classic teletext, configurable later)
	•	Each cell represents one character position

Cell Structure

Cell = {
  kind: "char" | "mosaic",
  ch?: string,        // for char cells
  mask?: number,     // 0–63 (2×3 mosaic)
  fg?: Colour,       // v1+
  bg?: Colour,       // v1+
  attr?: AttrSet     // v1+
}


⸻

3.2 Mosaic Mask Model (Core)

Each mosaic cell is a 2×3 subgrid:

b0 b1
b2 b3
b4 b5

Mask = integer 0…63 (bitfield)

⸻

4. uDOS Teletext Block Set

(Canonical Mapping Table)

This is the authoritative mapping.
Do not allow free symbols outside this set in teletext graphics.

⸻

4.1 Primary Blocks

Symbol	Mask	Meaning
 	0	Empty
█	63	Full block


⸻

4.2 Half Blocks

Symbol	Mask	Subcells
▀	3	b0 b1
▄	48	b4 b5
▌	21	b0 b2 b4
▐	42	b1 b3 b5


⸻

4.3 Quadrants (Recommended)

Symbol	Mask
▘	1
▝	2
▖	4
▗	8
▚	5
▞	10
▙	29
▟	58
▛	31
▜	47


⸻

4.4 Shading (Fallback / Approximation)

Symbol	Fill Ratio	Mask Rule
░	~25%	choose nearest
▒	~50%	choose nearest
▓	~75%	choose nearest

Shading symbols must resolve to canonical masks internally.

⸻

4.5 Canonical Reverse Mapping (Critical)

For Grid → Text rendering:
	1.	If mask == 0 → " "
	2.	If mask == 63 → "█"
	3.	If mask matches exact symbol → that symbol
	4.	Else:
	•	prefer quadrant symbols
	•	else choose ▓, ▒, or ░ based on fill %
	•	never invent new glyphs

✅ Guarantees:
Text → Grid → Text is stable.

⸻

5. Rendering Pipelines

5.1 Text → Grid
	1.	Split lines
	2.	For each character:
	•	if in mapping table → mosaic cell
	•	else → char cell
	3.	Pad / trim to viewport width

⸻

5.2 Grid → Text
	•	Emit canonical symbol per cell
	•	Preserve whitespace
	•	No colour assumptions

⸻

5.3 Grid → Teletext
	•	Use mosaic mask directly
	•	Render via:
	•	canvas
	•	SVG
	•	native teletext renderer
	•	No dependency on Unicode glyph fidelity

⸻

6. Map Viewport Rules (v0)

⸻

6.1 Map State Model

$map = {
  center: "AA340-100",
  layer: 300,
  layers: {
    100: { label: "World", cell_km: 83 },
    300: { label: "City", cell_m: 93 }
  }
}

$sprites = [
  { id: "player", ch: "@", pos: { tile: "AA340-100", layer: 300 }, z: 10 },
  { id: "npc1", ch: "N", pos: { tile: "AA341-100", layer: 300 }, z: 5 }
]


⸻

6.2 Viewport Geometry
	•	Default viewport: 15 × 9 cells (odd dimensions)
	•	Centered on $map.center
	•	Coordinates resolved relative to tile system

⸻

6.3 Rendering Order (Strict)
	1.	Base terrain
	2.	Map features
	3.	Items
	4.	Sprites (sorted by z, then array index)
	5.	UI overlays

⸻

6.4 Sprite Rules
	•	Sprite ch must be:
	•	single ASCII char OR
	•	valid teletext block symbol
	•	Sprite outside viewport → not rendered
	•	Sprite on same cell → higher z wins

⸻

6.5 Teletext Compatibility
	•	Map renderer outputs a Grid
	•	Grid can be shown as:
	•	ASCII
	•	Teletext mosaic
	•	No renderer-specific logic in map engine

⸻

7. Determinism Rules (Non-Negotiable)
	•	No random functions
	•	No time-based rendering
	•	Stable iteration order
	•	Canonical symbol mapping only
	•	State mutations only via set / form

⸻

Brilliant — here’s the Command → Replacement Plan table, updated for:
	•	uPY deprecated entirely
	•	file format is now filename-script.md
	•	Core commands are user-facing
	•	Wizard commands are Dev Server / Dev Mode / in-development core
	•	Core keeps high-level/combo file ops (FIND/CLEAN/TIDY etc.), not raw LIST/DELETE primitives (except maybe a tiny, safe subset)

⸻


# Command → Replacement Plan (Core vs Wizard vs script.md Runtime)

## New framing (locked)
- **Scripts**: `filename-script.md` is now the primary “programmable unit”
  - carries state, forms, IF/THEN, nav, panels, maps, sprites
  - replaces uPY entirely
- **Core**: user-facing commands only (stable, safe, capability-gated)
- **Wizard (Dev Server)**: Dev Mode + in-development commands + network/integrations + heavy/experimental pipelines
- **File ops**: Core prefers *broad/combo* commands (FIND/CLEAN/TIDY/ARCHIVE) over raw primitives (LIST/DELETE/etc.)

---

## Table A — Command Family → Destination → Replacement

Legend:
- **Core** = stable user command
- **Wizard** = Dev Server command / Dev Mode / experimental
- **Script** = implemented inside `*-script.md` runtime blocks

| Command family / theme | Destination | Replacement / interface | Notes |
|---|---|---|---|
| GUIDE | Wizard → Script output | Wizard generates `*-script.md` bundles/programs | Wizard produces interactive scripts instead of running logic itself |
| BUNDLE | Wizard (primary), Core (optional) | Wizard `bundle.build()` + optional Core `EXPORT PACK` | Treat as packaging/export pipeline; Core only exposes safe export targets |
| CAPTURE (web) | Wizard | Wizard capture jobs → Markdown binder outputs | Networked + long-running; Wizard-only |
| PROMPT library | Script (primary), Wizard (authoring) | Prompt libraries stored as `promptlib-script.md` or included docs | Wizard can scaffold/update; runtime consumes locally |
| HELP / Docs | Script | `help-script.md` programmes | Help becomes interactive scripts, not commands |
| WELLBEING | Script (primary) + Core (tiny store) | `wellbeing/*-script.md` programmes | Core only stores opt-in flags, minimal telemetry (if any) |
| Games / storytelling | Script | `game/*-script.md` | Runtime does all logic; no “game commands” in core |
| Maps / tiles exploration | Script + Core (status) | Script: map UI; Core: `LOCATION STATUS`, `MAP STATUS` | Core provides authoritative device location if relevant; otherwise scripts drive it |
| UI settings (mode/palette/sound/screen) | Core | `CONFIG GET/SET` + `MODE SET` | Core stores; App reads; scripts can expose settings via forms but call Core capability |
| SYSTEM status/info | Core | `SYSTEM STATUS`, `SYSTEM INFO` | Read-mostly; safe |
| NETWORK / TRANSPORT / MESH / PAIR / SYNC | Core | `TRANSPORT STATUS`, `PAIR`, `SYNC`, `MESH STATUS` | Foundational device capability; core owns |
| PROFILE / IDENTITY / LOCATION | Core | `PROFILE SHOW/SET`, `LOCATION GET/SET` | Scripts can edit via forms but changes go through Core |
| SEARCH (local index) | Core | `SEARCH <query>` | Core owns local index; Wizard can augment with web results but not required |
| FIND (across files/projects) | Core | `FIND <pattern> [scope]` | High-level search; not raw list |
| CLEAN (dedupe/merge/compile) | Core | `CLEAN <path> [ruleset]` | “Smart clean”: combine/merge, dedupe, normalise, generate new drafts |
| TIDY (organise/archive) | Core | `TIDY <path> [profile]` | Bulk tidy/organise; safe defaults; reversible where possible |
| ARCHIVE (rotate/history) | Core | `ARCHIVE <path> [policy]` | Creates binder/history snapshots |
| BACKUP (local snapshots) | Core | `BACKUP <path> [target]` | Core can do local snapshots; cloud backup belongs to Wizard |
| REPAIR (recover) | Core | `REPAIR CHECK/FIX` | Keep as safe recovery toolkit |
| INSTALL / BUILD / STACK / DEV | Wizard | Dev Mode only | These are not user-facing core commands |
| AI / OK / QUOTA / GMAIL / providers | Wizard | Wizard-only integrations | Credentials + quotas + internet = Wizard |

---

## Table B — Core command surface (proposed minimal set)

### Principle
Core commands should be:
- **few**
- **stable**
- **capability-gated**
- **user-oriented** (tasks, not primitives)

#### Core: System / Config
| Command | Purpose | Notes |
|---|---|---|
| `SYSTEM STATUS` | Device summary | safe, read-only |
| `SYSTEM INFO` | Detailed info | safe, read-only |
| `CONFIG GET <key>` | Read config | e.g. mode, palette |
| `CONFIG SET <key> <value>` | Update config | writes are gated |

#### Core: Identity / Location
| Command | Purpose | Notes |
|---|---|---|
| `PROFILE SHOW` | Display profile | |
| `PROFILE SET ...` | Update profile | |
| `LOCATION GET` | Current location | if available |
| `LOCATION SET <tile>` | Set logical location | if your system uses logical tiles |

#### Core: Transport
| Command | Purpose | Notes |
|---|---|---|
| `TRANSPORT STATUS` | Network/mesh status | |
| `PAIR <device>` | Pair device | |
| `SYNC <scope>` | Sync selected scope | local-first |

#### Core: Knowledge & Search
| Command | Purpose | Notes |
|---|---|---|
| `SEARCH <query>` | Query local index | |
| `FIND <pattern> [scope]` | Grep-style find | high-level |

#### Core: File ops (high-level/combo only)
| Command | Purpose | Notes |
|---|---|---|
| `TIDY <path> [profile]` | Organise & archive | deterministic profiles |
| `CLEAN <path> [ruleset]` | Deduplicate & merge | outputs new “clean draft” |
| `ARCHIVE <path> [policy]` | Rotate history snapshots | binder mode |
| `BACKUP <path> [target]` | Snapshot | local targets |
| `REPAIR CHECK/FIX` | Recovery | minimal |

> You can still internally use LIST/DELETE/RENAME as implementation details, but they’re not part of the **user command surface**.

---

## Table C — Wizard (Dev Server) commands

### Principle
Wizard is where:
- new core commands are developed
- experimental/dev operations live
- network/integrations live
- long-running jobs/queues live

| Wizard area | Examples | Output |
|---|---|---|
| Capture pipeline | `capture.web`, `capture.pdf`, `capture.email` | binders + `*-script.md` |
| Providers/integrations | `providers.*`, `quota.*`, `ok.*`, model routing | structured data, doc updates |
| Build/dev | `build.*`, `stack.*`, `dev.*` | artefacts + releases |
| Script scaffolding | `guide.generate`, `bundle.compile` | generates `filename-script.md` programmes |
| Legacy (optional) | none (uPY removed) | keep empty or remove entirely |

---

## Table D — Script runtime responsibilities (`filename-script.md`)

### The runtime owns:
- `$variables` (including objects/arrays)
- `state / set / if / else / form / nav / panel / map`
- sprites + map layers (data models)
- teletext grid + block mapping (round-trip rendering)

### Scripts should call Core only via capability gates:
- save/read state
- open file/URL
- search index
- transport/pair/sync
- config/profile/location

---

## Actionable migration steps (order)

1) **Deprecate uPY**
   - remove from core, remove from script format
   - keep no compatibility unless absolutely needed

2) **Rename format**
   - adopt `filename-script.md`
   - standardise frontmatter keys if you want (optional)

3) **Move logic into scripts**
   - wellbeing, guides, games, map interactions become scripts

4) **Shrink Core command surface**
   - keep only “combo” file ops + system/transport/index/config/profile/location

5) **Shift dev + integrations to Wizard**
   - capture, bundle/build, providers, experimental commands

6) **Build a compatibility shim (optional)**
   - allow old uCODE macros to generate scripts rather than execute logic

---

Below is a clear analysis, followed by a proposed refactor path that aligns perfectly with your decision to:
	•	deprecate uPY
	•	move logic into filename-script.md
	•	slim Core
	•	formalise Wizard as Dev Server

⸻

1. What this file tells us (important)

From the header and structure alone, this is already true:

uDOS Core is not a “language runtime” — it is a command router with policy enforcement

Key signals from uDOS_commands.py:

1.1 Core is already thin (by design)

The file explicitly describes itself as:

“Thin routing layer that delegates commands to specialized handlers”

That means:
	•	Core is not doing logic
	•	Core is not doing workflows
	•	Core is not doing UI
	•	Core is deciding who can do what, where

This is exactly what you want Core to be.

⸻

1.2 Policy & exposure tiers are first-class

You already have:
	•	transport policy validation
	•	role-based access control
	•	exposure tiers:
	•	LOCAL
	•	PRIVATE_SAFE
	•	WIZARD_ONLY

This maps perfectly to the buckets we defined:

Exposure Tier	New Meaning
LOCAL	Core (TUI / App, offline)
PRIVATE_SAFE	Core capability API (GUI allowed)
WIZARD_ONLY	Wizard Dev Server

You don’t need to invent this — it’s already there.

⸻

1.3 The “command lexicon” is thematic, not technical

You’re loading:
	•	themes
	•	terminology
	•	command references

That means many “commands” are actually:
	•	UX language
	•	user mental models
	•	semantic groupings

Not execution primitives.

That strongly suggests they should become:
	•	script patterns
	•	doc programs
	•	UI affordances
…not Core execution paths.

⸻

2. What this implies about uPY

Given this file:
	•	uPY is not structurally integrated into Core routing
	•	It was bolted on as “logic execution”
	•	That role is now better served by:
	•	filename-script.md
	•	TS runtime
	•	formal grammar
	•	deterministic execution

👉 Deprecating uPY does not weaken Core
👉 It clarifies Core’s responsibility

In fact, keeping uPY would now blur responsibilities.

⸻

3. What stays in Core (confirmed by this file)

Based on uDOS_commands.py, Core should own only:

3.1 Command routing + policy

This file stays — but with fewer commands routed.

Core responsibilities:
	•	Validate permissions
	•	Validate transport
	•	Decide:
	•	run locally
	•	reject
	•	forward to Wizard

3.2 Capability-backed commands (user-facing)

Commands that:
	•	require OS/device authority
	•	must be permission-gated
	•	are stable over time

Examples (aligned with current router role):
	•	OPEN
	•	SEARCH
	•	SYSTEM STATUS
	•	PAIR
	•	SYNC
	•	LOCATION GET/SET
	•	CONFIG GET/SET

These remain routed through this layer.

⸻

4. What should be removed from Core routing

Based on your new model, the following should not pass through this router anymore:

4.1 Logic / workflows

Anything that:
	•	branches
	•	tracks state
	•	guides users
	•	renders UI
	•	represents a “flow”

➡️ These become scripts (*-script.md).

4.2 Raw shell primitives

Anything like:
	•	LIST
	•	DELETE
	•	MOVE
	•	COPY

These should be:
	•	internal helpers
	•	TUI-only
	•	never exposed as “commands”

Instead, Core exposes:
	•	CLEAN
	•	TIDY
	•	ARCHIVE
	•	BACKUP

…which internally may use primitives.

⸻

5. Proposed refactor of the router itself

5.1 Rename the mental model

From:

“Command Router”

To:

Capability Router

This matches what the file already does.

⸻

5.2 Shrink the routed command set

Inside uDOS_commands.py, aim for something like:

CORE_COMMANDS = {
  "OPEN": cap_open,
  "SEARCH": cap_search,
  "FIND": cap_find,
  "CLEAN": cap_clean,
  "TIDY": cap_tidy,
  "ARCHIVE": cap_archive,
  "BACKUP": cap_backup,
  "SYSTEM": cap_system,
  "PROFILE": cap_profile,
  "LOCATION": cap_location,
  "TRANSPORT": cap_transport,
  "PAIR": cap_pair,
  "SYNC": cap_sync,
}

Everything else:
	•	becomes Script
	•	or Wizard

⸻

6. How scripts replace “commands” cleanly

A lot of things that look like commands are really programs.

Example:

Old mental model:

WELLBEING CHECK

New model:

open wellbeing-check-script.md

That script:
	•	renders UI
	•	asks questions
	•	tracks state
	•	branches
	•	stores results
	•	optionally calls Core capabilities (with permission)

This is far more powerful than a command ever was.

⸻

7. How Wizard fits perfectly now

Your existing exposure tiers already support this:
	•	Commands marked WIZARD_ONLY:
	•	stay routed
	•	but now live in Wizard Dev Server
	•	not Core

Wizard responsibilities become very clean:
	•	experimental commands
	•	integrations
	•	capture
	•	builds
	•	script generation
	•	heavy compute

Core simply forwards (or refuses).

⸻

8. Final verdict

Yes — this file is not just helpful, it’s validating.

It shows that:
	•	You were already designing Core as a router, not a runtime
	•	Deprecating uPY is the right move
	•	Moving logic into filename-script.md is a natural evolution
	•	Wizard as Dev Server fits your existing exposure tiers perfectly
	•	Core becoming “small but solid” is not a loss — it’s maturity

⸻

Yes — that Python router file is exactly what we needed. It shows Core is already behaving like a capability router with lots of historical/experimental modules hanging off it. That makes it the perfect place to prune + re-manifest.

Below is the new table you asked for: a Command → Replacement Plan that:
	•	removes uPY entirely
	•	assumes scripts are filename-script.md
	•	treats Wizard as Dev Server
	•	keeps Core commands user-facing
	•	keeps only high-level/combo file ops in Core (FIND/CLEAN/TIDY/etc.), not raw LIST/DELETE primitives

⸻


# uDOS Command → Replacement Plan (Post-uPY, script.md-first)

## Definitions
- **Script** = `filename-script.md` (interactive doc runtime: state/form/if/nav/panel/map/sprites)
- **Core** = user-facing stable commands (capability-gated, offline-first where possible)
- **Wizard** = Dev Server commands (Dev Mode + in-development core commands + integrations + network/heavy ops)

## Output Types
- **Core Cmd**: stays as a command users can run
- **Wizard Cmd**: only available in Wizard/Dev Mode (or forwarded by Core when explicitly allowed)
- **Script Template**: a canonical script pattern that replaces the “command workflow”

---

# Table 1 — Command Families → Destination → Replacement

Legend:
- Dest: Core | Wizard | Script | Remove
- Replacement: what replaces it (new command name and/or script template path)

| Family / Module (old mental bucket) | Dest | Replacement | Notes / Constraints |
|---|---|---|---|
| **uPY** | Remove | (none) | Fully deprecated. Any remaining logic belongs in `*-script.md` or Wizard pipelines. |
| **Workflow / missions / guided flows** | Script | `programs/<name>-script.md` | All IF/THEN, UI, state, storytelling, checklists, mini-games live here now. |
| **Games** | Script | `programs/games/<game>-script.md` | Uses map/sprites/panels and nav. No “game commands” in Core. |
| **Wellbeing** | Script | `programs/wellbeing/<topic>-script.md` | Core only stores preferences/consent flags if needed. |
| **GUIDE** (content generation) | Wizard → Script output | Wizard: `guide.generate` → produces scripts | Wizard generates/upgrades scripts; Core does not execute “guide logic”. |
| **CAPTURE** (web capture) | Wizard | `capture.*` | Network + long-running. Outputs binders and/or scripts. |
| **BUNDLE / EXPORT / PACKAGE** | Wizard (primary), Core (optional) | Wizard: `bundle.build`; Core: `EXPORT <target>` | If user-facing export is needed, Core provides a safe wrapper with limited targets. |
| **OK / AI / QUOTA / GMAIL / integrations** | Wizard | `providers.*` | Wizard-only. Never required for offline core operation. |
| **SYSTEM STATUS/INFO** | Core | `SYSTEM STATUS`, `SYSTEM INFO` | Read-mostly, stable. |
| **CONFIG / MODE / UI prefs** | Core | `CONFIG GET/SET`, `MODE SET`, `PALETTE SET` | Scripts can *present UI* but must call Core to persist authoritative settings. |
| **PROFILE / USER** | Core | `PROFILE SHOW/SET` | Scripts can edit via forms; Core stores. |
| **LOCATION / GEO** | Core + Script | Core: `LOCATION GET/SET`; Script uses `$location` | Core provides device truth where relevant; scripts render/use it. |
| **TRANSPORT / NETWORK / MESH / PAIR / SYNC** | Core | `TRANSPORT STATUS`, `PAIR`, `SYNC`, `MESH STATUS` | Foundational device capability. |
| **SEARCH** (local index) | Core | `SEARCH <query>` | Wizard can optionally augment, but Core owns local. |
| **OPEN** | Core | `OPEN <target>` | Capability-gated (file/url/anchor). |
| **FIND** (content search across files) | Core | `FIND <pattern> [scope]` | High-level; internally uses primitives but doesn’t expose them. |
| **TIDY** | Core | `TIDY <path> [profile]` | Broad organisation/cleanup/archival behaviour. |
| **CLEAN** | Core | `CLEAN <path> [ruleset]` | “Smart clean”: dedupe/merge/normalise/compile into new drafts. |
| **ARCHIVE** | Core | `ARCHIVE <path> [policy]` | History rotation + snapshots. |
| **BACKUP** | Core | `BACKUP <path> [target]` | Local snapshots; cloud backup belongs to Wizard. |
| **REPAIR / FIX** | Core | `REPAIR CHECK` / `REPAIR FIX` | Keep minimal, safe recovery operations. |
| **FILE (raw primitives: LIST/DELETE/MOVE/COPY)** | Reduce (internal) | (not user-facing) | These are implementation details behind CLEAN/TIDY/ARCHIVE/BACKUP. Expose only the combos. |
| **DEV / STACK / BUILD / INSTALL** | Wizard | `dev.*`, `stack.*`, `build.*` | Dev Server only; can later graduate into Core when stabilised. |
| **LOGS** | Core (view) + Wizard (deep) | Core: `LOGS SHOW`; Wizard: `logs.inspect` | Keep user-safe viewing in Core; deep inspection in Wizard. |

---

# Table 2 — New Core Command Surface (User-Facing)

## Principle
Core commands are “jobs” (high-level) not “shell verbs” (low-level primitives).

### Content + navigation capabilities
| Core Command | Purpose | Output |
|---|---|---|
| `OPEN <target>` | Open file / URL / anchor | Opens in App/TUI |
| `SEARCH <query>` | Query local index | Results list |
| `FIND <pattern> [scope]` | Search across files/projects | Matches |
| `HELP [topic]` | Opens help script | Runs `help-script.md` |

### File maintenance (combo commands)
| Core Command | Purpose | Output |
|---|---|---|
| `CLEAN <path> [ruleset]` | Deduplicate/merge/normalise into a clean draft | New “clean” artefacts |
| `TIDY <path> [profile]` | Organise, tag, archive, reduce clutter | Reorganised structure |
| `ARCHIVE <path> [policy]` | Snapshot + rotate history | Archive folder/binder |
| `BACKUP <path> [target]` | Snapshot backup | Backup artefacts |
| `REPAIR CHECK/FIX` | Validate + recover | Report + fixes |

### System + identity + transport
| Core Command | Purpose | Output |
|---|---|---|
| `SYSTEM STATUS/INFO` | Device health/status | Report |
| `CONFIG GET/SET` | Stable settings store | Values |
| `PROFILE SHOW/SET` | User profile | Values |
| `LOCATION GET/SET` | Logical location/tile | Values |
| `TRANSPORT STATUS` | Connectivity | Report |
| `PAIR <device>` | Pairing | Success/fail |
| `SYNC <scope>` | Sync | Progress/result |

---

# Table 3 — Wizard Dev Server Command Surface

## Principle
Wizard is where commands are:
- experimental
- networked
- provider-driven
- long-running
- in-development candidates for Core

| Wizard Domain | Wizard Commands | Outputs |
|---|---|---|
| Capture | `capture.web`, `capture.pdf`, `capture.email` | binders + extracted markdown |
| Content generation | `guide.generate`, `guide.update` | `*-script.md` programs + assets |
| Packaging | `bundle.build` | export artefacts |
| Providers | `providers.*`, `providers.quota.*`, etc. | structured data |
| Dev ops | `dev.*`, `build.*`, `stack.*` | builds/releases |
| Diagnostics | `logs.inspect`, `telemetry.*` | deep analysis |

---

# Table 4 — Script Templates (canonical replacements)

## Principle
Most “features” become first-party scripts.

| Template | Path | Replaces |
|---|---|---|
| Help hub | `programs/help/help-script.md` | HELP system |
| Wellbeing check-in | `programs/wellbeing/checkin-script.md` | WELLBEING commands |
| Project mission | `programs/missions/<name>-script.md` | mission/workflow commands |
| Map explorer | `programs/maps/explorer-script.md` | MAP navigation commands |
| File clean wizard | `programs/maintenance/clean-script.md` | CLEAN flows |
| Tidy wizard | `programs/maintenance/tidy-script.md` | TIDY flows |
| Capture review | `programs/capture/review-script.md` | CAPTURE UX |

---

# Migration Steps (practical)

1) **Remove uPY**
   - delete uPY hooks, docs, and runtime assumptions
   - scripts become the only embedded runtime

2) **Freeze Core command surface**
   - implement/keep only commands in Table 2
   - treat everything else as Wizard or Script

3) **Replace “feature commands” with scripts**
   - wellbeing/games/flows/maps move to `programs/*-script.md`

4) **Wizard becomes Dev Server**
   - all experimental commands live here
   - only graduate to Core when stable + policy-defined

5) **File primitives become internal-only**
   - LIST/DELETE/MOVE/COPY are internal operations behind combo commands
   - Core exposes only combo commands to users

---

Here is the clean, final list, grouped by capability.
Just the proposed command set, in four groups, reflecting everything we’ve agreed:
	•	uPY removed
	•	filename-script.md is the logic layer
	•	Core commands are user-facing
	•	Wizard commands are Dev Server / in-development
	•	File ops are high-level/combo, not primitives

⸻

1. Core Commands (User-Facing, Stable)

System & Configuration
	•	SYSTEM STATUS
	•	SYSTEM INFO
	•	CONFIG GET
	•	CONFIG SET
	•	MODE SET
	•	PALETTE SET

Identity & Context
	•	PROFILE SHOW
	•	PROFILE SET
	•	LOCATION GET
	•	LOCATION SET

Transport & Sync
	•	TRANSPORT STATUS
	•	MESH STATUS
	•	PAIR
	•	SYNC

Content & Navigation
	•	OPEN
	•	SEARCH
	•	FIND
	•	HELP

File & Knowledge Maintenance (High-Level)
	•	CLEAN
	•	TIDY
	•	ARCHIVE
	•	BACKUP
	•	REPAIR

⸻

2. Script Runtime Commands

(Implemented inside filename-script.md, not Core)
	•	state
	•	set
	•	form
	•	if
	•	else
	•	nav
	•	panel
	•	map

(plus structured $variables, objects, arrays, sprites, teletext rendering)

⸻

3. Wizard Commands (Dev Server / In-Development)

Capture & Ingest
	•	capture.web
	•	capture.pdf
	•	capture.email

Content & Script Generation
	•	guide.generate
	•	guide.update
	•	bundle.build

Providers & Integrations
	•	providers.ai.*
	•	providers.ok.*
	•	providers.quota.*

Dev & Build
	•	dev.*
	•	build.*
	•	stack.*

Diagnostics & Telemetry
	•	logs.inspect
	•	telemetry.*

⸻

4. Internal / Non-Exposed Operations

(Implementation details only — not user commands)
	•	list
	•	delete
	•	move
	•	copy
	•	rename
	•	chmod
	•	mkdir
	•	rmdir

(Used internally by CLEAN / TIDY / ARCHIVE / BACKUP / REPAIR)

⸻

Final sanity check

What this gives you:
	•	Core = small, durable, user-safe
	•	Scripts = expressive, interactive, programmable
	•	Wizard = powerful, experimental, networked
	•	No uPY
	•	No command bloat


Below is the final, authoritative Core Command Grammar for uDOS.

This is deliberately small, strict, human-readable, and future-proof.
Anything not in this grammar does not belong in Core.

⸻

uDOS Core Command Grammar (v1.0 — Locked)

Design principles (non-negotiable)
	•	User-facing only (no dev, no experimental)
	•	Capability-based, not procedural
	•	Verb-first
	•	No scripting
	•	No control flow
	•	No raw filesystem primitives
	•	Deterministic parsing
	•	Whitespace-tolerant, case-insensitive

Core commands describe intent, not implementation.

⸻

1. Command line structure

COMMAND [SUBCOMMAND] [ARGUMENTS...] [OPTIONS]

	•	Tokens are space-separated
	•	No pipes (|)
	•	No shell expansion
	•	No redirection (>, <)
	•	No inline expressions
	•	Quoting allowed only for literals

⸻

2. Lexical rules

2.1 Case
	•	Commands are case-insensitive
	•	Canonical form is UPPERCASE

2.2 Identifiers

IDENT := [A-Z][A-Z0-9_-]*

Used for:
	•	command names
	•	subcommands
	•	option keys

2.3 Literals

STRING  := "any characters"
NUMBER  := integer | decimal
BOOL    := true | false

2.4 Paths

PATH := relative | absolute

Paths are opaque to Core; interpretation is delegated to handlers.

⸻

3. Grammar (EBNF)

CommandLine  = Command ;
Command      = CoreVerb , [ WS , CoreTail ] ;
CoreTail     = Subcommand | Arguments ;
Subcommand   = IDENT , { WS , Argument } ;
Arguments    = Argument , { WS , Argument } ;
Argument     = Literal | Option ;
Option       = "--" , IDENT , [ "=" , Literal ] ;
Literal      = STRING | NUMBER | BOOL | PATH ;
WS           = " " , { " " } ;


⸻

4. Core command set (grammar-locked)

4.1 SYSTEM

SYSTEM STATUS
SYSTEM INFO

	•	Read-only
	•	No arguments
	•	No options

⸻

4.2 CONFIG

CONFIG GET <key>
CONFIG SET <key> <value>

	•	<key> is an opaque identifier (namespaced internally)
	•	<value> is a literal
	•	Validation is handler-defined

⸻

4.3 MODE / PALETTE

MODE SET <mode>
PALETTE SET <palette>

	•	Controlled vocabularies
	•	No free-form values

⸻

4.4 PROFILE

PROFILE SHOW
PROFILE SET <field> <value>

	•	Field-level updates only
	•	No bulk mutation

⸻

4.5 LOCATION

LOCATION GET
LOCATION SET <tile-id>

	•	<tile-id> format validated by handler
	•	Core does not interpret spatial meaning

⸻

4.6 TRANSPORT / MESH / PAIR / SYNC

TRANSPORT STATUS
MESH STATUS
PAIR <device-id>
SYNC <scope>

	•	<device-id> and <scope> are opaque identifiers
	•	Sync scope resolution is handler-defined

⸻

4.7 CONTENT & NAVIGATION

OPEN <target>
SEARCH <query>
FIND <pattern> [path]
HELP [topic]

	•	<target> may be:
	•	file path
	•	URL
	•	anchor
	•	SEARCH is indexed
	•	FIND is pattern-based

⸻

4.8 FILE & KNOWLEDGE MAINTENANCE (High-level only)

CLEAN <path> [ruleset]
TIDY <path> [profile]
ARCHIVE <path> [policy]
BACKUP <path> [target]
REPAIR CHECK
REPAIR FIX

	•	No delete/move/copy exposed
	•	All destructive actions must:
	•	be reversible, or
	•	produce a preview/report first (implementation rule)

⸻

5. Explicit exclusions (never Core)

These must not be added later:
	•	IF / THEN / loops
	•	Variables
	•	Inline logic
	•	Pipes
	•	Wildcards
	•	Raw filesystem verbs (LIST, DELETE, MOVE, etc.)
	•	Network endpoints
	•	Provider names
	•	Dev/build/install commands
	•	AI/model operations

If it needs any of the above → Wizard or Script, not Core.

⸻

6. Error handling (standardised)

All Core commands return one of:

OK
ERROR <code> <message>

Where <code> is stable and machine-readable.

No partial success.
No silent failure.

⸻

7. Capability gating (conceptual)

Before execution, every command resolves to:

ALLOW | DENY | FORWARD_TO_WIZARD

Core never escalates privileges implicitly.

⸻

8. Relationship to scripts (filename-script.md)
	•	Core commands do not appear inside scripts
	•	Scripts may request Core capabilities
	•	Core decides per capability:
	•	allow
	•	deny
	•	prompt user
	•	forward to Wizard

This keeps:
	•	Core = authority
	•	Script = intent
	•	Wizard = power

⸻

9. Stability promise

Once locked:
	•	Grammar changes are rare
	•	New functionality goes to:
	•	Scripts (first)
	•	Wizard (second)
	•	Core grows only when something is:
	•	universal
	•	stable
	•	capability-level

⸻



Summary: Core, Script, and Wizard Responsibilities (Locked Model)

1. Core → Capability Authority (User-Facing, Stable)

Core is not a logic engine.
It is the authoritative capability layer for the system.

Core’s job is to:
	•	Expose a small, stable set of user-facing commands
	•	Enforce permissions, safety, and device authority
	•	Provide offline-first, deterministic behaviour
	•	Act as the final decision-maker for actions that affect:
	•	the system
	•	files
	•	identity
	•	transport
	•	configuration

Core commands express intent, not procedure.
They do not contain logic, branching, variables, or workflows.

Examples of what Core owns:
	•	system status and configuration
	•	profile and location
	•	search and find
	•	high-level file maintenance (CLEAN, TIDY, ARCHIVE)
	•	transport, pairing, and sync

Core is deliberately boring — and that is a feature.

⸻

2. Scripts (filename-script.md) → Logic, Flow, Interaction

Scripts replace uPY entirely.
They are now the only embedded logic layer in the system.

A script is:
	•	a Markdown document
	•	with state, variables, IF/THEN logic
	•	UI elements (forms, navigation)
	•	panels, maps, sprites, teletext graphics
	•	deterministic execution

Scripts are where:
	•	workflows live
	•	wellbeing programs live
	•	games live
	•	guided experiences live
	•	interactive documentation lives

Scripts do not execute system actions directly.
Instead, they request capabilities from Core (open, save, search, etc.).

Core then decides:
	•	allow
	•	deny
	•	prompt the user
	•	forward to Wizard

This cleanly separates:
	•	intent (script)
	•	authority (core)

⸻

3. Wizard (Dev Server) → Power, Experimentation, Integration

Wizard is where complexity is allowed.

Wizard exists to handle:
	•	experimental features
	•	in-development core commands
	•	network access
	•	integrations (email, providers, quotas)
	•	web capture and ingestion
	•	build and packaging pipelines
	•	long-running or asynchronous jobs

Wizard commands are:
	•	not user-facing by default
	•	namespaced
	•	versioned
	•	allowed to change rapidly

Wizard often outputs scripts (filename-script.md) rather than executing logic itself.

In other words:
	•	Wizard creates tools
	•	Scripts run experiences
	•	Core guards the system

⸻

The Big Picture (Mental Model)
	•	Core = authority & safety
	•	Scripts = logic & experience
	•	Wizard = power & experimentation

This model:
	•	removes the need for uPY
	•	keeps Core small and durable
	•	makes scripts the centre of user value
	•	gives Wizard room to evolve without breaking users

It’s a clean, modern, and very hard-to-break architecture.

## Phase 1A / 1B Test Artifacts

- `memory/tests/phase1a_runtime_state.test.ts`: Covers the `StateStore` CRUD, snapshot, and persistence helpers.
- `memory/tests/phase1b_state_executor.test.ts`: Validates literal parsing plus default-only assignments inside the `state` block.
- `memory/tests/phase1b_set_executor.test.ts`: Exercises `set`, `inc`, `dec`, and `toggle` commands (dot-path and coercion rules).

Those files live in `memory/tests/` and execute through the `core` jest runner because `core/jest.config.js` includes `../memory/tests` as a root source.
