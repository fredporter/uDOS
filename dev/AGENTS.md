# AGENTS.md — Dev Mode Extension Framework

Last Updated: 2026-03-03
Milestone: v1.5 Dev Mode Rebaseline
Status: Active

---

## Purpose

The `/dev` subsystem is the installed Dev Mode extension framework for contributor workflows.

It exists for:
- contributor roadmaps
- contributor task tracking
- contributor governance files
- extension metadata
- distro/template framework content

---

## Required Files

`/dev` must contain:
- `AGENTS.md`
- `README.md`
- `extension.json`
- `ops/README.md`
- `ops/AGENTS.md`
- `ops/DEVLOG.md`
- `ops/project.json`
- `ops/tasks.md`
- `ops/tasks.json`
- `ops/completed.json`
- `ops/templates/uDOS-dev.code-workspace`
- `ops/templates/copilot-instructions.md`
- `docs/README.md`
- `docs/DEV-MODE-POLICY.md`
- `docs/decisions/README.md`
- `docs/devlog/README.md`
- `docs/roadmap/ROADMAP.md`
- `docs/tasks/README.md`
- `docs/specs/DEV-WORKSPACE-SPEC.md`
- `docs/howto/GETTING-STARTED.md`
- `docs/howto/VIBE-Setup-Guide.md`
- `docs/features/GITHUB-INTEGRATION.md`
- `goblin/README.md`
- `goblin/tests/README.md`

---

## Content Policy

`/dev` must contain only:
- contributor planning
- contributor governance
- contributor documentation
- contributor decisions, roadmaps, and task-management indexes
- extension templates and metadata
- distro-facing Dev Mode framework content
- distributable Goblin fixtures

`/dev` must not contain:
- primary runtime logic
- standard-user product planning
- production subsystem ownership that belongs in `core/` or `wizard/`

---

## Local vs Remote Split

`/dev` is the versioned extension scaffold and distro template root.

Local mutable work must remain separate from the remote template truth.

Allowed local-only working directories:
- `dev/files`
- `dev/relecs`
- `dev/dev-work`
- `dev/testing`

These are working areas only, not the canonical extension template payload.

Tracked sync payload:
- `/dev` governance files
- `dev/ops/`
- `dev/docs/`
- `dev/goblin/`
- `dev/goblin/tests/`

---

## Runtime Boundary

- Dev Mode is an extension lane, not the default runtime.
- `ucode` remains the standard runtime path.
- `vibe` is contributor-only Dev Mode tooling.
- Wizard owns Dev Mode install, uninstall, activation, deactivation, and GitHub sync behavior.
- If runtime logic is needed, implement it in `wizard/` or `core/`, not in `/dev/`.
- `dev/goblin/` is the distributable dev scaffold and testing-server layer.
- `dev/goblin/tests/` is the tracked overlay test lane for contributor and experimental features layered over Wizard.

---

End of File
