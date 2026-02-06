# ADR-0004: Data Layer Architecture

**Status:** APPROVED  
**Date:** 2026-01-29  
**Updated:** 2026-02-06  
**Author:** uDOS Engineering  
**Scope:** Data organization, storage layers, distribution model, vault-first design

---

## Context

uDOS follows a **vault-first, offline-local** architecture:
1. **Markdown is truth** — All content lives as `.md` files + assets on disk
2. **Vault-first** — Main vault at `~/Documents/uDOS Vault/` (not in repo)
3. **Seed data** in `/memory/system/` — Framework bootstrap templates (tracked)
4. **Local memory** in `/memory/` — User data, logs, secrets (gitignored)
5. **Public docs** in `/docs/` and `/wiki/` — Distributed via git (no `/knowledge/`)
6. **P2P sync** — User-to-user sharing via MeshCore, NFC, QR, Audio (not git)

### Current State (Problems Solved)

| Layer | Location | Status |
|-------|----------|--------|
| Framework | `/core/framework/` | ✅ Centralized schemas, templates, seeds |
| Docs | `/docs/`, `/wiki/` | ✅ Versioned reference only |
| User Vault | `~/Documents/uDOS Vault/` | ✅ Private/shared/submissions/publication |
| System Seeds | `/memory/system/` | ✅ Implemented in v1.3 |
| Local Data | `/memory/logs`, `/memory/private`, `/memory/user`, etc. | ✅ Gitignored |

---

## Decision

### 1. Four-Tier Data Model

