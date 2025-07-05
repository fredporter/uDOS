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
