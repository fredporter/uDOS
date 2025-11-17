# System Architecture Diagrams

Complete visual reference for uDOS system design

---

## Command Handler Flow

### Basic Command Pipeline
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INPUT (Terminal)                            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  INPUT PARSER (uDOS_parser.py)                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Tokenize    │─>│ Validate    │─>│ Extract     │─>│ Normalize   │   │
│  │ Input       │  │ Syntax      │  │ Command     │  │ Args        │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  COMMAND ROUTER (uDOS_commands.py)                                      │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Command Lookup Table                                 │             │
│  │  ┌──────────┬─────────────────────────┐               │             │
│  │  │ Command  │ Handler Module          │               │             │
│  │  ├──────────┼─────────────────────────┤               │             │
│  │  │ HELP     │ help_handler.py         │               │             │
│  │  │ GRID     │ grid_handler.py         │               │             │
│  │  │ MEMORY   │ memory_handler.py       │               │             │
│  │  │ GUIDE    │ guide_handler.py        │               │             │
│  │  │ ...      │ ...                     │               │             │
│  │  └──────────┴─────────────────────────┘               │             │
│  └───────────────────────────────────────────────────────┘             │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │  File      │  │  Memory    │  │  Knowledge │
        │  Handler   │  │  Handler   │  │  Handler   │
        └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
               │                │                │
               ▼                ▼                ▼
        ┌────────────────────────────────────────────┐
        │  EXECUTION LAYER                           │
        │  • Read/write files                        │
        │  • Query database                          │
        │  • Update memory state                     │
        │  • Generate output                         │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │  VIEWPORT RENDERER (uDOS_viewport.py)      │
        │  ┌──────────┬──────────┬──────────┐        │
        │  │ Format   │ Apply    │ Render   │        │
        │  │ Output   │ Theme    │ to Tier  │        │
        │  └──────────┴──────────┴──────────┘        │
        └────────────────┬───────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │  TERMINAL OUTPUT                           │
        │  Text with colors, formatting, borders     │
        └────────────────────────────────────────────┘
```

---

## Grid System Architecture

### Grid Management & Storage
```
┌─────────────────────────────────────────────────────────────────┐
│  GRID SYSTEM (uDOS_grid.py)                                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Grid Manager                                            │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │  │
│  │  │ Create │  │ Load   │  │ Save   │  │ Delete │         │  │
│  │  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘         │  │
│  │      │           │           │           │               │  │
│  │      └───────────┼───────────┼───────────┘               │  │
│  │                  │           │                           │  │
│  └──────────────────┼───────────┼───────────────────────────┘  │
│                     │           │                              │
│                     ▼           ▼                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Grid Storage (memory/grids/)                           │  │
│  │                                                          │  │
│  │  grid_001.json                                          │  │
│  │  ┌────────────────────────────────────────┐             │  │
│  │  │ {                                      │             │  │
│  │  │   "id": "grid_001",                   │             │  │
│  │  │   "name": "Main Workspace",           │             │  │
│  │  │   "dimensions": [80, 24],             │             │  │
│  │  │   "cells": [                          │             │  │
│  │  │     {"x": 0, "y": 0, "content": "A"}, │             │  │
│  │  │     {"x": 1, "y": 0, "content": "B"}, │             │  │
│  │  │     ...                                │             │  │
│  │  │   ],                                  │             │  │
│  │  │   "metadata": {...}                   │             │  │
│  │  │ }                                      │             │  │
│  │  └────────────────────────────────────────┘             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PANEL SYSTEM (panel_handler.py)                                │
│                                                                  │
│  Teletext Graphics Layer on top of Grid                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  24 Block Types: █▓▒░▀▄▌▐▘▝▖▗▚▞                         │  │
│  │  16 Terrain Patterns: ocean, forest, mountain, etc.     │  │
│  │  5 Fill Patterns: checkerboard, gradient, waves, etc.   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Rendering Pipeline                                      │  │
│  │                                                          │  │
│  │  Grid Cell ──> Apply Block ──> Apply Color ──> Output   │  │
│  │               Pattern          (ANSI)         Terminal   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## TIZO Mapping System

