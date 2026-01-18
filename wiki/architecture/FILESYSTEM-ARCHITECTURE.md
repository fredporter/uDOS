# uDOS Filesystem Architecture (v1.0.0.51)

## Overview

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
│   ├── ucode/               # User scripts (.upy)
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

| Directory | Content | Update Method |
|-----------|---------|---------------|
| `core/` | Python modules, constants | Software updates |
| `knowledge/` | Global knowledge bank | Knowledge updates |
| `mapdata/` | Pregenerated map tiles | Map data updates |
| `extensions/` | API, transport, tools | Extension updates |

**Characteristics**:
- Distributed with software releases
- User cannot directly modify
- Versioned independently (see `version.json`)
- Pulled from central repository

### User Data (Read-Write, Local)

| Directory | Content | Backup Method |
|-----------|---------|---------------|
| `memory/user.json` | Profile, settings | User backup |
| `memory/state.json` | Session state | Auto-save |
| `memory/ucode/` | User scripts | User backup |
| `memory/contributions/` | Wiki submissions | Sync to server |
| `memory/mapdata/` | Discoveries, bookmarks | User backup |
| `memory/saves/` | Game checkpoints | User backup |

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
├── version.json           # { "version": "1.0.0.0", "updated": "2026-01-06" }
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

**Article Format** (`.md` with frontmatter):
```markdown
---
title: Fire Starting Methods
category: survival
version: 1.2.0
contributors:
  - alice@example.com
  - bob@example.com
last_updated: 2026-01-05
tags: [fire, wilderness, emergency]
---

# Fire Starting Methods

Content here...
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

**Contribution Format**:
```json
{
  "contribution_id": "kb_edit_001",
  "type": "edit",
  "target": "knowledge/survival/fire-starting.md",
  "author": "user@device_id",
  "submitted": "2026-01-06T10:30:00Z",
  "status": "pending",
  "changes": {
    "section": "## Friction Methods",
    "action": "append",
    "content": "### Hand Drill Technique\n\nThe hand drill is one of the oldest..."
  },
  "review": {
    "votes_up": 0,
    "votes_down": 0,
    "reviewer_notes": []
  }
}
```

### Contribution Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE CONTRIBUTION FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. USER CREATES EDIT                                               │
│     └── memory/contributions/knowledge/pending/*.json               │
│                                                                     │
│  2. USER SUBMITS (via Wizard Server or Mesh)                        │
│     └── Contribution synced to review system                        │
│     └── Status: "submitted"                                         │
│                                                                     │
│  3. COMMUNITY REVIEW                                                │
│     └── Other users vote on contribution                            │
│     └── Reviewers add notes/suggestions                             │
│                                                                     │
│  4. APPROVAL                                                        │
│     └── Threshold reached (e.g., +5 votes)                          │
│     └── Moderator approves                                          │
│                                                                     │
│  5. MERGE INTO KNOWLEDGE BANK                                       │
│     └── Added to next knowledge/ version                            │
│     └── Contributor credited in frontmatter                         │
│     └── Distributed with knowledge update                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
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
│           └── scripts/         # Dungeon logic (.upy)
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

**Bookmark Format**:
```json
{
  "bookmarks": [
    {
      "id": "bm_001",
      "name": "Home",
      "coordinates": "L300:BD14-CG15-BT21",
      "layer": 300,
      "icon": "home",
      "created": "2026-01-05T08:00:00Z"
    },
    {
      "id": "bm_002", 
      "name": "Secret Cave",
      "coordinates": "L200:BD14-CG15-BT21",
      "layer": 200,
      "icon": "cave",
      "notes": "Found rare minerals here",
      "created": "2026-01-06T14:30:00Z"
    }
  ]
}
```

---

## Waypoint Contribution System

Users can propose new waypoints at real-world locations:

```
memory/contributions/waypoints/
├── pending/
│   └── wp_proposal_001.json
└── submitted/
    └── wp_proposal_001.json
```

**Waypoint Proposal Format**:
```json
{
  "proposal_id": "wp_prop_001",
  "type": "new_waypoint",
  "waypoint": {
    "name": "Central Park Fountain",
    "type": "nature",
    "coordinates": {
      "cascading": "L300:BD14-CG15-BT21",
      "lat": 40.7829,
      "lon": -73.9654
    },
    "description": "Beautiful fountain in the heart of Central Park",
    "photo_hash": "sha256:abc123...",
    "features": ["rest_point", "community_space"]
  },
  "author": "user@device_id",
  "submitted": "2026-01-06T12:00:00Z",
  "verification": {
    "gps_confirmed": true,
    "photo_verified": false,
    "community_votes": 0
  }
}
```

---

## Version Management

Each data category has independent versioning:

| Component | Version File | Example |
|-----------|--------------|---------|
| Core | `core/version.json` | v1.0.0.51 |
| Knowledge | `knowledge/version.json` | v1.0.0.0 |
| Map Data | `mapdata/version.json` | v1.0.0.0 |
| API | `extensions/api/version.json` | v1.0.3.0 |
| Transport | `extensions/transport/version.json` | v1.0.0.32 |

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

*Document Version: 1.0.0.51*
*Last Updated: 2026-01-06*
