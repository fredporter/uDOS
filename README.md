# uDOS v1.3

Offline-first OS layer for knowledge systems, tools, and portable environments.

**Core concept:** uDOS is a local Obsidian companion runtime for organizing vault workflows with `@workspace` and `@binder` contexts, fractal/layered filesystem structures, knowledge trees, and digital garden publishing patterns.

**Status:** v1.3.13 (dev cycle); latest released manifest remains v1.3.12 while monorepo continues toward v1.4 Wizard web view/rendering capabilities
**Primary target:** Alpine Linux (Sonic USB)
**Also supported:** macOS, Ubuntu, Windows (dev)

**Start here:**
- **Users/Beginners:** `wiki/Start-Here.md`
- **Developers:** `docs/README.md`
- **Release manifest (latest release):** `releases/v1.3.12.yml`

---

## Quick Start

```bash
./bin/ucli
```

Common first commands:
- `HELP`
- `STATUS`
- `WIZARD start`

Use [Obsidian](https://obsidian.md) as your editor/vault reader; uDOS works as the runtime and organization layer over the same files (no sync required).

Vault/data split:
- `vault/` is a distributable markdown scaffold (template only)
- `core/framework/seed/vault/` is canonical starter seed content
- `memory/vault/` is runtime user markdown data (local, not committed)
- `memory/` is runtime state (logs, cache, db, private credentials)

---

## What Ships in v1.3

- **Core** — Deterministic Markdown → HTML runtime (offline)
- **Wizard** — LAN gateway (AI routing, plugins, sync)
- **Sonic** — Bootable USB builder
  Repo: `https://github.com/fredporter/uDOS-sonic`
- **Obsidian Companion App** — private pre-release repo: `https://github.com/fredporter/oc-app`
- **Extensions** — Container/plugin ecosystem
- **Knowledge** — Static reference catalog

### Sonic Round Status

Sonic development round is complete in this monorepo:
- Bootloader profiles + reboot routing
- Windows launcher mode selector
- Device auto-detection + recommendations
- Media console workflows (Kodi + WantMyMTV)
- Windows gaming profile automation
- Release artifacts/checksum/signing readiness checks
- Wizard GUI Sonic entrypoints end-to-end

See:
- `docs/roadmap.md` (Sonic section complete)
- `docs/howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md`

## Core + Wizard Relationship

- **Core** is the runtime. It can operate without Wizard (limited features).
- **Wizard** is the connected extensions layer (networking, GUI, routing) and requires Core.
- Most extensions/add-ons expect both Core and Wizard to be present.

---

## Repo Layout (Public)

```
core/        TypeScript runtime + Python TUI
wizard/      API gateway + services
sonic/       Bootable USB builder (Sonic)
extensions/  Transport API definitions
library/     Container definitions
knowledge/   Static catalog
wiki/        User docs
docs/        Architecture + specs
```

## Monorepo Direction

- uDOS monorepo is currently under development.
- Obsidian Companion has been separated into `fredporter/oc-app` (private pre-release).
- Planned integration path is through Wizard web view/rendering capabilities rather than an in-repo `/app` module.

---

## Documentation

- `wiki/README.md` — user guides
- `docs/README.md` — canonical docs index and flow
- `docs/roadmap.md` — canonical roadmap
- `docs/howto/UCODE-COMMAND-REFERENCE.md` — canonical command surface
- `docs/DOCS-SPINE-v1.3.md` — spine redirect
- `docs/decisions/VAULT-MEMORY-CONTRACT.md` — vault/template/runtime contract

Documentation archive:
- historical/superseded docs now live under `/.compost/<date>/archive/` (organic archive policy)
- operational backup/trash flows are centralized under `/.compost` (see `docs/COMPOST-POLICY.md`)

---

## uDOS Ultimate VS Code Workspace

**Brief:** Native CLI-First Dev Cockpit (GitHub CLI + Vibe CLI)

**Objective**

Configure VS Code as a self-contained uDOS development cockpit where:
- The integrated terminal is the primary execution surface
- GitHub CLI (`gh`) is the canonical interface to GitHub
- Vibe CLI (`vibe`) is the canonical interface to uDOS
- Copilot assists within this loop (not replacing it)
- The workspace mirrors GitHub's repo view while supporting local-only dev artefacts

This workspace is optimized for testing, debugging, hardening, patching, and shakedown rounds, with broader refactors handled in Codex.

**Workspace Structure (Multi-Root)**

The `uDOS-Ultimate.code-workspace` defines a multi-root workspace that may include:
- `uDOS/` — primary repo root (GitHub source of truth)
- `Wizard/` — Wizard Services / MCP server (if separate)
- Optional external roots: `memory/` or `memory/logs/` (local-only dev artefacts)

This allows:
- Explorer tree to match GitHub by default
- Local-only folders to remain visible without polluting Git

**Terminal-First Design (Critical)**

VS Code's integrated terminal is treated as native uDOS runtime, not a helper.

Requirements:
- `gh` available on PATH and authenticated
- `vibe` available on PATH or via repo wrapper (`./bin/vibe`)
- Correct Python venv / env activated per repo

Opening a terminal should feel equivalent to:

"I am now inside uDOS"

**GitHub CLI (gh) Integration**

`gh` is the only supported GitHub interface inside VS Code. It is used for:
- Authentication
- Repo and PR management
- Issues, reviews, releases
- Scriptable automation (preferred over webhooks)

Expectations:
- VS Code terminal inherits user's `gh` auth session
- No browser-based GitHub flows required during dev
- Copilot may suggest GitHub actions, but execution happens via `gh`

Typical flows:
- `gh repo view`
- `gh issue view <id>`
- `gh pr create`
- `gh pr checkout <id>`
- `gh pr review`

**Vibe CLI (vibe) Integration**

`vibe` is the native uDOS command surface, equivalent in importance to `gh`.
It is responsible for:
- Running tests
- Linting and validation
- Log inspection
- Shakedown / hardening routines
- Wizard / MCP lifecycle (where applicable)

Canonical entry point:
- `vibe ...` (global install), or
- `./bin/vibe ...` (repo-local wrapper - preferred)

The wrapper may:
- Activate the correct Python venv
- Set uDOS env vars (`UDOS_ROOT`, `UDOS_MEMORY`, etc)
- Normalize paths across machines

**VS Code Tasks: Bridging Editor to CLI**

Common uDOS workflows are exposed as VS Code Tasks, not extensions.

Minimum recommended tasks:
- `uDOS: Vibe Status`
- `uDOS: Run Tests`
- `uDOS: Lint`
- `uDOS: Shakedown`
- `uDOS: Tail Logs`
- `uDOS: Start Wizard Services`

Tasks are thin wrappers over `vibe` commands - no logic duplication.

**Copilot's Role (Explicitly Scoped)**

Copilot is used for:
- Inline code assistance
- Small refactors
- Explaining code
- Suggesting next steps

Copilot is not:
- The primary execution engine
- A replacement for `vibe` or `gh`
- Responsible for environment state

When Copilot hits limits or usage is conserved:
- Offline analysis is done via `vibe` / Wizard / local models
- Outputs are written to files (`memory/reports/*.md`) and reviewed in-editor

**File Explorer Behavior**

The workspace is configured so that:
- Git-ignored files are hidden by default (Explorer mirrors GitHub)
- Local-only dev folders are either separate workspace roots or symlinked into visible locations

This preserves a clean mental model:

"What I see is what's in Git - unless explicitly local."

**Outcome**

When complete, this workspace enables:
- One VS Code window = full uDOS dev cockpit
- Zero reliance on browser GitHub UI
- Identical workflows across VS Code terminal, external terminal, and CI
- Clear separation between precision work (VS Code + Copilot + CLI) and broad reasoning (Codex Mac app)

**Definition of Done**

- `uDOS-Ultimate.code-workspace` loads cleanly
- Integrated terminal can run `gh` and `vibe` immediately
- Core uDOS workflows are runnable via VS Code Tasks
- Explorer tree matches GitHub repo view
- No mandatory custom VS Code extensions beyond Copilot + language support

---

## Contributing

- `CONTRIBUTORS.md` (canonical)
- `CODE_OF_CONDUCT.md`
- `docs/CONTRIBUTION-PROCESS.md`

---

## License

See `LICENSE.txt`.
