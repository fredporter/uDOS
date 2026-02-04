# Vibe CLI Integration Roadmap Alignment

**Date:** February 3, 2026
**Status:** Analysis of Mistral Vibe CLI recommendations vs. current uDOS roadmap

## 🎯 Executive Summary

Mistral Vibe CLI installation yields **5 core workflow recommendations**. Our roadmap **partially covers 3**, **documents 1**, and **lacks explicit planning for 1**.

The **uCODE TUI** is the linchpin—it must become the unified entry point that bridges all these workflows.

---

## Vibe CLI Recommendations (From Installation Output)

From the Mistral Vibe setup flow, the CLI recommends:

### 1. **VS Code Integration** ✅ Partially Covered
**Vibe Recommendation:**
> "For VS Code: Start by adding Vibe CLI commands to your tasks.json or terminal."

**Current Status:**
- ✅ `tasks.json` exists with multiple task definitions
- ✅ Can execute via `./start_udos.sh` and helpers
- ❌ **Gap:** No explicit documentation linking `tasks.json` to Vibe CLI workflows
- ❌ **Gap:** No Vibe CLI command runners in `tasks.json` (only shell scripts)

**Roadmap Reference:**
- [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — References uCODE TUI as main entry
- No dedicated "VS Code + Vibe" integration doc

**Action Needed for uCODE TUI:**
```
Add tasks.json entries that:
- Invoke vibe directly (vibe chat, vibe --with-context)
- Route Vibe output through TUI form/panel system
- Log Vibe interactions to memory/logs/
```

---

### 2. **Obsidian or Notion Integration** ✅ Documented
**Vibe Recommendation:**
> "For Obsidian/Notion: Decide whether you want local (Obsidian) or cloud integration."

**Current Status:**
- ✅ **Obsidian integration planned:**
  - [dev/docs/howto/SECRETS-MANAGEMENT.md](dev/docs/howto/SECRETS-MANAGEMENT.md) mentions `NOTION_INTEGRATION_TOKEN`
  - [dev/docs/howto/OFFLINE-AI-SETUP.md](dev/docs/howto/OFFLINE-AI-SETUP.md) references Vibe CLI setup
- ✅ **Notion mentioned** in NOTIFICATION-HISTORY.md as cloud sync option
- ❌ **Gap:** No formal integration spec for either platform
- ❌ **Gap:** No uCODE TUI command to trigger Obsidian/Notion sync

**Roadmap Reference:**
- [docs/TUI-Vibe-Integration.md](docs/TUI-Vibe-Integration.md) — Mentions story→keystore→Vibe IO hooks but not Obsidian/Notion
- [dev/docs/howto/OFFLINE-AI-SETUP.md](dev/docs/howto/OFFLINE-AI-SETUP.md) — References Vibe but not document platform sync

**Action Needed for uCODE TUI:**
```
Create uCODE TUI commands:
- OBSIDIAN SYNC     → export memory/bank/*/story to local vault
- NOTION SYNC       → push tasks/status to Notion database
- DOCUMENT IMPORT   → pull .md files into memory/bank/
- Both should support scheduled runs (see below)
```

---

### 3. **Scheduling via Cron Jobs or CI/CD Pipelines** ✅ Covered
**Vibe Recommendation:**
> "For Scheduling: Set up cron jobs or CI/CD pipelines to automate tasks."

**Current Status:**
- ✅ **Cron support:** [dev/docs/howto/public-private-sync.md](dev/docs/howto/public-private-sync.md) references automation details
- ✅ **CI/CD mentioned:** Distribution layer supports container pipelines
- ✅ **Memory test scheduler:** [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) states TUI polls `~/memory/tests/` and runs `automation.py`
- ✅ **Daily cycles documented:** [dev/docs/howto/OFFLINE-AI-SETUP.md](dev/docs/howto/OFFLINE-AI-SETUP.md) and `docs/WIZARD-ROUND2-PLAN.md` mention 14-cycle automation schedule
- ❌ **Gap:** No uCODE TUI command to inspect/manage cron jobs
- ❌ **Gap:** No scheduler status dashboard in TUI

**Roadmap Reference:**
- ✅ [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — "Align the Next Round work with the *critical daily cycles*"
- ✅ Memory test scheduler integrated into TUI startup
- ✅ [docs/Mission-Scheduler-Integration.md](docs/Mission-Scheduler-Integration.md) — How Vibe CLI + mission scheduler trigger renderer/export jobs

**Action Needed for uCODE TUI:**
```
Create uCODE TUI commands:
- SCHEDULER LIST    → show all scheduled tasks + next run time
- SCHEDULER RUN [id] → trigger a job immediately
- SCHEDULER LOGS    → view execution history
- SCHEDULER ADD     → guided creation of new automation
- Wire to cron via .env + wizard-key-store for secret rotation
```

---

### 4. **Python/Bash Script Automation** ✅ Covered
**Vibe Recommendation:**
> "Combine Vibe CLI with Python/Bash scripts to create powerful automation."

**Current Status:**
- ✅ **Vibe integration:** [dev/docs/howto/OFFLINE-AI-SETUP.md](dev/docs/howto/OFFLINE-AI-SETUP.md) has `bin/Setup-Vibe.command`
- ✅ **Script executor:** [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — "Build script executor + safety guard" ✅ Done
- ✅ **Scripting support:** Core runtime supports `script` blocks with sandbox
- ✅ **Bash/Python examples:** [core/docs/](core/docs/) and [memory/tests/](memory/tests/) contain executable samples
- ❌ **Gap:** No uCODE TUI command to manage/list custom scripts
- ❌ **Gap:** No TUI integration for Vibe chat context injection

**Roadmap Reference:**
- ✅ [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — "ScriptExecutor, allowScripts guard, and runtime tests" implemented
- ✅ [core/README.md](core/README.md) — Documents `script` block support

**Action Needed for uCODE TUI:**
```
Create uCODE TUI commands:
- SCRIPT LIST       → show all scripts in memory/bank/scripts/
- SCRIPT RUN [name] → execute with Vibe context injection
- SCRIPT CREATE     → guided wizard for new script
- SCRIPT LOGS       → view execution output + errors
- VIBE CHAT [query] → invoke Vibe with uDOS context (--with-context)
```

---

### 5. **Core User Workflow: Markdown + Execution** ⚠️ Partially Covered
**Vibe Recommendation (implicit):**
> "The workflow connects Obsidian/Notion → Vibe CLI → scheduled execution → results back to documents."

**Current Status:**
- ✅ **Executable markdown:** Core runtime fully supports md scripts
- ✅ **Markdown I/O:** Story system reads/writes markdown
- ✅ **Memory bank structure:** [memory/bank/](memory/bank/) provides organized storage
- ✅ **Form system:** TUI form renderer works with markdown frontmatter
- ⚠️ **Gap:** No unified "document execution" command in TUI
- ⚠️ **Gap:** No results collection/aggregation to `06_RUNS/` from TUI (only from renderer)
- ⚠️ **Gap:** No "watch markdown files and auto-execute" feature in TUI

**Roadmap Reference:**
- ✅ [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — "Phase 1E document runner enhancements that aggregate section output"
- ✅ [core/README.md](core/README.md) — DocumentRunner implementation
- ⚠️ [docs/TUI-Vibe-Integration.md](docs/TUI-Vibe-Integration.md) — Plans story IO but not document execution loop

**Action Needed for uCODE TUI:**
```
Create uCODE TUI commands:
- EXECUTE [path]    → run markdown document, collect output
- EXECUTE WATCH     → watch memory/bank/ for changes, re-run on save
- EXECUTE LOG       → view past execution results
- EXECUTE EXPORT    → write results to 06_RUNS/ (like renderer does)
```

---

## 📋 Summary: Gap Analysis by Component

| Feature | Vibe Rec | Roadmap Status | uCODE TUI Status | Priority |
|---------|----------|----------------|------------------|----------|
| **VS Code tasks.json integration** | ✅ Recommend | ⚠️ Partial | ❌ Missing | HIGH |
| **Obsidian sync** | ✅ Recommend | ⚠️ Mentioned | ❌ Missing | HIGH |
| **Notion sync** | ✅ Recommend | ✅ Documented | ❌ Missing | HIGH |
| **Cron job scheduling** | ✅ Recommend | ✅ Implemented | ⚠️ No TUI commands | MEDIUM |
| **Scheduler status/logs** | (Implicit) | ⚠️ Logging only | ❌ Missing | MEDIUM |
| **Python/Bash scripting** | ✅ Recommend | ✅ Implemented | ⚠️ Limited TUI | MEDIUM |
| **Vibe chat integration** | ✅ Recommend | ⚠️ Setup only | ❌ Missing | HIGH |
| **Markdown document execution** | ✅ Recommend | ✅ Engine exists | ⚠️ Limited TUI | HIGH |
| **Execution results aggregation** | (Implicit) | ✅ Renderer does it | ⚠️ TUI limited | MEDIUM |

---

## 🎯 Recommended uCODE TUI Command Set

To fully integrate Vibe CLI workflows, add these TUI commands:

### Immediate (v1.3.2)
```
# Core workflow
EXECUTE [path]              Execute markdown document
EXECUTE WATCH              Watch + auto-execute on changes
EXECUTE LOG                View execution history

# Document platforms
OBSIDIAN SYNC              Sync memory/bank/ to Obsidian vault
NOTION SYNC                Sync tasks to Notion database
DOCUMENT IMPORT [source]   Import docs from filesystem/Notion

# Vibe integration
VIBE CHAT [query]          Chat with Vibe CLI (--with-context)
VIBE CONFIG                View/edit Vibe configuration
```

### Near-term (v1.3.3+)
```
# Scheduler management
SCHEDULER LIST             Show all scheduled tasks
SCHEDULER RUN [id]         Trigger job immediately
SCHEDULER LOG [id]         View job execution history
SCHEDULER ADD              Create new scheduled task

# Script management
SCRIPT LIST                Show available scripts
SCRIPT RUN [name]          Execute script with context
SCRIPT CREATE              Wizard for new script
SCRIPT LOG [name]          View script execution log

# Status & aggregation
STATUS WORKFLOWS           Show all document workflows
STATUS EXECUTIONS          Show recent execution runs
EXPORT RESULTS             Collect all outputs to 06_RUNS/
```

---

## 🔗 Cross-References to Existing Roadmap

### Already Planned (Keep in Sync)
- [docs/TUI-Vibe-Integration.md](docs/TUI-Vibe-Integration.md) — `.env` + Wizard keystore boundary
- [docs/Mission-Scheduler-Integration.md](docs/Mission-Scheduler-Integration.md) — Vibe CLI + mission scheduler
- [dev/docs/howto/OFFLINE-AI-SETUP.md](dev/docs/howto/OFFLINE-AI-SETUP.md) — Vibe CLI setup
- [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — v1.3.2+ milestones mention "App v1.3 refactor" + "TUI ↔ Vibe integration"
- [core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md](core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md) — Sonic as TUI entry point

### Should Reference This Analysis
- [docs/ROADMAP-TODO.md](docs/ROADMAP-TODO.md) — v1.3.2 milestone section
- [core/docs/](core/docs/) — New uCODE TUI command reference
- [docs/specs/uCODE.md](docs/specs/uCODE.md) — Add Vibe/Obsidian/Notion commands here

---

## ✅ Action Plan for uCODE TUI

**Owner:** Core TUI / Sonic extension (per v1.3.3 roadmap: "Refactor Sonic extension as primary entry to uDOS TUI v1.3")

**Milestones:**
1. **v1.3.2:** Add EXECUTE, OBSIDIAN SYNC, NOTION SYNC, VIBE CHAT commands
2. **v1.3.3:** Add SCHEDULER and SCRIPT management commands
3. **v1.3.4:** Add STATUS/EXPORT aggregation commands

**Tests:**
- Integration tests for each Vibe CLI wrapper command
- Markdown execution roundtrip (read → execute → log → aggregate)
- Scheduler trigger verification
- Obsidian/Notion API mock tests

**Documentation:**
- Update [docs/specs/uCODE.md](docs/specs/uCODE.md) with all new commands
- Add examples in [docs/examples/](docs/examples/)
- Create [docs/howto/vibe-workflows.md](docs/howto/vibe-workflows.md)

---

## 📌 Key Insight: uCODE TUI is the Hub

The current architecture has **separate lanes** (Core TUI, Wizard, App, Sonic). Vibe CLI works best when there's **one unified entry point** that:
1. Reads from `.env` + Wizard keystore (already planned in [docs/TUI-Vibe-Integration.md](docs/TUI-Vibe-Integration.md))
2. Wraps Vibe CLI commands with context injection
3. Bridges document platforms (Obsidian, Notion, local markdown)
4. Manages scheduled tasks + scripting
5. Aggregates results back to memory/logs/

**This is exactly what v1.3.3's "Sonic → TUI Entry Point" section describes.**

The roadmap is **sound**; this analysis just makes the **Vibe CLI alignment explicit**.
---

## 🎉 Round 3 Status Update (Feb 4, 2026)

**Commit:** `caa88fe` — feat(v1.3): Add TypeScript renderer, theme packs, and vault scaffold

### ✅ Delivered

**v1.3 Core Infrastructure:**
- TypeScript renderer pipeline (MD→HTML) with deterministic output
- Task indexer with SQLite backend
- 5 theme packs (prose, nes, c64, medium, teletext) with shell.html + theme.json
- Obsidian-compatible vault structure (01_KNOWLEDGE → 07_LOGS)
- Mission/job run reports → `vault/06_RUNS/`
- Contribution bundle system → `vault/contributions/`

**Wizard Services:**
- `/api/renderer/*` endpoints (15 routes)
  - GET /themes, /site, /missions, /contributions
  - GET /spatial/anchors, /places, /file-tags
  - POST /render, /contributions (with role guards)
- ContributionService (pending/approved/rejected workflow)
- Spatial parser + store (LocID validation, frontmatter extraction)
- Permission guards (contributor/editor/maintainer roles)

**Dashboard + Control Plane:**
- SvelteKit `web-admin/` with theme picker, mission queue, contribution review
- Wizard dashboard Round 3 panels: ModOverlayPanel, PluginDashboardPanel
- Fixed a11y warnings (label associations, button semantics, ARIA roles)
- Added tsconfig.json with verbatimModuleSyntax
- Clean build (no warnings)

**Documentation:**
- [docs/uDOS-v1-3.md](docs/uDOS-v1-3.md) — Primary v1.3 spec
- [docs/Theme-Pack-Contract.md](docs/Theme-Pack-Contract.md) — Shell slots + theme.json
- [docs/Vault-Contract.md](docs/Vault-Contract.md) — Write-back rules
- [docs/Mission-Job-Schema.md](docs/Mission-Job-Schema.md) — Job frontmatter
- [docs/Contributions-Contract.md](docs/Contributions-Contract.md) — Patch bundles
- [docs/Mission-Scheduler-Integration.md](docs/Mission-Scheduler-Integration.md) — Vibe + scheduler
- [docs/CSS-Tokens.md](docs/CSS-Tokens.md), [docs/Universal-Components-Contract.md](docs/Universal-Components-Contract.md)
- [wizard/docs/renderer-ui-standards.md](wizard/docs/renderer-ui-standards.md) — Integration guide

**Tests:**
- ✅ v1-3/core/tests/renderer.test.mjs (deterministic MD→HTML)
- ✅ v1-3/core/tests/renderer_cli.test.mjs (CLI + vault integration)
- ✅ v1-3/core/tests/task_indexer.test.mjs (SQLite task storage)

### 🔄 In Progress

**Renderer CLI Wiring:**
- Core CLI built and tested
- Wizard routes registered
- Dashboard UI components ready
- **Next:** Wire dashboard to `/api/renderer/*` (live preview)

**Grid Canvas (80×30 Text Rendering):**
- Spec complete ([v1-3/docs/07-grid-canvas-rendering.md](v1-3/docs/07-grid-canvas-rendering.md))
- Canvas primitives stubbed
- **Next:** Calendar day layout, table primitive, Vibe TUI integration

### 🎯 Next Round Priorities

1. **Wire Renderer API → Dashboard** — Connect web-admin/ and wizard/dashboard to `/api/renderer/*`
2. **Grid Canvas MVP** — 80×30 calendar + table layouts for Vibe CLI output
3. **Obsidian Sync Command** — `OBSIDIAN SYNC` in uCODE TUI (export memory/bank/ → vault/)
4. **Scheduler Dashboard** — `SCHEDULER LIST/RUN/LOGS` commands + UI panel
5. **Vibe Chat Wrapper** — `VIBE CHAT [query]` command with context injection

### 📊 Alignment Score

| Component | Before Round 3 | After Round 3 | Target v1.3.3 |
|-----------|----------------|---------------|---------------|
| Renderer pipeline | ❌ Missing | ✅ Complete | ✅ |
| Theme packs | ❌ Missing | ✅ 5 themes | ✅ |
| Vault structure | ⚠️ Partial | ✅ Complete | ✅ |
| Mission/job schema | ⚠️ Documented | ✅ Implemented | ✅ |
| Contribution workflow | ❌ Missing | ✅ API + service | ✅ |
| Spatial metadata | ⚠️ Core only | ✅ Wizard routes | ✅ |
| Control plane UI | ❌ Missing | ✅ SvelteKit admin | ✅ |
| uCODE TUI commands | ⚠️ Limited | ⚠️ No new cmds | 🎯 v1.3.3 |
| Vibe CLI integration | ⚠️ Setup only | ⚠️ Planned | 🎯 v1.3.3 |
| Scheduler UI | ❌ Missing | ❌ Planned | 🎯 v1.3.3 |

**Round 3 delivered the data layer; Round 4 delivers the TUI commands.**