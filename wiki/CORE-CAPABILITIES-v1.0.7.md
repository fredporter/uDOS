# Core Capabilities Reference — v1.0.7.0

**Version:** 1.0.7.0
**Status:** Production
**Last Updated:** 2026-01-30
**Scope:** Offline TUI operations, no cloud dependencies

This document provides a comprehensive reference of Core's capabilities for offline terminal-based operations.

---

## Table of Contents

1. [Binder System](#1-binder-system)
2. [Markdown & Frontmatter](#2-markdown--frontmatter)
3. [Database Operations](#3-database-operations)
4. [File Handling & Maintenance](#4-file-handling--maintenance)
5. [Publication Workflow](#5-publication-workflow)
6. [Map & Grid Rendering](#6-map--grid-rendering)
7. [Teletext Block Graphics](#7-teletext-block-graphics)
8. [Pattern Generation](#8-pattern-generation)
9. [Diagram System](#9-diagram-system)
10. [Seed-Bank Management](#10-seed-bank-management)
11. [Workspace System](#11-workspace-system)

---

## 1. Binder System

**Status:** ✅ Production
**Module:** `core/binder/`

Binders are folder-based multi-chapter projects that compile to various output formats.

### Features

- **Multi-format compilation:** MD, JSON, TXT
- **Per-binder SQLite database:** `uDOS-table.db` (isolated context)
- **Metadata management:** `.binder-config` files
- **Structure validation:** Required/optional folder checks
- **RSS/JSON feeds:** Content syndication

### File Structure

```
MyBinder/
├── uDOS-table.db          # Required SQLite database
├── .binder-config         # Optional metadata
├── binder.md              # Optional home document
├── imports/               # Source data
├── tables/                # Exported tables
├── scripts/               # SQL/uPY scripts
└── chapters/              # Content chapters
    ├── 01-intro.md
    ├── 02-chapter.md
    └── ...
```

### Metadata Format (`.binder-config`)

```json
{
  "name": "My Research Binder",
  "version": "1.0.0",
  "created_at": "2026-01-30T10:00:00Z",
  "author": "Fred",
  "description": "Research notes and analysis",
  "tags": ["research", "data", "analysis"]
}
```

### TUI Commands

```
BINDER                          # Open binder picker
BINDER PICK [dir]               # Pick from specific directory
BINDER COMPILE <id> [format]    # Compile to single format (md/json/txt)
BINDER CHAPTERS <id>            # List chapters with metadata
```

**F4 Function Key:** Opens interactive binder picker

### Compilation Output

**Format: Markdown**
```
MyBinder-compiled.md       # Single markdown file
└── All chapters merged in order
```

**Format: JSON**
```json
{
  "binder_id": "my-binder",
  "compiled_at": "2026-01-30T10:00:00Z",
  "chapters": [
    {
      "chapter_id": "ch1",
      "title": "Introduction",
      "content": "...",
      "word_count": 500
    }
  ]
}
```

**Format: TXT**
```
Plain text output with chapters separated by headers
```

---

## 2. Markdown & Frontmatter

**Status:** ✅ Production
**Module:** `core/services/markdown_frontmatter.py`

### Standard Frontmatter

All markdown files support YAML frontmatter:

```yaml
---
# Essential
title: Document Title
description: Brief summary
tags: [tag1, tag2, tag3]

# Spatial
grid_locations:
  - L300-AB15
  - L300-AC20

# Binder
binder_id: my-project
chapter: 1

# Metadata
created_at: 2026-01-30T10:00:00Z
updated_at: 2026-01-30T14:30:00Z
author: username

# Custom fields
custom_key: custom_value
---

# Your content here
```

### Table Files (`.table.md`)

Database tables with schema definitions:

```yaml
---
table_name: contacts
columns:
  - name: id
    type: integer
    primary_key: true
  - name: email
    type: text
    not_null: true
  - name: created_at
    type: datetime
---

| id | email             | created_at          |
|----|-------------------|---------------------|
| 1  | alice@example.com | 2026-01-01 10:00:00 |
| 2  | bob@example.com   | 2026-01-02 14:30:00 |
```

**Type Mapping:**
- `integer`, `int` → INTEGER
- `text`, `string` → TEXT
- `real`, `float`, `decimal` → REAL
- `boolean`, `bool` → BOOLEAN
- `datetime`, `date`, `time` → TEXT
- `blob` → BLOB
- `json` → TEXT

### Layer Files (`.layer.md`)

**NEW in v1.0.7** — Map layers with frontmatter:

```yaml
---
layer_id: L300-brooklyn-surface
layer_type: surface
layer_band: SUR
resolution: 80x30
grid_size:
  columns: 80
  rows: 30
tags: [urban, brooklyn, nyc]
related_layers:
  - L299-subway
  - L301-rooftops
author: Fred
created: 2026-01-30
---

# Brooklyn Surface (L300)

## Description
Street-level surface layer covering Brooklyn neighborhoods.

## Grid Coordinates
- Prospect Park: AA15-BD20
- Brooklyn Bridge: DA10

## Map Block

​```map L300-AA10 80x30
# Embedded or referenced grid data
​```
```

---

## 3. Database Operations

**Status:** ✅ Production
**Module:** `core/binder/database.py`, `core/parsers/`

### Binder Database Context

Each binder has isolated SQLite access:

```python
from core.binder import BinderDatabase

# Open binder database (read-write by default)
with BinderDatabase(binder_path) as db:
    # Query data
    results = db.query("SELECT * FROM contacts WHERE active = ?", (True,))

    # Execute updates
    rows_affected = db.execute(
        "INSERT INTO contacts (email) VALUES (?)",
        ("new@example.com",)
    )
```

**Access Modes:**
- `READ_ONLY` — SELECT only (safe)
- `READ_WRITE` — SELECT, INSERT, UPDATE, DELETE
- `FULL` — CREATE, DROP, ALTER (dangerous)

### Data Import

**CSV/TSV Import:**
- Auto-detects delimiter (comma, tab, semicolon, pipe)
- Infers column types (INTEGER, FLOAT, DATE, BOOLEAN)
- Handles headers automatically
- Creates SQLite tables with proper schema

**Module:** `core/parsers/csv_tsv_importer.py`

### Table Export

**Supported Formats:**
- **SQLite** — Binary database file
- **CSV** — Comma-separated values
- **TXT** — Tab-separated plain text
- **XML** — Structured XML format
- **JSON** — JSON array of objects

**Module:** `core/parsers/table_exporter.py`

```python
from core.parsers import TableExporter

exporter = TableExporter()
exporter.export_to_csv(db_path, "contacts", output_path)
exporter.export_to_json(db_path, "contacts", output_path)
```

### SQL Script Execution

**Safety Constraints:**
- Executes in `/memory/sandbox` only
- Protected tables cannot be dropped
- Multi-statement support
- Transaction safety
- CTE and temp table support

**Module:** `core/parsers/sql_executor.py`

**Execution Modes:**
- `READ_ONLY` — SELECT statements only
- `READ_WRITE` — SELECT, INSERT, UPDATE allowed
- `FULL` — All operations (admin only)

---

## 4. File Handling & Maintenance

**Status:** ✅ Production
**Module:** `core/services/maintenance_utils.py`

### TIDY Operation

Moves junk files to `.archive/`:

```python
tidy(scope_root, recursive=True)
```

**Junk Patterns Detected:**
- `.DS_Store`, `Thumbs.db`
- `*.tmp`, `*.cache`, `*.bak`
- `*.pyc`, `__pycache__/`
- `.log` files older than 7 days
- Empty directories

### CLEAN Operation

Resets directory to default state:

```python
clean(scope_root, allowed_entries=['README.md', 'data/'], recursive=False)
```

Moves non-allowed entries to `.archive/`.

### COMPOST Operation

Archives old archives:

```python
compost(scope_root, recursive=True)
```

Moves `.archive/`, `.backup/`, `.tmp/` to `/.compost/` with timestamp.

### TUI Commands

```
REPAIR TIDY [scope]         # Move junk to .archive
REPAIR CLEAN [scope]        # Reset to defaults
REPAIR COMPOST [scope]      # Archive old archives
```

**Scopes:**
- `current` — Current directory only
- `+subfolders` — Current + subdirectories
- `workspace` — memory/ directory
- `all` — Entire repository

---

## 5. Publication Workflow

**Status:** 🚧 **Priority 1 — IMPLEMENT IMMEDIATELY**
**Module:** `core/commands/publish_handler.py` (NEW)

### Document Lifecycle

```
DRAFT → REVIEW → PUBLISHED → ARCHIVED
  ↓       ↓         ↓           ↓
@sandbox @bank   @public     .archive
         @shared
```

### Workspace Promotion

**Sandbox → Bank** (Personal archive)
```
PUBLISH @sandbox/story.md @bank/stories/
```

**Bank → Public** (Public submission)
```
PUBLISH @bank/story.md @public/ --submit
```

**Bank → Shared** (Collaborative)
```
PUBLISH @bank/data.csv @shared/datasets/
```

### Binder Promotion

```
PUBLISH BINDER my-research @bank/research/
PUBLISH BINDER my-research @public/ --submit
```

### Publication Rules

**Validation Checks:**
- ✅ Valid frontmatter
- ✅ No broken links
- ✅ Proper formatting
- ✅ Required metadata present

**@public Submission:**
- Requires `--submit` flag
- Creates submission record
- Adds to wiki submission queue
- Admin review required

### TUI Commands

```
PUBLISH <source> <dest>              # Promote document
PUBLISH BINDER <id> <dest>           # Promote entire binder
PUBLISH STATUS <path>                # Check eligibility
PUBLISH VALIDATE <path>              # Dry-run validation
PUBLISH LIST --pending               # Show pending submissions
```

---

## 6. Map & Grid Rendering

**Status:** ✅ Production
**Module:** `core/services/map_renderer.py`

### Grid System

**Viewport Sizes:**
- Standard: 80×30 tiles
- Mini: 40×15 tiles

**Layer Bands:**
- **SUR (Surface):** L300–L305 (Earth surface, 11km precision)
- **UDN (Underground):** L294–L299 (Subterranean, 3.1m precision)
- **SUB (Submarine):** L293–L288 (Ocean depths)

**Cell Addressing:**
- Columns: AA–DC (80 columns)
- Rows: 10–39 (30 rows, 2-digit format)
- Full address: `L300-AB15`

### Map Rendering

**ASCII Grid Output:**
```
+------------------------------------------------------------------------------+
| Brooklyn - Prospect Park                                                     |
| Layer: L300 | Timezone: America/New_York                                      |
+------------------------------------------------------------------------------+
     AA  AB  AC  AD  AE  AF  AG  AH  AI  AJ  ...
10    .   .   S   .   .   .   .   .   .   .  ...
11    .   W   .   .   .   P   .   .   .   .  ...
12    .   .   .   .   M   .   .   .   V   .  ...
...
+------------------------------------------------------------------------------+
| Legend: S=Structure V=Vehicle W=Waypoint P=POI M=Marker .=Empty             |
+------------------------------------------------------------------------------+
```

### TUI Commands

```
MAP                          # Show current location
MAP <location_id>            # Show specific location (e.g., L300-AB15)
PANEL <location> <region>    # Show specific region (e.g., AA10:BD14)
```

### Map Blocks in Markdown

```markdown
​```map L300-AA10 80x30
# Renders 80×30 viewport centered at L300-AA10
​```

​```map L300-AA10 40x15 quality=BLOCK coords
# Mini viewport with block graphics and coordinates
​```
```

---

## 7. Teletext Block Graphics

**Status:** ✅ Production
**Module:** `core/grid-runtime/src/teletext-renderer.ts` (renamed from sextant)

### Graphics Modes

**TELETEXT (2×3 pixels, 64 characters)**
- 6-bit encoding (top-left to bottom-right)
- Unicode block mosaic characters
- Highest quality for terminal graphics
- Example: 🬀 🬁 🬂 🬃 ▀ ▄ ▌ ▐ █

**BLOCK (2×2 pixels, 16 characters)**
- 4-bit quadrant encoding
- Standard Unicode blocks
- Good compatibility fallback
- Example: ▘ ▝ ▀ ▖ ▌ ▞ ▛ ▗ ▚ ▐ ▜ ▄ ▙ ▟ █

**SHADE (density-based, 5 characters)**
- Density levels: empty, light, medium, dark, full
- Works on older terminals
- Example: ` ░ ▒ ▓ █`

**ASCII (text-only, 5 characters)**
- Pure ASCII compatibility
- Last resort fallback
- Example: ` . : # @`

### Fallback Chain

```
TELETEXT (64) → BLOCK (16) → SHADE (5) → ASCII (5)
```

**Auto-detection:**
- Checks terminal `$TERM` environment variable
- Graceful degradation on older terminals
- Force ASCII mode: `UDOS_ASCII_ONLY=1`

### Pixel Grid Encoding

**TELETEXT (2×3 grid):**
```
Pixel layout:
TL TR
ML MR
BL BR

6-bit pattern: [TL, TR, ML, MR, BL, BR]
Example: [1,1,0,0,0,0] → ▀ (top half filled)
```

**BLOCK (2×2 grid):**
```
Pixel layout:
TL TR
BL BR

4-bit pattern: [TL, TR, BL, BR]
Example: [1,1,0,0] → ▀ (top half filled)
```

### Rendering API

```typescript
import { renderPixelGrid, RenderQuality } from 'teletext-renderer';

// Render with automatic fallback
const char = renderPixelGrid(pixelGrid, RenderQuality.TELETEXT);

// Detect terminal support
if (detectTeletextSupport()) {
  quality = RenderQuality.TELETEXT;
} else {
  quality = RenderQuality.BLOCK;
}
```

### Map Quality Options

```markdown
​```map L300-AA10 quality=TELETEXT
# Highest quality (64 chars)

​```map L300-AA10 quality=BLOCK
# Standard fallback (16 chars)

​```map L300-AA10 quality=SHADE
# Density-based (5 chars)

​```map L300-AA10 quality=ASCII
# Text-only (5 chars)
​```
```

---

## 8. Pattern Generation

**Status:** ✅ Production
**Module:** `core/services/pattern_generator.py`

### Available Patterns

1. **C64** — Commodore 64 loader (color cycling, transfer head)
2. **Chevrons** — Diagonal scrolling pattern
3. **Scanlines** — Horizontal gradient with CRT effect
4. **Raster** — Color bars with smooth transitions
5. **Progress** — Animated progress bar
6. **Mosaic** — Random block pattern

### TUI Commands

```
PATTERN                        # Show next pattern (cycles)
PATTERN <name>                 # Show specific pattern
PATTERN LIST                   # List available patterns
PATTERN CYCLE [seconds]        # Demo all patterns
PATTERN TEXT <message>         # ASCII block-text banner
PATTERN TEXT <msg> CENTER      # Centered banner
PATTERN TEXT <msg> COLOR cyan  # Colored banner
```

### Pattern Options

- **Width:** Auto-detects terminal width (default 80)
- **Height:** Configurable (default 30)
- **ASCII-only:** Force ASCII mode with `UDOS_ASCII_ONLY=1`
- **Colors:** 16-color ANSI palette

---

## 9. Diagram System

**Status:** 🔧 **Priority 3 — DESIGN & REFINE**
**Approach:** ASCII/Teletext-based, NO external dependencies

### Design Principles

1. **Text-native:** Diagrams as ASCII/teletext characters
2. **Markdown-embeddable:** Fenced code blocks
3. **No external tools:** No Mermaid, PlantUML, Graphviz
4. **Teletext graphics:** Use TELETEXT/BLOCK rendering
5. **Hand-editable:** Simple text format

### Proposed Formats

**Flowcharts (ASCII Box-Drawing):**
```
​```diagram flowchart
┌─────────┐
│  Start  │
└────┬────┘
     │
     ▼
  ┌──┴──┐
  │ Yes │ No
  └──┬──┘
     │
     ▼
┌─────────┐
│   End   │
└─────────┘
​```
```

**Block Diagrams (Teletext Graphics):**
```
​```diagram blocks
█████████   ─────▶   █████████
█ Input █            █ Output█
█████████   ◀─────   █████████
​```
```

**Schematics (Line Art):**
```
​```diagram schematic
    +5V
     │
     ├──[ R1 ]──┐
     │          │
    ┌┴┐       ┌─┴─┐
    │ │ C1    │LED│
    └┬┘       └─┬─┘
     │          │
     └──────────┴─── GND
​```
```

### Character Families

**Box Drawing:**
- Light: ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
- Heavy: ━ ┃ ┏ ┓ ┗ ┛ ┣ ┫ ┳ ┻ ╋
- Double: ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬

**Arrows:**
- Basic: ← → ↑ ↓ ↔ ↕
- Heavy: ⇐ ⇒ ⇑ ⇓ ⇔ ⇕
- Simple: < > ^ v

**Blocks:**
- TELETEXT: █ ▀ ▄ ▌ ▐
- Shading: ░ ▒ ▓
- Symbols: ● ○ ◆ ◇ ■ □

### Diagram Specification

**Scope:** Flowcharts and logic steps ONLY
**Format:** Markdown-based `.diagram.md` files (text-editable)
**Rendering:** Downgradable from Markdown flowchart → ASCII
**Color:** Monochrome for ASCII, 32-color uDOS palette for TELETEXT blocks

### Markdown Flowchart Format

Store flowcharts as structured markdown:

```markdown
---
title: User Login Flow
type: flowchart
style: ascii
colors: false
---

# User Login Flow

## START
→ Check credentials

## DECISION: Valid credentials?
YES → Grant access
NO → Show error

## END: Grant access
User is logged in

## END: Show error
Display "Invalid credentials"
```

### ASCII Rendering

**Monochrome output using box-drawing:**

```
┌─────────────┐
│    START    │
│ User Login  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   CHECK     │
│ Credentials │
└──────┬──────┘
       │
       ▼
    ┌──┴──┐
◆───┤Valid?├───◆
│   └─────┘   │
YES           NO
│             │
▼             ▼
┌──────┐  ┌──────┐
│Grant │  │Error │
│Access│  │ Msg  │
└──────┘  └──────┘
```

### TELETEXT Block Rendering

**32-color uDOS palette support:**

```
█████████████
█   START   █ (cyan background)
█████████████
      █
      █ (white arrows)
      ▼
█████████████
█   CHECK   █ (blue background)
█ Passwords █
█████████████
      █
    ◆═█═◆
    █   █
   YES  NO
    █   █
    ▼   ▼
█████████ █████████
█ GRANT █ █ ERROR █ (green/red backgrounds)
█████████ █████████
```

### Node Types

**Box (Process):**
```
┌─────────┐
│ Process │
└─────────┘
```

**Diamond (Decision):**
```
   ◆───┐
───┤   │
   ◆───┘
```

**Rounded (Start/End):**
```
╭─────────╮
│  Start  │
╰─────────╯
```

**Parallel (Data):**
```
╱─────────╲
│  Data   │
╲─────────╱
```

### Connection Lines

**Monochrome:**
- Straight: `│ ─`
- Corners: `┌ ┐ └ ┘`
- Joins: `├ ┤ ┬ ┴ ┼`
- Arrows: `→ ← ↑ ↓`

**TELETEXT blocks:**
- Solid: `█`
- Flow: `▀ ▄ ▌ ▐`
- Arrows: `▶ ◀ ▲ ▼`

### Logic Step Format

Simple sequential logic:

```markdown
## Logic: Calculate discount

1. IF customer_type == "premium"
   → discount = 0.20

2. ELSE IF order_total > 100
   → discount = 0.10

3. ELSE
   → discount = 0.00

4. RETURN discount
```

**ASCII Rendering:**
```
┌────────────────────────┐
│ 1. Check customer_type │
└───────────┬────────────┘
            │
         ┌──┴──┐
    ╔════╡Premium?╞════╗
    ║    └─────┘      ║
   YES                NO
    ║                 ║
    ▼                 ▼
┌────────┐      ┌──────────┐
│discount│      │2. Check  │
│= 0.20  │      │order>100?│
└────────┘      └─────┬────┘
                      │
                   ┌──┴──┐
              ╔════╡ >100?╞═══╗
              ║    └─────┘   ║
             YES             NO
              ║              ║
              ▼              ▼
         ┌────────┐    ┌────────┐
         │discount│    │discount│
         │= 0.10  │    │= 0.00  │
         └────────┘    └────────┘
```

### Implementation Roadmap

**Phase 1: ASCII Parser** (Priority 3)
- Parse `.diagram.md` markdown format
- Generate ASCII box-drawing output
- Support basic flowchart nodes (box, diamond, rounded)

**Phase 2: TELETEXT Renderer**
- Render flowcharts using TELETEXT blocks
- Apply 32-color uDOS palette
- Graceful fallback to ASCII

**Phase 3: Logic Step Parser**
- Parse IF/THEN/ELSE logic markdown
- Generate decision tree ASCII
- Support nested conditions

**Phase 4: TUI Integration**
- `DIAGRAM RENDER <file>` command
- Preview diagrams in terminal
- Export to ASCII/TELETEXT formats

---

## 10. Seed-Bank Management

**Status:** ✅ Production
**Module:** `core/framework/seed_installer.py`

### Seed System

Initial data bootstrap for fresh installations.

**Seed Location:** `core/framework/seed/`

**Seed Contents:**
- `locations-seed.json` — Initial location database (3 locations)
- `timezones-seed.json` — Timezone reference data
- `bank/help/` — Help templates and guides
- `bank/graphics/` — Diagram templates
- `bank/templates/` — Document templates

### Installation Process

**Automatic:** First run bootstraps seed data
**Manual:** Use `SEED INSTALL` command

**Target Structure:**
```
memory/bank/
├── locations/
│   └── locations.json       # Installed from seed
├── timezones.json           # Installed from seed
├── help/                    # Templates
├── graphics/                # Diagrams
│   └── diagrams/
│       └── templates/
└── templates/               # Document templates
```

### TUI Commands

```
SEED                    # Check installation status
SEED INSTALL            # Install seed data (skip existing)
SEED INSTALL --force    # Reinstall (overwrite)
SEED STATUS             # Show detailed status
```

### Status Output

```
Seed Installation Status:
----------------------------------------
Directories:       ✅
Locations seeded:  ✅
Timezones seeded:  ✅
Framework seed dir: ✅
```

---

## 11. Workspace System

**Status:** ✅ Production (with v1.0.7 updates)
**Module:** `core/services/spatial_filesystem.py`

### Workspace Hierarchy

| Workspace | Path | Access | Purpose |
|-----------|------|--------|---------|
| `@sandbox` | `memory/sandbox` | USER, ADMIN | Personal experimentation |
| `@bank` | `memory/bank` | USER, ADMIN | Personal data vault |
| `@public` | `memory/public` | ADMIN | Public wiki submissions |
| `@shared` | `memory/shared` | USER, ADMIN | Collaborative workspace |

### Role-Based Access

**ADMIN**
- Full access to all workspaces
- Can promote documents to @public
- Can manage wiki submissions
- System maintenance access

**USER**
- Read/write: @sandbox, @bank, @shared
- Read-only: @public (view submissions)
- Cannot publish to @public without admin review

**GHOST**
- Test user with limited UI
- Read-only: @public, @shared
- Cannot write to any workspace
- Used for testing and demos

### Workspace Operations

**Read/Write:**
```python
from core.services.spatial_filesystem import SpatialFilesystem

fs = SpatialFilesystem(user_role='USER')

# List workspace contents
files = fs.list_workspace('@sandbox')

# Write file
fs.write_to_workspace('@bank', 'story.md', content)

# Read file
content = fs.read_from_workspace('@bank', 'story.md')
```

**Grid Tagging:**
```python
# Tag file with location
fs.tag_location('@sandbox/story.md', 'L300-AB15')

# Find files at location
files = fs.find_by_location('L300-AB15')
```

**Content Discovery:**
```python
# Extract tags from frontmatter
tags = fs.extract_tags('@sandbox/story.md')

# Find documents by tags
docs = fs.find_by_tags(['forest', 'adventure'])
```

### Publication to @public

**Submission Workflow:**
```
1. Create/edit in @sandbox
2. Validate and refine
3. Promote to @bank (personal archive)
4. Submit to @public (requires --submit flag)
5. Admin review
6. Approval → Published to public wiki
7. Rejection → Returns to @bank with feedback
```

**Submission Record:**
```json
{
  "submission_id": "sub-20260130-001",
  "source_path": "@bank/my-article.md",
  "submitted_by": "username",
  "submitted_at": "2026-01-30T10:00:00Z",
  "status": "pending_review",
  "reviewer": null,
  "reviewed_at": null,
  "feedback": null
}
```

### TUI Commands

```
WORKSPACE LIST @sandbox           # List files
WORKSPACE INFO @sandbox/doc.md    # Show metadata
LOCATION TAG <file> <loc>         # Tag with grid location
LOCATION FIND L300-AB15           # Find files at location
TAGS SEARCH forest adventure      # Search by tags
```

---

## Implementation Priorities

### Priority 1: Publication Workflow (IMMEDIATE)

**Status:** 🚧 Implementation Required

**Files to Create:**
- `core/commands/publish_handler.py` — PUBLISH command
- `core/services/publication_service.py` — Validation & workflow
- `memory/public/.submissions/` — Submission tracking

**Commands to Implement:**
```
PUBLISH <source> <dest> [--submit]
PUBLISH BINDER <id> <dest> [--submit]
PUBLISH STATUS <path>
PUBLISH VALIDATE <path>
PUBLISH LIST --pending
```

**Validation Rules:**
- Valid frontmatter (title, description, tags)
- No broken internal links
- Proper markdown formatting
- Required metadata present (author, created_at)
- File size limits (max 1MB per file, 10MB per binder)

---

### Priority 2: Layer Markdown Format

**Status:** 🚧 Design Complete, Implementation Required

**Format:** `.layer.md` files with frontmatter

**Example:** See [Section 2: Layer Files](#layer-files-layermd)

**Implementation:**
- Parser for `.layer.md` frontmatter
- Grid block embedding/referencing
- Related layer linking
- TUI commands for layer management

---

### Priority 3: Diagram Support (DESIGN & REFINE)

**Status:** 🤔 Architecture Discussion Needed

**Key Questions:**
1. Which diagram types are essential?
   - Flowcharts (YES — common workflow documentation)
   - Schematics (MAYBE — technical diagrams)
   - Mind maps (MAYBE — knowledge organization)
   - Sequence diagrams (NO — too complex for ASCII)
   - State machines (MAYBE — system modeling)

2. Editing approach?
   - Hand-edit text files (SIMPLE, portable)
   - Interactive TUI editor (POWERFUL, harder to implement)
   - Hybrid: edit text, preview rendered (BALANCED)

3. Rendering strategy?
   - Pure ASCII (MAXIMUM compatibility)
   - Teletext blocks (BETTER visuals, terminal-dependent)
   - SVG export (NICE to have, requires external tool)

4. Color support?
   - 16-color ANSI (YES — adds clarity)
   - Monochrome only (SIMPLER, more portable)

**Recommendation:** Start with flowcharts using box-drawing characters + arrows. Hand-editable, no parser required. Add Teletext rendering later.

---

### Priority 4: Binder F-Key Enhancements

**Status:** ⏭️ Future Enhancement

**Current:** F4 opens binder picker

**Proposed:**
- **F4** — Open binder picker (current)
- **Shift+F4** — Compile active binder (quick action)
- **Ctrl+F4** — New binder wizard (guided setup)
- **Alt+F4** — Close active binder (save state)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.7.0 | 2026-01-30 | Initial capability reference |

---

## See Also

- [LAYER-ARCHITECTURE.md](LAYER-ARCHITECTURE.md) — Grid system details
- [KNOWLEDGE-LINKING-SYSTEM.md](KNOWLEDGE-LINKING-SYSTEM.md) — Wiki integration
- [FILESYSTEM-ARCHITECTURE.md](FILESYSTEM-ARCHITECTURE.md) — Data organization
- [SPATIAL-FILESYSTEM-QUICK-REF.md](../docs/SPATIAL-FILESYSTEM-QUICK-REF.md) — Command reference

---

**End of Document**
