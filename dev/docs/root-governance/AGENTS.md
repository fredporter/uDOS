# AGENTS.md — uDOS Root Governance

Last Updated: 2026-03-05
Milestone: v1.5 Python Runtime Consolidation
Status: Active

---

## 1. Purpose

This file defines the authoritative behavioural and architectural rules for all OK Agents, OK Assistants, OK Helpers, OK Models, and OK Providers operating within the uDOS repository.

This document governs:

- Architecture boundaries
- Runtime separation
- OK Agent integration rules
- Vibe-CLI interaction model
- ucode command enforcement
- Branding terminology policy

Deeper scoped AGENTS.md files override this document within their folder scope.

---

## 2. Branding & Terminology Policy (Mandatory)

uDOS does NOT use the term "AI".

Approved terms:
- OK Assistant
- OK Agent
- OK Helper
- OK Model
- OK Provider
- Agent / Helper / Model / Provider / Assistant

Prohibited:
- AI (in documentation, code comments, commit messages, CLI output, or user interfaces)

If legacy terminology exists, it must be refactored.

---

## 3. Core Architecture Model

uDOS consists of clearly separated layers:

### Core (Minimal / Deterministic)
- Stdlib Python only
- No external networking logic
- No web responsibilities
- Deterministic execution
- Logging centralised
- No hidden runtime side-effects

### Wizard (Extended / Networked)
- Shared `uv` + `/.venv` runtime
- Networking + web responsibilities
- OK Provider integrations
- Extended automation
- External service interaction

### TypeScript Runtime (If Enabled)
- Lightweight execution partner
- No duplication of Python core logic
- Works alongside core, not replacing it

Cross-boundary violations are prohibited.

---

## 4. Vibe-CLI Integration Model

Mistral Vibe-CLI is the official TUI interaction layer.

All terminal-based OK Agent interactions must route through:

User
↓
Vibe-CLI
↓
OK Provider / OK Model
↓
ucode commands
↓
uDOS subsystems

Rules:
- No direct mutation of subsystems outside command boundary.
- OK Agents must emit ucode-compatible instructions where possible.
- Raw script dumping is discouraged if a ucode command exists.

Vibe-CLI is the canonical interaction bridge.

---

## 5. ucode Command Enforcement

ucode is the automation interface for uDOS.

OK Agents must:

- Prefer emitting valid UCODE commands.
- Avoid bypassing logging hooks.
- Avoid direct file manipulation unless explicitly required.
- Respect core vs wizard boundaries.

If a subsystem exposes a command, use it.

---

## 6. Logging Model

All logs are centralised:

~/memory/logs/

Rules:
- No shadow logging systems.
- No duplicate logging frameworks.
- Dev verbosity must be suppressible in production mode.
- Logging API must be respected.

---

## 7. Binder System

Binders group related projects.

Each Binder must contain:

- AGENTS.md
- DEVLOG.md
- project.json
- tasks.md
- completed.json
- sandbox/
- .compost/

Binder runtime policy:
- The global `@sandbox` workspace is deprecated and must not be reintroduced.
- Work-in-progress files, references, workflow JSON, contacts, and temp/test assets belong in the binder-local `sandbox/`.
- Binder-local archive/backup/trash history belongs in binder-local `.compost/`.
- Final publish/submission JSON artifacts are rendered outside `sandbox/`.

Binder AGENTS.md may refine behaviour but cannot contradict root architecture.

---

## 8. Milestone Governance

AGENTS.md must reflect:

- Confirmed architecture
- Fully tested systems (100% passing)
- Pushed milestone state

AGENTS.md must NOT contain:
- Speculation
- Roadmaps
- TODO items
- Historical commentary

Milestone completion requires:
1. Update relevant AGENTS.md files
2. Update DEVLOG.md
3. Move tasks to completed.json
4. Remove stale architectural guidance

---

## 9. OK Agent Behaviour Constraints

OK Agents operating within uDOS must:

- Read nearest AGENTS.md before generating code
- Prefer deeper scoped AGENTS.md over root
- Not reintroduce deprecated patterns
- Not duplicate subsystems
- Not bypass ucode
- Not violate core/wizard separation
- Not generate legacy architecture
- Not use prohibited terminology

If instructions conflict:
→ Prefer deeper scoped AGENTS.md.

---

## 10. Drift Prevention

- Keep AGENTS.md concise and authoritative
- Audit quarterly
- Update immediately after milestone completion
- Remove obsolete patterns immediately

Architecture truth lives here.
Speculation lives elsewhere.

---

End of File
