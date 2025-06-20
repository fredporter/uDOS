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
- Corresponding  .md file uKnowledge bank

# uOS Visual ASCII UI Design

This document outlines the ASCII-based user interface design system for uOS, optimized for retro-style visuals, minimal processing, and immersive character-driven layouts. The goal is to create a flexible and extensible layout standard using fixed-width terminal output, leveraging a custom uOS ASCII blockset.

---

## 📐 Screen Resolution Layouts

### Default Terminal Grid
- Base resolution: 160x90 characters
- Extended modes supported via tiling and layer stacking

# uOS Visual ASCII UI Design

This document outlines the ASCII-based user interface design system for uOS, optimized for retro-style visuals, minimal processing, and immersive character-driven layouts. The goal is to create a flexible and extensible layout standard using fixed-width terminal output, leveraging a custom uOS ASCII blockset.

---

## 📐 Screen Resolution Layouts

### Default Terminal Grid
- Base resolution: `160x90` characters
- Extended modes supported via tiling and layer stacking

```
+--------------------------------------------------------------------------------------------------------------+
| uOS v0.1 - Wizard Console                                                                                   |
+--------------------------------------------------------------------------------------------------------------+
| █ Welcome, Wizard                                                                                           |
|                                                                                                              |
| 🗺️  Location: The Crypt                                                                                     |
| 🧠 Focus:   [████████░░░░░░░░░░░░░░] (38%)                                                                   |
| 💡 Energy:  [███████░░░░░░░░░░░░░░░] (29%)                                                                   |
| 📚 Memory:  [██████████████░░░░░░░░] (67%)                                                                   |
|                                                                                                              |
| ⌨️  Command >                                                                                                 |
|                                                                                                              |
+--------------------------------------------------------------------------------------------------------------+
```

---

## 🔤 uOS ASCII Blockset (Partial Preview)

```
█ ░ ▒ ▓ ─ │ ┌ ┐ └ ┘ ┼ ├ ┤ ┬ ┴ ═ ║ ╔ ╗ ╚ ╝ ╬ ☼ ☁ ☠ ☯ ⚙ ⌨ 🧠 📚 🧮 📁 📦 🗺️ 💡
```

---

## 📦 Interactive Components

### Panel Template
```
╔═══════════════════[ STATUS ]════════════════════╗
║ User: Wizard                                    ║
║ Active Script: meditation.uscript              ║
║ Time: 08:13                                     ║
╚═════════════════════════════════════════════════╝
```

### Tabs Interface
```
┌────[ MAP ]────┬────[ LOG ]────┬────[ SCRIPTS ]────┐
│ Current: Crypt of Ancients                          │
│ Path: /vault/crypt                                  │
└─────────────────────────────────────────────────────┘
```

---

## 🔁 Shortcode Integration

Shortcodes are used to connect UI to logic or container systems.

```markdown
[RUN:meditate.uscript] – Triggers containerized script execution
[SHOW:ascii_map.castle01] – Renders an ASCII art map block
[GRAPH:energy_stats] – Visual bar or sparkline output
```

---

## 🧱 Modular Layout Regions

Each UI screen can be divided into reusable components:

- `Header`: System name, user role, time
- `Main`: Scene description or interaction panel
- `Sidebar`: Status meters, inventory, or context-sensitive hints
- `Footer`: Command input or tips

---

## 🧪 Dynamic ASCII Rendering Logic (BASIC + uScript)

Example snippet:
```basic
REM draw user status bar
PRINT "💡 Energy:  "; CALL("bar_meter", 29)
```

uScript equivalent:
```python
# bar_meter.uscript
value = args.get("percent", 0)
bars = int(value / 4)
print("[" + "█" * bars + "░" * (25 - bars) + f"] ({value}%)")
```

---

## 🔮 Visual Themes

- `CRYPT` – Stone block edges, grey-toned gradients
- `TEMPLE` – Marble/white with gold highlights
- `ARCANE` – Purple/blue mystical glyphs and UI highlights

---

## Next Steps
- Develop `[CAST:mapblock]` support with custom ASCII terrains
- Design scroll-based navigation and page-switching using arrow keys
- Implement animated UI transitions using frame buffers (in memory)

---

Let me know which UI module you want to build or animate next!
