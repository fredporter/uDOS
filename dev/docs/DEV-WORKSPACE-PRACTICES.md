# Dev Workspace Practices

Updated: 2026-03-04

This guide defines how contributors should work inside the v1.5 `@dev` workspace.

## Core Rule

Treat `@dev` as a tracked framework payload, not a private project sandbox.

Tracked:

- `/dev` governance files
- `dev/docs/`
- `dev/goblin/`

Local-only:

- `dev/files/`
- `dev/relecs/`
- `dev/dev-work/`
- `dev/testing/`

## Workflow Pattern

1. Make runtime and operator changes in `core/`, `wizard/`, or other product lanes.
2. Record contributor-facing rules and setup changes in `dev/docs/`.
3. Put distributable dev fixtures in `dev/goblin/`.
4. Keep temporary scripts, experiments, and scratch notes in ignored local-only `@dev` paths until they are ready to promote.

## Documentation Rules

- Root `docs/` is for runtime, operator, feature, and public product material.
- `dev/docs/` is for contributor onboarding, Dev Mode policy, Goblin, workspace rules, and contributor GitHub integration.
- Mature contributor decisions should be advanced into `dev/docs/specs/`, `dev/docs/features/`, or `dev/docs/howto/`.
- Superseded contributor docs should be composted or deleted, not left active beside replacements.

## Git Hygiene

- Do not widen tracked `/dev` content casually.
- Do not commit secrets, caches, build outputs, `node_modules`, or ad hoc workspaces under `/dev`.
- If a new `@dev` file should sync publicly, update the workspace contract and ignore rules in the same change.

## Promotion Rule

Before moving anything from a local-only `@dev` path into the tracked payload, verify:

- it is generic rather than personal
- it supports the contributor framework rather than one-off local work
- it belongs in `dev/docs/` or `dev/goblin/`

Use `dev/docs/specs/DEV-WORKSPACE-SPEC.md` as the source of truth.
