# Dev Workspace Docs

Updated: 2026-03-04

`dev/docs/` is the contributor documentation root for the v1.5 `@dev` workspace.

Root `docs/` is reserved for runtime, operator, feature, and product-facing documentation. If a document is about contributor workflows, Dev Mode governance, Goblin, GitHub sync, Codex/Copilot/VS Code contributor setup, or the `vibe` contributor lane, it belongs here.

## Canonical Map

- Workspace policy:
  `DEV-MODE-POLICY.md`
- Workspace contract:
  `specs/DEV-WORKSPACE-SPEC.md`
- Stable release program:
  `specs/V1-5-STABLE-RELEASE-PROGRAM.md`
- Dev Mode compatibility inventory:
  `specs/V1-5-DEV-MODE-COMPAT-INVENTORY.md`
- Contributor operations:
  `../ops/README.md`
- Contributor decisions:
  `decisions/README.md`
- Contributor roadmap:
  `roadmap/ROADMAP.md`
- Contributor devlog index:
  `devlog/README.md`
- Contributor shared submissions:
  `contributors/README.md`
- Contributor task-management index:
  `tasks/README.md`
- Contributor onboarding:
  `howto/GETTING-STARTED.md`
- Dev Mode tooling setup:
  `howto/VIBE-Setup-Guide.md`
- GitHub integration:
  `features/GITHUB-INTEGRATION.md`
## Tracked Payload

The public, versioned `@dev` payload is intentionally small:

- `/dev` governance files
- `dev/ops/`
- `dev/docs/`
- `dev/goblin/`
- `dev/goblin/tests/`

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
- Draft contributor decisions/devlogs/roadmap proposals should start in `contributors/` and be promoted when stable.
