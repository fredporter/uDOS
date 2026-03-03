# GitHub Integration

Updated: 2026-03-04

## Purpose

GitHub integration for v1.5 Dev Mode is owned by Wizard and scoped to the `@dev` workspace.

The goal is to sync the tracked contributor payload without leaking local-only work areas.

## Managed Surface

Wizard manages GitHub integration through `/api/dev/*`:

- repository status via `GET /api/dev/github/status`
- PAT storage via `GET/POST/DELETE /api/dev/github/pat`
- webhook secret status and generation via `GET/POST /api/dev/webhook/github-secret*`

## Sync Rules

GitHub sync for the `@dev` lane should include only:

- `/dev` governance files
- `dev/docs/`
- `dev/goblin/`

GitHub sync must exclude:

- `dev/files/`
- `dev/relecs/`
- `dev/dev-work/`
- `dev/testing/`
- secrets, tokens, caches, runtime artifacts, and personal scratch content

## Operator Expectations

- Activate the Dev extension lane before using GitHub controls.
- Store GitHub credentials in Wizard-managed secrets, not in `/dev`.
- Treat `dev/goblin/` as the publishable test scaffold.
- Treat local test scripts and sandboxes as private working state until promoted.
