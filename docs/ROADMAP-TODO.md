# Roadmap TODO Tracker

This live tracker lists the remaining development items referenced by `docs/ROADMAP.md` and the new `ROUNDS-3-10` spec. Update statuses as work progresses.

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Finish Wizard Notion UI + plugin dashboard | Wizard | In progress | Round 3 components (Notion blocks, plugin cards, mod UI). |
| Implement Wizard dataset table + chart UI | Wizard | Pending | Requires `/api/v1/data/*` endpoints from Round 4 doc. |
| Prototype Canvas-based teletext renderer | Wizard | Pending | Round 5 NES button recommendation needs final decision. |
| Harden Beacon Portal + Sonic device catalog APIs | Wizard/Sonic | Pending | Round 6 quota + VPN tasks. |
| Migrate Goblin binder/Sonic features to Wizard | Goblin/Open | Experimental | Round 7 experiments waiting consolidation. |
| Ship plugin manifest service + registry | Wizard/Extensions | Pending | Round 8 plugin architecture + mod overlay loader. |
| Begin App Typo Editor + converters | App | Early dev | Round 9 Tauri + converter pipeline. |
| Build Groovebox Songscribe stack | Wizard | Planning | Round 10 Songscribe Markdown, audio synthesis, sample libs. |
| Update `docs/specs/ROUNDS-3-10.md` | Documentation | Done | New spec created to summarize the rounds. |
| Add DateTimeApproval + TUI story tests | Core | Done | Added regression coverage for approval/override flows. |
| Build script executor + safety guard | Core | Done | Added ScriptExecutor, allowScripts guard, and runtime tests. |
| Hot reload/self-heal training & docs | Core | Pending | Highlight services/hot-reload and training so TUI stays stable for future rounds. |

> 🔁 Keep this file synchronized with the next actions section of `docs/ROADMAP.md`.
