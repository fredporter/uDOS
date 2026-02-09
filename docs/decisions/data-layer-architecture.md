# ADR-0004: Data Layer Architecture

**Status:** PROPOSED
**Date:** 2026-01-29
**Author:** uDOS Engineering
**Scope:** Data organization, storage layers, distribution model

---

## Context

uDOS needs a clear data architecture that supports:
1. **Consistent formats** across all layers
2. **Distributable public content** (base layers)
3. **User-customized layers** in `/memory/` (not synced with git)
4. **Optional user-to-user sync** (P2P, not via git)
5. **Processing of extended `.md` script format** in Core
6. **Support for tables and databases** (JSON → SQLite migration path)

### Current State (Problems)

| Location | Contents | Issues |
|----------|----------|--------|
| `/core/data/` | timezones.json (4KB) | Inconsistent placement |
| `/core/locations*.json` | Location data (60KB+) | Growing, needs structure |
| `/knowledge/` | Mixed: guides, checklists, places, runtime | Needs cleanup—should be static only |
| `/memory/` | User data, logs | Needs `bank/` structure for templates |

---

## Decision

### 1. Three-Tier Data Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TIER 1: FRAMEWORK (Public, Distributed via Git)                │
│  ─────────────────────────────────────────────────              │
│  /core/framework/                                                │
│    ├── schemas/          # JSON schemas for validation          │
│    │   ├── location.schema.json                                 │
│    │   ├── binder.schema.json                                   │
│    │   └── knowledge.schema.json                                │
│    ├── templates/        # Default templates                    │
│    │   ├── location-template.json                               │
│    │   ├── binder-template.json                                 │
│    │   └── knowledge-entry.md                                   │
│    └── seed/             # Minimal seed data (examples)         │
│        ├── locations-seed.json     (< 10KB)                     │
│        └── timezones-seed.json     (< 5KB)                      │
│                                                                  │
│  TIER 2: KNOWLEDGE (Public, Static Reference Library)           │
│  ─────────────────────────────────────────────────              │
│  /knowledge/                                                     │
│    ├── guides/           # How-to guides (static .md)           │
│    ├── reference/        # Technical reference (static .md)     │
│    ├── places/           # Geographic knowledge (static .md)    │
│    │   ├── cities/       # City guides (tokyo.md, etc.)         │
│    │   ├── landmarks/    # Famous places                        │
│    │   └── regions/      # Geographic regions                   │
│    ├── skills/           # Survival/practical skills            │
│    └── _index.json       # Catalog of all knowledge entries     │
│                                                                  │
│  TIER 3: BANK (User Data, Local/Syncable)                       │
│  ─────────────────────────────────────────────────              │
│  /memory/bank/                                                   │
│    ├── system/           # System scripts (tracked as templates)│
│    │   ├── startup-script.md                                    │
│    │   └── reboot-script.md                                     │
│    ├── locations/        # User location data (extended)        │
│    │   ├── locations.json      # Full location database         │
│    │   ├── timezones.json      # Full timezone mappings         │
│    │   ├── user-locations.json # User-added locations           │
│    │   └── locations.db        # SQLite when > 500KB            │
│    ├── knowledge/        # User knowledge additions             │
│    │   ├── personal/     # User notes                           │
│    │   └── imported/     # Downloaded content                   │
│                                                                  │
│  /memory/logs/                                                   │
│    ├── monitoring/       # Health checks, audits, alerts         │
│    └── quotas/           # Provider quota snapshots              │
│                                                                  │
│  /memory/sandbox/                                               │
│    └── binders/          # User binder projects (sandbox)        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2. JSON → SQLite Migration Threshold

**Rule:** Migrate JSON to SQLite when file exceeds **500KB** or **1000 records**.

| Data Type | Current Size | Format | Action |
|-----------|--------------|--------|--------|
| timezones.json | 4KB | JSON | Keep as JSON |
| locations.json | 60KB | JSON | Keep as JSON (monitor) |
| locations-full | 35KB | JSON | Keep as JSON |
| User locations | Variable | JSON | Migrate at 500KB |

**Migration Path:**
```
locations.json (< 500KB)  →  locations.db (≥ 500KB)
                              ├── table: locations
                              ├── table: timezones
                              ├── table: connections
                              └── table: user_additions
```

---

### 3. Knowledge Directory Cleanup

**REMOVE from `/knowledge/`:** (Move to appropriate tier)

