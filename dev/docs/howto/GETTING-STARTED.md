# Dev Workspace Getting Started

Updated: 2026-03-04

This is the contributor entry point for the v1.5 `@dev` workspace.

## Setup

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
uv sync --extra udos-wizard --dev
UV_PROJECT_ENVIRONMENT=.venv uv run ./uDOS.py SETUP
```

## Open The Workspace

```bash
code dev/ops/templates/uDOS-dev.code-workspace
```

Use the workspace folders as follows:

- `uDOS`: runtime root
- `@dev`: contributor governance and templates
- `@docs`: contributor doc tree
- `@goblin`: distributable dev scaffold and testing-server layer

## Read In Order

- `dev/docs/root-governance/AGENTS.md`
- `dev/AGENTS.md`
- `dev/ops/AGENTS.md`
- `dev/docs/DEV-MODE-POLICY.md`
- `dev/docs/specs/DEV-WORKSPACE-SPEC.md`
- `dev/docs/howto/VIBE-Setup-Guide.md`

## Working Rules

- standard runtime work goes through `ucode`
- Dev Mode work goes through Wizard-gated `vibe`
- root `docs/` is not the place for contributor-only material
- mature contributor decisions should be advanced into `dev/docs/specs/`, `dev/docs/features/`, or `dev/docs/howto/`
- local-only work belongs in ignored `/dev` paths until promoted
