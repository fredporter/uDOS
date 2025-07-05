---
title: "uDOS Template & Format Guide"
version: "Beta v1.6.1"
id: "002"
tags: ["template", "formatting", "logging", "structure", "dashboard"]
created: 2025-07-05
updated: 2025-07-05
---

# 🧱 uDOS Template & Format Guide

This document consolidates all reusable templates, dashboard rendering logic, formatting specifications, and move log architecture for uDOS. It is intended to serve as a technical and structural reference for content creators, developers, and AI agents using or contributing to the system.

---

## 📘 Contents

1. [Templates](#templates)
   - [Move Template](#move-template)
   - [Mission Template](#mission-template)
   - [Milestone Template](#milestone-template)
2. [Dashboard Rendering](#dashboard-rendering)
3. [Date & Time Format](#date--time-format)
4. [Filenames & Folder Structure](#filenames--folder-structure)
5. [Move Log Roadmap](#move-log-roadmap)

---

## 🧾 Templates

### 📍 Move Template
# Move Template – uDOS

A **Move** is the smallest atomic operation in uDOS. Each Move consists of one user input and one system output. It represents a moment of interaction, reflection, execution, or expression.

Moves form the building blocks of Milestones and are counted toward system lifespan and progression.

---

## 📄 Move Template (Markdown)

```markdown
# Move: <short_title>

## 🔖 ID
move_<YYYY>_<MMDD>_<index>

## 📅 Timestamp
YYYY-MM-DD HH:MM:SS

## 📥 Input
User input or command (as written)

## 📤 Output
System response or result (rendered Markdown or uScript result)

## 🔗 Linked Context
- Mission: mission_<slug>
- Milestone: milestone_<slug>
- Related Files: uScript/... uKnowledge/...

## 🧠 Type
reflection | command | query | expression | system | creation

## 🧾 Notes
Any annotations, purpose tags, or user comments.
```

---

## 🧬 Properties


* **Timestamped**: Used to track temporal progression.
* **Compositional**: Multiple Moves contribute to a Milestone.

---

### 🧭 Mission Template
# uDOS Mission Template

A **Mission** in uDOS defines a future or in-progress purpose. Missions remain persistent even after completion, unless elevated to **Legacy** at the end-of-life (EOL) phase of the user's installation.

---

## 📘 Template Structure (Markdown)

```markdown
# Mission: <title>

## 🧭 Mission ID
mission_<slug>_<index>

## 🏷️ Tags
#learning #self #project #system

## 🗓️ Created
2025-05-27

## 🔄 Status
in-progress | planned | paused | complete

## 🎯 Description
Brief mission purpose and philosophical context.

## 🪜 Milestones
- [ ] milestone_001: Define knowledge taxonomy
- [ ] milestone_002: Draft bank index and search
- [ ] milestone_003: Build memory binding logic


## 🧠 Related Concepts
- uCode interface blocks: `[mission:status]`
- Map Tile: `A2` (Wizard Tower — Archive Wing)

## 📜 Legacy Potential
Flag: eligible | not-eligible | predefined
```

---

## 🔄 Key Relationships

* **Mission** links to 1+ **Milestones**
* **Milestones** may be:

  * Achieved (✔)
  * Reversible (↩️)
  * Archived at EOL into **Legacy**
* **Moves** (Input/Output operations) are atomic, and may trigger milestone creation or update

---

## 🔂 Redefinitions

* **Move**: A single atomic I/O event in uDOS. Like a message or script call. Stateless.
* **Milestone**: A goal-related unit of progression. Tracks meaningful progress. Reversible.
* **Mission**: A persistent objective composed of Milestones.
* **Legacy**: A sealed archive of missions + milestones defined at EOL.

---

### 🎯 Milestone Template
# Milestone Template – uDOS

Milestones are units of meaningful progress within uDOS. Each Milestone contributes to a Mission or Legacy and is composed of individual atomic Moves (input/output).

---

## 🪜 Milestone Template (Markdown)

```markdown
# Milestone: <title>

## 🪜 ID
milestone_<mission-id>_<index>

## 📅 Created
YYYY-MM-DD

## 🧠 Context
- Mission ID: mission_<slug>
- Associated Moves: move_<id>, move_<id>, ...
- Related Files: uKnowledge/..., uScript/...

## 🔄 Status
in-progress | complete | reversed | pending

## 📍 Description
Concise explanation of what this Milestone represents and its intended impact.

## 🧾 Activity Log
- [YYYY-MM-DD] Move ID: move_<id> — "User defined X"
- [YYYY-MM-DD] Move ID: move_<id> — "Script executed Y"
```

---

## 🔁 Key Features

* Each Milestone connects upward to a Mission and downward to a list of related Moves.

---

## 📊 Dashboard Rendering
```
╔════════════════════════════════════════════════════════╗
║                      uDOS DASHBOARD                    ║
╠════════════════════════════════════════════════════════╣
║ USER: Wizard_Owl         LOCATION: Mossy_Hollow       ║
║ UPTIME: 1523 Steps       STATUS: ★ Active             ║
╠════════════════════════╦══════════════════════════════╣
║ ➤ LEGACY MISSION       ║ "Preserve Family Lore"       ║
║   State: Pending       ║ Target: 3000 Moves           ║
╠════════════════════════╩══════════════════════════════╣
║ ➤ ACTIVE MISSIONS                                    ║
║ 1. Build uScript container system    (In Progress)    ║
║ 2. Map ancestral home                  (Not Started)   ║
║ 3. Archive books into uKnowledge      (Paused)         ║
╠════════════════════════════════════════════════════════╣
║ ➤ MEMORY BANKS                                       ║
║ Personal (45 entries)    | In-Progress (13 entries)    ║
║ Mission (21 entries)     | Legacy (1 tomb reserved)    ║
╠════════════════════════════════════════════════════════╣
║ RESOURCES                                              ║
║ Storage: ██▒▒▒▒▒▒▒▒▒▒▒ 32% used                        ║
║ Power:   ████████▒▒▒▒ 80% remaining                    ║
║ Tokens:  ██████████░░ 92% daily limit left             ║
╠════════════════════════════════════════════════════════╣
║ SHORTCUTS                                              ║
║ [C] Code Editor     [M] Mission List     [L] Lore Map  ║
║ [R] Resources       [V] View Moves Log   [D] Dev Logs  ║
╚════════════════════════════════════════════════════════╝

---

## ⏳ Date & Time Format
---
title: uDOS Date and Time Format Specification
version: 1.1
author: Otter (uDOS)
date: 2025-06-24
---

# 📅 uDOS Date and Time Format Specification

This document defines the standard formats for date and time used throughout uDOS, including log entries, filenames, and all time-based identifiers.

## 🧠 Goals
- Human-readable and machine-parsable
- Timezone-aware 
- Filename-safe (CAPS, NUMERALS, and `-` only)
- Lexicographically sortable

---

## 🕰️ Primary Timestamp Format (for display/logging)

```
YYYY-MM-DD HH:mm:ss.SSS ±hh:mm TIMEZ
```

**Example:**
```
2025-06-22 14:23:10.456 +10:00 AES
```

### Format Breakdown
| Field        | Description                      | Example       |
|--------------|----------------------------------|---------------|
| `YYYY-MM-DD` | ISO date                         | `2025-06-22`  |
| `HH:mm:ss`   | 24-hour time                     | `14:23:10`    |
| `.SSS`       | Milliseconds (delimiter `.`)     | `.456`        |
| `±hh:mm`     | Timezone offset (required)       | `+10:00`      |

---

## 🗂 Filename Timestamp Format

Used for naming all uDOS-generated files, folders, and unique log IDs. Designed for filesystem safety and maximum compatibility.

```
YYYYMMDD-HHMMSS-SSS-TZCODE
```

**Example:**
```
20250622-142310-456-P10
```

### Format Breakdown
| Field         | Description                             | Example     |
|---------------|-----------------------------------------|-------------|
| `YYYYMMDD`    | Compact ISO date                        | `20250622`  |
| `HHMMSS`      | Hour, minute, second                    | `142310`    |
| `SSS`         | Milliseconds, separate field            | `456`       |
| `TIMEZ`      | Encoded timezone

---

## 🗂️ Filenames & Folder Structure
# uDOS Filename and File Structure Specification (Beta v1.6.1)

This standard defines all filenames and folder conventions used within uDOS for logs, moves, tasks, maps, and sandbox operations.

---

## 1. Filename Format

All filenames follow this strict structure:

```
<type>-<YYYYMMDD-HHMMSSmmm>-<timezone>-<location>.md
```

### Example:

```
mission-20250623-142310361-AEST-F180327.md
```

Note: Location colons are removed for compatibility. Timezone comes before location.

### Components:

| Part          | Format                              | Example                |
| ------------- | ----------------------------------- | ---------------------- |
| Category Code | Type of file                        | mission                |
| DateTimeStamp | YYYYMMDD-HHMMSSmmm (24hr clock, milliseconds)     | 20250623-142310361     |
| Timezone      | Readable TZ (e.g. AEST, PST, UTC)        | AEST                   |
| LocationStamp | Tile Code from uMaps (no colons)         | F180327                |
| Extension     | Always .md (lowercase)              | .md                    |

Default timezone and location are derived at startup from /uMemory/state/location.txt.

---

## 2. Category Codes

| Code    | Type                |
|---------|---------------------|
| moves   | Move logs           |
| mission | Active missions     |
| legacy  | Archived records    |
| draft   | Drafted input       |
| map     | Map tile or region  |
| config  | Configuration file  |

---
📝 Note: All filenames and folders must follow Markdown-safe, ISO-date and lowercase-hyphenated formats for compatibility and readability. Spaces, special characters, and mixed case are disallowed.
---

## 3. Folder Structure

```
/uOS/
├── sandbox/             # Temporary scratchpad files
│   ├── uIO-*.md         # Input/output sessions
│   ├── uMD-*.md         # uMap draft content
│   └── uTA-*.md         # Task/action files
│
├── uMemory/             # Long-term system memory
│   ├── logs/            # System logs
│   │   └── uSL-*.md
│   ├── errors/          # Error logs
│   │   └── uSL-*.md
│   ├── moves/           # Recorded state transitions
│   │   └── uML-*.md
│   ├── milestones/      # Achievements and goals
│   │   └── *.md
│   ├── missions/        # Larger tasks or operations
│   │   └── *.md
│   └── legacy/          # Archived or migrated records
│       └── *.md
│
├── uKnowledge/          # Reference material and specs
│   └── general/         # Freeform documentation
│       └── *.md
│
├── uMaps/               # Cartographic logic and geography
│   ├── layers/          # Layer definitions and overlays
│   └── tiles/           # Physical and logical tiles
```

---

## Location Stamp Format (uMap Tile Convention)

Tiles follow a multi-resolution grid system:

- Base tiles: `Xnn` where X is column A–Z, and nn is row 01–60
  - Example: `F18` (e.g. coastal France)
- Submaps: `F18:zz` where `zz` is sub-tile within that 120×60 block
- Deep detail: `F18:zz:xy` — sub-sub coordinate system

Each base cell (120×60) represents \~3° lat × 3° lon. Zoom layers allow increasing precision down to \~0.05°/cell or better.

---

This structure ensures consistent naming, cross-compatibility with uMap addressing, and clean archival across all uDOS interfaces.

All filenames are safe for sorting, transfer, compression, and long-term storage.

End of spec.

---

## 📜 Move Log Roadmap
_uDOS v1.6.1 format_

# uDOS Move Log Roadmap (`uCode` Loop Protocol)

This document defines the logging behaviour at the beginning of each loop cycle in `uCode`, the user interaction shell within uDOS.

---

## 🔁 Loop End: Move Logging

At the **end of each loop**, after input/output completes, `uCode` captures a minimal **Move Log Entry**, appending it to the current day’s **daily move log** file 

### 📍 File Location

```
/uMemory/logs/moves-YYYY-MM-DD.md
```

### 🛠 What Gets Logged

Each entry includes:

- `Timestamp` – full 24h `HH:MM:SS.mmm`
- `Location` – current uMap tile code (e.g. F180327)
- `Input` – user command or raw input (prefixed `🌀→`)
- `Output` – single-line feedback or result (prefixed `💬←`)

This ensures that every user-driven action is timestamped and locationally grounded for future inspection or replay.

> Example Log Entry:

```markdown
🌀→ DASH | F180327 | 14:02:55.493
💬← ✅ Dashboard displayed.
```

---

## 📦 Daily Move Log Commit

At the end of the 24h session (or on manual trigger), the current log is moved into local persistent memory:

```
/uMemory/logs/moves-YYYYMMDD.md
```

This finalised `.md` file becomes read-only and serves as a durable, inspectable record of all user inputs for that day.

---

## 🧠 Purpose

- Provide **minimal but complete traceability** of session activity
- Enable future replay, summarisation, or audit of user-driven events
- Maintain a lightweight, human-readable log format consistent with Markdown-based uDOS design

---

⚠️ Important: The move log file format was simplified in Beta v1.6.1. Previous session-based logging and verbose formats were deprecated. Each move is now logged as a **single-line entry** in a daily `.md` file with only the essentials: command, timestamp, location, and brief response. No session IDs, user names, or assistant identifiers are recorded in `uMemory`.

---

## ✅ Summary

| When       | What                                | Where                                   |
| ---------- | ----------------------------------- | ----------------------------------------|
| Loop End   | Log input/output with timestamp after loop completes | `/uMemory/logs/moves-YYYY-MM-DD.md`     |
| Day’s End  | Finalise log to flat history        | `/uMemory/logs/moves-YYYYMMDD.md`       |

---
