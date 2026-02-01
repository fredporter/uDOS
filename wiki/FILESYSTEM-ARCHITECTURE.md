# uDOS Filesystem Architecture (v1.0.0.52)

**Last Updated:** 2026-01-24
**Status:** Active Standard
**Author:** uDOS Engineering

uDOS separates **system data** (read-only, distributed) from **user data** (read-write, local). This enables offline-first operation while supporting community contributions through a wiki-like update system.

---

## Directory Structure

```
uDOS/
├── core/                    # [SYSTEM] Core Python modules
│   ├── commands/            # Command handlers
│   ├── constants/           # Grid, realms, system constants
│   ├── data/                # System data files
│   │   ├── cities.json      # City reference data
│   │   └── system.json      # System configuration
│   ├── docs/                # System documentation
│   ├── runtime/             # uPY interpreter
│   ├── services/            # Core services
│   └── ui/                  # TUI components
│
├── knowledge/               # [SYSTEM] Global Knowledge Bank (read-only)
│   ├── version.json         # Knowledge bank version
│   ├── checklists/          # Task checklists
│   ├── communication/       # Communication guides
│   ├── fire/                # Fire-making knowledge
│   ├── food/                # Food preparation/foraging
│   ├── medical/             # First aid, health
│   ├── navigation/          # Orientation, maps
│   ├── shelter/             # Shelter building
│   ├── skills/              # General skills
│   ├── survival/            # Survival techniques
│   ├── tech/                # Technology guides
│   ├── tools/               # Tool usage
│   └── water/               # Water sourcing/purification
│
├── mapdata/                 # [SYSTEM] Pregenerated Map Layers
│   ├── version.json         # Map data version
│   ├── dungeons/            # Layers 100-199
│   │   ├── tutorial/        # 100-109: Hand-crafted tutorials
│   │   ├── easy/            # 110-129: Beginner dungeons
│   │   ├── medium/          # 130-149: Intermediate
│   │   ├── hard/            # 150-169: Advanced
│   │   ├── expert/          # 170-189: Expert
│   │   └── legendary/       # 190-199: Legendary
│   ├── earth/               # Layers 300-399
│   │   ├── L300/            # World overview tiles
│   │   ├── L310/            # Continental tiles
│   │   ├── L320/            # Regional tiles
│   │   └── L330/            # City tiles (major cities)
│   ├── space/               # Layers 600-899
│   │   ├── orbit/           # 600-699: Near space
│   │   ├── solar/           # 700-799: Solar system
│   │   └── galaxy/          # 800-899: Galactic data
│   └── waypoints/           # Global waypoint registry
│       ├── heritage.json    # Monument waypoints
│       ├── nature.json      # Park/nature waypoints
│       └── transit.json     # Transit hub waypoints
│
├── extensions/              # [SYSTEM] Extension modules
│   ├── api/                 # REST/WebSocket API
│   ├── transport/           # Mesh/BT/NFC transports
│   └── vscode/              # VS Code extension
│
├── memory/                  # [USER] User workspace (gitignored)
│   ├── user.json            # User profile & settings
│   ├── state.json           # Session state
│   ├── logs/                # Log files
│   ├── ucode/               # User scripts (TypeScript in .md)
│   ├── documents/           # User documents
│   ├── contributions/       # Pending wiki contributions
│   │   ├── knowledge/       # Knowledge bank edits
│   │   ├── waypoints/       # Waypoint proposals
│   │   └── mapfixes/        # Map correction reports
│   ├── mapdata/             # User map discoveries
│   │   ├── explored/        # Explored tile cache
│   │   ├── custom/          # User-created content
│   │   └── bookmarks/       # Saved locations
│   └── saves/               # Game saves / checkpoints
│
├── wizard/                  # [SYSTEM] Wizard Server (optional)
│   ├── providers/           # AI providers
│   ├── services/            # Web services
│   └── config/              # Wizard configuration
│
└── app/                     # [SYSTEM] Tauri desktop app
    ├── src/                 # Svelte frontend
    └── src-tauri/           # Rust backend
```

---

## Data Classification

### System Data (Read-Only, Distributed)