| Current | Move To | Reason |
|---------|---------|--------|
| `checklists/` | `/memory/bank/checklists/` | Runtime/user data |
| Runtime scripts | `/core/` or `/memory/bank/system/` | Not static knowledge |
| User templates | `/core/framework/templates/` | Framework component |

**KEEP in `/knowledge/`:** (Static reference only)

- `guides/` — How-to documentation
- `reference/` — Technical reference
- `places/` — Geographic knowledge (Markdown descriptions)
- `skills/` — Survival/practical skills
- `survival/`, `food/`, `water/`, `shelter/` — Emergency knowledge

**NEW Structure:**
```
/knowledge/
├── _index.json              # Catalog with tags, categories
├── README.md
│
├── guides/                  # How-to guides
│   ├── getting-started.md
│   └── command-reference.md
│
├── reference/               # Technical reference
│   ├── ucODE-syntax.md
│   └── transport-policy.md
│
├── places/                  # Geographic knowledge
│   ├── _index.json          # Place catalog with coordinates
│   ├── cities/              # City descriptions
│   ├── landmarks/           # Famous places
│   └── regions/             # Geographic regions
│
├── skills/                  # Practical skills
│   ├── survival/
│   ├── navigation/
│   └── communication/
│
└── emergency/               # Critical offline knowledge
    ├── first-aid/
    ├── shelter/
    └── water/
```

---

### 4. Knowledge Entry Format (Frontmatter Tags)

Every `.md` file in `/knowledge/` should have:

```yaml
---
title: "Tokyo City Guide"
id: tokyo-guide
type: place           # guide | reference | place | skill | emergency
category: cities
region: asia
tags: [japan, asia, megacity, technology]
location_id: L300-BB00      # Link to location data
coordinates: [35.6762, 139.6503]
last_updated: 2026-01-29
version: 1.0.0
---
```

**Tag Categories:**
- `type`: guide, reference, place, skill, emergency
- `category`: cities, landmarks, regions, survival, navigation, etc.
- `region`: asia, europe, americas, africa, oceania, space, etc.
- `tags`: freeform keywords for search

---

### 5. Location Data Linking

**Knowledge → Location Data Flow:**
```
/knowledge/places/cities/tokyo.md
  └── frontmatter: location_id: L300-BB00
        ↓
/memory/bank/locations/locations.json
  └── { "id": "L300-BB00", "name": "Tokyo Metropolitan", ... }
        ↓
/memory/bank/locations/timezones.json
  └── "L300-BB00": "Asia/Tokyo"
```

**Runtime Resolution:**
1. User queries knowledge → Get `location_id` from frontmatter
2. Lookup location data in bank → Get coordinates, connections
3. Display combined rich information

---

### 6. Distribution Model

```
┌────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTION LAYERS                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PUBLIC (Git Distributed):                                      │
│  ────────────────────────                                       │
│  /core/framework/       → Schemas, templates, seed data         │
│  /knowledge/            → Static reference library              │
│  /docs/                 → Engineering documentation             │
│                                                                 │
│  PRIVATE (Git Submodule):                                       │
│  ─────────────────────────                                      │
│  /dev/                  → Development tools, experimental       │
│                                                                 │
│  LOCAL (Gitignored):                                            │
│  ───────────────────                                            │
│  /memory/               → User data, logs, credentials          │
│    EXCEPT:                                                      │
│    /memory/bank/system/*.md  → Templates (tracked)              │
│                                                                 │
│  SYNCABLE (P2P, Not Git):                                       │
│  ────────────────────────                                       │
│  /memory/bank/locations/     → Via MeshCore/QR/Audio transport  │
│  /memory/bank/knowledge/     → Via MeshCore/QR/Audio transport  │
│  /memory/bank/binders/public/ → Via MeshCore/QR/Audio transport │
│  /memory/bank/binders/shared/ → Via MeshCore/QR/Audio transport │
│  /memory/bank/binders/submit/ → Via MeshCore/QR/Audio transport │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### 7. File Migration Plan

**Phase 1: Create Framework Structure**
```bash
mkdir -p core/framework/schemas
mkdir -p core/framework/templates
mkdir -p core/framework/seed
```

**Phase 2: Move Core Data**
```bash
# Move schemas
mv core/location.schema.json core/framework/schemas/
mv core/version.schema.json core/framework/schemas/

# Move examples to seed
mv core/location.example.json core/framework/seed/
# Create minimal seed from locations.json (first 10 entries)
```

**Phase 3: Setup Bank Structure**
```bash
mkdir -p memory/bank/locations
mkdir -p memory/bank/knowledge/personal
mkdir -p memory/bank/knowledge/imported
mkdir -p memory/bank/checklists

