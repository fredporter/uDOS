# uDOS DEV Mode — Specification Sheet

**Status:** Authoritative  
**Audience:** uDOS core developers / maintainers  
**Scope:** Development framework, logging, dev-rounds, and workflow integration

---

## 1. Repositories & Structure

### Core Repository
- **Public:** https://github.com/fredporter/uDOS

### DEV Framework Repository
- **Public (optional submodule):** https://github.com/fredporter/uDOS-dev

When installed as a submodule:
```
uDOS/
└─ dev/   # git submodule → github.com/fredporter/uDOS-dev
```

**Hard rule:** the `uDOS-dev` repo contains **only** setup, install, integration, and framework documentation.  
No roadmaps, priorities, or future plans.

---

## 2. Public vs Local Boundaries (Non-Negotiable)

### Public / Commit-Safe
- `uDOS/dev/**` (from `uDOS-dev` submodule)
- user-facing documentation
- redacted examples and templates

### Local-Only / Never Committed
- `**/.dev/**` (repo-local, any depth)
- `~/dev/docs/**` (private long-form dev notes)
- `~/memory/logs/**` (canonical logs + devlogs)

---

## 3. Repo-Local `.dev/` Folders

### Purpose
Private, ephemeral development workspaces used for:
- dev-round inputs and outputs
- local plans, notes, and experiments
- prompt drafts and agent experiments
- build, test, and debug artefacts

### Placement
`.dev/` folders may exist anywhere:
```
uDOS/
├─ .dev/
├─ core/
│  └─ .dev/
└─ wizard/
   └─ .dev/
```

### Git Rules
Root `.gitignore` **must** include:
```
.dev/
**/.dev/
```

`.dev/` folders are included in **COMPOST** and **CLEAN** runs when DEV Mode is enabled.

---

## 4. `~/dev/docs` — Private Developer Documentation

### Role
A persistent, cross-repository documentation space for:
- dev summaries
- architectural decisions
- exploratory notes
- long-running analysis

### Expected Structure
```
~/dev/docs/
├─ README.md
├─ uDOS/
│  ├─ summaries/
│  ├─ decisions/
│  ├─ scratch/
│  └─ archive/
└─ shared/
   ├─ templates/
   └─ assets/
```

Always local. Always private.

---

## 5. Canonical Devlogs & Memory: `~/memory/logs`

### Decision
All system logs and devlogs are unified under:
```
~/memory/logs/
```

This path is the **authoritative source of truth** for:
- runtime diagnostics
- debugging and error handling
- dev-round inputs
- historical analysis

### Suggested Structure
```
~/memory/logs/
├─ uDOS/
│  ├─ core/
│  ├─ wizard/
│  ├─ api/
│  ├─ devlogs/
│  └─ errors/
└─ system/
```

---

## 6. Unified Log / Devlog Event Model

All logs and dev-authored devlog entries should normalise to the following schema:

- `timestamp`
- `source` (`core | wizard | api | dev`)
- `severity` (`debug | info | warn | error | critical`)
- `component`
- `event_type` (`exception | assertion | perf | test | deploy | note`)
- `message`
- `context` (key/value map)
- `repro` (steps or command)
- `links` (commit, file paths, references)

---

## 7. COMPOST / CLEAN — DEV Mode Behaviour

### Inputs
When DEV Mode is active:

**Always included**
- all discovered `**/.dev/**` folders

**Optionally included**
- `~/dev/docs/uDOS/**`
- `~/memory/logs/uDOS/**`

### Pipeline
```
Collect → Normalise → Deduplicate → Summarise → Act → Archive
```

### Outputs (Local-Only)
- `.dev/rounds/outputs/`
- `~/dev/docs/uDOS/summaries/`

---

## 8. DEV Rounds (Primary Unit of Progress)

A **DEV Round** is a bounded, repeatable loop:

```
Inputs → Analysis → Actions → Review → Outputs → Queue Next Round
```

Typical inputs:
- recent errors from `~/memory/logs`
- repo diffs
- `.dev/inbox` notes
- dev-authored devlogs

Outputs remain local unless explicitly sanitised for public release.

---

## 9. Four Speeds of Operation

### 1. Sprint
- multiple rounds per day
- aggressive automation
- urgent fixes and spikes

### 2. Run
- one round per day
- accelerated, disciplined delivery

### 3. Walk
- one round per week
- maintenance, refactors, documentation

### 4. Pace (uDOS Ideal)
- low and slow, consistent progress
- minimal resource use
- local-first inference
- compounding improvements

---

## 10. `/dev/` Submodule Detection

uDOS should:
- detect presence of `./dev/`
- verify it matches `uDOS-dev`
- enable DEV Mode enhancements if present

If absent, uDOS operates normally.

---

## 11. Final Invariants

- Public repos stay clean and timeless
- All real planning lives locally
- Logs and devlogs share one memory system
- DEV Rounds are the atomic unit of progress
- Pace mode is the long-term optimisation target
