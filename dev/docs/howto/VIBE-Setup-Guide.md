# Vibe Setup Guide

Updated: 2026-03-04

Use this guide only for the v1.5 `@dev` contributor lane. `vibe` is not the standard runtime.

## Preconditions

- root runtime installed with `uv sync --extra udos-wizard --dev`
- `dev` certified profile enabled
- `admin` and `dev_mode` permissions granted
- Wizard Dev Mode lane activated

## Workspace

Open the contributor workspace file:

```bash
code ucode-dev.code-workspace
```

That workspace exposes:

- repo root as `uDOS`
- contributor docs as `@dev`
- Goblin scaffold as `@goblin`
- contributor doc tree as `@docs`

## Runtime Rules

- use `ucode` for standard runtime commands
- use `vibe` only for contributor workflows inside the active Dev Mode lane
- keep contributor docs and templates in `@dev`
- keep local-only scratch work out of the tracked `@dev` payload

## First Checks

```bash
uv run ./uDOS.py STATUS
printf 'STATUS\n' | ./bin/vibe
printf 'HEALTH\n' | ./bin/vibe
```

If `vibe` fails, verify the Dev Mode controls in Wizard and review `dev/docs/DEV-MODE-POLICY.md`.
