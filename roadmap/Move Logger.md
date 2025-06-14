```
╔════════════════════════════════════════════════════════╗
║                      uOS DASHBOARD                    ║
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

# Log Hook
- Any mission status change triggers `uScript/move_logger.sh`
- New moves are appended to `/uKnowledge/moves/move_log.md`
- Dashboard includes a live count of total moves
