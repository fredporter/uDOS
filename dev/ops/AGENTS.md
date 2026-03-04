# AGENTS.md — @dev Operations

Last Updated: 2026-03-04
Milestone: v1.5 Contributor Operations Consolidation
Status: Active

---

## Purpose

`dev/ops/` is the canonical contributor operations area for `@dev`.

It owns:
- contributor mission state
- contributor execution log
- contributor task and completion tracking
- shared contributor workspace/editor instructions
- reusable scheduler and workflow templates for Dev Mode

It does not own:
- runtime logic
- public operator docs
- production subsystem governance outside contributor operations

---

## Required Files

- `README.md`
- `AGENTS.md`
- `DEVLOG.md`
- `project.json`
- `tasks.md`
- `tasks.json`
- `completed.json`
- `templates/uDOS-dev.code-workspace`
- `templates/copilot-instructions.md`

---

## Rules

- Keep contributor planning and completion evidence here.
- Keep machine-readable contributor task state in `tasks.json`.
- Keep human-readable contributor narrative in `DEVLOG.md` and `tasks.md`.
- Keep shared Codex/Copilot/VS Code instructions aligned to the same contributor workflow.
- Do not duplicate runtime ownership from `core/` or `wizard/`.

---

End of File
