# Dev Workspace Templates

Updated: 2026-03-04

These templates are safe defaults for the v1.5 `@dev` workspace.

## Workspace Template

Use [uDOS-dev.code-workspace](/Users/fredbook/Code/uDOS/dev/ops/templates/uDOS-dev.code-workspace) as the canonical contributor workspace.

Expected folders:

- `uDOS`
- `@dev`
- `@docs`
- `@goblin`

## Task Template

Contributor tasks should describe:

- runtime lane touched
- `@dev` documentation updates
- Goblin fixture changes, if any
- verification performed

Example:

```markdown
# Task

- Runtime lane: `wizard`
- `@dev` impact: update `dev/docs/howto/...`
- Goblin impact: none
- Verification: `uv run python -m pytest ...`
```

## Doc Promotion Template

When promoting a contributor decision:

```markdown
# Promotion

- Source note:
- Destination:
- Why it belongs in tracked `@dev`:
- What was composted or removed:
```

## Goblin Fixture Template

Use `dev/goblin/` for distributable fixtures only:

- `server/` for server-layer config stubs
- `seed/` for reusable seed payloads
- `scenarios/` for repeatable test scenarios
- `test-vault/` for tracked vault fixtures
