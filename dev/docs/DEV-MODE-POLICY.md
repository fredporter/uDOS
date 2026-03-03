# Dev Mode Policy

Updated: 2026-03-04

## Scope

Dev Mode is the permission-gated contributor lane for the v1.5 `@dev` workspace.

- Workspace alias: `@dev`
- Framework root: `/dev`
- Runtime owner: `wizard`
- Contributor TUI/tooling lane: `vibe`
- Standard runtime: `ucode`

`/dev` carries the tracked framework payload and workspace contract. It does not own runtime logic.

## Required Gates

Dev Mode is available only when all of the following are true:

- the `dev` certified profile is enabled
- the user has both `admin` and `dev_mode` permissions
- `/dev` contains the required tracked framework files
- Wizard has activated the Dev extension lane

## Required Tracked Payload

The `@dev` workspace must ship with:

- `README.md`
- `AGENTS.md`
- `DEVLOG.md`
- `project.json`
- `tasks.md`
- `completed.json`
- `extension.json`
- `docs/README.md`
- `docs/DEV-MODE-POLICY.md`
- `docs/specs/DEV-WORKSPACE-SPEC.md`
- `docs/howto/GETTING-STARTED.md`
- `docs/howto/VIBE-Setup-Guide.md`
- `docs/features/GITHUB-INTEGRATION.md`
- `goblin/README.md`

## Sync Policy

Only the versioned framework payload is intended for public sync from `/dev`:

- `/dev` governance files
- `dev/docs/`
- `dev/goblin/`

The following paths are explicitly local-only and must stay out of public sync:

- `dev/files/`
- `dev/relecs/`
- `dev/dev-work/`
- `dev/testing/`

## API Contract

Wizard exposes the Dev Mode control plane through `/api/dev/*`.

Core lifecycle endpoints:

- `GET /api/dev/status`
- `GET /api/dev/health`
- `POST /api/dev/activate`
- `POST /api/dev/deactivate`
- `POST /api/dev/restart`
- `POST /api/dev/clear`
- `GET /api/dev/logs`

Contributor workspace endpoints:

- `GET /api/dev/scripts`
- `POST /api/dev/scripts/run`
- `GET /api/dev/tests`
- `POST /api/dev/tests/run`

GitHub endpoints:

- `GET /api/dev/github/status`
- `GET /api/dev/github/pat-status`
- `POST /api/dev/github/pat`
- `DELETE /api/dev/github/pat`
- `GET /api/dev/webhook/github-secret-status`
- `POST /api/dev/webhook/github-secret`

## Failure Modes

- `403`: admin or Dev Mode permission missing
- `409`: Dev Mode is installed but inactive
- `412`: `/dev` is missing or the tracked framework payload is incomplete

## Workspace Rules

- Use `@dev` for contributor docs, Goblin fixtures, and Dev Mode templates.
- Use root `docs/` only for runtime, operator, feature, and public product documentation.
- Use `dev/goblin/` as the distributable dev scaffold and testing-server layer.
- Do not store runtime state, secrets, or personal scratch work in the tracked `@dev` payload.