# Move runtime location data to memory bank
mv core/locations.json memory/bank/locations/
mv core/data/timezones.json memory/bank/locations/

# Create symlink or copy seed on first run
```

**Phase 4: Cleanup Knowledge**
```bash
# Move checklists to bank
mv knowledge/checklists memory/bank/

# Create _index.json catalog
# Add frontmatter to all .md files
```

---

### 8. Consistent Formats

| Data Type | Primary Format | When to Use | Migration |
|-----------|----------------|-------------|-----------|
| Schemas | `.schema.json` | Validation | — |
| Templates | `.template.json` or `.template.md` | Scaffolding | — |
| Seed Data | `.json` (< 10KB) | Framework distribution | — |
| Location Data | `.json` (< 500KB) | Runtime data | → SQLite |
| Location Data | `.db` (≥ 500KB) | Large datasets | Final |
| Knowledge | `.md` with frontmatter | Static reference | — |
| User Data | `.json` or `.db` | User additions | → SQLite |
| Scripts | `-script.md` | Executable uCODE | — |
| Binders | `.binder/` folder | Document projects | — |

---

### 9. Extended .md Script Support

**Core should process these script formats:**

| Extension | Purpose | Processed By |
|-----------|---------|--------------|
| `-script.md` | uCODE scripts | Core Runtime |
| `-story.md` | Interactive stories | Story Parser |
| `-ucode.md` | uCODE documents | uCODE Runner |
| `.table.md` | Markdown tables | Table Parser |
| `-form.md` | Interactive forms | Form Handler |

**Table/Database Support:**

```markdown
---
title: Location Database
type: table
source: locations.json
---

<!-- Inline table definition -->
| id | name | layer | cell |
|----|------|-------|------|
| L300-AA10 | Forest Clearing | 300 | AA10 |

<!-- Or reference external source -->
```sql
SELECT * FROM locations WHERE layer = 300 LIMIT 10;
```
```

---

## Consequences

### Benefits
1. **Clear separation** between framework, knowledge, and user data
2. **Consistent distribution** model across all installations
3. **Scalable storage** with JSON → SQLite migration path
4. **P2P syncable** user data without touching git
5. **Maintainable** knowledge base with proper tagging

### Trade-offs
1. **Migration effort** — Need to move existing files
2. **Two location lookups** — Knowledge → Location data resolution
3. **Symlink management** — Seed data copied on first run

### Risks
1. **Breaking existing paths** — Need compatibility layer during migration
2. **Knowledge catalog maintenance** — _index.json must be kept updated

---

## Implementation Priority

| Phase | Task | Effort | Priority |
|-------|------|--------|----------|
| 1 | Create `/core/framework/` structure | 30 min | HIGH |
| 2 | Move schemas and templates | 30 min | HIGH |
| 3 | Create seed data (minimal) | 1 hour | HIGH |
| 4 | Setup `/memory/bank/locations/` | 30 min | HIGH |
| 5 | Cleanup `/knowledge/` | 2 hours | MEDIUM |
| 6 | Add frontmatter to knowledge .md files | 2 hours | MEDIUM |
| 7 | Create `_index.json` catalogs | 1 hour | MEDIUM |
| 8 | Implement JSON → SQLite migration | 4 hours | LOW |
| 9 | P2P sync for bank data | 8 hours | FUTURE |

---

## Summary Decision Matrix

| Question | Decision |
|----------|----------|
| Move `/data/` to `/memory/bank/system/`? | **NO** — Move to `/core/framework/` for schemas/templates, `/memory/bank/locations/` for runtime data |
| Include templates in public repo? | **YES** — `/core/framework/templates/` and `/core/framework/seed/` |
| Consolidate to `/core/data/`? | **NO** — Split into framework (public) and bank (local) |
| Move location data to `/memory/bank/`? | **YES** — Full location/timezone data goes to `/memory/bank/locations/` |
| Keep location data in `/core/`? | **PARTIAL** — Only minimal seed data in `/core/framework/seed/` |
| Link to `/knowledge/`? | **YES** — Via `location_id` in frontmatter |
| Cleanup `/knowledge/`? | **YES** — Static knowledge only, no runtime/checklists/templates |
| JSON size threshold for SQLite? | **500KB** or **1000 records** |

---

**Status:** Ready for Review
**Next Step:** Approve and begin Phase 1 implementation
