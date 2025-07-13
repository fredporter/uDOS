---
title: "uDOS Template & Format Guide"
version: "Beta v1.7.0"
id: "002"
tags: ["template", "formatting", "logging", "structure", "dashboard", "vscode", "ai-enhanced"]
created: 2025-07-05
updated: 2025-07-13
status: "✅ Optimized"
---

# 🧱 uDOS Template & Format Guide

This document consolidates all reusable templates, dashboard rendering logic, formatting specifications, and move log architecture for uDOS. It serves as a technical and structural reference for content creators, developers, and AI agents using or contributing to the system.

**v1.7.0 Optimization Update*## ✅ Summary

| When       | What                                | Where                                   | v1.7.0 Enhancement |
| ---------- | ----------------------------------- | ----------------------------------------|-------------------|
| Loop End   | Log input/output with timestamp, AI context, performance after loop completes | `/uMemory/logs/moves-YYYY-MM-DD.md` | AI tracking, perf metrics |
| Day's End  | Finalize log to flat history with optimization summary | `/uMemory/logs/moves-YYYYMMDD.md` | Performance analytics |anced with VS Code integration patterns, AI-assisted templates, and optimized performance specifications.

---

## 📘 Contents

1. [Templates](#templates)
   - [Move Template](#move-template)
   - [Mission Template](#mission-template)
   - [Milestone Template](#milestone-template)
2. [Dashboard Rendering](#dashboard-rendering)
3. [VS Code Integration Formats](#vs-code-integration-formats)
4. [AI-Enhanced Template Patterns](#ai-enhanced-template-patterns)
5. [Date & Time Format](#date--time-format)
6. [Filenames & Folder Structure](#filenames--folder-structure)
7. [Move Log Roadmap](#move-log-roadmap)

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
reflection | command | query | expression | system | creation | vscode-task | ai-assisted

## 🧾 Notes
Any annotations, purpose tags, or user comments.

## 🤖 AI Enhancement (v1.7.0)
- Copilot suggestions for related moves
- Intelligent context linking
- Auto-completion for common patterns
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

## 🔧 VS Code Integration Formats

### Task Definition Template
```json
{
    "label": "🎯 Task Name",
    "type": "shell",
    "command": "./uCode/script.sh",
    "args": ["${input:parameter}"],
    "group": "build|test",
    "isBackground": false,
    "problemMatcher": ["$shell"],
    "detail": "Human-readable description"
}
```

### VS Code Settings Template
```json
{
    "files.associations": {
        "*.utemplate": "markdown",
        "ucode.sh": "shellscript"
    },
    "terminal.integrated.defaultProfile.osx": "zsh",
    "copilot.enable": {
        "*": true,
        "markdown": true,
        "shellscript": true
    }
}
```

### Workspace Configuration
```json
{
    "folders": [
        {
            "name": "uDOS",
            "path": "."
        }
    ],
    "settings": {
        "search.exclude": {
            "**/uMemory/logs/**": true,
            "**/sandbox/**": false
        }
    },
    "extensions": {
        "recommendations": [
            "github.copilot",
            "ms-vscode.vscode-markdown"
        ]
    }
}
```

---

## 🤖 AI-Enhanced Template Patterns

### Copilot-Friendly Documentation Structure
```markdown
<!-- Purpose: Clear intent for AI understanding -->
# Component: [Name]

## Intent
Brief description of what this component does

## Usage Pattern
```language
// Example usage with context
```

## Related Components
- Links to related files
- Dependencies and relationships

## AI Assistance Areas
- Code generation opportunities
- Pattern recognition hints
- Suggested improvements
```

### AI-Assisted Move Template
```markdown
# Move: <title>

## 🤖 AI Context
- **Copilot Suggestions**: Available for [specific areas]
- **Pattern Recognition**: Identifies [common patterns]
- **Auto-completion**: Enabled for [file types]

## 🔖 ID
move_<YYYY>_<MMDD>_<index>

## 📅 Timestamp
YYYY-MM-DD HH:MM:SS

## 📥 Input
User input or command (with AI suggestions noted)

## 📤 Output
System response (enhanced with AI assistance)

## 🧠 AI Enhancement Log
- Copilot suggested: [specific suggestions]
- Pattern matched: [recognized patterns]
- Efficiency gain: [time/error reduction]
```

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
# uDOS Filename and File Structure Specification (Beta v1.7.0)

This standard defines all filenames and folder conventions used within uDOS for logs, moves, tasks, maps, and sandbox operations. Enhanced with VS Code integration and AI assistance patterns.

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
_uDOS v1.7.0 optimized format_

# uDOS Move Log Roadmap (`uCode` Loop Protocol)

This document defines the logging behavior at the beginning of each loop cycle in `uCode`, the user interaction shell within uDOS. Enhanced with VS Code integration and AI assistance tracking.

---

## 🔁 Loop End: Move Logging

At the **end of each loop**, after input/output completes, `uCode` captures a minimal **Move Log Entry**, appending it to the current day’s **daily move log** file 

### 📍 File Location

```
/uMemory/logs/moves-YYYY-MM-DD.md
```

### 🛠 What Gets Logged (v1.7.0 Enhanced)

Each entry includes:

- `Timestamp` – full 24h `HH:MM:SS.mmm`
- `Location` – current uMap tile code (e.g. F180327)
- `Input` – user command or raw input (prefixed `🌀→`)
- `Output` – single-line feedback or result (prefixed `💬←`)
- `AI Context` – Copilot assistance level (prefixed `🤖`)
- `Performance` – execution time in optimized shell (prefixed `⚡`)

This ensures that every user-driven action is timestamped, locationally grounded, and AI-enhanced for future inspection or replay.

> Example Log Entry (v1.7.0):

```markdown
🌀→ DASH | F180327 | 14:02:55.493
💬← ✅ Dashboard displayed.
🤖 Copilot: Template suggestions provided
⚡ Execution: 0.3s (15x faster than v1.6.1)
```

---

## 📦 Daily Move Log Commit

At the end of the 24h session (or on manual trigger), the current log is moved into local persistent memory with optimization metrics:

```
/uMemory/logs/moves-YYYYMMDD.md
```

This finalized `.md` file becomes read-only and serves as a durable, inspectable record of all user inputs for that day, including AI assistance patterns and performance improvements.

---

## 🧠 Purpose (v1.7.0 Enhanced)

- Provide **minimal but complete traceability** of session activity
- Enable future replay, summarization, or audit of user-driven events
- Track **AI assistance effectiveness** and pattern recognition
- Monitor **performance improvements** from optimization
- Maintain a lightweight, human-readable log format consistent with Markdown-based uDOS design

---

⚠️ Important: The move log file format was enhanced in Beta v1.7.0. Added AI assistance tracking, performance metrics, and VS Code integration context. Each move is now logged as a **multi-line entry** with essentials plus optimization data: command, timestamp, location, brief response, AI context, and execution performance. No session IDs, user names, or assistant identifiers are recorded in `uMemory`.

---

## ✅ Summary

| When       | What                                | Where                                   |
| ---------- | ----------------------------------- | ----------------------------------------|
| Loop End   | Log input/output with timestamp after loop completes | `/uMemory/logs/moves-YYYY-MM-DD.md`     |
| Day’s End  | Finalise log to flat history        | `/uMemory/logs/moves-YYYYMMDD.md`       |

---
