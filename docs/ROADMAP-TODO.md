# Roadmap TODO Tracker

This live tracker lists the remaining development items referenced by `docs/ROADMAP.md` and the new `ROUNDS-3-10` spec. Update statuses as work progresses.

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Clean up Wizard dashboard navigation | Wizard | Done | Round 2 quick win: removed Setup menu from top nav and hamburger menu; rebuilt production assets. |
| Finish Wizard Notion UI + plugin dashboard | Wizard | In progress | Round 3 components (Notion blocks, plugin cards, mod UI). |
| Implement Wizard dataset table + chart UI | Wizard | Pending | Requires `/api/data/*` endpoints from Round 4 doc. |
| Prototype Canvas-based teletext renderer | Wizard | Pending | Round 5 NES button recommendation needs final decision. |
| Harden Beacon Portal + Sonic device catalog APIs | Wizard/Sonic | Pending | Round 6 quota + VPN tasks. |
| Migrate Goblin binder/Sonic features to Wizard | Goblin/Open | Experimental | Round 7 experiments waiting consolidation. |
| Ship plugin manifest service + registry | Wizard/Extensions | Pending | Round 8 plugin architecture + mod overlay loader. |
| Begin App Typo Editor + converters | App | Early dev | Round 9 Tauri + converter pipeline. |
| Build Groovebox Songscribe stack | Wizard | Planning | Round 10 Songscribe Markdown, audio synthesis, sample libs. |
| Update `docs/specs/ROUNDS-3-10.md` | Documentation | Done | New spec created to summarize the rounds. |
| Add DateTimeApproval + TUI story tests | Core | Done | Added regression coverage for approval/override flows. |
| Build script executor + safety guard | Core | Done | Added ScriptExecutor, allowScripts guard, and runtime tests. |
| Hot reload/self-heal training & docs | Core | Done | Automation logging plus `tui` stability guards added, hot-reload debouncing tested and documented. |
| Phase 1B DocumentRunner state/set coverage | Core | Done | DocumentRunner now exercises state/set blocks end-to-end and new TypeScript tests live in `memory/tests/phase1b_*.test.ts`; legacy `__tests__` moved into `memory/tests/legacy`. |
| Memory test scheduler & startup health hook | Core | Done | TUI now polls `~/memory/tests/` for new/changed test files, runs `automation.py`, and surfaces outcomes in the health summary/log. |

> 🔁 Keep this file synchronized with the next actions section of `docs/ROADMAP.md`.
