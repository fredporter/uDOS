---
title: Data Folder Consolidation (2026-01-13)
status: executed
version: 1.0.0
---

# Data Folder Consolidation Assessment

## Current State

### Three Data Locations

| Folder | Contents | Type | Git Status |
|--------|----------|------|------------|
| `/data` | `inventory.db`, `scenarios.db`, `survival.db` | User/runtime data | Should be gitignored |
| `/mapdata` | `earth/`, `space/`, `dungeons/`, `waypoints/` | User map data | Should be gitignored |
| `/core/data` | `geography/`, `locations.json`, `maps/`, `models/`, `prompts/`, `schemas/`, `templates/` | System reference | Version controlled ✅ |

---

## Recommendation: DO NOT Consolidate into /core/data

### Why Not?

**Different purposes:**
1. **`/core/data`** = System reference data (read-only, shipped with uDOS)
   - Configuration schemas
   - System prompts and templates
   - Reference models and geography data
   - Should be version controlled

2. **`/data` + `/mapdata`** = User runtime data (read-write, generated at runtime)
   - User game state (inventory, scenarios)
   - User-created maps and waypoints
   - Should NOT be version controlled
   - Should be in `/memory/` (user workspace)

---

## Correct Consolidation Plan

### Keep Separate by Purpose

```
/core/data/                     ← SYSTEM REFERENCE (stays in git)
├── geography/                  (reference location data)
├── locations.json              (location reference)
├── maps/                       (map templates)
├── models/                     (reference models)
├── prompts/                    (system prompts)
├── schemas/                    (configuration schemas)
└── templates/                  (system templates)

/memory/apps/                   ← USER/RUNTIME DATA (gitignored)
├── games/                      ✨ MOVE /data → here
│   ├── inventory.db
│   ├── scenarios.db
│   └── survival.db
└── maps/                       ✨ MOVE /mapdata → here
    ├── earth/
    ├── space/
    ├── dungeons/
    └── waypoints/

/data                           ✨ DELETE (moved to memory/apps/games/)
/mapdata                        ✨ DELETE (moved to memory/apps/maps/)
```

---

## Why This Structure is Correct

### 1. Separation of Concerns
- **Core** = System (shipped)
- **Memory** = User (local)

### 2. Git Discipline
- `/core/data` is tracked (reference data)
- `/memory/` is gitignored (user data)

### 3. TinyCore Linux Compatibility
- `/core/data` → read-only system files
- `/memory/` → user writable space

### 4. Backup & Sync
- System data: Git
- User data: User chooses (cloud, USB, mesh)

---

## Migration Commands (If You Want to Proceed)

```bash
# 1. Create directories
mkdir -p memory/apps/games
mkdir -p memory/apps/maps

# 2. Move user data
mv data/* memory/apps/games/
mv mapdata/* memory/apps/maps/

# 3. Delete empty folders
rmdir data
rmdir mapdata

# 4. Update code references (if any)
# Search for: "data/inventory.db", "mapdata/earth", etc.
# Replace with: "memory/apps/games/inventory.db", "memory/apps/maps/earth", etc.
```

---

## Answer to Your Question

**"Can /data and /mapdata be consolidated into /core?"**

**No.** They serve different purposes:
- `/core/data` = System reference (version controlled)
- `/data` + `/mapdata` = User runtime (should NOT be version controlled)

**Instead:** Move `/data` and `/mapdata` to `/memory/apps/` where user data belongs.

---

## Summary

| Action | Folder | Destination | Reason |
|--------|--------|-------------|--------|
| **KEEP** | `/core/data` | (unchanged) | System reference, version controlled |
| **MOVE** | `/data` | `memory/apps/games/` | User runtime data, gitignored |
| **MOVE** | `/mapdata` | `memory/apps/maps/` | User runtime data, gitignored |

---

*Assessment Date: 2026-01-13*  
*Recommendation: Keep separate by purpose*
