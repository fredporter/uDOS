---
title: "uDOS Interface Philosophy and Design"
version: "Beta v1.6.1"
id: "004"
tags: ["ux", "ascii", "dashboard", "interface", "mockup"]
created: 2025-07-05
updated: 2025-07-05
---

# 🖥️ uDOS Interface Philosophy and Design

This document defines the visual, structural, and philosophical interface standards of uDOS. It covers ASCII UI rendering, layout mockups, dashboard structures, ethos, and display mode handling.

---

## 📘 Contents

1. [UX Vision & Philosophy](#ux-vision--philosophy)
2. [ASCII Interface Design](#ascii-interface-design)
3. [Interface Ethos](#interface-ethos)
4. [Dashboard Concepts](#dashboard-concepts)
5. [Display Modes](#display-modes)
6. [Visual Mockups](#visual-mockups)

---

## 🎯 UX Vision & Philosophy
# uOS UX Philosophy

## Overview

The user experience (UX) of uOS is designed to be minimal, non-distracting, and purpose-driven. It borrows inspiration from retro computing interfaces and humanistic design to provide a focused, intelligent, and non-invasive environment.

## Core UX Principles

1. **Markdown-First**:
   - All user interaction is based on structured Markdown.
   - Markdown provides clarity, portability, and longevity.

2. **Single-Process Focus**:
   - One Move at a time, no parallel threads.
   - Encourages deliberate interaction and reflection.

3. **No GUI Overhead**:
   - No graphical clutter or windowed interface.
   - uOS interfaces are terminal- or plaintext-oriented.

4. **Contextual Awareness**:
   - The system is always aware of Location and historical context.
   - UX adapts based on Mission, recent Moves, and current Location.

5. **Quiet Intelligence**:
   - AI interventions are subtle, non-intrusive.
   - Feedback is suggestive, never interruptive.

6. **Temporal Memory**:
   - System remembers where you were, not just what you said.
   - UX design mimics long-form thought rather than chat sessions.

---

## Accessibility

- All navigation is keyboard- and markdown-compatible.
- No dependence on mouse or screen size.

---

## 🧱 ASCII Interface Design
# uOS Dashboard

## Overview

The **Dashboard** is the single-entry summary view of the user’s current state in uOS. It is composed entirely of Markdown and ASCII, and is dynamically generated at each session entry or on request.

## Core Sections

- **Today’s Focus**:
  - Currently active Mission or Milestone.
  - Suggested next Move.
  - Location pointer.

- **Recent Moves**:
  - Last 5–10 user Moves with context snippets.
  - Linked to full Move logs.

- **Map Peek**:
  - ASCII visualization of current Region with unlocked paths.


## Interaction Model

- Markdown-formatted cards or boxes.
- Collapsible views based on verbosity preference.
- Corresponding  .md file uMemory bank

# uOS Visual ASCII UI Design

---

## ✨ Interface Ethos
# ASCII Display Ethos in uOS

## Overview

uOS uses ASCII and plain-text graphical metaphors as a core aesthetic and functional philosophy. This design choice reinforces its goals of simplicity, portability, and longevity.

## Guiding Principles

1. **Timeless Display**:
   - ASCII-based visuals render on any device from modern terminals to retro displays.
   - Interfaces degrade gracefully.

2. **Symbolic Navigation**:
   - Symbols and layout convey structure, priority, or action.
   - Borders, arrows, and indentation substitute for color or GUI widgets.

3. **Portable Logs**:
   - Everything can be stored, reviewed, printed, and parsed as plain text.
   - Enables future-proofing and inspection with any text tool.

4. **Minimalism as UX**:
   - ASCII encourages intentionality.
   - User attention is directed to knowledge and action, not decoration.

---

## 📊 Dashboard Concepts
# uOS Dashboard — Specification

## Purpose
The uOS Dashboard serves as the user's live mission control panel. It aggregates personal progress and uMemory state into a single screen view.

---

## 🧩 Core Sections

### 🧭 1. TODAY'S FOCUS
- **Active Mission**: Top-level goal or long-term user intention.
- **Active Milestone**: Sub-goal related to current Mission.
- **Suggested Next Move**: Intelligent pointer 
- **Location**: Current region within the user's Map structure.

### 📜 2. RECENT MOVES
- Chronological list of last 5 executed Moves.
- Each Move includes:
  - ✔️ Status
  - Description snippet
  - Timestamp

### 🗺️ 3. MAP PEEK
- ASCII minimap of current user region
- Shows visited areas and next directions
- Interconnected nodes (e.g. `[Creative Valley] --> [Structure Peak]`)


# uOS Dashboard

## Overview

The **Dashboard** is the single-entry summary view of the user’s current state in uOS. It is composed entirely of Markdown and ASCII, and is dynamically generated at each session entry or on request.

## Core Sections

- **Today’s Focus**:
  - Currently active Mission or Milestone.
  - Suggested next Move.
  - Location pointer.

- **Recent Moves**:
  - Last 5–10 user Moves with context snippets.
  - Linked to full Move logs.

- **Map Peek**:
  - ASCII visualization of current Region with unlocked paths.

- **Tower Snapshot**:
  - Recent updates to uKnowledge.
  - New rooms/floors added.

- **Health Check**:
  - System status: logs, syncs, encryption flags, pending exports.

## Interaction Model

- Markdown-formatted cards or boxes.
- Collapsible views based on verbosity preference.
- Hyperlinked summaries to respective .md files.

---

## 🖥️ Display Modes
---
title: uOS Display Modes Specification
version: 1.0
author: Otter (uOS)
date: 2025-06-22
---

# 🖥️ uOS Display Modes Specification

This document outlines the supported display modes for uOS, including dimensions, ratios, viewport area, and dashboard placement.

## 🎯 Purpose
- Define resolution grids for terminal layouts
- Support consistent UI scaling across all devices
- Enable predictable markdown and CLI output formatting

---

## 📐 Display Modes (Ordered by Size)

| Mode     | Grid Size   | Native Ratio | Dash State | Viewport Size | Viewport Ratio | Dashboard Position | Dash Size (W×H) |
|----------|-------------|---------------|------------|----------------|------------------|--------------------|-----------------|
| micro    | 80 × 45     | 16:9          | ✅ Visible  | 80 × 30        | 4:3              | 📏 Bottom          | 80 × 15         |
|          |             |               | 🚫 Hidden   | 80 × 45        | 16:9             | 🚫 Hidden          | —               |
| mini     | 80 × 60     | 4:3           | ✅ Visible  | 80 × 45        | 16:9             | 📏 Bottom          | 80 × 15         |
|          |             |               | 🚫 Hidden   | 80 × 60        | 4:3              | 🚫 Hidden          | —               |
| compact  | 160 × 90    | 16:9          | ✅ Visible  | 120 × 90       | 4:3              | 📐 Right           | 40 × 90         |
|          |             |               | 🚫 Hidden   | 160 × 90       | 16:9             | 🚫 Hidden          | —               |
| console  | 160 × 120   | 4:3           | ✅ Visible  | 160 × 90       | 16:9             | 📏 Bottom          | 160 × 30        |
|          |             |               | 🚫 Hidden   | 160 × 120      | 4:3              | 🚫 Hidden          | —               |
| wide     | 320 × 180   | 16:9          | ✅ Visible  | 240 × 180      | 4:3              | 📐 Right           | 80 × 180        |
|          |             |               | 🚫 Hidden   | 320 × 180      | 16:9             | 🚫 Hidden          | —               |
| full     | 320 × 240   | 4:3           | ✅ Visible  | 320 × 180      | 16:9             | 📏 Bottom          | 320 × 60        |
|          |             |               | 🚫 Hidden   | 320 × 240      | 4:3              | 🚫 Hidden          | —               |
| mega     | 640 × 360   | 16:9          | ✅ Visible  | 560 × 360      | 4:3              | 📐 Right           | 80 × 360        |
|          |             |               | 🚫 Hidden   | 640 × 360      | 16:9             | 🚫 Hidden          | —               |
| ultra    | 640 × 480   | 4:3           | ✅ Visible  | 640 × 420      | 16:9             | 📏 Bottom          | 640 × 60        |
|          |             |               | 🚫 Hidden   | 640 × 480      | 4:3              | 🚫 Hidden          | —               |

---

## ✅ Notes
- Viewport dimensions define usable text space for Markdown and CLI output
- Dashboard position impacts input/output structure and message formatting
- Dashboards can be toggled off for full viewport use

---

*End of spec.*

---

## 🧩 Visual Mockups
# uOS ASCII Dashboard UI

This ASCII dashboard serves as the main interface for users running uOS. It's rendered entirely in a character grid (e.g. 160x90), uses uBASIC for layout/interaction, and invokes uScript containers for dynamic content.

## 📊 Dashboard Layout (160x32)

```
+------------------------------------------------------------------------------------------------------------------------------+
| ████ uOS :: WIZARD DASHBOARD ████                                                                                             |
+----------------------+----------------------+----------------------+----------------------+----------------------+-------------+
| 🧠 MEMORY:  12.3 MB   | 🔋 RESOURCES: 89%     | ⌛ LIFESPAN: 27,391    | 🪙 LEGACY: 3 TOMES     | 🧭 STEPS: 1,203,556     | @U: Wizard     |
+----------------------+----------------------+----------------------+----------------------+----------------------+-------------+
| 📁 ACTIVE MISSION:                                                                                                            |
| "Recover the Tome of Ancestral Lore from the 3rd Layer of Forgotten Depths"                                                  |
+------------------------------------------------------------------------------------------------------------------------------+
| 📘 LOGBOOK (Last 3 entries):                                                                                                  |
| - [x] Entered 3rd Layer, battled Shadow Scribes.                                                                             |
| - [ ] Located chamber of Lore. Cloaked puzzle locks remain.                                                                 |
| - [ ] Backup scheduled in 3 Steps.                                                                                           |
+------------------------------------------------------------------------------------------------------------------------------+
| 📦 Containers:                                                                                                                |
| - (mem-check)   -> `[run:mem.py]`   | - (backup-crypt) -> `[run:backup.sh]` | - (runesolver) -> `[run:rune.py --layer=3]`     |
+------------------------------------------------------------------------------------------------------------------------------+
| 📍 LOCATION: Forgotten Depths / Layer 3         🗺 MAP: [view:ascii-map]     🎮 MODE: Exploration                              |
+------------------------------------------------------------------------------------------------------------------------------+
```

## 🔧 Shortcode Logic (uBASIC)

```uCode
IF mode == "exploration" THEN
  SHOW map_overlay
ENDIF

IF mission_complete == TRUE THEN
  ADD legacy_tome += 1
  LOG "Tome recovered. New entry stored."
ENDIF

IF resources < 15 THEN
  ALERT "Resources low. Initiate container: regen"
ENDIF
```

## 🧪 Container Execution (uScript)

```markdown
[run:mem.py]         # Displays current memory statistics
[run:backup.sh]      # Triggers local encrypted backup
[run:rune.py --layer=3]  # Solves rune puzzle at specified map layer
```

## 🧱 ASCII Elements (Example Blocks)

```ascii
🧠 = MEMORY MODULE
🔋 = RESOURCE MODULE
⌛ = LIFESPAN CLOCK
🪙 = LEGACY TOMES
🧭 = MOVE COUNTER
📦 = SCRIPT CONTAINER
📘 = LOGBOOK
📁 = ACTIVE MISSION
🗺 = MAP OVERLAY
```

---

## 🧪 Interface Drafts and Render Planning
# uOS Dashboard Interface

```
+-----------------------------------------------------+
|                   [🧠 uOS DASHBOARD]                 |
+----------------------+------------------------------+
| 🌱 MOVES             |  📜 MISSIONS                |
+----------------------+------------------------------+
| Current:     17       |  In Progress:   🧭 Map Codex |
| Total at EOL: ∞       |  Planned:       🌌 uBasic AI |
| Reversible:  ✅       |  Completed:     ✅           |
+----------------------+------------------------------+
| 🗺️ LOCATION MAP LINKED TO STATE                      |
+-----------------------------------------------------+
| 🔗 ACTIVE TILE: ⚔️ Wizard Tower                      |
| → Memory:     📘 uKnowledge/Spells Index             |
| → Mission:    🧭 Map Codex (editing)                 |
| → Legacy:     N/A                                   |
+-----------------------------------------------------+
| 🔮 LEGACY (EOL)                                     |
| User-Set:   📘 Tome of Ancestors                     |
| Condition:  Awaiting EOL                           |
+-----------------------------------------------------+
| ⏳ SYSTEM STATUS                                     |
| AI Mode: Wizard   | Memory Slots: [███░░░░░░░░░░]    |
| Resources: ⚡ 73%  | Container: uScript Running ✅   |
+-----------------------------------------------------+
```

## Section Logic

* **\[Moves]**

  * Current steps taken during the user’s journey.
  * Reversible Moves indicated with ✅.
  * EOL Moves accumulate for Legacy determination.

* **\[Missions]**

  * Missions are *never* deleted, only completed.
  * Remain valid until transformed into a Legacy at EOL.
  * In-progress and future states tracked.

* **\[Legacy]**

  * Legacy = End-of-life Mission.
  * May be set by user during lifetime.
  * Converts at EOL condition met.

* **\[Location Map]**

  * Each tile can link to a uMemory milestone (past), active mission (present), or legacy (knowledge for the future).


* **\[System Status]**

  * Displays current mode, memory capacity, and whether containerized `uScript` services are active.