### Geographic Coordinate Grid
```
┌──────────────────────────────────────────────────────────────────────┐
│  TIZO GRID SYSTEM (uDOS_map.py)                                      │
│                                                                       │
│  Global Grid: AA-ZZ × 001-999                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                                                             │    │
│  │   AA001 ─────────────────────> ZZ001                       │    │
│  │     │                              │                        │    │
│  │     │    World divided into        │                        │    │
│  │     │    26×26 letter grid         │                        │    │
│  │     │    × 999 numeric zones       │                        │    │
│  │     │                              │                        │    │
│  │   AA999 ─────────────────────> ZZ999                       │    │
│  │                                                             │    │
│  │  Example locations:                                         │    │
│  │  • KBFI = Seattle-Tacoma Int'l Airport (US)               │    │
│  │  • EGLL = London Heathrow (UK)                            │    │
│  │  • RJTT = Tokyo Haneda (Japan)                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  TILE System (v1.0.20b)                                     │    │
│  │                                                             │    │
│  │  Geographic Database:                                       │    │
│  │  ┌──────────┬─────────────┬────────────┬──────────────┐   │    │
│  │  │ TZONE    │ City        │ Country    │ Coordinates  │   │    │
│  │  ├──────────┼─────────────┼────────────┼──────────────┤   │    │
│  │  │ KBFI     │ Seattle     │ USA        │ 47.45N 122W  │   │    │
│  │  │ EGLL     │ London      │ UK         │ 51.47N 0.46W │   │    │
│  │  │ RJTT     │ Tokyo       │ Japan      │ 35.55N 139E  │   │    │
│  │  │ ...      │ ...         │ ...        │ ...          │   │    │
│  │  └──────────┴─────────────┴────────────┴──────────────┘   │    │
│  │                                                             │    │
│  │  250 cities, 50 countries, 120 timezones                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4-Tier Knowledge Bank Architecture

### Memory Hierarchy & Security
```
┌───────────────────────────────────────────────────────────────────────┐
│  4-TIER KNOWLEDGE ARCHITECTURE (v1.0.20)                              │
│                                                                        │
│  Security ▲  Speed ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ TIER 1: PRIVATE (Encrypted)                    🔐 HIGHEST     │ │
│  │ ┌─────────────────────────────────────────────────────────────┐│ │
│  │ │ • Personal notes, passwords, private data                  ││ │
│  │ │ • AES-256 encryption                                       ││ │
│  │ │ • User-only access                                         ││ │
│  │ │ • Storage: memory/PRIVATE/                                 ││ │
│  │ │ • Commands: PRIVATE LIST, PRIVATE ADD, PRIVATE SEARCH      ││ │
│  │ └─────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ TIER 2: SHARED (Selective)                     🔓 HIGH        │ │
│  │ ┌─────────────────────────────────────────────────────────────┐│ │
│  │ │ • Shared with trusted contacts                             ││ │
│  │ │ • Permission-based access                                  ││ │
│  │ │ • Optional encryption                                      ││ │
│  │ │ • Storage: memory/SHARED/                                  ││ │
│  │ │ • Commands: SHARED LIST, SHARED GRANT, SHARED REVOKE       ││ │
│  │ └─────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ TIER 3: COMMUNITY (Groups)                     🌐 MEDIUM      │ │
│  │ ┌─────────────────────────────────────────────────────────────┐│ │
│  │ │ • Group knowledge bases                                    ││ │
│  │ │ • Community contributions                                  ││ │
│  │ │ • Collaborative editing                                    ││ │
│  │ │ • Storage: memory/COMMUNITY/                               ││ │
│  │ │ • Commands: COMMUNITY JOIN, COMMUNITY SHARE, COMMUNITY LIST││ │
│  │ └─────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ TIER 4: PUBLIC (Open Knowledge)                📚 LOWEST     │ │
│  │ ┌─────────────────────────────────────────────────────────────┐│ │
│  │ │ • Public knowledge base (500+ guides)                      ││ │
│  │ │ • No encryption                                            ││ │
│  │ │ • Full-text search (SQLite FTS)                            ││ │
│  │ │ • Storage: knowledge/                                      ││ │
│  │ │ • Commands: KB LIST, KB SEARCH, KB SHOW                    ││ │
│  │ └─────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Search Performance (Full-Text):                                      │
│  ┌────────────┬──────────────┬────────────┬─────────────┐            │
│  │ Tier       │ Size         │ Speed      │ Security    │            │
│  ├────────────┼──────────────┼────────────┼─────────────┤            │
│  │ PRIVATE    │ < 10MB       │ <10ms      │ Encrypted   │            │
│  │ SHARED     │ < 50MB       │ <25ms      │ Selective   │            │
│  │ COMMUNITY  │ < 200MB      │ <50ms      │ Group-based │            │
│  │ PUBLIC     │ < 500MB      │ <100ms     │ Open        │            │
│  └────────────┴──────────────┴────────────┴─────────────┘            │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Extension System Architecture

