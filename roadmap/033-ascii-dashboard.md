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