| Directory     | Content                   | Update Method     |
| ------------- | ------------------------- | ----------------- |
| `core/`       | Python modules, constants | Software updates  |
| `knowledge/`  | Global knowledge bank     | Knowledge updates |
| `mapdata/`    | Pregenerated map tiles    | Map data updates  |
| `extensions/` | API, transport, tools     | Extension updates |

**Characteristics**:

- Distributed with software releases
- User cannot directly modify
- Versioned independently (see `version.json`)
- Pulled from central repository

### User Data (Read-Write, Local)

| Directory               | Content                | Backup Method  |
| ----------------------- | ---------------------- | -------------- |
| `memory/user.json`      | Profile, settings      | User backup    |
| `memory/state.json`     | Session state          | Auto-save      |
| `memory/ucode/`         | User scripts           | User backup    |
| `memory/contributions/` | Wiki submissions       | Sync to server |
| `memory/mapdata/`       | Discoveries, bookmarks | User backup    |
| `memory/saves/`         | Game checkpoints       | User backup    |

**Characteristics**:

- Fully controlled by user
- Never uploaded without consent
- Gitignored (not in repo)
- Portable between devices via mesh sync

---

## Knowledge Bank System

### Global Knowledge (Read-Only)

```
knowledge/
├── version.json           # { "version": "1.0.0.0", "updated": "2026-01-24" }
├── survival/
│   ├── _index.md          # Category overview
│   ├── fire-starting.md   # Individual article
│   ├── shelter-types.md
│   └── water-finding.md
├── medical/
│   ├── _index.md
│   ├── first-aid.md
│   └── cpr-guide.md
└── ...
```

### User Contributions (Wiki System)

Users can propose changes to the knowledge bank:

```
memory/contributions/knowledge/
├── pending/
│   └── survival-fire-starting-edit-001.json
├── submitted/
│   └── survival-fire-starting-edit-001.json
└── approved/
    └── (cleared after merge)
```

---

## Map Data System

### Pregenerated Content (System)

```
mapdata/
├── version.json
├── dungeons/
│   └── tutorial/
│       └── L100/
│           ├── manifest.json    # Dungeon metadata
│           ├── tiles/           # Tile data files
│           │   ├── AA10.json
│           │   ├── AA11.json
│           │   └── ...
│           ├── entities/        # NPCs, items, enemies
│           └── scripts/         # Dungeon logic (TypeScript in .md)
├── earth/
│   └── L300/
│       ├── manifest.json
│       └── tiles/
│           ├── AA10.json        # Each tile: terrain, POIs, waypoints
│           └── ...
└── waypoints/
    └── global.json              # Master waypoint registry
```

### User Map Data

```
memory/mapdata/
├── explored/                    # Discovered tiles (cache)
│   └── L300/
│       └── BD14.json            # User's explored version
├── custom/                      # User-created content
│   ├── dungeons/                # Custom dungeon designs
│   └── buildings/               # Custom building interiors
├── bookmarks/                   # Saved locations
│   └── bookmarks.json
└── discoveries/                 # User discoveries
    └── discoveries.json
```

---

## Version Management

Each data category has independent versioning:

| Component | Version File                        | Current  |
| --------- | ----------------------------------- | -------- |
| Core      | `core/version.json`                 | v1.1.0.0 |
| Knowledge | `knowledge/version.json`            | v1.0.0.0 |
| Map Data  | `mapdata/version.json`              | v1.0.0.0 |
| API       | `extensions/api/version.json`       | v1.1.0.0 |
| Transport | `extensions/transport/version.json` | v1.0.1.0 |

**Update Independence**:

- Knowledge can update without core changes
- Map data can update without knowledge changes
- Users choose which updates to apply

---

## Offline-First Principles

1. **All system data bundled locally** - No internet required for base operation
2. **User data never leaves device** - Unless explicitly synced
3. **Contributions queue locally** - Submitted when connectivity available
4. **Mesh sync for user-to-user** - Direct device sharing without cloud

---

## Related Documentation

- [Layer Architecture](LAYER-ARCHITECTURE.md) — Spatial layer organization
- [Database Architecture](DATABASE-ARCHITECTURE.md) — Data indexing and querying
- [../../AGENTS.md](../../AGENTS.md) — Development guidelines
- [../../docs/development-streams.md](../../docs/development-streams.md) — Implementation roadmap

---

**Status:** Active Architecture Standard
**Repository:** https://github.com/fredporter/uDOS
