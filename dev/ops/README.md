# @dev Operations

Updated: 2026-03-04

`dev/ops/` is the canonical contributor operations area for the v1.5 `@dev` workspace.

Use it for:

- contributor mission state
- roadmap-linked task tracking
- completion evidence
- contributor operation instructions
- shared Codex, Copilot, and VS Code workspace templates
- reusable dev scheduler, workflow, and utility templates

Canonical files:

- `AGENTS.md`
- `DEVLOG.md`
- `project.json`
- `tasks.md`
- `tasks.json`
- `completed.json`

Supporting subtrees:

- `templates/`: shared contributor templates and editor instructions
- `workspace/`: canonical VS Code/Codex workspace assets
- `scheduler/`: reusable dev schedule templates
- `workflows/`: contributor workflow templates
- `utils/`: small operational guides for the contributor toolchain
- `reports/`: generated release-readiness and preflight outputs
- `release/`: future-version release planning artifacts generated from audit output

Pre-release automation command surface:

- `./bin/udos doctor`
- `./bin/udos audit --target-version v1.6`
- `./bin/udos release-check`

By default these commands write Dev Mode artifacts to:

- `dev/ops/reports/udos_pre_release_audit.json`
- `dev/ops/release/<target_version>/future_release_plan.json`
