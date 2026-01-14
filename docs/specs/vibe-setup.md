---
title: Vibe (Offline Agent) Setup
status: active
version: 1.0.0
promoted: 2026-01-13
from: dev/roadmap/VibeCLI.md
---

# Vibe Setup: VS Code + Copilot + Offline Agent Context

> Preserve Agent instructions across devices using a shared context spine.

---

## Overview

Your setup uses **two kinds of instructions**:

1. **Project instructions** (portable, shared) → stored in repo (git)
2. **Personal/device instructions** (local, optional) → synced via VS Code Settings Sync or dotfiles

---

## 1. Project Instructions (In Repo)

These files travel with the repo on any machine and define how work happens:

### `.github/` Files
- **`AGENTS.md`** (root) — Canonical "how we work" rules
- **`.github/copilot-instructions.md`** — Repo-wide Copilot instructions
- **`.github/instructions/*.instructions.md`** — Scoped instructions with `applyTo` globs:
  - `core.instructions.md` (applies to `core/**`)
  - `app.instructions.md` (applies to `app/**`)
  - `wizard.instructions.md` (applies to `wizard/**`)
  - `extensions.instructions.md` (applies to `extensions/**`)

### Documentation Spine (`/docs`)
- **`_index.md`** — Engineering index and entry point
- **`roadmap.md`** — Now/Next/Later
- **`devlog/YYYY-MM.md`** — Monthly development notes
- **`decisions/ADR-*.md`** — Architecture Decision Records (immutable)
- **`specs/*.md`** — Finalized technical specifications
- **`howto/*.md`** — Repeatable procedures

**Outcome:** Any device that clones the repo gets the same "brain."

---

## 2. VS Code Settings Sync (Device-Specific)

VS Code has built-in Settings Sync to preserve personal tooling across devices.

### Setup (Once Per Device)
```
VS Code → Manage (⚙️) → Backup and Sync Settings… → turn on
```

### What Gets Synced
- Settings
- Extensions
- Keybindings
- Snippets
- UI state preferences

**Note:** Settings Sync doesn't sync extensions into SSH/devcontainers/WSL the same way, but for uDOS that's fine — your truth is in-repo.

---

## 3. Vibe Configuration (Offline Agent)

Vibe (Mistral's CLI agent) looks for config in this order:

1. `./.vibe/config.toml` (project-local)
2. `~/.vibe/config.toml` (user fallback)

### Best Practice
- **Public defaults** → `/.vibe/config.toml` (in repo)
- **Secrets/machine overrides** → `~/.vibe/config.toml` (local-only, never git)

This way:
- Every device gets consistent behavior by default
- Secrets never land in git

### Example `.vibe/config.toml`
```toml
[project]
name = "uDOS"
version = "1.0.2.0"

[model]
# Offline-first by default
provider = "ollama"
model = "devstral-small-2"
endpoint = "http://127.0.0.1:11434"

# Cloud routing disabled by default
# See docs/decisions/wizard-model-routing-policy.md
cloud_enabled = false

[context]
context_files = [
    "AGENTS.md",
    "docs/_index.md",
    "docs/roadmap.md",
    ".vibe/CONTEXT.md"
]

include = [
    "core/**/*.py",
    "app/**/*.{ts,svelte}",
    "wizard/**/*.py",
    "extensions/**/*.py",
    "docs/**/*.md",
    "*.md"
]

exclude = [
    "**/.dev/**",
    "**/.archive/**",
    "**/node_modules/**",
    "**/.venv/**",
    "**/dist/**",
    "**/target/**",
    "memory/**",
    "library/**",
    "**/__pycache__/**"
]
```

### `.vibe/CONTEXT.md` (Human-Readable Pointer)
```markdown
# uDOS Vibe Context

## Read First (in order)
1. AGENTS.md — How we work
2. docs/_index.md — Engineering index
3. docs/roadmap.md — Current priorities
4. docs/decisions/ — Architecture decisions
5. docs/devlog/ — Recent work

## Subsystem Entry Points
- **Core**: core/README.md + core/docs/
- **App**: app/README.md + app/docs/
- **Wizard**: wizard/README.md
- **Extensions**: extensions/README.md
```

---

## 4. Cloud Routing (OpenRouter) — Optional, Secure

If you add OpenRouter for "burst capacity":

### Store Credentials Safely
- **Never commit real keys**
- Store in one of:
  - `wizard/config/*.json` (local-only, gitignored)
  - OS keychain (macOS: Keychain; Linux: Secret Service; Windows: Credential Manager)
  - Environment variables (CI/CD)

### Preserve Behavior via Policy
- **Policy** (in repo): `docs/decisions/wizard-model-routing-policy.md`
- **Keys** (local only): Wizard config or keychain
- **Routing**: Handled by Wizard Server

This separation means:
- You preserve "offline first, cloud when needed" policy in git
- Keys never leak
- Devices can have different keys (e.g., different OpenRouter quotas)

---

## 5. Sync Across Devices: The Complete Recipe

### Via Git (Portable)
```
AGENTS.md
.github/copilot-instructions.md
.github/instructions/*.instructions.md
/docs/**
.vibe/config.toml (NO secrets)
```

### Via VS Code Settings Sync (Personal)
```
Extensions
Settings
Snippets
Keybindings
```

### Via Dotfiles Manager or Manual (Secrets + Endpoints)
```
~/.vibe/config.toml (user overrides, if any)
Wizard/OpenRouter keys (local-only)
OS keychain entries
```

---

## 6. Quick Reference: What Lives Where

| Content | Location | Sync Method | Notes |
|---|---|---|---|
| Working rules | AGENTS.md | Git ✅ | Portable across devices |
| Copilot instructions | .github/instructions/ | Git ✅ | Scoped per subsystem |
| Dev log | docs/devlog/ | Git ✅ | Monthly files |
| Architecture decisions | docs/decisions/ | Git ✅ | Immutable, links to commits |
| Project roadmap | docs/roadmap.md | Git ✅ | Single source of truth |
| Vibe defaults | .vibe/config.toml | Git ✅ | No secrets |
| Vibe user overrides | ~/.vibe/config.toml | Dotfiles/Manual | Per-device |
| OpenRouter keys | wizard/config/ | Keychain/Env | Never git |
| VS Code settings | Settings Sync | VS Code Sync | Per-device UI prefs |
| Extensions list | Settings Sync | VS Code Sync | Keeps tooling consistent |

---

## 7. Checklist: Activate This Setup

- [ ] Review `.vibe/config.toml` (already in repo)
- [ ] Review `.vibe/CONTEXT.md` (updated below)
- [ ] Run Vibe to confirm Ollama/Devstral is available:
  ```bash
  vibe chat "Hello, what is uDOS?"
  ```
- [ ] Enable VS Code Settings Sync (one time, per device)
- [ ] Confirm `.github/instructions/` exists and is scoped correctly
- [ ] Add any personal overrides to `~/.vibe/config.toml` (if needed)

---

## 8. Why This Matters

- **Offline-first**: Devstral runs locally; cloud is optional
- **Portable**: Git repo is self-contained; new device = same context
- **Secure**: Keys stay local; no secrets in git
- **Flexible**: Different devices can have different quotas/keys
- **Scalable**: Vibe, VS Code, and Copilot all read the same truth

---

*Promoted from: dev/roadmap/VibeCLI.md (2026-01-13)*  
*Status: Active (v1.0.0)*
