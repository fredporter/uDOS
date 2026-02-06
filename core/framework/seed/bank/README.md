# Bank Seed Data

**Purpose:** Canonical seed data for `memory/system/` + `vault-md/bank/` initialization

---

## 📁 Structure

```
seed/bank/
├── graphics/           # Graphics & rendering seed data (TRACKED)
│   ├── themes/         # TUI/runtime themes
│   ├── diagrams/       # ASCII/teletext/SVG diagram templates
│   └── teletext/       # Teletext palettes & patterns
│
├── help/               # Help template seeds (TRACKED)
│   ├── system_commands.json
│   ├── file_commands.json
│   └── assistant_commands.json
│
└── templates/          # Runtime template seeds (TRACKED)
    ├── story.template.json
    ├── user.template.json
    └── setup-script.md
```

---

## 🔄 Initialization Flow

**On first run or `REPAIR --seed`:**

1. Check if `memory/system/graphics/` exists
2. If missing → copy from `core/framework/seed/bank/graphics/`
3. User can then customize in `vault-md/bank/` (gitignored)
4. Original seeds remain tracked in framework

---

## 📊 Data Categories

### Graphics (themes, diagrams, teletext)

**Themes:**
- Schema: `_schema.json` (defines variable types)
- Index: `_index.json` (theme catalog)
- Default: `default.json` (base theme)
- Custom: `templates/` (user-customizable themes)

**Diagrams:**
- ASCII templates (25): flowcharts, systems, progress, timelines, etc.
- Teletext palettes (4): classic, earth, terminal, amber
- SVG styles (3): technical, simple, detailed
- Sequence diagrams (5): message flows, API requests, error handling
- Flowcharts (5): decision trees, processes

**Catalog:** `diagrams/catalog.json` (full template registry)

### Help Templates

Command reference templates for TUI:
- System commands (SHAKEDOWN, REPAIR, VERSION, etc.)
- File commands (LIST, EDIT, SAVE, etc.)
- Assistant commands (ASK, EXPLAIN, GENERATE, etc.)
- Grid commands (MAP, GRID, VIEWPORT, etc.)

### Templates

Runtime templates for scripting:
- `story.template.json` — Interactive story format
- `user.template.json` — User profile template
- `setup-script.md` — Setup/onboarding script
- `adventure-template.md` — Adventure game template
- `form_validation-script.md` — Form validation example
- `menu_system-script.md` — Menu system template

---

## 🎨 Theme System

Themes define TUI appearance and variable mappings:

**Core Variables:**
- System: `THEME_NAME`, `VERSION`, `STYLE`, `VERBOSE_LEVEL`
- User: `USER_NAME`, `USER_LOCATION`, `USER_TIMEZONE`, `USER_PROJECT`
- Character: `CHARACTER_NAME`, `CHARACTER_CLASS`, `CHARACTER_LEVEL`, HP/XP stats
- Object: `OBJECT_NAME`, `OBJECT_TYPE`, `OBJECT_RARITY`, durability/value

**Use Cases:**
- TUI customization (colors, prompts, banners)
- Variable interpolation in templates
- Context-aware help text
- Progress indicators & status displays

---

## 📚 Diagram Catalog

**Format Support:**
- **ASCII** — Plain text (25 templates)
- **Teletext** — 8-color terminal (4 palettes)
- **SVG** — Vector graphics (3 styles)
- **Sequence** — Actor-based flows (js-sequence, 5 templates)
- **Flow** — Flowcharts (flowchart.js, 5 templates)

**Categories:**
- Flowcharts (vertical, horizontal)
- System diagrams (components, layers)
- Progress indicators (bars, steps)
- Timelines (horizontal, vertical, Gantt)
- Decision trees (binary, hierarchical)
- Organization charts (hierarchical, flat)
- Network diagrams (star, mesh, hierarchy)
- Data visualization (tables, matrices)

**Layer maps:** Detailed layer templates (Earth surface, infrastructure, subterranean, virtual, galaxy relays) reside under `graphics/layers/` and align with the docs’ L300-L899 “fractal” layer references; edit those JSON files to update the catalogs.

---

## 🚀 Usage

### Manual Seed

```bash
# Copy all seed data to bank
cp -r core/framework/seed/bank/* memory/system/

# Copy specific category
cp -r core/framework/seed/bank/graphics memory/system/
```

### Programmatic Seed (Handler)

```python
from core.services.file_service import FileService
from pathlib import Path

seed_path = Path("core/framework/seed/bank/graphics")
bank_path = Path("memory/system/graphics")

if not bank_path.exists():
    FileService.copy_directory(seed_path, bank_path)
```

### Repair Command

```bash
REPAIR --seed    # Re-seed missing bank data
```

---

## 🔒 Git Policy

| Path | Git Status | Purpose |
|------|-----------|---------|
| `core/framework/seed/bank/` | ✅ **TRACKED** | Canonical seed data |
| `vault-md/bank/` | ❌ Gitignored | User customizations |

**Rule:** Seeds are version-controlled, user data is not.

---

## 📦 Distributables

These seeds are packaged with uDOS distributions:
- Alpine packages (apk)
- Wizard plugin bundles
- Standalone installers

Users can reset to defaults via `REPAIR --seed`.

---

**Version:** 1.0.0
**Last Updated:** 2026-01-29
**Tracked:** Yes (canonical seed data)
