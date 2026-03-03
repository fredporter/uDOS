# Wizard And `@dev`

Updated: 2026-03-04

Wizard owns the live Dev Mode control plane for the v1.5 `@dev` workspace.

## Ownership

Wizard is responsible for:

- Dev Mode activation and deactivation
- permission gates
- contributor script and test execution
- GitHub PAT and webhook secret management
- reporting `@dev` workspace health and status

`/dev` provides the tracked framework payload. It does not host a separate runtime.

## Control Surface

Use the Wizard Dev Mode screen or `/api/dev/*` routes to manage:

- workspace status
- activation state
- contributor scripts and tests
- GitHub integration state

## Workspace Expectations

Wizard expects the `@dev` payload to include:

- `/dev` governance files
- `dev/docs/`
- `dev/goblin/`

If the tracked payload is incomplete, Wizard should report the workspace as unavailable rather than silently falling back.
