# Dev Workspace Docs

Updated: 2026-03-04

`dev/docs/` is the contributor documentation root for the v1.5 `@dev` workspace.

Root `docs/` is reserved for runtime, operator, feature, and product-facing documentation. If a document is about contributor workflows, Dev Mode governance, Goblin, GitHub sync, or the `vibe` contributor lane, it belongs here.

## Canonical Map

- Workspace policy:
  `DEV-MODE-POLICY.md`
- Workspace contract:
  `specs/DEV-WORKSPACE-SPEC.md`
- Contributor onboarding:
  `howto/GETTING-STARTED.md`
- Dev Mode tooling setup:
  `howto/VIBE-Setup-Guide.md`
- GitHub integration:
  `features/GITHUB-INTEGRATION.md`
- Restructure brief:
  `restructure-v-1-5.md`

## Tracked Payload

The public, versioned `@dev` payload is intentionally small:

- `/dev` governance files
- `dev/docs/`
- `dev/goblin/`

Everything else under `/dev` is local working state unless explicitly promoted into the tracked payload.

## Local-Only Areas

These paths are working areas and should not be treated as distributable framework content:

- `dev/files/`
- `dev/relecs/`
- `dev/dev-work/`
- `dev/testing/`

## Doc Rules

- Mature decisions should be advanced into `specs/`, `features/`, or `howto/` documents.
- Superseded contributor docs should be composted instead of left active in root `docs/`.
- `vibe` and Dev Mode documentation should reference the `@dev` workspace explicitly.