```
┌──────────────────────────────────────────────────────────────────┐
│                    VAULT-FIRST ARCHITECTURE                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TIER 1: FRAMEWORK (Public, Git-Distributed)                     │
│  ──────────────────────────────────────────                      │
│  /core/framework/                                                 │
│    ├── schemas/          # JSON schemas for validation            │
│    │   ├── location.schema.json                                   │
│    │   ├── binder.schema.json                                     │
│    │   └── knowledge.schema.json                                  │
│    ├── templates/        # Default templates                      │
│    │   ├── location-template.json                                 │
│    │   ├── binder-template.json                                   │
│    │   └── knowledge-entry.md                                     │
│    └── seed/             # Minimal seed data (examples)           │
│        ├── locations-seed.json     (< 10KB)                       │
│        └── timezones-seed.json     (< 5KB)                        │
│                                                                   │
│  TIER 2: DOCS (Public, Git-Distributed)                          │
│  ─────────────────────────────────────────────────               │
│  /docs/                                                          │
│  /wiki/                                                          │
│                                                                   │
│  TIER 3: SYSTEM SEEDS (Tracked Templates, Local)                 │
│  ────────────────────────────────────────────────                │
│  /memory/system/                                                  │
│    ├── startup-script.md        # System startup hooks            │
│    ├── reboot-script.md         # Reboot hooks                    │
│    ├── locations/               # Seed location data              │
│    │   ├── locations-seed.json  # Initial location data           │
│    │   └── timezones-seed.json  # Timezone mappings               │
│    └── themes/                  # Default theme packs             │
│        └── prose/               # Tailwind prose theme            │
│                                                                   │
│  TIER 4: LOCAL DATA (User, Gitignored)                           │
│  ──────────────────────────────────────                          │
│  /memory/                                                         │
│    ├── private/          # User secrets (never commit)            │
│    │   ├── wizard_secret_store.key                                │
│    │   ├── github-webhook-secret.txt                              │
│    │   └── current_user.txt                                       │
│    ├── user/             # User credentials  (gitignored)         │
│    │   ├── gmail_credentials.json                                 │
│    │   └── .gmail_token.enc                                       │
│    ├── logs/             # Runtime logs                           │
│    │   ├── monitoring/   # Health checks, audits                  │
│    │   └── quotas/       # Provider quota snapshots               │
│    ├── story/            # User workflows                         │
│    ├── sandbox/          # Drafts & experiments                   │
│    ├── wizard/           # Wizard daemon state                    │
│    └── [other]/          # User projects                          │
│                                                                   │
│  TIER 5: VAULT-MD (User's Main Vault, External)                  │
│  ──────────────────────────────────────────────────              │
│  ~/Documents/uDOS Vault/ (Obsidian-compatible, not in repo)      │
│    ├── bank/             # Primary knowledge store                │
│    │   ├── personal.md   # User notes                             │
│    │   └── [...].md      # User curated content                   │
│    ├── sandbox/          # Drafts & experiments                   │
│    ├── inbox/            # Intake/imports                         │
│    ├── public-open/      # Public/published content               │
│    │   └── submissions/  # Contribution intake                    │
│    ├── private-explicit/ # Explicit private shares                │
│    ├── private-shared/   # Proximity-verified shares              │
│    ├── 05_DATA/          # User data & indexes                    │
│    │   └── sqlite/       # Task/workflow databases                │
│    └── _site/            # Static HTML exports (theme/)           │
│        ├── prose/        # Rendered Markdown (default theme)      │
│        └── [theme]/      # Other theme exports                    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

### 2. Vault-MD Role (User's Obsidian Vault)

The **vault-md** at `~/Documents/uDOS Vault/` is the **user's primary knowledge store**, handling:

| Feature | Location | Sync Method |
|---------|----------|-------------|
| **Private content** | `vault/private-explicit/` | Manual, encrypted P2P |
| **Shared content** | `vault/private-shared/` | NFC, Bluetooth (proximity-verified) |
| **Submissions** | `vault/public-open/submissions/` | QR code, MeshCore |
| **Published docs** | `vault/public-open/` | Static export to Wizard |
| **User notes** | `vault-md/` | Local only, optional backup |
| **Task database** | `vault/05_DATA/sqlite/` | Optional, local SQLite |
| **Rendered output** | `vault/_site/{theme}/` | Static HTML, served by Wizard |

**Important:** This vault is **NOT in the repo** and remains readable without uDOS installed.

---

### 3. Docs + Vault-MD Organization

**Current rule:** Local docs live in **vault-md** at `~/Documents/uDOS Vault/` (system Documents folder).  
Public reference docs live in `docs/` and `wiki/` (repo-tracked).

**Change:** Docs previously staged in `/memory/` or `/knowledge/` are now consolidated into vault-md or `docs/`/`wiki/`. The `/knowledge/` directory is no longer part of the active architecture.

**Vault-MD structure (local):**
```
~/Documents/uDOS Vault/
├── bank/
├── inbox-dropbox/
├── sandbox/
├── public-open-published/
├── private-explicit/
├── private-shared/
├── 05_DATA/sqlite/
└── _site/
```

---

### 4. Location Data Linking

**Vault-MD → Location Data Flow:**
```
~/Documents/uDOS Vault/01_KNOWLEDGE/places/cities/tokyo.md
  └── frontmatter: location_id: L300-BB00
        ↓
/vault-md/bank/locations/locations.json
  └── { "id": "L300-BB00", "name": "Tokyo Metropolitan", ... }
        ↓
/vault-md/bank/locations/timezones.json
  └── "L300-BB00": "Asia/Tokyo"
