# Concept Diagrams for uDOS

Conceptual diagrams showing relationships, hierarchies, and mental models.

## Table of Contents
1. [Command Category Tree](#1-command-category-tree)
2. [Knowledge Interconnections](#2-knowledge-interconnections)
3. [Skill Progression Paths](#3-skill-progression-paths)
4. [Feature Dependencies](#4-feature-dependencies)
5. [Memory Tier Hierarchy](#5-memory-tier-hierarchy)
6. [Extension Architecture](#6-extension-architecture)
7. [Theme System](#7-theme-system)
8. [File Organization](#8-file-organization)
9. [User Workflow Patterns](#9-user-workflow-patterns)
10. [Learning Path](#10-learning-path)
11. [Data Flow Concepts](#11-data-flow-concepts)
12. [Security Model](#12-security-model)
13. [Viewport Adaptation](#13-viewport-adaptation)
14. [Grid Coordinate System](#14-grid-coordinate-system)
15. [uCODE Language Structure](#15-ucode-language-structure)
16. [Knowledge Bank Organization](#16-knowledge-bank-organization)
17. [Command Pipeline](#17-command-pipeline)
18. [API Integration](#18-api-integration)
19. [Offline-First Philosophy](#19-offline-first-philosophy)
20. [Community Ecosystem](#20-community-ecosystem)

---

## 1. Command Category Tree

```
uDOS Commands (80+)
│
├── File Management
│   ├── LOAD          Load files
│   ├── SAVE          Save files
│   ├── FILES         List directory
│   └── CD            Change directory
│
├── Knowledge Access
│   ├── GUIDE         Interactive guides
│   ├── DIAGRAM       ASCII diagrams
│   ├── DOC           Documentation
│   ├── MANUAL        Quick reference
│   ├── HANDBOOK      Structured reader
│   └── EXAMPLE       Code examples
│
├── Graphics & Display
│   ├── GRID          Grid system
│   ├── PANEL         Teletext blocks
│   ├── THEME         Color themes
│   └── VIEWPORT      Screen info
│
├── Scripting & Automation
│   ├── RUN           Execute scripts
│   ├── EDIT          Script editor
│   └── DEBUG         uCODE debugger
│
├── Mapping & Navigation
│   ├── MAP           Global mapping
│   ├── TIZO          Timezone/location
│   └── NAVIGATE      Route planning
│
├── System & Configuration
│   ├── CONFIG        Settings
│   ├── REPAIR        Diagnostics
│   ├── STATUS        System info
│   └── VERSION       Version info
│
└── Help & Information
    ├── HELP          Command help
    ├── INFO          Detailed info
    └── ABOUT         About uDOS
```

**Dependencies**:
- File commands underpin all data operations
- Knowledge commands build on file system
- Graphics requires viewport + theme system
- Scripting integrates all command categories

---

## 2. Knowledge Interconnections

```
                    Knowledge Bank
                    ┌──────────────┐
                    │  500+ Guides │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌─────────┐       ┌──────────┐      ┌──────────┐
  │ Survival│       │  Skills  │      │ Projects │
  └────┬────┘       └─────┬────┘      └────┬─────┘
       │                  │                 │
       ├──Water           ├──Building       ├──Homesteading
       ├──Food            ├──Crafts         ├──Energy Systems
       ├──Shelter         ├──Tools          └──Automation
       └──Medical         └──Navigation

Cross-References:
  Water ←→ Survival + Health
  Building ←→ Skills + Projects
  Tools ←→ All categories

Search Indices:
  • Full-text (SQLite FTS5)
  • Category tags
  • Skill level
  • Dependencies
```

**Key Insight**: Knowledge is interconnected, not siloed.
Cross-references enable discovery paths.

---

## 3. Skill Progression Paths

```
                    Beginner
                    ┌──────┐
                    │ Start│
                    └───┬──┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    Terminal        Knowledge       Scripting
    ┌──────┐        ┌──────┐        ┌──────┐
    │ HELP │        │GUIDE │        │ RUN  │
    │ DIR  │        │ DOC  │        │ EDIT │
    └───┬──┘        └───┬──┘        └───┬──┘
        │               │               │
        ▼               ▼               ▼
    Intermediate    Intermediate    Intermediate
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  GRID    │    │ HANDBOOK │    │  DEBUG   │
    │  PANEL   │    │ DIAGRAM  │    │ LIBRARY  │
    └─────┬────┘    └─────┬────┘    └─────┬────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                      Advanced
                    ┌──────────┐
                    │EXTENSION │
                    │  AUTHOR  │
                    └──────────┘
```

**Learning Milestones**:
1. Basic commands (Day 1)
2. Knowledge access (Week 1)
3. Scripting basics (Week 2)
4. Advanced features (Month 1)
5. Extension development (Month 3)

---

## 4. Feature Dependencies

```
Core Features
┌─────────────────────────────────────┐
│  File System + Command Parser       │
└───────────┬─────────────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌─────────┐
│Viewport │   │ Theme   │
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌─────────┐
│  GRID   │   │ PANEL   │
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            │
            ▼
    ┌──────────────┐
    │   Graphics   │
    │   Commands   │
    └──────────────┘

Knowledge Features
┌─────────────────────────────────────┐
│  Knowledge Bank (Markdown files)    │
└───────────┬─────────────────────────┘
            │
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
 GUIDE   DIAGRAM  HANDBOOK
```

**Dependency Rules**:
- Core features must be stable first
- Graphics builds on viewport + themes
- Knowledge builds on file system
- Extensions can use all features

---

## 5. Memory Tier Hierarchy

```
             Speed ↑           Security ↑
             Access Time ↓     Isolation ↑

PRIVATE (Tier 0)     ←→  Encrypted, User-only
  ⎪ <10ms access         • Personal notes
  ⎪ Encrypted            • Passwords
  ⎪ User-only            • Private scripts
  ↓

SHARED (Tier 1)      ←→  Selective sharing
  ⎪ <25ms access         • Team documents
  ⎪ Encrypted            • Shared configs
  ⎪ Selective            • Collaboration
  ↓

COMMUNITY (Tier 2)   ←→  Group access
  ⎪ <50ms access         • Community guides
  ⎪ Plain text           • Shared scripts
  ⎪ Group-level          • Templates
  ↓

PUBLIC (Tier 3)      ←→  Open access
  ⎪ <100ms access        • Public docs
  ⎪ Plain text           • Examples
  ⎪ Everyone             • Knowledge base

Storage Matrix:
┌─────────┬──────┬──────────┬──────┐
│ Tier    │Speed │ Security │Access│
├─────────┼──────┼──────────┼──────┤
│PRIVATE  │ 10ms │ AES-256  │ User │
│SHARED   │ 25ms │ AES-128  │ Team │
│COMMUNIT │ 50ms │ None     │Group │
│PUBLIC   │100ms │ None     │ All  │
└─────────┴──────┴──────────┴──────┘
```

**Trade-offs**: Speed vs Security vs Accessibility

---

## 6. Extension Architecture

```
Extension Lifecycle
┌──────────────────────────────────────┐
│ 1. Discovery                         │
│    Scan extensions/ directory        │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 2. Validation                        │
│    Check metadata + dependencies     │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 3. Loading                           │
│    Import Python modules             │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 4. Registration                      │
│    Add commands to router            │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 5. Active                            │
│    Available for execution           │
└──────────────────────────────────────┘

Extension Types:
├── Command Extensions
│   └── Add new commands
├── Handler Extensions
│   └── Modify command behavior
├── Theme Extensions
│   └── New color schemes
└── Font Extensions
    └── Custom fonts
```

**Extension API**:
- `create_handler()` factory
- Command routing hooks
- Viewport access
- Theme system integration

---

## 7. Theme System

```
Theme Hierarchy
┌───────────────┐
│  Base Theme   │  ←─ Default colors
└───────┬───────┘
        │
    ┌───┴───┐
    │       │
    ▼       ▼
┌───────┐ ┌───────┐
│Modern │ │Retro  │
└───┬───┘ └───┬───┘
    │         │
    ├─Cyberpunk    ├─Commodore
    ├─Hacker       ├─Apple ][
    └─Matrix       └─Teletext

Color Mapping:
┌──────────┬──────────┬──────────┐
│ Element  │  Modern  │  Retro   │
├──────────┼──────────┼──────────┤
│ Primary  │ #00ff00  │ #00aa00  │
│ Secondary│ #00cccc  │ #5555ff  │
│ Error    │ #ff0000  │ #ff5555  │
│ Warning  │ #ffaa00  │ #ffff55  │
└──────────┴──────────┴──────────┘

ANSI Escape Codes:
  Modern → 256 colors
  Retro  → 16 colors
  Basic  → 8 colors
```

**Adaptation**: Themes adapt to terminal capabilities

---

## 8. File Organization

```
uDOS Directory Structure
┌─────────────────────────────────────┐
│ uDOS/                               │
├─────────────────────────────────────┤
│ ├── core/           Python modules │
│ │   ├── commands/   Command handlers│
│ │   ├── services/   Core services  │
│ │   └── utils/      Utilities      │
│ │                                   │
│ ├── wiki/           Documentation  │
│ │   ├── diagrams/   ASCII diagrams │
│ │   └── guides/     User guides    │
│ │                                   │
│ ├── knowledge/      Knowledge Bank │
│ │   ├── survival/   Survival guides│
│ │   ├── skills/     Skill tutorials│
│ │   └── datasets/   Reference data │
│ │                                   │
│ ├── extensions/     Extensions     │
│ │   ├── bundled/    Built-in       │
│ │   ├── core/       Core extensions│
│ │   └── fonts/      Font files     │
│ │                                   │
│ ├── memory/         Runtime data   │
│ │   ├── modules/    User scripts   │
│ │   └── logs/       Log files      │
│ │                                   │
│ └── examples/       Code examples  │
│     ├── *.uscript   uCODE scripts  │
│     └── *.py        Python examples│
└─────────────────────────────────────┘
```

**Organization Principles**:
- Separation of code (core) and content (knowledge)
- User data isolated in memory/
- Extensions modular and optional

---

## 9. User Workflow Patterns

```
Common Workflows

1. Learning New Skill
   GUIDE LIST → GUIDE START <skill> → GUIDE NEXT → ... → GUIDE COMPLETE

2. Building Project
   DOC <topic> → HANDBOOK <chapter> → EXAMPLE <name> → RUN/EDIT

3. Scripting Automation
   EXAMPLE LIST → EXAMPLE <name> → EDIT → DEBUG → RUN → SAVE

4. Knowledge Discovery
   GUIDE SEARCH → DIAGRAM SHOW → DOC <topic> → HANDBOOK

5. System Configuration
   CONFIG → THEME → VIEWPORT → STATUS → SAVE

Workflow Graph:
   LEARN ──→ EXPLORE ──→ BUILD ──→ AUTOMATE
     ↑         ↓          ↓          ↓
     │      RESEARCH   TEST      DEPLOY
     │         ↓          ↓          ↓
     └─────  REFINE ←── DEBUG ←── ITERATE
```

**User Journey**: Learn → Explore → Build → Automate → Share

---

## 10. Learning Path

```
30-Day uDOS Learning Path
┌────────────────────────────────────┐
│ Week 1: Foundations                │
├────────────────────────────────────┤
│ Day 1-2:  Terminal basics          │
│           HELP, FILES, CD          │
│ Day 3-4:  Knowledge access         │
│           GUIDE, DOC, HANDBOOK     │
│ Day 5-7:  Practice & exploration   │
└────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│ Week 2: Intermediate               │
├────────────────────────────────────┤
│ Day 8-10:  Graphics system         │
│            GRID, PANEL, THEME      │
│ Day 11-12: Scripting basics        │
│            RUN, EDIT, EXAMPLE      │
│ Day 13-14: First automation        │
└────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│ Week 3: Advanced                   │
├────────────────────────────────────┤
│ Day 15-17: uCODE language          │
│ Day 18-20: Debugging & testing     │
│ Day 21:    Project work            │
└────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│ Week 4: Mastery                    │
├────────────────────────────────────┤
│ Day 22-25: Extension development   │
│ Day 26-28: Knowledge contribution  │
│ Day 29-30: Community participation │
└────────────────────────────────────┘

Milestones:
  ● Day 7:  First useful workflow
  ● Day 14: First automation script
  ● Day 21: Complete personal project
  ● Day 30: Contribute to community
```

---

## 11. Data Flow Concepts

```
Request → Process → Response Pattern

User Input
    ↓
┌─────────────┐
│   Parser    │  Tokenize + validate
└──────┬──────┘
       ↓
┌─────────────┐
│   Router    │  Find handler
└──────┬──────┘
       ↓
┌─────────────┐
│  Handler    │  Execute logic
└──────┬──────┘
       ↓
┌─────────────┐
│  Viewport   │  Format output
└──────┬──────┘
       ↓
Terminal Output

Error Handling:
  Parser Error → Syntax help
  Router Error → Command not found
  Handler Error → Graceful message
  Viewport Error → Fallback formatting
```

**Pipeline Philosophy**: Each stage has single responsibility

---

## 12. Security Model

```
Security Layers (v1.1.0 planned)

┌─────────────────────────────────────┐
│ User Roles                          │
├─────────────────────────────────────┤
│ Root    → Full access (2FA)         │
│ Wizard  → VSCode + Git              │
│ Power   → API + Extensions          │
│ User    → Standard commands         │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Command-Based I/O                   │
├─────────────────────────────────────┤
│ API/OK       → Gemini access        │
│ WEB/FETCH    → HTTP requests        │
│ OFFLINE/PROMPT → Local AI           │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Installation Types                  │
├─────────────────────────────────────┤
│ Clone  → Development (Wizard)       │
│ Spawn  → Production (User)          │
│ Hybrid → Power users (Power)        │
└─────────────────────────────────────┘

Principle: Explicit beats implicit
```

---

## 13. Viewport Adaptation

```
Screen Tier Adaptation (15 tiers, 0-14)

Content Complexity →
                ┌────────────────┐
    Tier 0      │ 40×12 Terminal │  Text only
                └────────────────┘
                        ↓
    Tier 5      ┌────────────────┐
                │ 80×24 Standard │  ASCII art
                └────────────────┘
                        ↓
    Tier 10     ┌────────────────┐
                │ 120×40 Wide    │  Tables + diagrams
                └────────────────┘
                        ↓
    Tier 14     ┌────────────────┐
                │ 200×60 Ultra   │  Full features
                └────────────────┘

Adaptation Rules:
  • Tier 0-4:   Text only, no tables
  • Tier 5-9:   ASCII art, simple tables
  • Tier 10-14: Full features, complex layouts

Auto-detection: Terminal size → Tier selection
```

---

## 14. Grid Coordinate System

```
Global Grid (AA-ZZ × 001-999)

     001   002   003  ...  999
AA  [   ] [   ] [   ] ... [   ]
AB  [   ] [   ] [   ] ... [   ]
AC  [   ] [   ] [   ] ... [   ]
...
ZZ  [   ] [   ] [   ] ... [   ]

Total cells: 676 columns × 999 rows = 675,324 cells

Cell References (Excel-style):
  AA001, AB123, ZZ999

TIZO Integration:
  20 global cities mapped to cells
  Example: "New York" → "NY001"

Navigation:
  Distance (Haversine formula)
  Bearing (compass direction)
  Route planning (A* pathfinding)
```

---

## 15. uCODE Language Structure

```
uCODE Syntax Hierarchy

Program
  ├── Variables
  │   └── VAR name = value
  │
  ├── Control Flow
  │   ├── IF condition THEN
  │   ├── WHILE condition DO
  │   └── FOR var IN range
  │
  ├── Functions
  │   └── FUNCTION name(args)
  │
  ├── Commands
  │   └── Built-in uDOS commands
  │
  └── Comments
      └── # Comment text

Execution Model:
  Parse → AST → Interpret → Output

Debugging:
  • Breakpoints
  • Step-through
  • Variable inspection
  • Watch expressions
```

---

## 16. Knowledge Bank Organization

```
Knowledge Categories (500+ guides)

Survival ────┬──── Water (purification, storage, sources)
             ├──── Food (foraging, preservation, cooking)
             ├──── Shelter (building, materials, locations)
             └──── Fire (starting, maintaining, safety)

Skills ──────┬──── Building (carpentry, masonry, planning)
             ├──── Crafts (textiles, pottery, metalwork)
             ├──── Tools (making, maintaining, using)
             └──── Navigation (maps, compass, stars)

Projects ────┬──── Homesteading (gardening, animals, self-sufficiency)
             ├──── Energy (solar, wind, hydro, storage)
             └──── Automation (systems, monitoring, control)

Cross-links: 1000+ internal references
Tags: 200+ categories
Search: Full-text + category + tag
```

---

## 17. Command Pipeline

```
Command Execution Pipeline

Input → Preprocessing → Execution → Output

┌────────────┐
│ User Input │
└─────┬──────┘
      │ "GUIDE LIST"
      ▼
┌────────────┐
│   Parser   │  Split: cmd="GUIDE", args=["LIST"]
└─────┬──────┘
      │
      ▼
┌────────────┐
│   Router   │  Find: guide_handler
└─────┬──────┘
      │
      ▼
┌────────────┐
│  Handler   │  Execute: list_guides()
└─────┬──────┘
      │ Result data
      ▼
┌────────────┐
│  Viewport  │  Format for tier 5 (80×24)
└─────┬──────┘
      │ Formatted text
      ▼
┌────────────┐
│   Output   │
└────────────┘

Error paths:
  Parse error → Syntax help
  Route error → "Command not found"
  Execute error → Error message
  Format error → Raw output
```

---

## 18. API Integration

```
API Architecture (v1.1.0)

┌─────────────────────────────────────┐
│ uDOS Core                           │
└──────────┬──────────────────────────┘
           │
   ┌───────┴───────┐
   │               │
   ▼               ▼
┌──────┐      ┌──────┐
│Gemini│      │ Web  │
│ API  │      │ API  │
└───┬──┘      └───┬──┘
    │             │
    │ API/OK      │ WEB/FETCH
    │ API/ASSIST  │ WEB/CRAWL
    │             │
    ▼             ▼
Protected by     Protected by
• Rate limits    • Whitelist
• Cost tracking  • SSL verify
• Auth tokens    • No JS exec

Offline-First:
  • Cache responses
  • Fallback content
  • Local AI option (Ollama)
```

---

## 19. Offline-First Philosophy

```
Offline-First Design Principles

┌─────────────────────────────────────┐
│ All core features work offline      │
├─────────────────────────────────────┤
│ ✓ Knowledge bank (500+ guides)      │
│ ✓ Commands (80+)                    │
│ ✓ Documentation (1000+ pages)       │
│ ✓ Examples & diagrams               │
│ ✓ Scripting & automation            │
│ ✓ Grid & graphics                   │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Optional online features            │
├─────────────────────────────────────┤
│ • API integration (Gemini)          │
│ • Web content fetch                 │
│ • Community sharing                 │
│ • Extension downloads               │
└─────────────────────────────────────┘

Storage Requirements:
  Core: 50MB
  Knowledge: 100MB
  Full: <200MB total

Principle: "Rebuild civilization from a USB stick"
```

---

## 20. Community Ecosystem

```
Community Participation Model

┌─────────────────────────────────────┐
│ Individual Users                    │
│ Learn → Use → Share                 │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Contributors                        │
│ • Write guides                      │
│ • Create examples                   │
│ • Report bugs                       │
│ • Suggest features                  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Extension Developers                │
│ • Build extensions                  │
│ • Share code                        │
│ • Maintain packages                 │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Core Team                           │
│ • Review contributions              │
│ • Maintain codebase                 │
│ • Set direction                     │
└─────────────────────────────────────┘

GitHub Workflow:
  Fork → Branch → Develop → PR → Review → Merge

License: Open source (check LICENSE.txt)
```

---

## Related Documentation

- [System Architecture Diagrams](../system/README.md)
- [Data Flow Diagrams](../dataflow/README.md)
- [UI Mockups](../ui/README.md)
- [Documentation Handbook](../../Documentation-Handbook.md)

---

**Note**: These are conceptual diagrams to understand uDOS architecture and philosophy. For implementation details, see code documentation and API references.
