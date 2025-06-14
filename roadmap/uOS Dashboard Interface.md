# uOS Dashboard Interface

```
+-----------------------------------------------------+
|                   [🧠 uOS DASHBOARD]                 |
+----------------------+------------------------------+
| 🌱 STEPS             |  📜 MISSIONS                |
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

* **\[Steps]**

  * Current steps taken during the user’s journey.
  * Reversible Steps indicated with ✅.
  * EOL Steps accumulate for Legacy determination.

* **\[Missions]**

  * Missions are *never* deleted, only completed.
  * Remain valid until transformed into a Legacy at EOL.
  * In-progress and future states tracked.

* **\[Legacy]**

  * Legacy = End-of-life Mission.
  * May be set by user during lifetime.
  * Converts at EOL condition met.

* **\[Location Map]**

  * Each tile links to a uKnowledge memory (past), active mission (present), or legacy (future).
  * Example: ⚔️ Wizard Tower → Active Mission → Editing Map Codex

* **\[System Status]**

  * Displays current AI mode, memory capacity, and whether containerized `uScript` services are active.

---

Next: Would you like this ASCII dashboard to become interactive via `[shortcodes]` calling `uScript` containers for live updates, or proceed with building the map tile rendering logic?
