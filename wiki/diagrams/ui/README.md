# UI Mockups for uDOS

ASCII mockups showing interface layouts across different viewport tiers.

## Table of Contents
1. [Tier 0: Minimal Terminal (40×12)](#1-tier-0-minimal-terminal-40×12)
2. [Tier 5: Standard Terminal (80×24)](#2-tier-5-standard-terminal-80×24)
3. [Tier 10: Wide Terminal (120×40)](#3-tier-10-wide-terminal-120×40)
4. [Tier 14: Ultra-Wide (200×60)](#4-tier-14-ultra-wide-200×60)
5. [Command Palette](#5-command-palette)
6. [Grid Panel Layout](#6-grid-panel-layout)
7. [GUIDE Interface](#7-guide-interface)
8. [DIAGRAM Viewer](#8-diagram-viewer)
9. [HANDBOOK Reader](#9-handbook-reader)
10. [File Browser](#10-file-browser)
11. [uCODE Editor](#11-ucode-editor)
12. [Debug Interface](#12-debug-interface)
13. [MAP View](#13-map-view)
14. [Theme Selector](#14-theme-selector)
15. [Configuration Panel](#15-configuration-panel)
16. [Help System](#16-help-system)
17. [Dashboard Layout](#17-dashboard-layout)
18. [Error Display](#18-error-display)
19. [Progress Indicators](#19-progress-indicators)
20. [Status Bar](#20-status-bar)

---

## 1. Tier 0: Minimal Terminal (40×12)

```
┌──────────────────────────────────────┐
│uDOS v1.0.22           [TIER 0]    OK│
├──────────────────────────────────────┤
│> GUIDE LIST                          │
│                                      │
│Guides (12):                          │
│1. Water Purification                 │
│2. Knot Tying                         │
│3. Fire Starting                      │
│4. Shelter Building                   │
│5. First Aid                          │
│                                      │
│Use: GUIDE START <name>               │
│                                      │
└──────────────────────────────────────┘
```

**Tier 0 Characteristics**:
- Text only, no boxes (shown for clarity)
- Single column layout
- Minimal formatting
- Essential info only
- Abbreviated labels

---

## 2. Tier 5: Standard Terminal (80×24)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  uDOS v1.0.22 - Offline-First Operating System              [Tier 5] [80×24] │
├──────────────────────────────────────────────────────────────────────────────┤
│  > GUIDE LIST                                                                │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  Available Guides (12)                                               ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║                                                                      ║   │
│  ║  1. Water Purification Methods          [Survival] [Beginner]       ║   │
│  ║  2. Knot Tying Techniques                [Skills]   [Beginner]      ║   │
│  ║  3. Fire Starting Without Matches        [Survival] [Intermediate]  ║   │
│  ║  4. Emergency Shelter Construction       [Survival] [Intermediate]  ║   │
│  ║  5. Basic First Aid & Wound Care         [Medical]  [Beginner]      ║   │
│  ║  6. Foraging Wild Edible Plants          [Food]     [Advanced]      ║   │
│  ║  7. Navigation Without GPS               [Skills]   [Intermediate]  ║   │
│  ║  8. Building a Solar Still               [Water]    [Intermediate]  ║   │
│  ║  9. Tool Sharpening & Maintenance        [Tools]    [Beginner]      ║   │
│  ║  10. Reading Weather Patterns            [Skills]   [Intermediate]  ║   │
│  ║                                                                      ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  Commands: GUIDE START <name> | GUIDE SEARCH <query> | HELP GUIDE           │
│                                                                              │
│  Status: 5/12 guides completed | Last: Water Purification (100%)            │
├──────────────────────────────────────────────────────────────────────────────┤
│  [HELP] [BACK] [QUIT]                                              [Grid:--] │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Tier 5 Characteristics**:
- Box drawing characters
- Category tags
- Status information
- Command hints
- Basic formatting

---

## 3. Tier 10: Wide Terminal (120×40)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  uDOS v1.0.22 - Offline-First Operating System                                          [Tier 10] [120×40]       OK │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                      │
│  > HANDBOOK VOL1                                                                               📖 Reading Progress   │
│                                                                                                                      │
│  ╔═══════════════════════════════════════════════════════╦═══════════════════════════════════════════════════════╗  │
│  ║  Volume 1: System & Commands                          ║  Chapter Preview                                      ║  │
│  ║                                                        ║                                                       ║  │
│  ║  TABLE OF CONTENTS                                     ║  Getting Started with uDOS                            ║  │
│  ║  ══════════════════════════════════════════════════    ║  ─────────────────────────────────────────────────    ║  │
│  ║                                                        ║                                                       ║  │
│  ║  ✅ 1. Getting Started                    (15 pages)   ║  Welcome to uDOS, the offline-first operating         ║  │
│  ║     • Installation & Setup                             ║  system designed for resilience and knowledge         ║  │
│  ║     • First Commands                                   ║  preservation. This guide will walk you through...   ║  │
│  ║     • Basic Workflows                                  ║                                                       ║  │
│  ║                                                        ║  Prerequisites:                                       ║  │
│  ║  ✅ 2. Command Reference                  (80 pages)   ║    • Terminal emulator (macOS Terminal, iTerm2...)   ║  │
│  ║     • File Commands                                    ║    • Python 3.9+ installed                            ║  │
│  ║     • Knowledge Commands                               ║    • Basic command-line familiarity                   ║  │
│  ║     • Graphics Commands                                ║                                                       ║  │
│  ║     • System Commands                                  ║  Installation Steps:                                  ║  │
│  ║                                                        ║    1. Clone or download uDOS                          ║  │
│  ║  📖 3. System Architecture                (45 pages)   ║    2. Run: source .venv/bin/activate                  ║  │
│  ║     • Command Pipeline                                 ║    3. Run: ./start_udos.sh                            ║  │
│  ║     • Grid System                                      ║    4. Try: HELP                                       ║  │
│  ║     • Knowledge Bank                                   ║                                                       ║  │
│  ║                                                        ║  [Read Full Chapter]  [Next: Command Reference]       ║  │
│  ║  ⬜ 4. Configuration                      (35 pages)   ║                                                       ║  │
│  ║     • Settings & Preferences                           ║                                                       ║  │
│  ║     • Theme System                                     ║                                                       ║  │
│  ║     • Custom Fonts                                     ║                                                       ║  │
│  ║                                                        ║                                                       ║  │
│  ║  ⬜ 5. Troubleshooting                    (55 pages)   ║                                                       ║  │
│  ║     • Common Issues                                    ║                                                       ║  │
│  ║     • Repair Modes                                     ║                                                       ║  │
│  ║     • Debug Logging                                    ║                                                       ║  │
│  ║                                                        ║                                                       ║  │
│  ║  ─────────────────────────────────────────────────     ║                                                       ║  │
│  ║  Progress: 2/5 chapters (40%)                          ║                                                       ║  │
│  ║  [█████████░░░░░░░░░░░]                                ║                                                       ║  │
│  ╚═══════════════════════════════════════════════════════╩═══════════════════════════════════════════════════════╝  │
│                                                                                                                      │
│  Commands: HANDBOOK <chapter> | HANDBOOK NEXT | HANDBOOK BOOKMARK | HANDBOOK PROGRESS                               │
│                                                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [VOL1] [VOL2] [VOL3] [VOL4]    [PREV] [NEXT] [BOOKMARK]    [HELP] [BACK] [QUIT]                    [AA001] [Tier10]│
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Tier 10 Characteristics**:
- Split-pane layout
- Rich metadata
- Progress tracking
- Multiple action buttons
- Preview panels

---

## 4. Tier 14: Ultra-Wide (200×60)

**Note**: Shown at reduced width for documentation. Full version would span 200 characters.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  uDOS v1.0.22                                                    [Tier 14] [200×60]  OK│
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  Three-column dashboard layout with:                                                  │
│  • Left: Navigation tree                                                              │
│  • Center: Main content                                                               │
│  • Right: Context/help panel                                                          │
│                                                                                        │
│  Plus: Header with breadcrumbs, status indicators, and quick actions                  │
│        Footer with extensive command palette and system stats                         │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Command Palette

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Command Palette                                                 [Ctrl+P]    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  > gui_                                                                      │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ GUIDE                         Interactive guide viewer                 │ │
│  │ GUIDE LIST                    List all available guides                │ │
│  │ GUIDE SEARCH                  Search guides by keyword                 │ │
│  │ GUIDE START                   Begin a guided tutorial                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Recent Commands:                                                            │
│    • GUIDE START water-purification                                          │
│    • DOC configuration                                                       │
│    • HANDBOOK VOL1                                                           │
│                                                                              │
│  Quick Actions:                                                              │
│    [Ctrl+H] Help    [Ctrl+D] Docs    [Ctrl+G] Guides                         │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [ESC] Close  [↑↓] Navigate  [ENTER] Execute                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Grid Panel Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  GRID VIEW - Position: AA001                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   AA  AB  AC  AD  AE  AF  AG  AH  AI  AJ  AK  AL  AM  AN  AO  AP            │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐                         │
│01│██│░░│░░│▒▒│▒▒│░░│  │  │  │░░│▓▓│▓▓│  │  │░░│  │  Water: ░░              │
│02│░░│░░│▒▒│▓▓│▓▓│▒▒│░░│  │░░│▒▒│▓▓│▓▓│▒▒│░░│  │  │  Grass: ▒▒              │
│03│░░│▒▒│▓▓│▓▓│██│▓▓│▒▒│░░│▒▒│▓▓│██│▓▓│▒▒│  │  │  │  Forest: ▓▓             │
│04│▒▒│▓▓│██│██│██│██│▓▓│▒▒│▓▓│██│██│██│▓▓│  │  │  │  Mountain: ██           │
│05│▒▒│▓▓│██│██│⛰ │██│▓▓│▒▒│▓▓│██│██│██│▓▓│▒▒│  │  │  Peak: ⛰               │
│06│▒▒│▓▓│██│██│██│██│▓▓│▒▒│▓▓│██│██│██│▓▓│▒▒│░░│  │  Desert: ⋱⋱             │
│07│░░│▒▒│▓▓│▓▓│██│▓▓│▒▒│░░│▒▒│▓▓│██│▓▓│▒▒│░░│  │  │  Building: ▪           │
│08│░░│░░│▒▒│▒▒│▓▓│▒▒│░░│  │░░│▒▒│▓▓│▒▒│░░│  │  │  │                         │
│09│░░│  │░░│▒▒│▒▒│░░│  │  │  │░░│▒▒│░░│  │  │  │  │  Legend at right        │
│10│  │  │  │░░│░░│  │  │  │  │  │░░│  │  │  │  │  │                         │
│  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘                         │
│                                                                              │
│  Current: AA001 (Water) | Nearby: AB001 (Grass), AA002 (Grass)              │
│                                                                              │
│  Commands: GRID SET <pos> | PANEL <block> | GRID SAVE <name>                │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [ZOOM+] [ZOOM-] [CENTER] [SAVE]                              [Grid: AA001] │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. GUIDE Interface

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  GUIDE: Water Purification Methods                       [Step 3/8] [60%]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════     │
│  STEP 3: BOILING METHOD                                                      │
│  ═══════════════════════════════════════════════════════════════════════     │
│                                                                              │
│  Boiling is the most reliable method to kill pathogens in water.            │
│                                                                              │
│  MATERIALS NEEDED:                                                           │
│    ✓ Heat source (fire, stove, solar)                                       │
│    ✓ Heat-safe container                                                    │
│    ✓ Water to purify                                                        │
│                                                                              │
│  PROCEDURE:                                                                  │
│    1. Bring water to a rolling boil                                          │
│    2. Maintain boil for 1 minute (3 min at altitude >6,500 ft)              │
│    3. Let cool before drinking                                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  ASCII Diagram:                                                        │  │
│  │                                                                        │  │
│  │     Container          Heat Source                                     │  │
│  │    ┌────────┐                                                          │  │
│  │    │ ∼∼∼∼∼∼ │  <-  Water boiling (bubbles)                            │  │
│  │    │∼∼○∼○∼∼ │                                                          │  │
│  │    │∼○∼∼∼○∼ │                                                          │  │
│  │    └────────┘                                                          │  │
│  │    │ ░░░░░░ │  <-  Heat                                                │  │
│  │    │ ░░▓▓░░ │                                                          │  │
│  │  ═════════════                                                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  TIPS:                                                                       │
│    • Higher altitudes need longer boiling time                               │
│    • Cover container to reduce boiling time                                  │
│    • Boiled water is safe but tastes flat (aerate to improve)                │
│                                                                              │
│  Progress: [████████████░░░░░░░░░░] 60%                                     │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [PREV] [NEXT] [JUMP] [COMPLETE] [QUIT]                   [Survival] [Help] │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. DIAGRAM Viewer

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  DIAGRAM: Knot Types Reference                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Common Knots for Survival & Camping                                         │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │  1. BOWLINE (King of Knots)           2. CLOVE HITCH                  │  │
│  │     Use: Fixed loop, rescue                Use: Securing to pole      │  │
│  │                                                                        │  │
│  │        ╭─────╮                                    │                    │  │
│  │        │     │                                ────┼────                │  │
│  │        │  ⌒  │                                    │╱                   │  │
│  │    ════╰─────╯                                    ╱│                   │  │
│  │                                                ────┼────                │  │
│  │                                                    │                    │  │
│  │                                                                        │  │
│  │  3. SQUARE KNOT                        4. FIGURE-8                     │  │
│  │     Use: Joining ropes                     Use: Stopper knot          │  │
│  │                                                                        │  │
│  │    ═══╮   ╭═══                                ╭──╮                     │  │
│  │       ╰─X─╯                                   │  │                     │  │
│  │       ╭─X─╮                                ╭──╯  ╰──╮                 │  │
│  │    ═══╯   ╰═══                            │        │                  │  │
│  │                                            ╰────────╯                  │  │
│  │                                                │                       │  │
│  │  5. TAUT-LINE HITCH                    6. PRUSIK LOOP                 │  │
│  │     Use: Adjustable tent line              Use: Climbing, rescue      │  │
│  │                                                                        │  │
│  │        │                                      ║                        │  │
│  │    ════╯╲                                 ════║════                    │  │
│  │        │ ╲                                ╭───║───╮                    │  │
│  │    ════╯  ╲                               │   ║   │                    │  │
│  │        │                                  ╰───║───╯                    │  │
│  │                                           ════║════                    │  │
│  │                                               ║                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Navigation:  [←][→] Browse knots    [Z] Zoom    [E] Export                 │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [PREV] [NEXT] [LIST] [SEARCH] [COPY] [HELP]                   [Skills]     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. HANDBOOK Reader

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  📕 HANDBOOK - Volume 2: Knowledge Library                    Page 47/250    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Chapter 2: Skill Trees                                                     │
│  ════════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  SURVIVAL SKILL PROGRESSION                                                  │
│                                                                              │
│  The survival skill tree follows a natural progression from basic            │
│  needs to advanced self-sufficiency. Master each level before moving         │
│  to the next for best results.                                               │
│                                                                              │
│  Level 1: IMMEDIATE SURVIVAL (Hours)                                         │
│    ├─ Water: Finding & purifying                                             │
│    ├─ Shelter: Emergency construction                                        │
│    ├─ Fire: Starting & maintaining                                           │
│    └─ Signaling: Rescue techniques                                           │
│                                                                              │
│  Level 2: SHORT-TERM (Days)                                                  │
│    ├─ Food: Foraging & trapping                                              │
│    ├─ Tools: Basic implement crafting                                        │
│    ├─ Navigation: Finding direction                                          │
│    └─ First Aid: Wound care basics                                           │
│                                                                              │
│  Level 3: MEDIUM-TERM (Weeks)                                                │
│    ├─ Preservation: Food storage                                             │
│    ├─ Hunting: Tracking & processing                                         │
│    ├─ Building: Improved shelter                                             │
│    └─ Medicine: Plant remedies                                               │
│                                                                              │
│  Level 4: LONG-TERM (Months+)                                                │
│    ├─ Agriculture: Growing food                                              │
│    ├─ Advanced Tools: Metalworking                                           │
│    ├─ Community: Group organization                                          │
│    └─ Knowledge: Teaching others                                             │
│                                                                              │
│  ───────────────────────────────────────────────────────────────────────     │
│  See Also: Water Purification (p.12), Shelter Building (p.34),              │
│            Tool Crafting (p.89), First Aid Guide (p.156)                     │
│                                                                              │
│  [Continue reading...]                                                       │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [◀ PREV] [NEXT ▶] [INDEX] [BOOKMARK] [SEARCH]                 [VOL2] [47%] │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. File Browser

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  FILES - /Users/user/uDOS/knowledge/                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📁 Current Directory: knowledge/survival/                                   │
│                                                                              │
│  Type  Name                                Size      Modified                │
│  ────  ──────────────────────────────────  ────────  ──────────────────      │
│  📁    water/                               (dir)     2024-11-15             │
│  📁    food/                                (dir)     2024-11-14             │
│  📁    shelter/                             (dir)     2024-11-13             │
│  📁    fire/                                (dir)     2024-11-12             │
│  📁    medical/                             (dir)     2024-11-11             │
│  📄    README.md                            2.4 KB    2024-11-15             │
│  📄    water-purification-methods.md        12.8 KB   2024-11-14             │
│  📄    emergency-shelter-guide.md           8.5 KB    2024-11-13             │
│  📄    fire-starting-techniques.md          15.2 KB   2024-11-12             │
│  📄    basic-first-aid.md                   18.9 KB   2024-11-11             │
│                                                                              │
│  Total: 5 directories, 5 files (57.8 KB)                                     │
│                                                                              │
│  Commands:                                                                   │
│    CD <dir>        Change directory                                          │
│    LOAD <file>     View file contents                                        │
│    FILES           Refresh listing                                           │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [PARENT] [REFRESH] [SORT] [SEARCH]                         [knowledge/...]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. uCODE Editor

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  EDIT - hello-automation.uscript                              [Modified]     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1  # Hello Automation - Example uCODE script                               │
│   2  # Demonstrates basic uCODE syntax                                       │
│   3                                                                          │
│   4  VAR greeting = "Hello from uDOS!"                                       │
│   5  VAR count = 0                                                           │
│   6                                                                          │
│   7  FUNCTION say_hello()                                                    │
│   8      PRINT greeting                                                      │
│   9      count = count + 1                                                   │
│  10  END                                                                     │
│  11                                                                          │
│  12  # Main execution                                                        │
│  13  WHILE count < 5 DO                                                      │
│  14      say_hello()    ◀── Cursor here                                     │
│  15      PRINT "Count:", count                                               │
│  16  END                                                                     │
│  17                                                                          │
│  18  PRINT "Done!"                                                           │
│  19                                                                          │
│  20  # Output will show greeting 5 times                                     │
│  21                                                                          │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│  Output Console:                                                             │
│  > RUN                                                                       │
│  Hello from uDOS!                                                            │
│  Count: 1                                                                    │
│  Hello from uDOS!                                                            │
│  Count: 2                                                                    │
│  ...                                                                         │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [SAVE] [RUN] [DEBUG] [HELP]                              Ln:14 Col:20  [*]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Debug Interface

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  DEBUG - hello-automation.uscript                      [Paused at line 14]   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Code                           │ Variables            │ Call Stack          │
│  ────────────────────────────── │ ──────────────────── │ ─────────────────   │
│  7  FUNCTION say_hello()        │ greeting: "Hello..." │ main()              │
│  8      PRINT greeting          │ count: 2             │ └─ say_hello()      │
│  9      count = count + 1       │                      │                     │
│ 10  END                         │ Watches:             │ Breakpoints:        │
│ 11                              │ • count > 0 ✓        │ • Line 14           │
│ 12  # Main execution            │ • greeting != "" ✓   │                     │
│ 13  WHILE count < 5 DO          │                      │                     │
│ 14 ▶    say_hello()   ⬅BREAK   │                      │                     │
│ 15      PRINT "Count:", count   │                      │                     │
│ 16  END                         │                      │                     │
│                                 │                      │                     │
│  ─────────────────────────────────────────────────────────────────────────   │
│  Console Output:                                                             │
│  Hello from uDOS!                                                            │
│  Count: 1                                                                    │
│  Hello from uDOS!                                                            │
│  Count: 2                                                                    │
│  [PAUSED at breakpoint]                                                      │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [STEP] [NEXT] [CONTINUE] [STOP] [WATCH] [BREAKPOINT]       [Debug: Active] │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. MAP View

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  MAP - Global Cities & Navigation                        [Cell: NY001]      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ASCII Map (North America)                                                   │
│  ─────────────────────────────────────────────────────────────────────────   │
│                                                                              │
│              ╭──────────────────────────────────╮                            │
│             ╱                                    ╲                           │
│            ╱                CA                    ╲                          │
│           │    ⊕ Vancouver                         │                         │
│           │                                        │                         │
│           │         ⊕ Calgary                      │                         │
│            ╲                                       │                         │
│             ╲                      ⊕ Toronto       │                         │
│          US  ╲     ⊕ Chicago       ⊕ Montréal    ╱                          │
│    ⊕ Seattle  ╲                                 ╱                           │
│                ╲    ⊕ Denver                   ╱                            │
│    ⊕ Portland   ╲                  ⊕ New York★╱ ← Current                  │
│                  ╲                             ╱                            │
│  ⊕ San Francisco  ╲   ⊕ Phoenix   ⊕ Atlanta  ╱                             │
│                    ╲                         ╱                              │
│    ⊕ Los Angeles    ╲    ⊕ Dallas          ╱                               │
│                      ╲   ⊕ Houston        ╱                                │
│                       ╲  ⊕ Miami         ╱                                 │
│                        ╰─────────────────╯                                  │
│                                                                              │
│  Location: New York, NY, USA                    Grid: NY001                  │
│  Coordinates: 40.7128°N, 74.0060°W              TIZO: America/New_York      │
│                                                                              │
│  Nearby Cities:                                                              │
│    • Montréal    (531 km NNE)                                                │
│    • Toronto     (552 km NW)                                                 │
│    • Chicago     (1145 km W)                                                 │
│    • Atlanta     (1197 km SW)                                                │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [METRO] [NAVIGATE] [LOCATE] [ZOOM] [LAYERS]                   [Layer: L0]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Theme Selector

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  THEME - Choose Color Scheme                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ● Matrix (Current)                                                     │  │
│  │   Green on black, hacker aesthetic                                     │  │
│  │   ┌──────────────────────────────────────┐                            │  │
│  │   │ > LOAD data.txt                      │                            │  │
│  │   │ ✓ File loaded successfully           │                            │  │
│  │   │ ⚠ Warning: Large file                │                            │  │
│  │   │ ✗ Error: Permission denied           │                            │  │
│  │   └──────────────────────────────────────┘                            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ○ Cyberpunk                                                            │  │
│  │   Neon colors, futuristic vibe                                         │  │
│  │   ┌──────────────────────────────────────┐                            │  │
│  │   │ > LOAD data.txt                      │                            │  │
│  │   │ ✓ File loaded successfully           │                            │  │
│  │   │ ⚠ Warning: Large file                │                            │  │
│  │   │ ✗ Error: Permission denied           │                            │  │
│  │   └──────────────────────────────────────┘                            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ○ Commodore                                                            │  │
│  │   Classic C64 blue/light blue                                          │  │
│  │   ┌──────────────────────────────────────┐                            │  │
│  │   │ > LOAD data.txt                      │                            │  │
│  │   │ ✓ File loaded successfully           │                            │  │
│  │   │ ⚠ Warning: Large file                │                            │  │
│  │   │ ✗ Error: Permission denied           │                            │  │
│  │   └──────────────────────────────────────┘                            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  [↑↓] Navigate  [ENTER] Select  [P] Preview  [ESC] Cancel                   │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  12 themes available | Current: Matrix | Font: ChicagoFLF                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Configuration Panel

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  CONFIG - System Settings                                      [Modified]    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  Display                                                             ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  Theme:          [Matrix ▼]                                          ║   │
│  ║  Font:           [ChicagoFLF ▼]                                      ║   │
│  ║  Screen Tier:    [Auto-detect ▼] (Currently: Tier 5)                ║   │
│  ║  Color Depth:    [256 colors ▼]                                      ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  Performance                                                         ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  Cache Size:     [100 MB ▼]                                          ║   │
│  ║  Log Level:      [INFO ▼]                                            ║   │
│  ║  Auto-save:      [☑] Every 5 minutes                                 ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  Knowledge                                                           ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  Search Method:  [FTS5 Full-Text ▼]                                  ║   │
│  ║  Index Updates:  [☑] Auto-rebuild on changes                         ║   │
│  ║  Guide Progress: [☑] Track completion                                ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  Advanced                                                            ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  Debug Mode:     [☐] Enable verbose logging                          ║   │
│  ║  Experimental:   [☐] Enable beta features                            ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [SAVE] [RESET] [CANCEL] [DEFAULTS]                          [Has Changes]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 16. Help System

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  HELP - uDOS Command Reference                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Command Categories:                                                         │
│                                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │ 📁 FILE OPERATIONS  │  │ 📚 KNOWLEDGE ACCESS │  │ 🎨 GRAPHICS & UI    │  │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤  │
│  │ LOAD    Load file   │  │ GUIDE   Tutorials   │  │ GRID    Grid system │  │
│  │ SAVE    Save file   │  │ DIAGRAM ASCII art   │  │ PANEL   Teletext    │  │
│  │ FILES   List files  │  │ DOC     Docs        │  │ THEME   Colors      │  │
│  │ CD      Change dir  │  │ MANUAL  Reference   │  │ VIEWPORT Screen info│  │
│  │ EDIT    Edit file   │  │ HANDBOOK Reader     │  │                     │  │
│  │ EXPORT  Export data │  │ EXAMPLE  Examples   │  │                     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│                                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │ ⚡ SCRIPTING & AUTO │  │ 🗺️  MAPPING & NAV   │  │ ⚙️  SYSTEM & CONFIG │  │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤  │
│  │ RUN     Execute     │  │ MAP     Global map  │  │ CONFIG  Settings    │  │
│  │ DEBUG   Debugger    │  │ TIZO    Timezones   │  │ REPAIR  Diagnostics │  │
│  │ LIBRARY Manage code │  │ NAVIGATE Routes     │  │ STATUS  System info │  │
│  │                     │  │ LOCATE  Find places │  │ VERSION Version     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│                                                                              │
│  Quick Start:                                                                │
│    1. HELP <command>     Get detailed command help                           │
│    2. GUIDE LIST         Browse available guides                             │
│    3. DOC getting-start  Read getting started guide                          │
│                                                                              │
│  Shortcuts:                                                                  │
│    Ctrl+C  Cancel        Ctrl+D  Exit         Ctrl+L  Clear screen           │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [TOPICS] [COMMANDS] [SEARCH] [QUIT]                      80+ commands       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 17. Dashboard Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  uDOS Dashboard                                        Today: 2024-11-17     │
├────────────────────────────────────┬─────────────────────────────────────────┤
│  Quick Actions                     │  Recent Activity                        │
│  ────────────────────────────────  │  ─────────────────────────────────────  │
│  [GUIDE]    Continue learning      │  • Completed: Water Purification        │
│  [DOC]      Browse documentation   │  • Started: Knot Tying                  │
│  [EXAMPLE]  Run code examples      │  • Edited: automation-script.uscript    │
│  [MAP]      Explore locations      │  • Viewed: Command Reference            │
│  [CONFIG]   Adjust settings        │                                         │
│                                    │  Statistics                             │
│  Current Progress                  │  ─────────────────────────────────────  │
│  ────────────────────────────────  │  Guides completed:     5/12  (42%)      │
│  Guides: [████░░░░░░] 42%          │  Knowledge pages:      147              │
│  Skills: [███░░░░░░░] 30%          │  Scripts created:      3                │
│                                    │  Extensions active:    2                │
├────────────────────────────────────┼─────────────────────────────────────────┤
│  System Status                     │  Knowledge Highlights                   │
│  ────────────────────────────────  │  ─────────────────────────────────────  │
│  ✅ Core systems operational       │  📍 Featured: Emergency Preparedness    │
│  ✅ Knowledge bank indexed         │  🔥 Popular: Fire Starting Techniques   │
│  ✅ Extensions loaded (2)          │  ⭐ New: Solar Energy Guide             │
│  ⚠️  Cache 85% full (clean?)       │  📚 Recommended: Tool Maintenance       │
│                                    │                                         │
│  Grid: AA001 | Theme: Matrix      │  [Browse All Knowledge →]               │
├────────────────────────────────────┴─────────────────────────────────────────┤
│  Type a command or HELP for assistance                        [Tier 5][OK]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 18. Error Display

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ERROR - Command Execution Failed                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  ❌ FileNotFoundError                                                ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║                                                                      ║   │
│  ║  Command: LOAD nonexistent-file.txt                                 ║   │
│  ║                                                                      ║   │
│  ║  Error: File not found                                              ║   │
│  ║    Path: /Users/user/uDOS/nonexistent-file.txt                      ║   │
│  ║                                                                      ║   │
│  ║  Suggestions:                                                       ║   │
│  ║    • Check the filename spelling                                    ║   │
│  ║    • Use FILES to list available files                              ║   │
│  ║    • Use CD to navigate to the correct directory                    ║   │
│  ║                                                                      ║   │
│  ║  Similar files found:                                               ║   │
│  ║    • nonexistent.txt (in current directory)                         ║   │
│  ║    • recent-file.txt (modified today)                               ║   │
│  ║                                                                      ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  Actions:                                                                    │
│    [FILES]  List directory contents                                          │
│    [HELP]   Show LOAD command help                                           │
│    [RETRY]  Try again                                                        │
│    [CANCEL] Return to prompt                                                 │
│                                                                              │
│  Error ID: ERR_20241117_143022                                               │
│  Logged to: memory/logs/error.log                                            │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  [HELP] [RETRY] [CANCEL]                                        [Error Log]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 19. Progress Indicators

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Progress Indicator Examples                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Linear Progress Bar (Determinate)                                        │
│     Loading knowledge base...                                                │
│     [████████████████░░░░░░░░░░░░] 60% (300/500 guides)                     │
│                                                                              │
│  2. Percentage Only (Simple)                                                 │
│     Processing: 42%                                                          │
│                                                                              │
│  3. Multi-stage Progress                                                     │
│     ┌────────────────────────────────────────────────────────────────────┐   │
│     │ Stage 1: Scanning files          [████████████████████] 100%      │   │
│     │ Stage 2: Building index          [████████░░░░░░░░░░░░]  45%      │   │
│     │ Stage 3: Validating data         [░░░░░░░░░░░░░░░░░░░░]   0%      │   │
│     └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  4. Spinner (Indeterminate)                                                  │
│     Connecting to server... ⠋                                                │
│                              (Cycles: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏)                          │
│                                                                              │
│  5. Download Progress                                                        │
│     Downloading extension...                                                 │
│     [████████████████████████░░░░] 80% (4.0 MB / 5.0 MB)                    │
│     Speed: 1.2 MB/s | ETA: 0:00:08                                           │
│                                                                              │
│  6. Step Progress                                                            │
│     Installation: Step 3 of 5                                                │
│     ● Validate → ● Extract → ◉ Configure → ○ Test → ○ Complete              │
│                                                                              │
│  7. Compact Progress (Tier 0-4)                                              │
│     [===>    ] 45%                                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 20. Status Bar

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Status Bar Variations                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Minimal (Tier 0-4)                                                       │
│  ──────────────────────────────────────────────────────────────────────────  │
│     [OK] [Tier2]                                                             │
│                                                                              │
│  2. Standard (Tier 5-9)                                                      │
│  ──────────────────────────────────────────────────────────────────────────  │
│     [HELP] [BACK] [QUIT]                              [Grid: AA001] [Tier5]  │
│                                                                              │
│  3. Informational (Tier 10+)                                                 │
│  ──────────────────────────────────────────────────────────────────────────  │
│     [F1:Help] [F2:Save] [F3:Load] [Esc:Quit]    Grid:AA001  Time:14:30  OK  │
│                                                                              │
│  4. With System Status                                                       │
│  ──────────────────────────────────────────────────────────────────────────  │
│     Commands: 82 | Guides: 12/12 | Extensions: 2 | Cache: 45MB | Tier:10    │
│                                                                              │
│  5. With Location & Context                                                  │
│  ──────────────────────────────────────────────────────────────────────────  │
│     📁 knowledge/survival/ | 📄 water-purification.md | Ln:42 | ✅ Saved      │
│                                                                              │
│  6. Error State                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│     ❌ ERROR: Command failed | See error.log | [HELP] [REPAIR]               │
│                                                                              │
│  7. Loading State                                                            │
│  ──────────────────────────────────────────────────────────────────────────  │
│     ⏳ Processing... | [████░░░░] 60% | ETA: 0:00:15                         │
│                                                                              │
│  8. Success State                                                            │
│  ──────────────────────────────────────────────────────────────────────────  │
│     ✅ Operation completed successfully | 127 items processed                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [System Architecture Diagrams](../system/README.md)
- [Data Flow Diagrams](../dataflow/README.md)
- [Concept Diagrams](../concepts/README.md)
- [Documentation Handbook](../../Documentation-Handbook.md)

---

**Design Principles**:
1. **Clarity**: Information hierarchy is obvious
2. **Consistency**: Similar functions use similar layouts
3. **Adaptability**: Works across all viewport tiers (0-14)
4. **Efficiency**: Minimal keystrokes to common actions
5. **Accessibility**: ASCII-only, works on any terminal

**Implementation Notes**:
- All mockups use box-drawing characters (Unicode)
- Fallbacks available for ASCII-only terminals
- Colors shown conceptually (actual colors depend on theme)
- Layouts adapt automatically based on viewport tier