### POKE Server & Extension Loading
```
┌──────────────────────────────────────────────────────────────────────┐
│  EXTENSION SYSTEM (v1.0.11)                                          │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Extension Directory Structure                                 │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  extensions/                                             │ │ │
│  │  │  ├── core/          (System extensions, always loaded)   │ │ │
│  │  │  ├── bundled/       (Pre-installed extensions)           │ │ │
│  │  │  │   ├── web/       (Web server, POKE endpoints)         │ │ │
│  │  │  │   └── teletext/  (Teletext graphics renderer)         │ │ │
│  │  │  ├── cloned/        (User-installed from repos)          │ │ │
│  │  │  └── fonts/         (Font collection)                    │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  POKE Server (uDOS_server.py)                                 │ │
│  │                                                                │ │
│  │  REST API Endpoints:                                          │ │
│  │  ┌──────────────┬────────────────────────────────────────┐   │ │
│  │  │ Endpoint     │ Function                               │   │ │
│  │  ├──────────────┼────────────────────────────────────────┤   │ │
│  │  │ /api/exec    │ Execute uDOS command                   │   │ │
│  │  │ /api/grid    │ Get/update grid data                   │   │ │
│  │  │ /api/memory  │ Access memory tiers                    │   │ │
│  │  │ /api/status  │ System status                          │   │ │
│  │  │ /api/theme   │ Get/set theme                          │   │ │
│  │  │ ...          │ (62 total endpoints)                   │   │ │
│  │  └──────────────┴────────────────────────────────────────┘   │ │
│  │                                                                │ │
│  │  Extension Loading:                                           │ │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  │ │
│  │  │ Discover │─>│ Validate  │─>│ Load     │─>│ Register  │  │ │
│  │  │ metadata │  │ manifest  │  │ module   │  │ handlers  │  │ │
│  │  └──────────┘  └───────────┘  └──────────┘  └───────────┘  │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Viewport System (Screen Tier Adaptation)

### 15-Tier Responsive Layout
```
┌──────────────────────────────────────────────────────────────────────┐
│  VIEWPORT SYSTEM (uDOS_viewport.py)                                  │
│                                                                       │
│  Screen Tier Detection & Adaptation (0-14)                           │
│  ┌────┬────────┬────────┬──────────────────────────────────────┐    │
│  │Tier│ Width  │ Height │ Device Examples                      │    │
│  ├────┼────────┼────────┼──────────────────────────────────────┤    │
│  │ 0  │ 40     │ 12     │ Smartwatch, tiny displays           │    │
│  │ 1  │ 40     │ 15     │ Old mobile phones                   │    │
│  │ 2  │ 60     │ 20     │ Feature phones                      │    │
│  │ 3  │ 80     │ 24     │ Classic terminals, VT100            │    │
│  │ 4  │ 80     │ 24     │ DOS terminals                       │    │
│  │ 5  │ 100    │ 30     │ Modern terminals (default)          │    │
│  │ 6  │ 120    │ 40     │ Large terminal windows              │    │
│  │ 7  │ 132    │ 43     │ VT220, wide terminals               │    │
│  │ 8  │ 140    │ 45     │ Wide screen terminals               │    │
│  │ 9  │ 160    │ 50     │ Extra wide terminals                │    │
│  │ 10 │ 200    │ 60     │ Modern monitors (recommended)       │    │
│  │ 11 │ 220    │ 70     │ Large monitors                      │    │
│  │ 12 │ 240    │ 80     │ Extra large monitors                │    │
│  │ 13 │ 280    │ 90     │ 4K displays                         │    │
│  │ 14 │ 320    │ 100    │ 4K ultra-wide displays              │    │
│  └────┴────────┴────────┴──────────────────────────────────────┘    │
│                                                                       │
│  Content Adaptation:                                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Tier 0-2:  Minimal text, essential commands only           │   │
│  │  Tier 3-4:  Standard terminal, 80-column layout             │   │
│  │  Tier 5-9:  Enhanced features, diagrams, colors             │   │
│  │  Tier 10+:  Full features, rich graphics, panels            │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

**See Also**:
- [Architecture](../Architecture.md) - Detailed system design
- [Data Flow Diagrams](../diagrams/dataflow/) - Process visualization
- [Concept Maps](../diagrams/concepts/) - Learning aids
- [UI Mockups](../diagrams/ui/) - Interface layouts