```

**Runtime Resolution:**
1. User queries vault-md knowledge → Get `location_id` from frontmatter
2. Lookup location data in vault-md/bank → Get coordinates, connections
3. Display combined rich information

---

### 5. Distribution Model

```
┌────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTION LAYERS                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PUBLIC (Git Distributed):                                      │
│  ────────────────────────                                       │
│  /core/framework/       → Schemas, templates, seed data         │
│  /docs/                → Engineering documentation             │
│  /wiki/                → User documentation                    │
│                                                                 │
│  PRIVATE (Git Submodule):                                       │
│  ─────────────────────────                                      │
│  /dev/                  → Development tools, experimental       │
│                                                                 │
│  LOCAL (Gitignored):                                            │
│  ───────────────────                                            │
│  /memory/               → User data, logs, credentials          │
│    EXCEPT:                                                      │
│    /memory/system/*.md  → Templates (tracked)                   │
│                                                                 │
│  SYNCABLE (P2P, Not Git):                                       │
│  ────────────────────────                                       │
│  /vault-md/bank/locations/   → Via MeshCore/QR/Audio transport  │
│  ~/Documents/uDOS Vault/01_KNOWLEDGE/ → Via MeshCore/QR/Audio transport │
│  /vault-md/bank/binders/     → Via MeshCore/QR/Audio transport  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### 6. File Migration Plan

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

**Phase 3: Setup Vault Structure**
```bash
mkdir -p vault-md/bank/locations
mkdir -p vault-md/bank/spatial
mkdir -p vault-md/bank/binders

# Move runtime location data to vault
# (Legacy: data previously in memory/bank/locations/)
```

**Phase 4: Vault-MD Knowledge Setup**
```bash
# Vault-MD knowledge paths (local docs vault)
mkdir -p ~/Documents/uDOS\\ Vault/01_KNOWLEDGE
mkdir -p ~/Documents/uDOS\\ Vault/01_KNOWLEDGE/places
```

---

### 7. Consistent Formats

| Data Type | Primary Format | When to Use | Migration |
|-----------|----------------|-------------|-----------|
| Schemas | `.schema.json` | Validation | — |
| Templates | `.template.json` or `.template.md` | Scaffolding | — |
| Seed Data | `.json` (< 10KB) | Framework distribution | — |
| Location Data | `.json` (< 500KB) | Runtime data | → SQLite |
| Location Data | `.db` (≥ 500KB) | Large datasets | Final |
| Vault-MD Notes | `.md` with frontmatter | Local knowledge | — |
| User Data | `.json` or `.db` | User additions | → SQLite |
| Scripts | `-script.md` | Executable uCODE | — |
| Binders | `.binder/` folder | Document projects | — |

---

### 8. Extended .md Script Support

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
1. **Clear separation** between framework, vault-md, and local runtime data
2. **Consistent distribution** model across all installations
3. **Scalable storage** with JSON → SQLite migration path
4. **P2P syncable** user data without touching git
5. **Maintainable** vault-md docs with consistent structure

### Trade-offs
1. **Migration effort** — Need to move existing files
2. **Two location lookups** — Vault-MD → Location data resolution
3. **Symlink management** — Seed data copied on first run

### Risks
1. **Breaking existing paths** — Need compatibility layer during migration
2. **Vault-MD catalog maintenance** — indexes must be kept updated

---

## Implementation Priority

| Phase | Task | Effort | Priority |
|-------|------|--------|----------|
| 1 | Create `/core/framework/` structure | 30 min | HIGH |
| 2 | Move schemas and templates | 30 min | HIGH |
| 3 | Create seed data (minimal) | 1 hour | HIGH |
| 4 | Setup `/vault-md/bank/` | 30 min | HIGH |
| 5 | Setup vault-md structure | 1 hour | MEDIUM |
| 6 | Add frontmatter to vault-md docs | 2 hours | MEDIUM |
| 7 | Create `_index.json` catalogs | 1 hour | MEDIUM |
| 8 | Implement JSON → SQLite migration | 4 hours | LOW |
| 9 | P2P sync for vault-md data | 8 hours | FUTURE |

---

## Summary Decision Matrix

| Question | Decision |
|----------|----------|
| Move data files to vault? | **YES** — `/vault-md/bank/` for user data, `/memory/system/` for system templates |
| Include templates in public repo? | **YES** — `/memory/system/` templates tracked in git |
| Consolidate to `/core/data/`? | **NO** — Split into system (tracked) and vault (local) |
| Move location data to vault? | **YES** — Full location/timezone data goes to `/vault-md/bank/locations/` |
| Keep location data in `/core/`? | **PARTIAL** — Only minimal seed data in `/core/framework/seed/` |
| Link to vault-md? | **YES** — Via `location_id` in frontmatter |
| Keep `/knowledge/`? | **NO** — Deprecated in favor of vault-md |
| JSON size threshold for SQLite? | **500KB** or **1000 records** |

---

**Status:** Ready for Review  
**Next Step:** Approve and begin Phase 1 implementation
